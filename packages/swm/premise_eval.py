"""Premise evaluator — the autonomous backend for the guaranteed premise check.

Two-tier, fail-open:
  1. Rule-based floor (always runs, deterministic, zero deps): catches the cheapest
     high-value danger — a PROVISIONAL premise now being treated as settled/final in
     recent context (the dominant p3-style failure) + direct negation of a premise.
  2. Ollama upgrade (local llama3.1, no API cap): real semantic verdict per premise.
     If Ollama is down or returns junk, we keep the rule-based floor.

Never raises; returns a verdict list. A rule-detected `invalid` is a floor that the
LLM may not downgrade (don't let a small local model wave away a clear danger).
"""
from __future__ import annotations

import json
import re
import os
import urllib.request

# Backend tier: prefer Sonnet (premise-validity is a judgment task — quality first) via
# `claude -p`; fall back to local Ollama only if claude -p is unreachable. claude -p works
# on this machine (subscription OAuth), so Sonnet is the live primary. Override per-project
# with SWM_PREMISE_MODEL.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from shared.llm import extract as _llm_extract, Model as _Model, LLMExtractionError  # noqa: E402
from shared.models import PremiseCheckResult                                          # noqa: E402

CLAUDE_MODEL = os.environ.get("SWM_PREMISE_MODEL", "sonnet")
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:latest"

_HEDGE = re.compile(r"\b(provisional|pending|unverified|unvalidated|pre-audit|rough estimate|not (yet )?(final|confirmed|closed|audited)|may move|hasn'?t closed)\b", re.I)
_PROMOTE = re.compile(r"\b(final|finalized|confirmed|audited|locked|definitely|certain|settled|for sure)\b", re.I)
_STOP = {"the", "a", "an", "is", "are", "of", "to", "and", "our", "we", "it", "that", "this", "but", "not", "yet"}


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9$]+", text.lower()) if len(w) > 3 and w not in _STOP}


def _rule_screen(premises: list[dict], recent: str) -> dict[str, dict]:
    """Return {premise_id: {status, reason}} for premises the cheap screen can judge."""
    out: dict[str, dict] = {}
    recent_low = recent.lower()
    promote_present = bool(_PROMOTE.search(recent_low))
    for pm in premises:
        pid, text = pm.get("id", ""), pm.get("text", "")
        # provisional-promotion: premise was hedged AND recent context promotes a shared topic to "final/confirmed"
        if _HEDGE.search(text) and promote_present:
            shared = _content_words(text) & _content_words(recent)
            if shared:
                out[pid] = {"status": "invalid",
                            "reason": f"provisional premise now treated as settled (shared: {', '.join(list(shared)[:3])})"}
                continue
        # direct negation of a premise's core terms in recent context
        cw = list(_content_words(text))[:4]
        if cw and all(w in recent_low for w in cw) and re.search(r"\b(no longer|not true|was wrong|turned out|actually|incorrect)\b", recent_low):
            out[pid] = {"status": "challenged", "reason": "premise terms appear contradicted in recent context"}
    return out


def _build_prompt(premises: list[dict], recent: str) -> str:
    return (
        "You audit whether stated ASSUMPTIONS still hold given RECENT CONTEXT.\n"
        "For each premise return status: 'valid' (clearly still true), 'challenged' (unverified/uncertain), "
        "or 'invalid' (contradicted, or a provisional fact now treated as final).\n\n"
        "PREMISES:\n" + "\n".join(f"- [{p.get('id')}] {p.get('text')}" for p in premises) +
        "\n\nRECENT CONTEXT:\n" + recent[-2500:] +
        '\n\nReturn JSON exactly: {"verdicts":[{"id":"...","status":"valid|challenged|invalid","reason":"<short>"}]}'
    )


def _parse_verdicts(inner: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for v in inner.get("verdicts", []):
        if v.get("id") and v.get("status") in {"valid", "challenged", "invalid"}:
            out[v["id"]] = {"status": v["status"], "reason": str(v.get("reason", ""))[:200]}
    return out


def _shared_llm_eval(premises: list[dict], recent: str) -> dict[str, dict]:
    """Primary LLM backend via shared.llm.extract — subscription-native, no regex.

    Uses Sonnet for premise validity (judgment-heavy task).
    Raises LLMExtractionError on failure so _llm_eval can fall back to Ollama.
    """
    result = _llm_extract(
        system_prompt=(
            "You audit whether stated ASSUMPTIONS still hold given RECENT CONTEXT. "
            "For each premise return status: 'valid' (clearly still true), "
            "'challenged' (uncertain or unverified), or 'invalid' "
            "(contradicted, or a provisional fact now treated as final). "
            "Include a short reasoning for each verdict."
        ),
        schema=PremiseCheckResult,
        context=(
            "PREMISES:\n" +
            "\n".join(f"[{p.get('id')}] {p.get('text')}" for p in premises) +
            "\n\nRECENT CONTEXT:\n" + recent[-2500:]
        ),
        model=_Model.smart,   # Sonnet — premise validity is a judgment call
    )
    return {
        v.premise_id: {"status": v.status, "reason": v.reasoning[:200]}
        for v in result.verdicts
        if v.status in {"valid", "challenged", "invalid", "uncertain"}
    }


def _ollama_eval(premises: list[dict], recent: str, timeout: float = 25.0) -> dict[str, dict]:
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": _build_prompt(premises, recent),
                       "stream": False, "format": "json", "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read())
    return _parse_verdicts(json.loads(resp.get("response", "{}")))


def _llm_eval(premises: list[dict], recent: str) -> tuple[dict[str, dict], str]:
    """Tiered: try Haiku (best), fall back to local Ollama. Returns (verdicts, backend)."""
    try:
        v = _shared_llm_eval(premises, recent)
        if v:
            return v, "sonnet(shared.llm)"
    except (LLMExtractionError, Exception):
        pass
    try:
        return _ollama_eval(premises, recent), "ollama(llama3.1)"
    except Exception:
        return {}, "none"


def evaluate(premises: list[dict], recent: str, use_llm: bool = True) -> list[dict]:
    """Return [{premise_id, status, evidence, source}] for every premise. Never raises.

    use_llm=False → rule floor only (instant; for every-turn screening). use_llm=True
    → also run the tiered LLM semantic upgrade (Haiku via claude -p, else local Ollama;
    for the cadence pass)."""
    rule = _rule_screen(premises, recent)
    llm: dict[str, dict] = {}
    backend = "rule-only"
    if use_llm:
        llm, backend = _llm_eval(premises, recent)
    results = []
    for pm in premises:
        pid = pm.get("id", "")
        if rule.get(pid, {}).get("status") == "invalid":
            v, src = rule[pid], "rule(floor)"          # clear danger — LLM cannot downgrade
        elif pid in llm:
            v, src = llm[pid], backend
        elif pid in rule:
            v, src = rule[pid], "rule"
        else:
            v, src = {"status": "challenged", "reason": "not evaluated (no backend)"}, "default"
        results.append({"premise_id": pid, "status": v["status"], "evidence": v.get("reason", ""), "source": src})

    # SUIT groundedness gate: downgrade ungrounded "valid" verdicts → "challenged".
    # The weak local model can assert a confident, ungrounded clean bill of health;
    # this catches it. Fail-open — never let the gate break the check.
    try:
        import premise_trust
        premise_by_id = {p.get("id", ""): p.get("text", "") for p in premises}
        results = premise_trust.gate_verdicts(results, premise_by_id, recent, threshold=0.30)
    except Exception:
        pass
    return results
