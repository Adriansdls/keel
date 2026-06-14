"""Structured committed-facts store — the durable source of truth for SWM memory.

Each project has a committed.jsonl (one fact per line). strategic-state.md is a RENDERED
view of it, regenerated on every mutation, so the inject hook and git stay human-readable.

A fact record:
    {id, kind, text, turn_added, last_seen, source}

- id         : sha1(kind + normalized text)[:12] — stable, dedupes exact repeats
- kind       : decision | constraint | elimination | premise
- last_seen  : turn index of the most recent (re-)observation — drives time-decay
- source     : "capture" (Haiku auto-commit) | "manual" (swm cli) | "consolidate"

Auto-commit (every substantive turn) writes here. Dedup is two-layer: exact id match,
then a cheap token-overlap near-dup guard. The subtle near-duplicates that survive are
cleaned by the Sonnet consolidation pass (swm_consolidate.py) when the store goes over
budget. Time-decay never hard-deletes: stale facts are flagged for the consolidation
pass, which keeps durable facts (deadlines, hard constraints) with judgment.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

KINDS = ("decision", "constraint", "elimination", "premise")

# Render order + section headers.
SECTION = {
    "decision": "Decisions",
    "constraint": "Constraints",
    "elimination": "Eliminations / rejected",
    "premise": "Premises (provisional)",
}

# Budget: per-section fact cap + total rendered-text char cap. Going over either
# triggers the Sonnet consolidation pass. Tuned so the injected block stays bounded
# (re-injected every turn — unbounded growth = unbounded per-turn token cost).
MAX_PER_SECTION = 25
MAX_TOTAL_CHARS = 6000

# Facts not re-observed in this many turns are flagged for consolidation review.
DECAY_TURNS = 60


def _norm(text: str) -> str:
    # Lowercase, strip punctuation to spaces, collapse whitespace. Punctuation-only
    # variants ("realpath(cwd)" vs "realpath cwd", "per-project" vs "per project")
    # collapse to the same normalized form → exact-id dedup catches them.
    t = re.sub(r"[^a-z0-9]+", " ", (text or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def fid(kind: str, text: str) -> str:
    return hashlib.sha1(f"{kind}:{_norm(text)}".encode()).hexdigest()[:12]


# --- fact invariants (declared in schemas/fact_list.json, enforced here) ----------
# The capture step is an *agentic* step (Haiku). Its output is caged by these
# invariants at the commit chokepoint so leaked markdown headers and ephemeral
# session-actions never enter the durable store. This is the single gate every fact
# passes through (auto-commit from detect AND precompact), so enforcing here is
# sufficient — no per-caller duplication.

# Lines that are document structure, not strategic facts.
_MARKDOWN_LEAD = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|>\s|\||\d+[.)]\s|```)")
# Ephemeral first-person / session-state phrasing — an action-in-progress, not a fact.
_EPHEMERAL = re.compile(
    r"^\s*(i['’]?ll\b|i will\b|next i\b|now i\b|then i\b|let me\b|we['’]?ll\b|we will\b"
    r"|going to\b|will (commit|run|add|fix|write|update|build)\b|todo\b)",
    re.IGNORECASE,
)
# Session-scoped artifacts that leaked in (hook/turn/session machinery).
_SESSION_NOISE = re.compile(r"\b(this session|this turn|stop hook|session-scoped|hook is active)\b",
                            re.IGNORECASE)


def valid_fact(kind: str, text: str) -> tuple[bool, str]:
    """Gate a candidate fact against the declared invariants. Returns (ok, reason).
    Rejects markdown structure, ephemeral first-person actions, and session noise.
    (atomic_facts / no_overlap are handled separately by the dedup pass.)"""
    if kind not in KINDS:
        return False, "bad_kind"
    t = (text or "").strip()
    if not t:
        return False, "empty"
    if _MARKDOWN_LEAD.match(t):
        return False, "no_markdown_headers"
    if _EPHEMERAL.match(t):
        return False, "no_ephemeral_actions"
    if _SESSION_NOISE.search(t):
        return False, "no_ephemeral_actions"
    return True, ""


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def _atomic_write(path: Path, content: str) -> None:
    """Write content atomically via a temp file + os.replace (POSIX-atomic rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".swm-tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def save(path: Path, facts: list[dict]) -> None:
    body = "\n".join(json.dumps(f, ensure_ascii=False) for f in facts)
    _atomic_write(path, body + ("\n" if facts else ""))


def _near_dup(a: str, b: str, thresh: float = 0.6) -> bool:
    """Cheap token-overlap (Jaccard) near-duplicate guard. The subtle cases are left
    for Sonnet consolidation — this only catches obvious restatements to keep the store
    from ballooning between consolidation passes."""
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if not wa or not wb:
        return False
    return len(wa & wb) / len(wa | wb) >= thresh


def _subsumes(a: str, b: str) -> bool:
    """True if a's token set fully contains b's (b is a less-informative subset of a).
    Catches the compound/split case Jaccard misses: a compound fact "X; Y" subsumes its
    atomic halves "X" and "Y" even though token counts differ ~2x. Requires b to carry
    real content (>=3 tokens) so trivial fragments don't trigger collapses."""
    wa, wb = set(_norm(a).split()), set(_norm(b).split())
    if len(wb) < 3 or not wa:
        return False
    return wb < wa  # strict subset


def _related(a: str, b: str) -> bool:
    return _near_dup(a, b) or _subsumes(a, b) or _subsumes(b, a)


def _dedupe_once(facts: list[dict]) -> list[dict]:
    kept: list[dict] = []
    for f in facts:
        text = (f.get("text") or "").strip()
        if not text:
            continue
        anchor = next((g for g in kept
                       if g.get("kind") == f.get("kind") and _related(g.get("text", ""), text)), None)
        if anchor is None:
            kept.append(dict(f))
            continue
        # Merge into whichever phrasing is longer / more complete.
        if len(text) > len(anchor.get("text", "")):
            anchor["text"] = text
            anchor["id"] = fid(anchor["kind"], text)
        anchor["last_seen"] = max(int(anchor.get("last_seen", 0)), int(f.get("last_seen", 0)))
        anchor["turn_added"] = min(int(anchor.get("turn_added", 10**9)), int(f.get("turn_added", 10**9)))
    return kept


def _dedupe_facts(facts: list[dict]) -> list[dict]:
    """Collapse near-dups and containment pairs within a same-kind set, keeping the
    longer (more complete) text and merging metadata (max last_seen, min turn_added).

    Iterates to a fixpoint: a compound fact may subsume several atomic splits, and the
    first pass only absorbs the splits seen before it. Re-running until the count stops
    shrinking guarantees every subsumed fact is collapsed regardless of input order."""
    prev = facts
    for _ in range(8):  # bounded; converges in 1-2 passes in practice
        cur = _dedupe_once(prev)
        if len(cur) == len(prev):
            return cur
        prev = cur
    return prev


def dedupe(path: Path) -> int:
    """Maintenance pass: collapse dupes already in the store. Returns count removed."""
    facts = load(path)
    cleaned = _dedupe_facts(facts)
    if len(cleaned) != len(facts):
        save(path, cleaned)
    return len(facts) - len(cleaned)


def commit_facts(path: Path, facts: list[dict], turn: int, source: str = "capture") -> dict:
    """Add facts to the store. Exact-id, near-dup and containment matches bump last_seen
    (and adopt the longer phrasing) instead of adding a row. Returns {"added", "bumped"}."""
    existing = load(path)
    by_id = {f.get("id"): f for f in existing}
    added = bumped = dropped = 0
    rejects: list[dict] = []
    for f in facts:
        kind = f.get("kind")
        text = (f.get("text") or "").strip()
        ok, reason = valid_fact(kind, text)
        if not ok:
            if text:
                rejects.append({"kind": kind, "text": text, "reason": reason})
            dropped += 1
            continue
        _id = fid(kind, text)
        if _id in by_id:
            by_id[_id]["last_seen"] = turn
            bumped += 1
            continue
        match = next((g for g in existing
                      if g.get("kind") == kind and _related(g.get("text", ""), text)), None)
        if match is not None:
            match["last_seen"] = turn
            # Adopt the longer phrasing so a compound restatement upgrades an atomic stub.
            if len(text) > len(match.get("text", "")):
                match["text"] = text
                match["id"] = fid(kind, text)
                by_id[match["id"]] = match
            bumped += 1
            continue
        rec = {"id": _id, "kind": kind, "text": text,
               "turn_added": turn, "last_seen": turn, "source": source}
        # carry through routing provenance + strategic-priority linkage when present
        for k in ("project", "routed_from", "route_confidence", "traces_to"):
            if f.get(k) is not None:
                rec[k] = f[k]
        existing.append(rec)
        by_id[_id] = rec
        added += 1
    # Final fixpoint pass catches intra-batch containment chains the incremental
    # first-match merge above misses (a compound subsuming several atomic splits).
    existing = _dedupe_facts(existing)
    save(path, existing)
    if rejects:
        _append_archive(path.parent / "dropped.jsonl", rejects, reason="invariant")
    return {"added": added, "bumped": bumped, "dropped": dropped}


def remove(path: Path, archive_path: Path, fact_id: str) -> bool:
    """Tombstone a fact (move to archive). Used by `swm dismiss` to correct a bad
    auto-commit. Returns True if a fact was removed."""
    facts = load(path)
    keep = [f for f in facts if f.get("id") != fact_id]
    if len(keep) == len(facts):
        return False
    dropped = [f for f in facts if f.get("id") == fact_id]
    _append_archive(archive_path, dropped, reason="dismissed")
    save(path, keep)
    return True


def forget(path: Path, archive_path: Path, ids: set[str]) -> int:
    """Tombstone multiple facts by id (move to archive). Returns count removed."""
    facts = load(path)
    keep = [f for f in facts if f.get("id") not in ids]
    dropped = [f for f in facts if f.get("id") in ids]
    if dropped:
        _append_archive(archive_path, dropped, reason="dismissed")
        save(path, keep)
    return len(dropped)


def max_turn(path: Path) -> int:
    """Highest turn_added in the store. Used as the high-water mark when a priority is created:
    its created_turn is floored to max_turn+1 so a new spine holds only FUTURE captures
    accountable — not the whole pre-existing backlog. Clock-consistent with the capture path
    (turn_added and this max share the same counter; the inject bump-counter does NOT)."""
    return max((int(f.get("turn_added") or 0) for f in load(path)), default=0)


def link_trace(path: Path, fact_id: str, priority_id: str) -> bool:
    """Link a fact UP to a strategic priority (idempotent). Matches id or id-prefix."""
    facts = load(path)
    hit = False
    for f in facts:
        if f.get("id") == fact_id or f.get("id", "").startswith(fact_id):
            tt = f.get("traces_to") or []
            if priority_id not in tt:
                tt.append(priority_id)
            f["traces_to"] = tt
            hit = True
    if hit:
        save(path, facts)
    return hit


def untraced(path: Path, since_turn: int = 0) -> list[dict]:
    """Decisions/constraints that ladder up to no priority — the drift surface.

    `since_turn` scopes to work captured AFTER the spine existed: facts predating the earliest
    active priority are not held accountable to it (no retroactive drift on backlog)."""
    return [f for f in load(path)
            if f.get("kind") in ("decision", "constraint")
            and not (f.get("traces_to") or [])
            and int(f.get("turn_added") or 0) >= since_turn]


def _append_archive(archive_path: Path, facts: list[dict], reason: str) -> None:
    if not facts:
        return
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("a") as fh:
        for f in facts:
            rec = dict(f, archived_reason=reason)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def premises(path: Path) -> list[dict]:
    """Premise-kind facts in the shape premise_eval expects: [{id, text}]."""
    return [{"id": f["id"], "text": f["text"]}
            for f in load(path) if f.get("kind") == "premise" and f.get("text")]


def over_budget(path: Path) -> bool:
    facts = load(path)
    if not facts:
        return False
    per: dict[str, int] = {}
    for f in facts:
        per[f.get("kind")] = per.get(f.get("kind"), 0) + 1
    if any(c > MAX_PER_SECTION for c in per.values()):
        return True
    total = sum(len(f.get("text", "")) for f in facts)
    return total > MAX_TOTAL_CHARS


def decayed(path: Path, now_turn: int) -> list[dict]:
    """Facts not re-observed within DECAY_TURNS — candidates for consolidation review."""
    return [f for f in load(path)
            if now_turn - int(f.get("last_seen", f.get("turn_added", 0))) > DECAY_TURNS]


def render(path: Path, state_md: Path) -> None:
    """Regenerate strategic-state.md from the store. Empty store → remove the file.

    Self-discovers priorities.jsonl beside committed.jsonl and prepends the strategic-priority
    spine at the TOP (above the fact sections) when any active priority exists — so the spine
    rides into context through the existing inject path with no inject-hook change."""
    facts = load(path)
    spine = ""
    try:  # lazy: priorities are optional; absence must not break fact rendering
        import swm_priority as _prio
        spine = _prio.render_section(_prio.load(path.parent / "priorities.jsonl"))
    except Exception:
        spine = ""
    if not facts and not spine:
        if state_md.exists():
            state_md.unlink()
        return
    lines = [
        "# Strategic State",
        "",
        "_Durable world-model — auto-maintained by SWM, re-injected each turn._",
        "",
    ]
    if spine:
        lines.append(spine)
    for kind in KINDS:
        fs = [f for f in facts if f.get("kind") == kind]
        if not fs:
            continue
        # Most-recently-seen first, capped per section.
        fs.sort(key=lambda f: (-int(f.get("last_seen", 0)), int(f.get("turn_added", 0))))
        lines.append(f"## {SECTION[kind]}")
        for f in fs[:MAX_PER_SECTION]:
            lines.append(f"- {f['text']}")
        lines.append("")
    _atomic_write(state_md, "\n".join(lines).rstrip() + "\n")
