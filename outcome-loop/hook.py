#!/usr/bin/env python3
"""Stop hook — outcome loop cadence trigger.

Runs every 40 turns (less frequent than entropy — Sonnet is more expensive).
Calls cadence.run_if_due() — returns immediately if conditions not met.
Fail-open: exit 0 on any error.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

_EVERY_N_TURNS = 40


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main() -> int:
    event = _read_event()
    cwd   = event.get("cwd", "")

    try:
        from shared.store import match_project_by_cwd, load_turn_counter
        project_id = match_project_by_cwd(cwd) or "_global"
        turns = load_turn_counter(project_id)
    except Exception:
        return 0

    if turns % _EVERY_N_TURNS != 0:
        return 0

    try:
        # Dynamic import — avoids hyphenated package issue
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location(
            "cadence", Path(__file__).parent / "cadence.py")
        _mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)

        results = _mod.run_if_due()
        if results:
            n_verdicts = sum(len(r.verdicts) for r in results.values())
            print(f"[outcome-loop] {len(results)} project(s) reviewed, "
                  f"{n_verdicts} verdict(s)", file=sys.stderr)
    except Exception as e:
        print(f"[outcome-loop] hook error (fail-open): {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[outcome-loop] fatal (fail-open): {e}", file=sys.stderr)
        sys.exit(0)
