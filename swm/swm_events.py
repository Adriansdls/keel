#!/usr/bin/env python3
"""Importable event-entry surface for the strategic-working-memory skill.

The live Claude Code hooks are dash-named adapter scripts (inject-strategic-state.py,
detect-strategic-candidates.py, precompact-snapshot.py, premise-check-cadence.py) that
read a hook event off stdin and act. Those filenames are not importable, so skills2
cannot bind to them by `module:callable`.

This module exposes the same four behaviors as plain importable functions that take a
hook-event dict — the binding targets named in skill.toml `[events]`:

    UserPromptSubmit -> swm_events:inject       (returns the context block to inject)
    Stop             -> swm_events:capture      (Haiku capture -> auto-commit)
    PreCompact       -> swm_events:snapshot     (backup + last-window capture)
    cadence          -> swm_events:premise_check (Sonnet premise audit)

It orchestrates the same importable primitives the dash scripts use (capture_extract,
swm_store, swm_consolidate, premise_eval, cold_log, swm_paths), so behavior tracks the
live hooks. The dash scripts remain the CC-hook adapters; consolidating them to delegate
here is a follow-up (see DESIGN bucket A / full-merge). Every function fails open.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from capture_extract import extract_facts  # noqa: E402
import swm_store as store  # noqa: E402
import swm_consolidate  # noqa: E402
import cold_log as cl  # noqa: E402
import premise_eval  # noqa: E402
import swm_paths  # noqa: E402
from swm_paths import resolve, disabled  # noqa: E402
try:
    import project_router  # noqa: E402
except Exception:  # pragma: no cover - router optional
    project_router = None

MIN_TURN_CHARS = 200          # skip Haiku capture on trivial turns
PREMISE_CADENCE = 4           # full premise audit every Nth Stop (or on danger)
ROUTE_ENABLED = "1"           # SWM_ROUTE != "0" enables topic routing at capture


# ---- routing + commit (shared by capture + snapshot) -------------------------

def _commit_render(P, facts, turn: int) -> dict:
    # Auto-link facts UP to THIS store's strategic spine (LLM judgment). Fires only when the
    # project has active priorities, so projects without a spine pay nothing. Untraced facts
    # surface in the ⚠ DRIFT banner. Fail-open: never blocks the commit.
    try:
        import swm_priority as _prio
        _active = _prio.active(_prio.load(P.committed.parent / "priorities.jsonl"))
        if _active:
            import priority_link
            priority_link.tag_facts(facts, _active)
    except Exception:
        pass
    res = store.commit_facts(P.committed, facts, turn)
    store.render(P.committed, P.state)
    if store.over_budget(P.committed):
        swm_consolidate.consolidate(P.committed, P.state, P.archive, turn)
    return res


def _append_queue(P, facts, r: dict, turn: int) -> None:
    """Record a medium-confidence cross-project guess for async `swm reroute` review."""
    try:
        import os as _os
        entry = {
            "turn": turn,
            "suggested_project": r.get("project_id"),
            "confidence": r.get("confidence"),
            "reason": r.get("reason", ""),
            "fact_ids": [store.fid(f["kind"], f["text"]) for f in facts
                         if f.get("kind") and f.get("text")],
        }
        P.reroute_queue.parent.mkdir(parents=True, exist_ok=True)
        with P.reroute_queue.open("a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass



# ── Bidirectional bridge: SWM → ra-pm ─────────────────────────────────────────
def _maybe_sync_decision_to_rapm(fact: dict, project_id: str) -> None:
    """When SWM auto-commits a decision, write a matching record to the ra-pm
    decision store so it appears in ra_decisions and the outcome loop.

    Dedup: skip if the first 60 chars of the fact text appear verbatim in an
    existing decision (catches the common case when ra-pm and SWM are both active).
    Semantic dedup is left to Entropy Manager's field health pass — too expensive here.

    Fail-open: SWM commit already succeeded; any error here is swallowed.
    Source marked "swm-bridge" so it's distinguishable from explicit ra-pm decisions.
    """
    if fact.get("kind") != "decision":
        return
    try:
        import sys as _sys
        from pathlib import Path as _Path
        _sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
        from shared.store import (
            save_decision as _save_decision,
            next_decision_id as _next_id,
            load_decisions as _load_decisions,
        )
        from shared.models import Decision as _Decision
        existing = _load_decisions(project_id)
        snippet = (fact.get("text") or "")[:60].lower()
        if any(snippet in (d.decision or "").lower() for d in existing):
            return  # already captured — skip
        new_id = _next_id(project_id)
        _save_decision(project_id, _Decision(
            id=new_id,
            decision=fact["text"],
            rationale="(auto-captured from session — see SWM committed.jsonl for full context)",
            alternatives_rejected=[],
            source="swm-bridge",
        ))
    except Exception:
        pass  # fail-open always

def route_and_commit(P, facts, text: str, turn: int, event: dict) -> dict:
    """Route the turn's facts to a project, then commit. One router call, three actions:
       route  -> file in the routed project's store (high confidence, different project)
       queue  -> file at the cwd-project + flag for async review (medium confidence)
       prior  -> file at the cwd-project (default)."""
    import os as _os
    cwd = (event or {}).get("cwd") or _os.getcwd()
    r = None
    if facts and project_router is not None and _os.environ.get("SWM_ROUTE", ROUTE_ENABLED) != "0":
        try:
            r = project_router.route(text, cwd)
        except Exception:
            r = None
    action = (r or {}).get("action", "prior")
    if action == "route" and r.get("project_id"):
        dest = swm_paths.for_project(r["project_id"])
        rf = swm_paths.project_key(cwd)
        for f in facts:
            f["project"] = r["project_id"]
            f["routed_from"] = rf
            f["route_confidence"] = r.get("confidence")
        res = _commit_render(dest, facts, turn)
        res["routed_to"] = r["project_id"]
        return res
    res = _commit_render(P, facts, turn)
    # Bridge: sync decision facts to ra-pm store
    _proj_key = swm_paths.project_key(event.get("cwd", "") if event else "")
    for _f in (facts or []):
        _maybe_sync_decision_to_rapm(_f, _proj_key)
    if action == "queue" and r.get("project_id"):
        _append_queue(P, facts, r, turn)
        res["queued_for"] = r["project_id"]
    return res


# ---- shared transcript helpers (mirrors the dash adapters) -------------------

def _text_from_message(msg) -> str:
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        content = msg.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return " ".join(
                b.get("text", "") for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            )
    return ""


def _iter_messages(transcript_path: str):
    p = Path(transcript_path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = ev.get("type") or ev.get("role")
        yield role, _text_from_message(ev.get("message", ev))


def _last_turn(transcript_path: str) -> str:
    last_user = last_assistant = ""
    for role, txt in _iter_messages(transcript_path):
        if role == "user" and txt:
            last_user = txt
        elif role == "assistant" and txt:
            last_assistant = txt
    return f"{last_user}\n{last_assistant}".strip()


def _recent(transcript_path: str, n: int = 8) -> str:
    msgs = [(r, t) for r, t in _iter_messages(transcript_path) if t]
    return "\n".join(t for _, t in msgs[-n:])


def _turn(P) -> int:
    try:
        return int(P.turn_counter.read_text().strip())
    except Exception:
        return 0


# ---- event functions (skill.toml [events] binding targets) -------------------

def capture(event: dict) -> dict:
    """Stop: Haiku-extract strategic facts from the last turn and auto-commit them."""
    if disabled():
        return {"skipped": "disabled"}
    P = resolve(event)
    cl.configure(P.cold)
    tpath = event.get("transcript_path", "")
    if not tpath:
        return {"skipped": "no_transcript"}
    text = _last_turn(tpath)
    if not text or len(text) < MIN_TURN_CHARS:
        return {"skipped": "trivial_turn"}
    turn = _turn(P)
    sid = event.get("session_id", "")
    if sid:
        try:
            cl.append(sid, "turn", text)
        except Exception:
            pass
    state_text = P.state.read_text() if P.state.exists() else ""
    facts = extract_facts(text, committed_state_text=state_text)
    if not facts:
        return {"added": 0, "bumped": 0, "dropped": 0}
    return route_and_commit(P, facts, text, turn, event)


def snapshot(event: dict) -> dict:
    """PreCompact: back up state + capture the about-to-be-compacted window into the store."""
    if disabled():
        return {"skipped": "disabled"}
    P = resolve(event)
    cl.configure(P.cold)
    # durable backup of the rendered state before compaction touches anything
    if P.state.exists():
        try:
            P.backups.mkdir(parents=True, exist_ok=True)
            turn = _turn(P)
            (P.backups / f"state-precompact-{turn}.md").write_text(P.state.read_text())
        except Exception:
            pass
    tpath = event.get("transcript_path", "")
    if not tpath:
        return {"skipped": "no_transcript"}
    text = _recent(tpath, n=20)
    if not text or len(text) < MIN_TURN_CHARS:
        return {"added": 0}
    turn = _turn(P)
    state_text = P.state.read_text() if P.state.exists() else ""
    facts = extract_facts(text, committed_state_text=state_text)
    if not facts:
        return {"added": 0}
    res = store.commit_facts(P.committed, facts, turn)
    store.render(P.committed, P.state)
    if store.over_budget(P.committed):
        swm_consolidate.consolidate(P.committed, P.state, P.archive, turn)
    return res


def premise_check(event: dict, cadence: int = PREMISE_CADENCE) -> dict:
    """cadence: every Nth Stop, audit committed premises against recent evidence (Sonnet)."""
    if disabled():
        return {"skipped": "disabled"}
    P = resolve(event)
    premises = store.premises(P.committed)
    if not premises:
        return {"skipped": "no_premises"}
    # bump the premise cadence counter
    try:
        n = int(P.premise_counter.read_text().strip()) + 1
    except Exception:
        n = 1
    try:
        store._atomic_write(P.premise_counter, str(n))
    except Exception:
        pass
    tpath = event.get("transcript_path", "")
    recent = _recent(tpath, n=8) if tpath else ""
    use_llm = (n % cadence == 0)
    findings = premise_eval.evaluate(premises, recent, use_llm=use_llm)
    # enrich each finding with the premise text so inject can render it
    pmap = {p["id"]: p.get("text", "") for p in premises}
    for f in findings:
        f["text"] = pmap.get(f.get("premise_id"), "")
    try:
        store._atomic_write(P.findings, json.dumps(findings, ensure_ascii=False, indent=2))
    except Exception:
        pass
    return {"checked": len(premises), "llm": use_llm, "findings": findings}


def inject(event: dict) -> str:
    """UserPromptSubmit: build the strategic-memory context block to inject this turn.

    Returns the block as a string (empty string when there is nothing to surface)."""
    if disabled():
        return ""
    P = resolve(event)
    cl.configure(P.cold)
    block: list[str] = []
    state = P.state.read_text().strip() if P.state.exists() else ""
    if state:
        block.append(state)
    # premise findings: surface invalid/challenged premises
    if P.findings.exists():
        try:
            findings = json.loads(P.findings.read_text())
            flagged = [f for f in findings if f.get("status") in ("invalid", "challenged")]
            if flagged:
                block.append("\n## ⚠ premise check")
                for f in flagged:
                    mark = "⛔" if f.get("status") == "invalid" else "⚠"
                    detail = f.get("text") or f.get("premise_id", "")
                    block.append(f"- {mark} {detail} — {f.get('evidence', f.get('status'))}")
        except Exception:
            pass
    return "\n".join(block).strip()


# ---- standalone smoke (not used by hooks) ------------------------------------

if __name__ == "__main__":
    ev = {}
    try:
        raw = sys.stdin.read()
        ev = json.loads(raw) if raw.strip() else {}
    except Exception:
        ev = {}
    print(inject(ev))
