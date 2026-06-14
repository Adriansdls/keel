#!/usr/bin/env python3
"""Stop hook (L1) — continuous Haiku capture + auto-commit to durable memory.

After each substantive turn, a Haiku extractor pulls strategic facts (decisions,
constraints, eliminations, premises) from the latest user + assistant messages and
AUTO-COMMITS them straight into the per-project committed store (committed.jsonl),
which is rendered to strategic-state.md and re-injected every turn. No human-review
gate — re-observation bumps last_seen (dedup), and when the store goes over budget a
Sonnet consolidation pass merges/drops with judgment.

Fail-open: any error → exit 0, never block the user.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from capture_extract import extract_facts  # noqa: E402  (Haiku primary, rule fallback)
import swm_store as store  # noqa: E402  (structured committed-facts store + render)
import swm_consolidate  # noqa: E402  (Sonnet consolidation when over budget)
import cold_log as cl  # noqa: E402  (append-only full log for recall)
from swm_paths import resolve, disabled  # noqa: E402  (per-project state, global kill switch)

# Module-level defaults; rebound per-project from the event cwd inside main().
STATE_FILE = HERE / "strategic-state.md"
CANDIDATES_FILE = HERE / "strategic-candidates.jsonl"

# Skip the Haiku capture call on trivial turns — short turns carry no strategic
# facts, and a per-turn Haiku subprocess in every project is the main cost driver.
MIN_TURN_CHARS = 200


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _text_from_message(msg) -> str:
    if isinstance(msg, str):
        return msg
    if isinstance(msg, dict):
        content = msg.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _last_turn(transcript_path: str) -> str:
    """Return the most recent user text + assistant text from the transcript."""
    p = Path(transcript_path)
    if not p.exists():
        return ""
    last_user = last_assistant = ""
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = ev.get("type") or ev.get("role")
        txt = _text_from_message(ev.get("message", ev))
        if role == "user" and txt:
            last_user = txt
        elif role == "assistant" and txt:
            last_assistant = txt
    return f"{last_user}\n{last_assistant}".strip()


def _turn(P) -> int:
    try:
        return int(P.turn_counter.read_text().strip())
    except Exception:
        return 0


def main() -> int:
    if disabled():
        return 0
    event = _read_event()
    global STATE_FILE
    P = resolve(event)
    STATE_FILE = P.state
    cl.configure(P.cold)
    tpath = event.get("transcript_path", "")
    if not tpath:
        return 0
    text = _last_turn(tpath)
    if not text or len(text) < MIN_TURN_CHARS:
        return 0
    turn = _turn(P)
    # append this turn to the untouched cold log so recall works even after compaction drops it
    sid = event.get("session_id", "")
    if sid:
        try:
            cl.append(sid, "turn", text)
        except Exception:
            pass
    # Haiku capture → auto-commit straight into the durable store (no review gate)
    state_text = STATE_FILE.read_text() if STATE_FILE.exists() else ""
    facts = extract_facts(text, committed_state_text=state_text)
    if not facts:
        return 0
    # route the turn to the right project, then commit + render + (over-budget) consolidate
    import swm_events  # noqa: E402  (shared routing + commit)
    swm_events.route_and_commit(P, facts, text, turn, event)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[detect-strategic-candidates] {e}", file=sys.stderr)
        sys.exit(0)
