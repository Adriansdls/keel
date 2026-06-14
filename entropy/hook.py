#!/usr/bin/env python3
"""Stop hook — entropy manager cadence trigger.

Runs after every Nth turn (default: every 20 turns, checked via SWM turn counter).
Calls cadence.run_if_due() — returns immediately if conditions not met.
Fail-open: exit 0 on any error, never blocks the user.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

COWORK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(COWORK_ROOT))

# Only run every N turns to avoid entropy check on every single stop
_EVERY_N_TURNS = 20


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _turn_count(project_id: str) -> int:
    try:
        from shared.store import load_turn_counter
        return load_turn_counter(project_id)
    except Exception:
        return 0


def main() -> int:
    event = _read_event()
    cwd = event.get("cwd", "")

    try:
        from shared.store import match_project_by_cwd
        project_id = match_project_by_cwd(cwd) or "_global"
    except Exception:
        return 0

    # Throttle: only fire every N turns
    turns = _turn_count(project_id)
    if turns % _EVERY_N_TURNS != 0:
        return 0

    try:
        from entropy.cadence import run_if_due
        report = run_if_due()
        if report:
            print(f"[entropy] brief complete — leakage: {report.leakage_rate}, "
                  f"dormant: {report.dormant_idea_count}", file=sys.stderr)
    except Exception as e:
        print(f"[entropy] hook error (fail-open): {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[entropy] fatal (fail-open): {e}", file=sys.stderr)
        sys.exit(0)
