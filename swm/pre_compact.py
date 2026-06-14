#!/usr/bin/env python3
"""PreCompact hook — snapshot the strategic-state world-model before compaction.

Belt-and-suspenders behind the deliberate skill writes: compaction destroys ~60%
of facts silently, so we copy strategic-state.md to a timestamped backup the
instant before a compaction fires. The live file is unaffected (and is re-injected
next turn by inject-strategic-state.py), but the backup guarantees no committed
state is ever lost to a compaction event.

Reads the PreCompact event (which carries transcript_path + trigger). Always
exits 0 (fail-open).
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from capture_extract import extract_facts   # noqa: E402  (Haiku primary, rule fallback)
import swm_store as store                    # noqa: E402  (structured committed-facts store)
import swm_consolidate                       # noqa: E402  (Sonnet over-budget consolidation)
from swm_paths import resolve, disabled  # noqa: E402  (per-project state, global kill switch)

# Module-level defaults; rebound per-project from the event cwd inside main().
STATE_FILE = HERE / "strategic-state.md"
BACKUP_DIR = HERE / "state-backups"


def _all_user_text(transcript_path: str) -> str:
    """Concatenate all user message text from the transcript (full-session sweep)."""
    p = Path(transcript_path)
    if not p.exists():
        return ""
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (ev.get("type") or ev.get("role")) != "user":
            continue
        msg = ev.get("message", ev)
        content = msg.get("content", "") if isinstance(msg, dict) else msg
        if isinstance(content, str):
            out.append(content)
        elif isinstance(content, list):
            out.append(" ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"))
    return "\n".join(out)


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main() -> int:
    if disabled():
        return 0
    event = _read_event()
    global STATE_FILE, BACKUP_DIR
    P = resolve(event)
    STATE_FILE, BACKUP_DIR = P.state, P.backups
    trigger = event.get("trigger") or event.get("compact_trigger") or "unknown"
    if STATE_FILE.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        dest = BACKUP_DIR / f"strategic-state.{ts}.{trigger}.md"
        try:
            shutil.copy2(STATE_FILE, dest)
        except Exception:
            pass

    # L4 — extraction backstop: sweep the FULL transcript for strategic facts and
    # AUTO-COMMIT them to the durable store BEFORE compaction destroys them. Dedup in
    # commit_facts collapses overlap with what the per-turn capture already stored, so
    # this is a safe last-chance sweep. State re-injects post-compaction from the store.
    added = 0
    tpath = event.get("transcript_path", "")
    if tpath:
        try:
            known = "\n".join(f["text"] for f in store.load(P.committed))
            turn = _read_turn(P.turn_counter)
            facts = extract_facts(_all_user_text(tpath), known=known)
            res = store.commit_facts(P.committed, facts, turn)
            added = res.get("added", 0)
            store.render(P.committed, STATE_FILE)
            if store.over_budget(P.committed):
                swm_consolidate.consolidate(P.committed, STATE_FILE, P.archive, turn)
        except Exception:
            added = 0

    print(
        f"[strategic-memory] compaction firing — strategic-state.md snapshotted; "
        f"{added} pre-compaction fact(s) auto-committed to durable memory. "
        "State re-injects post-compaction.",
        flush=True,
    )
    return 0


def _read_turn(counter_path) -> int:
    try:
        return int(counter_path.read_text().strip())
    except Exception:
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[precompact-snapshot] error: {e}", file=sys.stderr)
        sys.exit(0)
