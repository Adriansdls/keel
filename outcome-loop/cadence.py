"""Outcome loop cadence — threshold + schedule trigger.

Fires run_all() when any condition is met:
  - no prior run ever
  - days since last run >= config.outcomes.check_every_days (default 7)
  - any open bet older than config.outcomes.flag_stale_bets_after_days (default 60)
  - any decision older than config.outcomes.decision_check_after_days (default 30)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared.store import load_bets, load_config, load_decisions, load_projects, root
from shared.models import BetStatus, ExperimentStatus, OutcomeReport


def _loop_dir() -> Path:
    d = root() / "outcome-loop"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _last_run() -> datetime | None:
    p = _loop_dir() / "last-run.json"
    if not p.exists():
        return None
    try:
        return datetime.fromisoformat(json.loads(p.read_text())["ran_at"])
    except Exception:
        return None


def _write_last_run() -> None:
    (_loop_dir() / "last-run.json").write_text(
        json.dumps({"ran_at": datetime.now().isoformat()})
    )


def should_run() -> bool:
    cfg = load_config()
    last = _last_run()

    # Never run before
    if last is None:
        return True

    # Schedule threshold
    if (datetime.now() - last).days >= cfg.outcomes.check_every_days:
        return True

    from datetime import date
    today = date.today()

    # Any open bet past stale threshold
    for p in load_projects():
        if p.status != "active":
            continue
        for b in load_bets(p.id):
            if b.status == BetStatus.active and b.created:
                if (today - b.created).days >= cfg.outcomes.flag_stale_bets_after_days:
                    return True
        for d in load_decisions(p.id):
            if d.logged and (today - d.logged).days >= cfg.outcomes.decision_check_after_days:
                return True

    return False


def run_now() -> dict[str, OutcomeReport]:
    """Run unconditionally across all projects. Updates last-run."""
    import importlib.util as _ilu, pathlib as _pl
    _spec = _ilu.spec_from_file_location("agent",
        _pl.Path(__file__).parent / "agent.py")
    _mod = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_mod)
    run_all = _mod.run_all
    results = run_all()
    _write_last_run()
    return results


def run_if_due() -> dict | None:
    if not should_run():
        return None
    return run_now()
