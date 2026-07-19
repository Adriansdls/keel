from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shared.models import OutcomeReport


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Agent:
    def __init__(self):
        self.runs = []

    def project_has_actionable(self, project_id):
        return True

    def run_project(self, project_id, raise_on_error=False):
        self.runs.append(project_id)
        return OutcomeReport()


class CadenceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"KEEL_HOME": self.tmp.name}, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_outcome_processes_one_due_project_per_invocation(self):
        cadence = load_module("test_outcome_cadence", ROOT / "outcome-loop/cadence.py")
        agent = _Agent()
        projects = [
            SimpleNamespace(id="a", status="active"),
            SimpleNamespace(id="b", status="active"),
            SimpleNamespace(id="c", status="active"),
        ]
        config = SimpleNamespace(outcomes=SimpleNamespace(check_every_days=7))
        with (
            mock.patch.object(cadence, "_agent", return_value=agent),
            mock.patch.object(cadence.store, "load_projects", return_value=projects),
            mock.patch.object(cadence.store, "load_config", return_value=config),
        ):
            first = cadence.run_if_due({"cwd": "/project", "session_id": "s1"})
            second = cadence.run_if_due({"cwd": "/project", "session_id": "s2"})
        self.assertEqual(agent.runs, ["a", "b"])
        self.assertEqual(first["project_id"], "a")
        self.assertEqual(second["project_id"], "b")

    def test_outcome_lock_skips_overlapping_invocation(self):
        cadence = load_module("test_outcome_cadence_lock", ROOT / "outcome-loop/cadence.py")
        with mock.patch.object(cadence, "try_lock") as lock:
            lock.return_value.__enter__.return_value = False
            lock.return_value.__exit__.return_value = False
            self.assertIsNone(cadence.run_if_due({}))

    def test_entropy_reads_canonical_counter_and_rejects_zero(self):
        hook = load_module("test_entropy_hook", ROOT / "entropy/hook.py")
        fake_module = types.ModuleType("swm.swm_paths")
        with tempfile.TemporaryDirectory() as td:
            counter = Path(td) / ".swm-turn-counter"
            counter.write_text("20")
            fake_module.resolve = lambda event: SimpleNamespace(turn_counter=counter)
            with mock.patch.dict(sys.modules, {"swm.swm_paths": fake_module}):
                self.assertEqual(hook._turn_count({"cwd": "/project"}), 20)
            counter.write_text("0")
            with mock.patch.dict(sys.modules, {"swm.swm_paths": fake_module}):
                self.assertEqual(hook._turn_count({"cwd": "/project"}), 0)

    def test_new_verdicts_are_project_attributed(self):
        agent = load_module("test_outcome_agent", ROOT / "outcome-loop/agent.py")
        report = OutcomeReport.model_validate({
            "verdicts": [{
                "target_id": "1",
                "target_type": "bet",
                "verdict": "still_open",
                "reasoning": "No evidence yet.",
            }]
        })
        with mock.patch.object(agent.store, "save_verdict") as save:
            agent._apply_verdicts("project-x", report)
        self.assertEqual(save.call_args.args[0].project_id, "project-x")


if __name__ == "__main__":
    unittest.main()
