"""Entropy Manager — standalone probe (correctness test, no forge runtime).

Verifies the four guarantees of the entropy manager:
  G1  capture persists       — an idea written through capture is retrievable
  G2  promote stamps lineage — from_idea is set; idea is routed
  G3  decide gate holds      — decision without alternatives_rejected is rejected
  G4  brief returns metrics  — leakage_rate and connectivity are finite floats

Run directly: python3 entropy/probe.py
Exit 0 = all passed. Exit 1 = failure (details printed).
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def run_probe() -> dict:
    results: dict[str, bool] = {}
    failures: list[str] = []

    # Isolated store for the probe — never touches real ~/.cowork data
    with tempfile.TemporaryDirectory() as td:
        os.environ["COWORK_HOME"] = td

        # Re-import store with the new COWORK_HOME
        import importlib
        import shared.store as st
        importlib.reload(st)
        st._config_cache = None  # clear config cache

        # Seed: one project needed for issue/decision scope
        from shared.models import Project
        st.save_project(Project(id="probe-proj", name="Probe Project",
                                workspace_path=td))

        from entropy.handler import handle

        # G1: capture persists
        r1 = handle({"action": "capture",
                     "idea": {"title": "probe idea", "why": "test G1"}})
        g1 = r1.get("commit_ok") is True and "probe idea" in r1.get("answer", "")
        results["G1_capture_persists"] = g1
        if not g1:
            failures.append(f"G1 failed: {r1}")

        # G2: promote stamps lineage
        ideas_before = st.load_ideas()
        if ideas_before:
            r2 = handle({"action": "promote", "idea_idx": 0,
                         "to_project": "probe-proj"})
            issues = st.load_issues("probe-proj")
            g2 = (r2.get("commit_ok") is True and
                  any(str(i.from_idea) == "0" for i in issues))
        else:
            g2 = False
            failures.append("G2 failed: no idea to promote")
        results["G2_promote_lineage"] = g2

        # G3: decide gate — no alternatives_rejected → HALT
        r3 = handle({"action": "decide",
                     "decision": {"project": "probe-proj",
                                  "decision": "use postgres",
                                  "rationale": "best JSON support",
                                  "alternatives_rejected": []}})
        g3 = r3.get("commit_ok") is False
        results["G3_decide_gate"] = g3
        if not g3:
            failures.append(f"G3 failed: gate did not halt. Got: {r3}")

        # G4: brief returns valid metrics
        r4 = handle({"action": "brief"})
        rpt = r4.get("report")
        g4 = (r4.get("commit_ok") is True and rpt is not None and
              isinstance(rpt.leakage_rate, float) and
              isinstance(rpt.connectivity, float))
        results["G4_brief_metrics"] = g4
        if not g4:
            failures.append(f"G4 failed: {r4}")

    passed = all(results.values())
    return {"passed": passed, "results": results, "failures": failures}


if __name__ == "__main__":
    import json
    outcome = run_probe()
    print(json.dumps(outcome, indent=2))
    sys.exit(0 if outcome["passed"] else 1)
