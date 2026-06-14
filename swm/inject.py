#!/usr/bin/env python3
"""UserPromptSubmit hook — re-inject the strategic-state world-model every turn.

This is the mechanism that makes compaction harmless: the durable world-model
lives in strategic-state.md, OUTSIDE the conversation, and is re-injected into
context on every turn. Compaction can shred the chat; the state survives in the
file and re-enters context next turn.

Also folds in the periodic premise-check nudge (every N turns) — the dominant
strategic failure is a confidently-wrong premise, and the cheapest defense is a
visible, recurring reminder to run the un-skippable premise check.

Pattern mirrors ~/.claude/hooks/beast-pre-turn.py: read stdin JSON, print the
block to stdout (which lands in the model's next-turn context), always exit 0
(fail-open — never block the user).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # ~/raising-agents/.claude/hooks
sys.path.insert(0, str(HERE))
from capture_patterns import load_candidates     # noqa: E402
import cold_log as cl                             # noqa: E402  (recall from untouched full log)
from swm_paths import resolve, disabled           # noqa: E402  (per-project state, global kill switch)
import swm_store as store                         # noqa: E402  (atomic_write)

# Module-level defaults; rebound per-project from the event cwd inside main().
STATE_FILE = HERE / "strategic-state.md"
CANDIDATES_FILE = HERE / "strategic-candidates.jsonl"
FINDINGS_FILE = HERE / "premise-findings.json"
COUNTER_FILE = HERE / ".swm-turn-counter"
PREMISE_NUDGE_EVERY = 5
MAX_INJECT_BYTES = 12_000  # guardrail: strategic state must stay small


def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _bump_counter() -> int:
    try:
        n = int(COUNTER_FILE.read_text().strip()) if COUNTER_FILE.exists() else 0
    except Exception:
        n = 0
    n += 1
    try:
        store._atomic_write(COUNTER_FILE, str(n))
    except Exception:
        pass
    return n


def main() -> int:
    if disabled():
        return 0
    event = _read_event()
    global STATE_FILE, CANDIDATES_FILE, FINDINGS_FILE, COUNTER_FILE
    P = resolve(event)
    STATE_FILE, CANDIDATES_FILE, FINDINGS_FILE, COUNTER_FILE = (
        P.state, P.candidates, P.findings, P.turn_counter)
    cl.configure(P.cold)
    prompt = event.get("prompt") or event.get("user_prompt") or ""
    sid = event.get("session_id", "")
    # RECALL: if the user references something earlier, fetch it from the untouched cold log
    # (covers anything compaction/pruning dropped from the live window).
    recall_block = ""
    if prompt and sid and cl.wants_recall(prompt):
        try:
            hits = cl.recall(prompt, sid, k=3)
        except Exception:
            hits = []
        if hits:
            recall_block = "↺ recalled from full session log:\n" + "\n".join(
                f"  · {h['text'][:240]}" for h in hits)
    # Committed world-model (may not exist yet on a fresh project — that's fine;
    # pending candidates / findings / recall must still surface so capture is
    # never invisible, otherwise a new project can never bootstrap its state).
    content = ""
    try:
        if STATE_FILE.exists():
            content = STATE_FILE.read_text()
    except Exception:
        content = ""
    if len(content.encode()) > MAX_INJECT_BYTES:
        content = content.encode()[:MAX_INJECT_BYTES].decode(errors="ignore")
        content += "\n… [strategic-state truncated — it is over budget; prune live items]"

    turn = _bump_counter()
    block = []
    if content.strip():
        block.append(
            "╭─ strategic working memory (durable world-model — survives compaction) ─")
        block.append(content.rstrip())
    if recall_block:
        block.append(recall_block)

    # Session goal (L4) — always-visible milestone + exploration counter.
    # Prepended FIRST so it's the anchor you see before all other context.
    try:
        import session_goal as sg
        _gp = P.committed.parent / "session_goal.json"
        _g = sg.load(_gp, sid)
        if _g:
            _gb = sg.render_block(_g)
            if _gb.strip():
                if not block:
                    block.append(
                        "╭─ strategic working memory (durable world-model — survives compaction) ─")
                block.insert(1 if len(block) > 1 else len(block), _gb.rstrip())
    except Exception:
        pass

    # Capture is fully automatic now (Stop + PreCompact hooks auto-commit to the store),
    # so there is no pending-candidate queue to nag about. Correct a wrong auto-commit
    # with `swm forget <id>`; inspect with `swm show`.

    # Premise-check findings (written by the guaranteed-cadence Stop hook).
    findings = None
    try:
        if FINDINGS_FILE.exists():
            findings = json.loads(FINDINGS_FILE.read_text())
    except Exception:
        findings = None
    if findings and findings.get("invalid"):
        bad = {r["premise_id"]: r.get("evidence", "") for r in findings.get("results", []) if r["status"] == "invalid"}
        block.append(f"⛔ PREMISE CHECK — {len(bad)} INVALID premise(s) detected ({findings.get('backend','')}). "
                     "STOP: do not build further on these until corrected:")
        for pid, why in bad.items():
            block.append(f"  ⛔ {pid}: {why}")
    elif findings and findings.get("challenged"):
        block.append(f"⚠ premise check ({findings.get('backend','')}): challenged → "
                     f"{', '.join(findings['challenged'])}. Verify before relying on them.")
    elif findings:
        block.append(f"✅ premise check ({findings.get('backend','')}): all operating-premise facts hold.")
    elif content.strip() and turn % PREMISE_NUDGE_EVERY == 0:
        block.append("⚠ premise check pending — the cadence hook has not run yet this session.")
    # Reroute queue — facts that may belong to another project, awaiting review.
    try:
        if P.reroute_queue.exists():
            qn = sum(1 for ln in P.reroute_queue.read_text().splitlines() if ln.strip())
            if qn:
                block.append(f"↪ {qn} fact(s) may belong to another project → `swm reroute`")
    except Exception:
        pass
    # Strategic spine — the priorities work must ladder up to. Default-on in EVERY project:
    #   (1) no spine + project has a ra-pm thesis  → auto-seed from it (no fabrication)
    #   (2) no spine + project has real decisions   → session-once nudge, offer to propose one
    #   (3) spine exists                            → DRIFT gate on untraced post-spine work
    try:
        import swm_priority as prio
        prio_path = P.committed.parent / "priorities.jsonl"
        act = prio.active(prio.load(prio_path))
        if not act:  # (1) auto-seed from ra-pm thesis where strategy already lives — idempotent
            try:
                seed_turn = max(turn, store.max_turn(P.committed) + 1)  # exclude pre-spine backlog
                prio.sync_from_rapm(prio_path, P.base.name, seed_turn)
                act = prio.active(prio.load(prio_path))
                if act:
                    store.render(P.committed, P.state)
            except Exception:
                pass
        # L5→L3 nudge: active ra-pm issues not linked to any priority.
        # Soft: appears once per session alongside the spine, not a blocker.
        try:
            import sys as _sys
            _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
            from shared.store import load_issues as _load_issues
            active_s = {"planned", "in-progress", "idea", "blocked"}
            pid = P.base.name
            unlinked = [i for i in _load_issues(pid)
                        if (i.status if hasattr(i, "status") else i.get("status")) in active_s
                        and not (i.traces_to_priority if hasattr(i, "traces_to_priority") else i.get("traces_to_priority"))]
            if unlinked:
                block.append(
                    f"◌ UNLINKED ISSUES ({len(unlinked)}): active ra-pm issues not traced to a priority. "
                    "Fix: `swm link-issue {project} <id> <priority-id>` or `swm priority list` to pick one.")
        except Exception:
            pass
        if act:  # (3) drift gate
            since = min(p.created_turn for p in act)
            un = store.untraced(P.committed, since_turn=since)
            if un:
                names = "; ".join(f"[{p.id}] {p.statement}" for p in act[:5])
                block.append(
                    f"⚠ DRIFT — {len(un)} decision(s)/constraint(s) ladder up to NO strategic priority. "
                    f"Active spine: {names}. For each: `swm trace <fact-id> <priority-id>`, open a new "
                    "priority if this is genuinely new direction, or tell Adrian it is off-mission.")
                for f in un[:5]:
                    block.append(f"  ↯ [{f['id']}] ({f['kind']}) {f['text'][:140]}")
        # Session goal nudge — fires ONCE per session if spine exists but no session goal is set.
        # Gives the user a clear choice: anchor the session (/swm-goal) or run strategy-free.
        if act:
            try:
                import session_goal as sg
                _gp = P.committed.parent / "session_goal.json"
                _g = sg.load(_gp, sid)
                if _g is None and sid:
                    _sentinel = P.committed.parent / f".goal-nudged-{sid}"
                    if not _sentinel.exists():
                        try:
                            _sentinel.write_text("1")
                        except Exception:
                            pass
                        block.append(
                            "◇ NO SESSION GOAL — `/swm-goal` to set one and anchor drift tracking, "
                            "or continue strategy-free. (This nudge fires once per session.)")
            except Exception:
                pass
        else:  # (2) no spine anywhere — nudge ONCE per session if the project has real decisions
            decisions = sum(1 for f in store.load(P.committed) if f.get("kind") == "decision")
            sentinel = P.base / f".spine-nudged-{sid}" if sid else P.base / ".spine-nudged"
            if decisions >= 3 and not sentinel.exists():
                try:
                    sentinel.write_text(str(turn))
                except Exception:
                    pass
                block.append(
                    f"◇ NO STRATEGIC SPINE — this project has {decisions} decisions tracing to no priority. "
                    "Strategic memory can't detect drift without a spine. Set one (`swm priority add \"...\"` "
                    "or `swm priority sync <ra-pm-id>`), or ask me to PROPOSE priorities from the decision "
                    "history for you to ratify (`swm priority propose`).")
    except Exception:
        pass

    # Cross-project: inject global facts (decisions/constraints with project=None)
    try:
        import sys as _sys
        _sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
        from shared.store import load_facts as _load_global_facts
        from shared.models import FactKind
        _global = _load_global_facts(project_id=None, kinds=[FactKind.decision, FactKind.constraint])
        if _global:
            _glines = ["─ global (all projects) ─"]
            for _gf in _global[:10]:  # budget cap: 10 global facts max
                _glines.append(f"  [{_gf.kind}] {_gf.text[:120]}")
            block.append("\n".join(_glines))
    except Exception:
        pass
    if not block:
        return 0
    # Frame the whole block. Top border already added when committed state exists;
    # if not, open one now so pending-only output is still visually delimited.
    if not block[0].startswith("╭─"):
        block.insert(0, "╭─ strategic working memory ─")
    block.append("╰─")
    print("\n".join(block), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[inject-strategic-state] error: {e}", file=sys.stderr)
        sys.exit(0)
