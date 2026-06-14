"""StrategicPriority — the per-project strategic spine that sits ABOVE ra-pm.

SWM is the strategic layer; ra-pm (theses, bets, issues) is the tactical layer that
executes against it. A StrategicPriority is the forward-looking object the four existing
fact kinds (decision/constraint/elimination/premise) ladder UP to. Work that traces to no
active priority is drift — the inject hook surfaces a soft nudge so the agent either
connects it, opens a new priority, or flags it to Adrian as off-mission.

Storage: priorities.jsonl in the same per-project dir as committed.jsonl (one priority per
line). Rendered at the TOP of strategic-state.md, above the fact sections, because it is the
spine everything else hangs off.

Single-source coordination (not ownership): `sync_from_rapm` SEEDS priorities from the
ra-pm thesis where strategy currently lives, but SWM is the higher layer — once seeded,
priorities are SWM-native and authoritative; ra-pm bets/issues should trace up to them.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

STATUSES = ("active", "achieved", "paused", "dropped")

# Budget: the priority list is the spine, kept short on purpose. Too many "priorities"
# is itself a drift signal — if everything is a priority, nothing is.
MAX_ACTIVE = 7


def _norm(text: str) -> str:
    t = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def pid(statement: str) -> str:
    """Stable slug id from the statement text — dedupes exact repeats."""
    return hashlib.sha1(_norm(statement).encode()).hexdigest()[:10]


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
class StrategicPriority:
    """A forward-looking strategic objective. Work and tactical (ra-pm) artifacts trace to it."""

    statement: str
    rank: int = 100               # lower = higher priority; render order
    status: str = "active"        # active | achieved | paused | dropped
    source: str = "manual"        # manual | ra-pm:thesis:<pid> | ra-pm:bet:<id> | em
    source_card: str = ""         # L2 anchor: "A001:AI2" | "D020" | "V006" — links up to dept/company strategy
    rationale: str = ""           # why this is load-bearing
    created_turn: int = 0
    last_seen: int = 0
    id: str = field(default="")

    def __post_init__(self) -> None:
        self.statement = (self.statement or "").strip()
        if self.status not in STATUSES:
            self.status = "active"
        if not self.id:
            self.id = pid(self.statement)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "StrategicPriority":
        known = {k: d.get(k) for k in (
            "statement", "rank", "status", "source", "source_card", "rationale",
            "created_turn", "last_seen", "id",
        ) if d.get(k) is not None}
        return cls(**known)


# --- store ------------------------------------------------------------------------

def load(path: Path) -> list[StrategicPriority]:
    if not path.exists():
        return []
    out: list[StrategicPriority] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(StrategicPriority.from_dict(json.loads(line)))
        except Exception:
            continue
    return out


def save(path: Path, items: list[StrategicPriority]) -> None:
    _atomic_write(path, "\n".join(json.dumps(p.to_dict()) for p in items) + ("\n" if items else ""))


def active(items: list[StrategicPriority]) -> list[StrategicPriority]:
    a = [p for p in items if p.status == "active"]
    a.sort(key=lambda p: (p.rank, p.created_turn))
    return a


def upsert(path: Path, priority: StrategicPriority, turn: int) -> dict:
    """Add a new priority or refresh an existing one (matched by id). Returns {added|updated, id}."""
    items = load(path)
    by_id = {p.id: p for p in items}
    if priority.id in by_id:
        ex = by_id[priority.id]
        ex.last_seen = turn
        if priority.rationale:
            ex.rationale = priority.rationale
        if priority.source and priority.source != "manual":
            ex.source = priority.source
        if priority.source_card:
            ex.source_card = priority.source_card
        save(path, items)
        return {"updated": priority.id}
    priority.created_turn = priority.created_turn or turn
    priority.last_seen = turn
    items.append(priority)
    save(path, items)
    return {"added": priority.id}


def set_status(path: Path, pid_: str, status: str, turn: int) -> bool:
    if status not in STATUSES:
        return False
    items = load(path)
    for p in items:
        if p.id == pid_ or p.id.startswith(pid_):
            p.status = status
            p.last_seen = turn
            save(path, items)
            return True
    return False


def render_section(items: list[StrategicPriority]) -> str:
    """Render the priority spine for strategic-state.md (top section)."""
    act = active(items)
    if not act:
        return ""
    lines = ["## Strategic priorities (the spine — work must ladder up to these)"]
    for i, p in enumerate(act, 1):
        src = f"  ·{p.source}" if p.source and p.source != "manual" else ""
        card = f"  [↑{p.source_card}]" if p.source_card else ""
        lines.append(f"{i}. [{p.id}] {p.statement}{src}{card}")
        if p.rationale:
            lines.append(f"   ↳ {p.rationale}")
    lines.append("")
    return "\n".join(lines)


# --- ra-pm seed (coordination, not ownership) -------------------------------------

def is_anchored(items: list[StrategicPriority]) -> bool:
    """True if any active priority carries a source_card pointing up to L1/L2 strategy.
    Used by EM to determine UNANCHORED status — replaces the dead vault_anchor check."""
    return any(p.source_card for p in items if p.status == "active")


def sync_from_rapm(path: Path, project_id: str, turn: int) -> dict:
    """SEED priorities from the ra-pm thesis for `project_id`. SWM stays the higher layer:
    this only bootstraps from where strategy currently lives; it never overwrites SWM-native
    priorities. Fail-open: any error → no change."""
    ra = Path.home() / ".ra"
    seeded: list[str] = []
    try:
        import yaml  # type: ignore
    except Exception:
        return {"seeded": 0, "error": "no yaml"}
    # thesis statement -> rank 1 priority
    tf = ra / "thesis" / f"{project_id}.yaml"
    if tf.exists():
        try:
            t = yaml.safe_load(tf.read_text()) or {}
            stmt = (t.get("statement") or "").strip() if isinstance(t, dict) else ""
            if stmt:
                r = upsert(path, StrategicPriority(
                    statement=stmt, rank=1, source=f"ra-pm:thesis:{project_id}",
                    rationale="seeded from ra-pm thesis",
                ), turn)
                if "added" in r:
                    seeded.append(r["added"])
        except Exception:
            pass
    return {"seeded": len(seeded), "ids": seeded}
