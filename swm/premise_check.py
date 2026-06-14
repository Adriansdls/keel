#!/usr/bin/env python3
"""Stop hook (background) — GUARANTEED premise-check cadence.

The dominant strategic failure is premise-error amplification: a confidently-wrong
belief that compounds. A text nudge the agent can ignore is not enough. This hook
makes the check actually FIRE, autonomously, without relying on the agent:

  - every turn: run the instant rule-based floor (catches a provisional premise now
    treated as settled — the dominant failure — deterministically, zero latency);
  - every CADENCE turns OR when the floor flags danger: run the full Ollama semantic
    evaluation (local llama3.1, no API cap).

Writes premise-findings.json; the inject hook surfaces it (invalid → STOP banner).
Registered as a BACKGROUND Stop hook so the ~15s Ollama pass never blocks the user;
findings land and surface on the next turn. Fail-open: any error → exit 0.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import premise_eval  # noqa: E402
import swm_store as store  # noqa: E402  (premises live in the structured store)
from swm_paths import resolve, disabled  # noqa: E402  (per-project state, global kill switch)

# Module-level defaults; rebound per-project from the event cwd inside main().
STATE_FILE = HERE / "strategic-state.md"
COMMITTED = HERE / "committed.jsonl"
FINDINGS_FILE = HERE / "premise-findings.json"
COUNTER_FILE = HERE / ".swm-premise-counter"
CADENCE = 4  # full Sonnet eval at least every N turns


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _operating_premise() -> list[dict]:
    # Premises live in the structured committed store (kind == "premise"), rendered
    # into strategic-state.md for the human/agent. premise-check reads the store
    # directly so it operates on the same facts SWM auto-commits and inject surfaces.
    return store.premises(COMMITTED)


def _recent_text(transcript_path: str, n_msgs: int = 8) -> str:
    p = Path(transcript_path)
    if not p.exists():
        return ""
    msgs = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = ev.get("type") or ev.get("role")
        if role not in ("user", "assistant"):
            continue
        msg = ev.get("message", ev)
        content = msg.get("content", "") if isinstance(msg, dict) else msg
        if isinstance(content, list):
            content = " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
        if content:
            msgs.append(f"{role}: {content}")
    return "\n".join(msgs[-n_msgs:])


def _bump() -> int:
    try:
        n = int(COUNTER_FILE.read_text().strip()) if COUNTER_FILE.exists() else 0
    except Exception:
        n = 0
    n += 1
    try:
        COUNTER_FILE.write_text(str(n))
    except Exception:
        pass
    return n


def main() -> int:
    if disabled():
        return 0
    event = _read_event()
    global STATE_FILE, COMMITTED, FINDINGS_FILE, COUNTER_FILE
    P = resolve(event)
    STATE_FILE, COMMITTED, FINDINGS_FILE, COUNTER_FILE = P.state, P.committed, P.findings, P.premise_counter
    premises = _operating_premise()
    if not premises:
        return 0
    recent = _recent_text(event.get("transcript_path", ""))

    n = _bump()
    # instant rule floor first; escalate to the full LLM pass on cadence or on danger
    floor = premise_eval.evaluate(premises, recent, use_llm=False)
    danger = any(r["status"] == "invalid" for r in floor)
    full = (n % CADENCE == 0) or danger
    results = premise_eval.evaluate(premises, recent, use_llm=True) if full else floor
    if full:
        try:
            COUNTER_FILE.write_text("0")
        except Exception:
            pass

    findings = {
        "ts": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
        "turns_since_full": 0 if full else n,
        "backend": "+".join(sorted({r.get("source", "?") for r in results})) if full else "rule-only",
        "results": results,
        "invalid": [r["premise_id"] for r in results if r["status"] == "invalid"],
        "challenged": [r["premise_id"] for r in results if r["status"] == "challenged"],
    }
    FINDINGS_FILE.write_text(json.dumps(findings, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[premise-check-cadence] {e}", file=sys.stderr)
        sys.exit(0)
