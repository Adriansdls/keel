"""Sonnet consolidation + decay review for the SWM committed store.

Triggered when a project's store goes over budget (too many facts, or rendered state too
large). Sonnet merges near-duplicates, drops genuinely superseded facts, and keeps the
load-bearing ones — with judgment, never blind truncation. Decayed facts (not re-seen in
DECAY_TURNS) are handed to Sonnet flagged as low-confidence rather than time-expired
blindly, so a durable-but-quiet fact (a deadline, a hard constraint) survives.

Models: capture uses Haiku (high-recall extraction, runs every turn); consolidation uses
Sonnet (rare, high-stakes — it can delete memory, so it gets the stronger reasoner).
Fail-open: on any error the store is left exactly as it was.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import swm_store as store  # noqa: E402

SUB_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}

_PROMPT = (
    "You are consolidating a project's durable strategic memory. Below is a JSON list of facts, "
    "each with: id, kind (constraint|decision|elimination|premise), text, and stale=true if it has "
    "not been re-observed recently.\n\n"
    "Rules:\n"
    "- MERGE facts that say the same thing; keep the clearest single phrasing.\n"
    "- DROP facts that are genuinely superseded or obsolete.\n"
    "- KEEP durable facts even if stale=true (deadlines, hard constraints, irreversible decisions). "
    "Only drop a stale fact if it is clearly no longer relevant.\n"
    "- Do NOT invent facts. Preserve kind. Keep text short and verbatim-ish.\n"
    "- Return the trimmed set; aim well under the original count when there is redundancy.\n\n"
    'Output ONLY JSON: {"facts":[{"id":"<existing id or empty>","kind":"...","text":"..."}]}\n\nFACTS:\n'
)


def _sonnet(payload: str, timeout: float = 90.0) -> list[dict]:
    with tempfile.TemporaryDirectory() as td:
        p = subprocess.run(
            ["claude", "-p", "--model", "sonnet", "--output-format", "json", "--setting-sources", "project",
             _PROMPT + payload],
            cwd=td, capture_output=True, text=True, timeout=timeout, env=SUB_ENV, stdin=subprocess.DEVNULL,
        )
    if not p.stdout.strip():
        raise RuntimeError(f"empty stdout rc={p.returncode}")
    outer = json.loads(p.stdout)
    body = outer.get("result", "") if isinstance(outer, dict) else ""
    if "usage limit" in body.lower():
        raise RuntimeError("capped")
    m = re.search(r"\{.*\}", body, re.DOTALL)
    if not m:
        raise RuntimeError("no json")
    facts = json.loads(m.group(0)).get("facts", [])
    return [f for f in facts if f.get("kind") in store.KINDS and (f.get("text") or "").strip()]


def consolidate(committed_path: Path, state_md: Path, archive_path: Path, now_turn: int) -> dict:
    """Run one consolidation pass. Returns {before, after, dropped} or {skipped: reason}."""
    facts = store.load(committed_path)
    if len(facts) < 4:
        return {"skipped": "too few facts"}

    decayed_ids = {f["id"] for f in store.decayed(committed_path, now_turn)}
    payload = json.dumps(
        [{"id": f["id"], "kind": f["kind"], "text": f["text"], "stale": f["id"] in decayed_ids} for f in facts],
        ensure_ascii=False,
    )
    try:
        kept = _sonnet(payload)
    except Exception as e:
        return {"skipped": f"sonnet unavailable: {e}"}
    if not kept:
        return {"skipped": "empty result (kept store)"}

    by_id = {f["id"]: f for f in facts}
    new_facts: list[dict] = []
    kept_ids: set[str] = set()
    for k in kept:
        text = k["text"].strip()
        _id = store.fid(k["kind"], text)
        orig = by_id.get(k.get("id")) or by_id.get(_id)
        if orig:
            rec = dict(orig)
            rec["text"] = text  # accept merged phrasing
        else:
            rec = {"id": fid, "kind": k["kind"], "text": text,
                   "turn_added": now_turn, "last_seen": now_turn, "source": "consolidation"}
        if rec["id"] not in kept_ids:
            new_facts.append(rec)
            kept_ids.add(rec["id"])

    dropped = [f for f in facts if f["id"] not in {nf["id"] for nf in new_facts}]
    if dropped:  # archive, never hard-delete
        with archive_path.open("a", encoding="utf-8") as fh:
            for d in dropped:
                d = dict(d); d["archived_turn"] = now_turn
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")

    store.save(committed_path, new_facts)
    store.render(committed_path, state_md)
    return {"before": len(facts), "after": len(new_facts), "dropped": len(dropped)}
