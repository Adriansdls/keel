"""Incremental, locked cadence for automatic outcome reviews."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import store
from shared.runtime import try_lock

_FAILURE_BACKOFF = timedelta(hours=1)


def _loop_dir() -> Path:
    path = store.root() / "outcome-loop"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _state_path() -> Path:
    return _loop_dir() / "state.json"


def _load_state() -> dict:
    try:
        return json.loads(_state_path().read_text(encoding="utf-8"))
    except Exception:
        return {"projects": {}}


def _write_state(state: dict) -> None:
    store._atomic_write(_state_path(), json.dumps(state, indent=2))


def _append_run(record: dict) -> None:
    path = _loop_dir() / "runs.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, default=str) + "\n")


def _agent():
    spec = importlib.util.spec_from_file_location("outcome_agent", Path(__file__).parent / "agent.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse_time(value: str | None) -> datetime | None:
    try:
        return datetime.fromisoformat(value) if value else None
    except Exception:
        return None


def _is_due(project_id: str, project_state: dict, now: datetime, agent) -> bool:
    if not agent.project_has_actionable(project_id):
        return False
    last_attempt = _parse_time(project_state.get("last_attempt_at"))
    if project_state.get("last_status") == "failed" and last_attempt:
        if now - last_attempt < _FAILURE_BACKOFF:
            return False
    last_success = _parse_time(project_state.get("last_success_at"))
    interval = timedelta(days=store.load_config().outcomes.check_every_days)
    return last_success is None or now - last_success >= interval


def _select_due_project(state: dict, now: datetime, agent) -> str | None:
    candidates: list[tuple[datetime, str]] = []
    floor = datetime.min
    for project in store.load_projects():
        if project.status != "active":
            continue
        project_state = state["projects"].get(project.id, {})
        if _is_due(project.id, project_state, now, agent):
            candidates.append((_parse_time(project_state.get("last_success_at")) or floor, project.id))
    return min(candidates)[1] if candidates else None


def run_if_due(trigger: dict | None = None) -> dict | None:
    """Review at most one globally due project. Returns a compact result record."""
    trigger = trigger or {}
    with try_lock("outcome-loop") as acquired:
        if not acquired:
            return None

        agent = _agent()
        state = _load_state()
        state.setdefault("projects", {})
        now = datetime.now()
        project_id = _select_due_project(state, now, agent)
        if not project_id:
            return None

        run_id = str(uuid.uuid4())
        project_state = state["projects"].setdefault(project_id, {})
        project_state["last_attempt_at"] = now.isoformat()
        project_state["last_status"] = "running"
        _write_state(state)

        record = {
            "run_id": run_id,
            "pid": os.getpid(),
            "trigger_session_id": trigger.get("session_id", ""),
            "trigger_cwd": trigger.get("cwd", ""),
            "project_id": project_id,
            "started_at": now.isoformat(),
        }
        try:
            report = agent.run_project(project_id, raise_on_error=True)
            finished = datetime.now()
            project_state["last_success_at"] = finished.isoformat()
            project_state["last_status"] = "succeeded"
            project_state["consecutive_failures"] = 0
            record.update({
                "status": "succeeded",
                "finished_at": finished.isoformat(),
                "duration_seconds": round((finished - now).total_seconds(), 3),
                "verdict_count": len(report.verdicts) if report else 0,
            })
        except Exception as exc:
            finished = datetime.now()
            project_state["last_status"] = "failed"
            project_state["consecutive_failures"] = int(project_state.get("consecutive_failures", 0)) + 1
            record.update({
                "status": "failed",
                "finished_at": finished.isoformat(),
                "duration_seconds": round((finished - now).total_seconds(), 3),
                "error": str(exc)[:500],
            })
        _write_state(state)
        _append_run(record)
        return record


def run_all_manual() -> dict:
    """Explicit full sweep, protected by the same machine-wide lock."""
    with try_lock("outcome-loop") as acquired:
        if not acquired:
            return {}
        return _agent().run_all()
