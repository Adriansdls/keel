"""Per-project state resolution for the globally-installed strategic-working-memory hooks.

The shipped hooks stored all state next to the script (HERE.parent). That is correct for a
single project but wrong once the hooks are installed globally and shared by every Claude
Code project: every project would read/write ONE shared world-model and cross-contaminate.

This resolves a per-project state directory keyed off the session cwd, mirroring how Claude
Code itself stores per-project transcripts (~/.claude/projects/<escaped-cwd>/). Each project
gets its own isolated strategic state, candidates, premise findings, counters and cold log.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.store import swm_root as _swm_root
ROOT = _swm_root()  # reads $COWORK_HOME/swm, default ~/.cowork/swm

# The kernel (habitat) owns project identity. We key state by the kernel's project_id so
# every subdir of a project shares ONE world-model (no per-cwd fragmentation) and so a
# fact's home is its PROJECT, not the directory it was typed in. Best-effort import: if the
# kernel is unavailable we fall back to the legacy realpath-tag (still correct, just per-cwd).
_HABITAT = Path.home() / "habitat"
if str(_HABITAT) not in sys.path:
    sys.path.insert(0, str(_HABITAT))
try:
    from kernel.project import resolve_project as _resolve_project  # type: ignore
except Exception:  # kernel not importable — degrade to cwd-tag keying
    _resolve_project = None


def _tag(cwd: str) -> str:
    # Mirror Claude Code's project-dir escaping: /Users/x/y -> -Users-x-y.
    # realpath (not abspath) so a hook event cwd ("/tmp/x") and the process cwd
    # ("/private/tmp/x" after macOS symlink resolution) normalize to the SAME tag —
    # otherwise the hook and the CLI would key to different state dirs for symlinked paths.
    return os.path.realpath(cwd or os.getcwd()).replace("/", "-")


def project_key(cwd: str) -> str:
    """Resolve the storage key for a cwd. Prefer the kernel project_id (so all subdirs of a
    project share one store); fall back to the realpath cwd-tag for untracked dirs."""
    cwd = cwd or os.getcwd()
    if _resolve_project is not None:
        try:
            pid = _resolve_project(cwd)
            if pid and pid not in ("unknown", ""):
                return pid.replace("/", "-")
        except Exception:
            pass
    return _tag(cwd)


def project_dir(cwd: str) -> Path:
    d = ROOT / project_key(cwd)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _ns(base: Path) -> SimpleNamespace:
    return SimpleNamespace(
        base=base,
        # committed.jsonl is the SOURCE OF TRUTH (structured, per-fact metadata).
        # strategic-state.md is a rendered VIEW of it, regenerated on every mutation,
        # so inject + git stay human-readable.
        committed=base / "committed.jsonl",
        archive=base / "committed.archive.jsonl",
        state=base / "strategic-state.md",
        candidates=base / "strategic-candidates.jsonl",
        findings=base / "premise-findings.json",
        turn_counter=base / ".swm-turn-counter",
        premise_counter=base / ".swm-premise-counter",
        backups=base / "state-backups",
        cold=base / "cold-logs",
        reroute_queue=base / "reroute-queue.jsonl",
    )


def resolve(event: dict) -> SimpleNamespace:
    """Resolve all per-project state paths from a hook event. cwd comes from the event
    (Claude Code populates it); falls back to the process cwd (hooks run in the project dir)."""
    return _ns(project_dir((event or {}).get("cwd") or os.getcwd()))


def for_project(project_id: str) -> SimpleNamespace:
    """Resolve the state paths for an explicit project_id (used by the topic router when a fact
    is filed into a project other than the one the cwd resolves to)."""
    base = ROOT / (project_id or "unknown").replace("/", "-")
    base.mkdir(parents=True, exist_ok=True)
    return _ns(base)


def disabled() -> bool:
    """Global kill switch: export SWM_DISABLE=1 to turn the whole stack off everywhere."""
    return bool(os.environ.get("SWM_DISABLE"))
