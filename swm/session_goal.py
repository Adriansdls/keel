"""SessionGoal — L4 in the anti-drift hierarchy.

A session goal is a time-bounded milestone: "build the harness to run experiments." It is NOT
project strategy (that's StrategicPriority, L3). It's the one thing you're trying to achieve in
this CC session. Claude Code drifts when it finds interesting tangents mid-session — this module
tracks that drift via an exploration budget (consecutive off-goal turns) and injects an always-
visible counter so you always know where you stand.

Mechanism:
  - Set a goal: `swm goal set "..." [--budget N] [--priority <pid>]`
  - The goal_align observer (Stop hook, Haiku-judged) fires each turn → verdict: on-goal | exploring
  - This module reads that verdict, updates consecutive_exploring counter
  - Inject hook reads session_goal.json and prepends goal + counter to EVERY turn
  - When consecutive_exploring >= budget_turns: ⚠ EXPLORATION nudge fires (NOT blocking)
  - Counter resets to 0 on any on-goal turn

Storage: ~/.claude/swm/<project>/session_goal.json  (one active goal per project per session)
Session-gate: a new CC session (new session_id) auto-clears any prior active goal.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path


def _gid(statement: str) -> str:
    return hashlib.sha1((statement or "").strip().encode()).hexdigest()[:12]


def _atomic_write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@dataclass
class SessionGoal:
    """A session-scoped milestone. Work explores — but must eventually return here."""

    statement: str
    session_id: str = ""
    traces_to: str = ""           # StrategicPriority.id — soft, nudge if unset
    budget_turns: int = 5         # consecutive off-goal turns before nudge fires
    turns_elapsed: int = 0        # total turns since goal was set
    turns_on_goal: int = 0
    consecutive_exploring: int = 0
    status: str = "active"        # active | achieved | abandoned
    id: str = field(default="")

    def __post_init__(self) -> None:
        self.statement = (self.statement or "").strip()
        if not self.id:
            self.id = _gid(self.statement)
        if self.status not in ("active", "achieved", "abandoned"):
            self.status = "active"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SessionGoal":
        known = {k: d.get(k) for k in (
            "statement", "session_id", "traces_to", "budget_turns",
            "turns_elapsed", "turns_on_goal", "consecutive_exploring",
            "status", "id",
        ) if d.get(k) is not None}
        return cls(**known)

    @property
    def turns_remaining(self) -> int:
        """Consecutive on-goal turns before the exploration budget resets."""
        return max(0, self.budget_turns - self.consecutive_exploring)

    @property
    def is_exploring(self) -> bool:
        return self.consecutive_exploring > 0

    @property
    def budget_exceeded(self) -> bool:
        return self.consecutive_exploring >= self.budget_turns


# --- store -----------------------------------------------------------------------

def load(path: Path, session_id: str = "") -> "SessionGoal | None":
    """Load active goal. Returns None if no active goal or session has changed."""
    if not path.exists():
        return None
    try:
        d = json.loads(path.read_text())
        g = SessionGoal.from_dict(d)
        if g.status != "active":
            return None
        if session_id and g.session_id and g.session_id != session_id:
            return None  # new session — prior goal is implicitly stale
        return g
    except Exception:
        return None


def save(path: Path, goal: "SessionGoal | None") -> None:
    if goal is None:
        if path.exists():
            path.unlink()
        return
    _atomic_write(path, json.dumps(goal.to_dict(), indent=2))


def set_goal(path: Path, statement: str, session_id: str, budget: int = 5,
             traces_to: str = "") -> SessionGoal:
    """Create or replace the session goal for this project."""
    g = SessionGoal(statement=statement, session_id=session_id,
                    budget_turns=budget, traces_to=traces_to)
    save(path, g)
    return g


def record_verdict(path: Path, session_id: str, on_goal: bool) -> "SessionGoal | None":
    """Called by goal_align after each turn verdict. Updates counter. Returns updated goal."""
    g = load(path, session_id)
    if g is None or g.status != "active":
        return g
    g.turns_elapsed += 1
    if on_goal:
        g.turns_on_goal += 1
        g.consecutive_exploring = 0   # reset on return
    else:
        g.consecutive_exploring += 1
    save(path, g)
    return g


def extend(path: Path, session_id: str, n: int = 5) -> "SessionGoal | None":
    """Extend the exploration budget by N turns."""
    g = load(path, session_id)
    if g is None:
        return None
    g.budget_turns += n
    save(path, g)
    return g


def set_status(path: Path, session_id: str, status: str) -> bool:
    g = load(path, session_id)
    if g is None:
        return False
    g.status = status
    save(path, g)
    return True


# --- render (for inject hook) ----------------------------------------------------

def render_block(goal: "SessionGoal") -> str:
    """One-block summary for injection at the top of strategic-state. Always visible."""
    if goal.status != "active":
        return ""
    exp = goal.consecutive_exploring
    bud = goal.budget_turns
    elapsed = goal.turns_elapsed
    pri = f"  ↳ priority: [{goal.traces_to[:8]}...]" if goal.traces_to else \
          "  ↳ ⚠ not linked to a project priority (`swm goal set ... --priority <pid>`)"
    counter = f"turn {elapsed} · exploring: {exp}/{bud}"
    header = f"## Session goal  [{counter}]"
    lines = [header, f'"{goal.statement}"', pri]
    if goal.budget_exceeded:
        lines.append(
            f"⚠ EXPLORATION ({exp}/{bud}): {exp} consecutive turns off-goal. "
            "Return to goal or `swm goal extend` to budget +5.")
    return "\n".join(lines) + "\n"
