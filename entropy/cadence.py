"""Entropy Manager cadence — threshold + schedule trigger.

Fires entropy.brief() when any condition is met:
  - days since last run  >= config.health.check_every_days (default 7)
  - leakage_rate of last report > config.health.warn_if_idea_leakage_above (default 0.40)
  - open inbox ideas     > config.health.open_ideas_threshold (default 30)

On fire:
  1. handler.handle({"action": "brief"}) → EntropyReport
  2. Appends report to ~/.keel/entropy/findings.jsonl (one JSON line per run)
  3. Updates ~/.keel/entropy/last-run.json

Fail-open: errors never crash a hook.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.store import load_config, load_ideas, root
from shared.models import EntropyReport


def _entropy_dir() -> Path:
    d = root() / "entropy"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _last_run() -> datetime | None:
    p = _entropy_dir() / "last-run.json"
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        return datetime.fromisoformat(data["ran_at"])
    except Exception:
        return None


def _last_report() -> EntropyReport | None:
    p = _entropy_dir() / "findings.jsonl"
    if not p.exists():
        return None
    try:
        lines = [l for l in p.read_text().splitlines() if l.strip()]
        if not lines:
            return None
        return EntropyReport.model_validate_json(lines[-1])
    except Exception:
        return None


def _write_last_run() -> None:
    p = _entropy_dir() / "last-run.json"
    p.write_text(json.dumps({"ran_at": datetime.now().isoformat()}))


def _append_finding(report: EntropyReport) -> None:
    p = _entropy_dir() / "findings.jsonl"
    with p.open("a") as f:
        f.write(report.model_dump_json() + "\n")


def should_run() -> bool:
    cfg = load_config()

    # schedule threshold
    last = _last_run()
    if last is None:
        return True
    days_since = (datetime.now() - last).days
    if days_since >= cfg.health.check_every_days:
        return True

    # leakage threshold
    rpt = _last_report()
    if rpt and rpt.leakage_rate > cfg.health.warn_if_idea_leakage_above:
        return True

    # volume threshold
    if len(load_ideas()) > cfg.health.open_ideas_threshold:
        return True

    return False


def run_now() -> EntropyReport:
    """Run brief unconditionally. Writes findings. Updates last-run."""
    from entropy.handler import handle
    result = handle({"action": "brief"})
    report: EntropyReport = result["report"]
    _append_finding(report)
    _write_last_run()
    return report


def run_if_due() -> EntropyReport | None:
    """Run only if conditions are met. Returns report or None."""
    if not should_run():
        return None
    return run_now()
