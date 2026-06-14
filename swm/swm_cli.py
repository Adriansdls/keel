#!/usr/bin/env python3
"""Agent-facing CLI for strategic-working-memory — per-project, resolved off cwd.

Capture now auto-commits every extracted fact into the structured store
(committed.jsonl), which renders to strategic-state.md and is re-injected each turn.
This CLI is the control surface for inspecting and *correcting* that memory:

    python ~/.claude/hooks/swm/swm_cli.py show               # committed facts (with ids) + findings
    python ~/.claude/hooks/swm/swm_cli.py add "<kind>: text" # manually add a fact
    python ~/.claude/hooks/swm/swm_cli.py forget <id> ...    # remove wrong fact(s) -> archive
    python ~/.claude/hooks/swm/swm_cli.py consolidate        # force a Sonnet dedup/decay pass
    python ~/.claude/hooks/swm/swm_cli.py path               # print resolved state paths

`dismiss` is kept as an alias of `forget`. State is keyed off the current working
directory, so run it from inside the project.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from swm_paths import resolve  # noqa: E402
import swm_store as store  # noqa: E402

KIND_LABEL = {
    "decision": "Decisions",
    "constraint": "Constraints",
    "elimination": "Eliminations / rejected",
    "premise": "Premises (provisional)",
}


def _paths():
    # No hook event here; resolve() falls back to os.getcwd(), which is the project dir.
    return resolve({})


def _turn(p) -> int:
    try:
        return int(p.turn_counter.read_text().strip())
    except Exception:
        return 0


def cmd_show() -> int:
    p = _paths()
    facts = store.load(p.committed)
    if not facts:
        print("(no committed strategic state yet)")
    else:
        now = _turn(p)
        for kind in store.KINDS:
            fs = [f for f in facts if f.get("kind") == kind]
            if not fs:
                continue
            fs.sort(key=lambda f: (-f.get("last_seen", 0), f.get("turn_added", 0)))
            print(f"\n## {KIND_LABEL[kind]}")
            for f in fs:
                age = now - f.get("last_seen", f.get("turn_added", 0))
                stale = "  ⏳stale" if age > store.DECAY_TURNS else ""
                print(f"[{f['id']}] {f['text']}{stale}")
        print("\nforget a wrong fact with:  swm forget <id> [<id> ...]")
    # surface premise-check findings if present
    if p.findings.exists():
        try:
            data = json.loads(p.findings.read_text())
            flagged = [x for x in data.get("findings", []) if x.get("status") != "ok"]
            if flagged:
                print(f"\n--- {len(flagged)} premise finding(s) ---")
                for x in flagged:
                    print(f"  ⚠ {x.get('premise','?')} :: {x.get('note','')}")
        except Exception:
            pass
    return 0


def cmd_add(arg: str) -> int:
    p = _paths()
    kind, _, text = arg.partition(":")
    kind, text = kind.strip().lower(), text.strip()
    if kind not in store.KINDS or not text:
        print(f"usage: add \"<kind>: text\"  (kind in {store.KINDS})", file=sys.stderr)
        return 2
    res = store.commit_facts(p.committed, [{"kind": kind, "text": text, "source": "manual"}], _turn(p))
    store.render(p.committed, p.state)
    print(f"added {res['added']} fact(s) -> {p.state}")
    return 0


def cmd_forget(ids: list[str]) -> int:
    p = _paths()
    n = store.forget(p.committed, p.archive, set(ids))
    store.render(p.committed, p.state)
    print(f"forgot {n} fact(s) (moved to archive; will not resurface)")
    return 0


def cmd_consolidate() -> int:
    p = _paths()
    try:
        import swm_consolidate
        res = swm_consolidate.consolidate(p.committed, p.state, p.archive, _turn(p))
        store.render(p.committed, p.state)
        print(f"consolidation: {res}")
    except Exception as e:  # noqa: BLE001
        print(f"consolidation failed (store untouched): {e}", file=sys.stderr)
        return 1
    return 0


def _read_queue(p):
    if not p.reroute_queue.exists():
        return []
    out = []
    for line in p.reroute_queue.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def cmd_reroute(args: list[str]) -> int:
    import swm_paths
    p = _paths()
    queue = _read_queue(p)
    if not queue:
        print("(reroute queue empty)")
        return 0
    facts = {f["id"]: f for f in store.load(p.committed)}
    if "--apply" in args or "--clear" in args:
        apply = "--apply" in args
        moved = 0
        hints = p.base / "routing-hints.jsonl"
        for e in queue:
            dest_id = e.get("suggested_project")
            ids = [i for i in e.get("fact_ids", []) if i in facts]
            if apply and dest_id and ids:
                dest = swm_paths.for_project(dest_id)
                store.commit_facts(dest.committed, [facts[i] for i in ids], e.get("turn", 0))
                store.render(dest.committed, dest.state)
                store.forget(p.committed, p.archive, set(ids))
                # feedback: teach the router this filing
                try:
                    with hints.open("a") as fh:
                        for i in ids:
                            fh.write(json.dumps({"text": facts[i]["text"], "project": dest_id}) + "\n")
                except Exception:
                    pass
                moved += len(ids)
        store.render(p.committed, p.state)
        p.reroute_queue.unlink(missing_ok=True)
        print(f"reroute {'applied' if apply else 'cleared'}: moved {moved} fact(s); queue cleared")
        return 0
    # list
    print(f"{len(queue)} reroute suggestion(s) — review, then `swm reroute --apply` or `--clear`:\n")
    for e in queue:
        print(f"  → {e.get('suggested_project')} (conf {e.get('confidence')}) — {e.get('reason','')}")
        for i in e.get("fact_ids", []):
            if i in facts:
                print(f"      [{i}] {facts[i]['text']}")
    return 0


def cmd_path() -> int:
    p = _paths()
    for k, v in vars(p).items():
        print(f"{k:14} {v}")
    return 0


def _prio_path(p):
    return p.committed.parent / "priorities.jsonl"


def cmd_priority(args: list[str]) -> int:
    import swm_priority as prio
    p = _paths()
    pp = _prio_path(p)
    sub = args[0] if args else "list"
    rest = args[1:]
    turn = _turn(p)
    if sub in ("list", "ls", ""):
        items = prio.active(prio.load(pp))
        if not items:
            print("(no active strategic priorities — `swm priority add \"...\"` or `swm priority sync`)")
            return 0
        for i, it in enumerate(items, 1):
            src = f"  ·{it.source}" if it.source != "manual" else ""
            card = f"  [↑{it.source_card}]" if it.source_card else "  [unanchored]"
            print(f"{i}. [{it.id}] {it.statement}{src}{card}")
            if it.rationale:
                print(f"     ↳ {it.rationale}")
        return 0
    if sub == "add":
        if not rest:
            print('usage: priority add "<statement>" [--rank N] [--why "..."] [--source X]', file=sys.stderr)
            return 2
        stmt = rest[0]
        rank, why, source, source_card = 100, "", "manual", ""
        for i, a in enumerate(rest):
            if a == "--rank" and i + 1 < len(rest):
                try:
                    rank = int(rest[i + 1])
                except ValueError:
                    pass
            elif a == "--why" and i + 1 < len(rest):
                why = rest[i + 1]
            elif a == "--source" and i + 1 < len(rest):
                source = rest[i + 1]
            elif a == "--source-card" and i + 1 < len(rest):
                source_card = rest[i + 1]
        act = prio.active(prio.load(pp))
        if len(act) >= prio.MAX_ACTIVE:
            print(f"⚠ {len(act)} active priorities already (budget {prio.MAX_ACTIVE}). "
                  "If everything is a priority, nothing is — retire one first (`priority done|drop <id>`).",
                  file=sys.stderr)
        seed_turn = max(turn, store.max_turn(p.committed) + 1)  # new spine excludes pre-spine backlog
        r = prio.upsert(pp, prio.StrategicPriority(
            statement=stmt, rank=rank, rationale=why, source=source, source_card=source_card), seed_turn)
        store.render(p.committed, p.state)
        print(f"priority {r}")
        return 0
    if sub in ("done", "achieved", "drop", "pause"):
        if not rest:
            print(f"usage: priority {sub} <id>", file=sys.stderr)
            return 2
        status = {"done": "achieved", "achieved": "achieved", "drop": "dropped", "pause": "paused"}[sub]
        ok = prio.set_status(pp, rest[0], status, turn)
        store.render(p.committed, p.state)
        print(f"priority {rest[0]} → {status}" if ok else f"no priority matching {rest[0]}")
        return 0 if ok else 1
    if sub == "propose":
        import priority_link
        decisions = [f["text"] for f in store.load(p.committed)
                     if f.get("kind") == "decision" and f.get("text")]
        cands = priority_link.propose(decisions)
        if not cands:
            print("could not propose (no decisions, or LLM call failed)")
            return 1
        print("Candidate priorities (drafted from decision history — RATIFY before adding):\n")
        for c in sorted(cands, key=lambda x: x.get("rank", 99)):
            print(f"  [{c.get('rank','?')}] {c.get('statement','').strip()}")
            if c.get("rationale"):
                print(f"      ↳ {c['rationale'].strip()}")
        print('\nAdd the ones you approve:  swm priority add "<statement>" --rank N --why "..."')
        return 0
    if sub == "backfill":
        act = prio.active(prio.load(pp))
        if not act:
            print("no active priorities to backfill against", file=sys.stderr)
            return 1
        since = min(pr.created_turn for pr in act)
        allf = store.load(p.committed)
        targets = [f for f in allf if f.get("kind") in ("decision", "constraint")
                   and not (f.get("traces_to") or []) and int(f.get("turn_added") or 0) >= since]
        if not targets:
            print("nothing to backfill — no untraced post-spine facts")
            return 0
        import priority_link
        priority_link.tag_facts(targets, act)  # mutates dicts in-place (refs into allf)
        store.save(p.committed, allf)
        store.render(p.committed, p.state)
        linked = sum(1 for f in targets if f.get("traces_to"))
        print(f"backfill: {linked}/{len(targets)} facts linked to a priority "
              f"({len(targets) - linked} genuinely off-spine → remain in drift)")
        return 0
    if sub == "sync":
        import os
        import swm_paths
        proj = rest[0] if rest else swm_paths.project_key(os.getcwd())
        if not proj:
            print("usage: priority sync <ra-pm-project-id>", file=sys.stderr)
            return 2
        res = prio.sync_from_rapm(pp, proj, max(turn, store.max_turn(p.committed) + 1))
        store.render(p.committed, p.state)
        print(f"sync from ra-pm '{proj}': {res}")
        return 0
    print(f"unknown priority subcommand: {sub}", file=sys.stderr)
    return 2


def cmd_trace(args: list[str]) -> int:
    if len(args) < 2:
        print("usage: trace <fact-id> <priority-id>", file=sys.stderr)
        return 2
    p = _paths()
    ok = store.link_trace(p.committed, args[0], args[1])
    store.render(p.committed, p.state)
    print(f"linked {args[0]} → priority {args[1]}" if ok else f"no fact matching {args[0]}")
    return 0 if ok else 1


def cmd_drift() -> int:
    import swm_priority as prio
    p = _paths()
    act = prio.active(prio.load(_prio_path(p)))
    if not act:
        print("(no active priorities — drift undefined. Set the spine first: `swm priority add`/`sync`)")
        return 0
    since = min(pr.created_turn for pr in act)
    un = store.untraced(p.committed, since_turn=since)
    backlog = len(store.untraced(p.committed)) - len(un)
    print(f"Active priorities: {len(act)} | untraced since spine (turn ≥{since}): {len(un)} "
          f"| pre-spine backlog (not held accountable): {backlog}\n")
    if un:
        print("⚠ DRIFT — these ladder up to no priority:")
        for f in un:
            print(f"  [{f['id']}] ({f['kind']}) {f['text']}")
        print("\nConnect with `swm trace <fact-id> <priority-id>`, or open a new priority.")
    else:
        print("✓ all decisions/constraints trace to a priority.")
    return 0


def _goal_path(p):
    return p.committed.parent / "session_goal.json"


def _sid() -> str:
    import os
    return os.environ.get("CLAUDE_SESSION_ID", "")


def cmd_link_issue(args: list[str]) -> int:
    """Link an ra-pm issue (L5) UP to a SWM StrategicPriority (L3).
    Usage: swm link-issue <project-id> <issue-id> <priority-id>
    Writes traces_to_priority into the issue's frontmatter."""
    if len(args) < 3:
        print("usage: link-issue <project-id> <issue-id> <priority-id>", file=sys.stderr)
        print("  project-id: e.g. my-app, backend-api", file=sys.stderr)
        print("  issue-id:   numeric id from `ra_issues`", file=sys.stderr)
        print("  priority-id: from `swm priority list`", file=sys.stderr)
        return 2
    project, issue_id_str, priority_id = args[0], args[1], args[2]
    try:
        issue_id = int(issue_id_str)
    except ValueError:
        print(f"issue-id must be numeric, got: {issue_id_str}", file=sys.stderr)
        return 2
    try:
        import sys as _sys, pathlib as _pl
        _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
        from shared.store import load_issues as _li, save_issue as _si
        # link_issue_to_priority: find issue, set traces_to_priority, save
        _issues = _li(project)
        _issue = next((i for i in _issues if i.id == issue_id), None)
        if _issue:
            _issue.traces_to_priority = priority_id
            _si(project, _issue)
        ok = _issue is not None
        if ok:
            print(f"linked issue #{issue_id} ({project}) → priority {priority_id}")
        else:
            print(f"issue #{issue_id} not found in project '{project}'", file=sys.stderr)
        return 0 if ok else 1
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def cmd_goal(args: list[str]) -> int:
    import session_goal as sg
    p = _paths()
    gp = _goal_path(p)
    sid = _sid()
    sub = args[0] if args else "status"
    rest = args[1:]
    if sub == "status":
        g = sg.load(gp, sid)
        if g is None:
            print("(no active session goal — `swm goal set \"...\"`)")
            return 0
        print(sg.render_block(g))
        return 0
    if sub == "set":
        if not rest:
            print('usage: goal set "<statement>" [--budget N] [--priority <pid>]', file=sys.stderr)
            return 2
        stmt = rest[0]
        budget, pri = 5, ""
        for i, a in enumerate(rest):
            if a == "--budget" and i + 1 < len(rest):
                try:
                    budget = int(rest[i + 1])
                except ValueError:
                    pass
            elif a == "--priority" and i + 1 < len(rest):
                pri = rest[i + 1]
        g = sg.set_goal(gp, stmt, sid, budget=budget, traces_to=pri)
        print(f"Session goal set: \"{g.statement}\" (budget: {g.budget_turns} exploration turns)")
        if not g.traces_to:
            print("  tip: link to a project priority with --priority <pid> (from `swm priority list`)")
        return 0
    if sub == "extend":
        n = int(rest[0]) if rest else 5
        g = sg.extend(gp, sid, n)
        print(f"Budget extended to {g.budget_turns} exploration turns" if g else "no active goal")
        return 0 if g else 1
    if sub in ("done", "achieved"):
        ok = sg.set_status(gp, sid, "achieved")
        print("Goal marked achieved." if ok else "no active goal")
        return 0 if ok else 1
    if sub in ("clear", "abandon"):
        ok = sg.set_status(gp, sid, "abandoned")
        print("Goal abandoned." if ok else "no active goal")
        return 0 if ok else 1
    print(f"unknown goal subcommand: {sub}", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    if not argv:
        return cmd_show()
    cmd, rest = argv[0], argv[1:]
    if cmd == "show":
        return cmd_show()
    if cmd == "add":
        return cmd_add(rest[0]) if rest else (print('usage: add "<kind>: text"', file=sys.stderr) or 2)
    if cmd in ("forget", "dismiss"):
        return cmd_forget(rest) if rest else (print("usage: forget <id> ...", file=sys.stderr) or 2)
    if cmd == "reroute":
        return cmd_reroute(rest)
    if cmd == "consolidate":
        return cmd_consolidate()
    if cmd == "path":
        return cmd_path()
    if cmd == "priority":
        return cmd_priority(rest)
    if cmd == "trace":
        return cmd_trace(rest)
    if cmd == "drift":
        return cmd_drift()
    if cmd == "goal":
        return cmd_goal(rest)
    if cmd == "link-issue":
        return cmd_link_issue(rest)
    print(f"unknown command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
