from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shared import llm
from shared import store


class _SuccessfulProc:
    pid = 1234
    returncode = 0

    def __init__(self, args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def communicate(self, timeout=None):
        return json.dumps({"result": '{"events": []}'}), ""


class _TimeoutProc(_SuccessfulProc):
    def communicate(self, timeout=None):
        if timeout is None:
            return "", ""
        raise subprocess.TimeoutExpired(self.args, timeout)


class RuntimeSafetyTests(unittest.TestCase):
    def test_internal_claude_disables_user_settings_and_sets_sentinel(self):
        with mock.patch.object(subprocess, "Popen", _SuccessfulProc):
            raw = llm._call_subprocess("prompt", "model", 1)
        self.assertEqual(raw, '{"events": []}')
        created = []

        def make_proc(args, **kwargs):
            proc = _SuccessfulProc(args, **kwargs)
            created.append(proc)
            return proc

        with mock.patch.object(subprocess, "Popen", side_effect=make_proc):
            llm._call_subprocess("prompt", "model", 1)
        proc = created[0]
        self.assertIn("--setting-sources", proc.args)
        self.assertEqual(proc.args[proc.args.index("--setting-sources") + 1], "project")
        self.assertEqual(proc.kwargs["env"]["KEEL_INTERNAL_LLM"], "1")
        self.assertTrue(proc.kwargs["start_new_session"])

    def test_timeout_kills_complete_process_group(self):
        proc = _TimeoutProc(["claude"])
        with (
            mock.patch.object(subprocess, "Popen", return_value=proc),
            mock.patch.object(os, "killpg") as killpg,
            self.assertRaises(llm.LLMExtractionError),
        ):
            llm._call_subprocess("prompt", "model", 1)
        killpg.assert_called_once_with(proc.pid, mock.ANY)

    def test_every_installed_hook_has_internal_guard(self):
        hooks = [
            "swm/inject.py",
            "swm/capture.py",
            "swm/premise_check.py",
            "swm/pre_compact.py",
            "auto-capture/hook.py",
            "entropy/hook.py",
            "outcome-loop/hook.py",
            "ra-pm/hook.py",
        ]
        env = {**os.environ, "KEEL_INTERNAL_LLM": "1"}
        python = ROOT / ".venv/bin/python"
        executable = str(python if python.exists() else sys.executable)
        for hook in hooks:
            result = subprocess.run(
                [executable, str(ROOT / hook)],
                input="{}",
                text=True,
                capture_output=True,
                env=env,
                timeout=5,
            )
            self.assertEqual(result.returncode, 0, f"{hook}: {result.stderr}")

    def test_installer_reconciles_async_hook_specs(self):
        text = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn('"outcome-loop/hook.py"), "timeout": 210, "async": True', text)
        self.assertIn('"entropy/hook.py"), "timeout": 120, "async": True', text)
        self.assertIn("desired_commands", text)

    def test_jsonl_append_preserves_concurrent_writers(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "records.jsonl"
            threads = [
                threading.Thread(target=store._atomic_jsonl_append, args=(path, {"id": i}))
                for i in range(40)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            records = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual({record["id"] for record in records}, set(range(40)))


if __name__ == "__main__":
    unittest.main()
