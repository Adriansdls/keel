#!/usr/bin/env python3
"""Stop hook: trigger one incremental global outcome review when due."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main() -> int:
    if os.environ.get("KEEL_INTERNAL_LLM") == "1":
        return 0
    event = _read_event()
    try:
        from shared.store import match_project_by_cwd
        if not match_project_by_cwd(event.get("cwd", "")):
            return 0

        import importlib.util
        spec = importlib.util.spec_from_file_location("outcome_cadence", Path(__file__).parent / "cadence.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.run_if_due(event)
        if result:
            print(
                f"[outcome-loop] {result['project_id']} {result['status']} "
                f"({result.get('verdict_count', 0)} verdicts)",
                file=sys.stderr,
            )
    except Exception as exc:
        print(f"[outcome-loop] hook error (fail-open): {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
