"""Groundedness gate for premise verdicts — reuses SUIT's trust scoring.

The autonomous premise check (premise-check-cadence + premise_eval) is backed by a
weak local model (llama3.1). A small model can assert status="valid" with `evidence`
that doesn't derive from the source — a confident, ungrounded clean bill of health on
the dominant-failure defense. This gate asks SUIT's question: did the evidence actually
come from the source, or was it fabricated? It downgrades ungrounded "valid" → "challenged".

GRIP (hedging→low confidence) + VEIN (vocab overlap with source) only; GRAIN is excluded
(needs a card-retrieval provenance log we don't have). Deterministic, no API call.

Direction is safe by construction: a downgrade only ADDS caution (a verify-prompt); it
never removes a flag or forces a decision. Conservative threshold (0.30) — gate only
blatant ungrounding.

Runtime uses SUIT directly when importable (single source of truth); falls back to a
vendored copy so this
safety-critical hook never breaks if SUIT moves. test_premise_trust.py asserts parity.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from types import SimpleNamespace

# ── Vendored implementation (self-contained, no external dependencies) ──
BACKEND = "vendored"

_HEDGE_RE = re.compile(
    r"\b(i think|i believe|might|may|perhaps|possibly|probably|likely|"
    r"seems|appears|unclear|uncertain|not sure|could be|somewhat|"
    r"approximately|it is possible|it seems)\b",
    re.IGNORECASE,
)
_CARD_REF_RE = re.compile(r"\[[A-Z]\d{3,4}\]")
_STOP = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "this", "that", "these",
    "those", "i", "we", "you", "he", "she", "it", "they", "and", "or",
    "but", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "about", "as", "into", "if", "then", "so", "not", "no", "its", "their",
    "which", "what", "when", "where", "who", "how", "all", "also", "just",
    "more", "than", "our", "his", "her", "out", "one", "use", "any",
    "each", "here", "there", "them", "they", "very", "own", "see",
}
_VEIN_THRESHOLD = 0.20
_SKIP_HEADINGS = {
    "behavior contract", "trust score", "cards used",
    "verbatim source", "confidence", "## ",
}

def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-z]{3,}", text.lower())
    return {w for w in words if w not in _STOP}

def score_grip(response: str) -> tuple[float, str]:
    if not response:
        return 0.50, "no response text"
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", response) if len(s.strip()) > 10]
    n_sentences = max(len(sentences), 1)
    hedge_count = len(_HEDGE_RE.findall(response))
    hedge_ratio = min(hedge_count / n_sentences, 1.0)
    card_refs = len(_CARD_REF_RE.findall(response))
    citation_boost = min(0.15, card_refs * 0.025)
    score = round(max(0.0, min(1.0, (1.0 - hedge_ratio * 0.55) + citation_boost)), 3)
    hedge_level = "low" if hedge_count <= 1 else "moderate" if hedge_count <= 4 else "high"
    return score, f"{hedge_level} hedging ({hedge_count} hedge words) · {card_refs} card ID citations"

def score_vein(response: str, grains) -> tuple[float, str]:
    if not response or not grains:
        return 0.50, "no response or no cited cards"
    card_pool = _tokenize(" ".join(g.content for g in grains))
    if not card_pool:
        return 0.50, "cited cards have no content"
    sentences = []
    for sent in re.split(r"(?<=[.!?])\s+", response):
        sent = sent.strip()
        if len(sent) < 20:
            continue
        low = sent.lower()
        if any(skip in low for skip in _SKIP_HEADINGS):
            continue
        if sent.startswith(("#", "|", "-")):
            continue
        sentences.append(sent)
    if not sentences:
        return 0.50, "no scoreable sentences found"
    grounded = 0
    for sent in sentences:
        tokens = _tokenize(sent)
        if tokens and len(tokens & card_pool) / len(tokens) >= _VEIN_THRESHOLD:
            grounded += 1
    ratio = round(grounded / len(sentences), 3)
    return ratio, f"{grounded}/{len(sentences)} sentences covered (≥{_VEIN_THRESHOLD:.0%} vocab overlap)"


# ── Groundedness for a premise verdict ──────────────────────────────
def score_groundedness(evidence: str, source_text: str) -> tuple[float, dict]:
    """Did `evidence` derive from `source_text`? 0..1.

    VEIN-dominant (0.75) — groundedness IS attribution. GRIP (0.25) only modulates.
    A confident-but-unattributed claim (high GRIP, zero VEIN) is the dangerous case and
    must score low: 0.75*0 + 0.25*1 = 0.25 < the 0.30 gate. GRIP must not rescue it.
    """
    grip, grip_d = score_grip(evidence or "")
    vein, vein_d = score_vein(evidence or "", [SimpleNamespace(content=source_text or "")])
    g = round(0.75 * vein + 0.25 * grip, 3)
    return g, {"grip": grip, "vein": vein, "grip_detail": grip_d, "vein_detail": vein_d, "backend": BACKEND}


def gate_verdicts(verdicts: list[dict], premise_by_id: dict[str, str],
                  recent_text: str = "", threshold: float = 0.30) -> list[dict]:
    """Downgrade ungrounded 'valid' verdicts → 'challenged'. Annotate all with groundedness.

    Safe direction: only 'valid' is touched, and only ever toward more caution.
    """
    for v in verdicts:
        src = (premise_by_id.get(v.get("premise_id", ""), "") + " " + recent_text).strip()
        g, detail = score_groundedness(v.get("evidence", ""), src)
        v["groundedness"] = g
        if v.get("status") == "valid" and g < threshold:
            v["status"] = "challenged"
            v["evidence"] = f"[trust-gated: ungrounded valid g={g}] " + v.get("evidence", "")
            v["source"] = "trust-gated"
    return verdicts