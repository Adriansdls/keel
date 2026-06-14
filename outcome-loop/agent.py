"""Outcome Loop agent — retrospective bet/decision/experiment reviewer.

For each project with open items, builds a context block from recent activity
and asks Sonnet: what has resolved, what is contradicted, what is stale?

Applies verdicts back to the store:
  - resolved bet        → confidence updated, status → validated
  - contradicted bet    → status → invalidated
  - resolved experiment → status → completed
  - contradicted decision / stale bet → written to warnings.jsonl (never auto-mutated)

Decisions are never auto-mutated — the loop flags, humans act.
Fail-open on every step: a verdict error never blocks the next one.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import store
from shared.llm import LLMExtractionError, Model, extract
from shared.models import (
    BetStatus, ExperimentStatus, OutcomeReport, OutcomeVerdict,
)

_MAX_CONTEXT_CHARS = 6000

_SYSTEM_PROMPT = (
    "You are a retrospective reviewer. Given RECENT ACTIVITY and a list of "
    "OPEN BETS, OLD DECISIONS, and OPEN EXPERIMENTS for a project, judge each item:\n\n"
    "  resolved     — clear evidence the bet paid off / experiment concluded / decision validated\n"
    "  still_open   — not enough evidence to judge yet\n"
    "  contradicted — recent actions directly contradict a decision or invalidate a bet\n"
    "  stale        — no new relevant evidence in > 60 days\n\n"
    "Rules:\n"
    "  - Be conservative: prefer 'still_open' over premature resolution.\n"
    "  - confidence_delta: only set for bets; range -0.5 to +0.5; 0.0 if not resolved/contradicted.\n"
    "  - target_id: the exact id string shown in brackets (e.g. '3').\n"
    "  - Include all items; emit 'still_open' for anything you cannot judge.\n"
    "  - stale_bet_ids / contradicted_decision_ids: populate from verdicts for convenience.\n"
    "  - narrative: 2-3 sentence plain-language summary of the key findings."
)


# ── Warnings file ─────────────────────────────────────────────────────────────

def _warnings_path() -> Path:
    p = store.root() / "outcome-loop" / "warnings.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _write_warning(kind: str, project_id: str, item_id: str, reasoning: str) -> None:
    rec = {"type": kind, "project": project_id, "id": item_id,
           "reasoning": reasoning[:300], "flagged_at": datetime.now().isoformat()}
    with _warnings_path().open("a") as f:
        f.write(json.dumps(rec) + "\n")


# ── Context builder ───────────────────────────────────────────────────────────

def _build_context(project_id: str, cfg) -> str:
    sections: list[str] = []
    today = date.today()

    # Recent activity
    activity: list[str] = []
    handoff = store.latest_handoff_text(project_id)
    if handoff:
        activity.append("Latest handoff:\n" + handoff[:1500])
    findings = store.load_findings(project_id)
    recent_f = [f for f in findings
                if f.logged and (today - f.logged).days <= cfg.outcomes.decision_check_after_days]
    for f in recent_f[:3]:
        activity.append(f"Finding: {f.result[:300]} → {f.implication[:200]}")
    done_issues = [i for i in store.load_issues(project_id)
                   if i.status in ("done", "blocked")
                   and i.updated and (today - i.updated).days <= cfg.outcomes.decision_check_after_days]
    if done_issues:
        activity.append("Recent issue updates: " +
                        ", ".join(f"{i.title} ({i.status})" for i in done_issues[:5]))
    if activity:
        sections.append("RECENT ACTIVITY:\n" + "\n".join(activity))

    # Open bets
    bets = [b for b in store.load_bets(project_id) if b.status == BetStatus.active]
    if bets:
        lines = [f"  [{b.id}] {b.statement} | confidence: {b.confidence} | "
                 f"logged: {b.created}\n      evidence needed: {b.evidence_needed}"
                 for b in bets]
        sections.append(f"OPEN BETS ({len(bets)}):\n" + "\n".join(lines))

    # Old decisions
    old_dec_threshold = cfg.outcomes.decision_check_after_days
    old_decisions = [d for d in store.load_decisions(project_id)
                     if d.logged and (today - d.logged).days >= old_dec_threshold]
    if old_decisions:
        lines = [f"  [{d.id}] {d.decision} | logged: {d.logged}" for d in old_decisions[:10]]
        sections.append(f"DECISIONS >{old_dec_threshold}d OLD ({len(old_decisions)}):\n"
                        + "\n".join(lines))

    # Open experiments
    exps = [e for e in store.load_experiments(project_id)
            if e.status == ExperimentStatus.running]
    if exps:
        lines = []
        for e in exps:
            ef = [f for f in findings if f.experiment_id == e.id]
            lines.append(f"  [{e.id}] {e.hypothesis} | findings: {len(ef)}")
        sections.append(f"OPEN EXPERIMENTS ({len(exps)}):\n" + "\n".join(lines))

    ctx = "\n\n".join(sections)
    # Hard cap — truncate from the top (activity), never from items
    if len(ctx) > _MAX_CONTEXT_CHARS:
        ctx = "...[activity truncated]\n\n" + "\n\n".join(sections[1:])
        ctx = ctx[:_MAX_CONTEXT_CHARS]
    return ctx


# ── Verdict application ───────────────────────────────────────────────────────

def _apply_verdicts(project_id: str, report: OutcomeReport) -> list[str]:
    applied: list[str] = []
    for v in report.verdicts:
        store.save_verdict(v)
        try:
            if v.target_type == "bet":
                bets = store.load_bets(project_id)
                bet  = next((b for b in bets if str(b.id) == str(v.target_id)), None)
                if not bet:
                    continue
                if v.verdict == "resolved":
                    bet.confidence = round(max(0.0, min(1.0,
                                          bet.confidence + v.confidence_delta)), 3)
                    bet.status = BetStatus.validated
                    bet.updates.append({
                        "by": "outcome-loop", "delta": v.confidence_delta,
                        "reasoning": v.reasoning[:200],
                        "at": v.checked_at.isoformat(),
                    })
                    store.save_bet(project_id, bet)
                    applied.append(f"bet #{v.target_id} resolved (Δ{v.confidence_delta:+.2f})")
                elif v.verdict == "contradicted":
                    bet.status = BetStatus.invalidated
                    store.save_bet(project_id, bet)
                    _write_warning("contradicted_bet", project_id, str(v.target_id), v.reasoning)
                    applied.append(f"bet #{v.target_id} invalidated")
                elif v.verdict == "stale":
                    _write_warning("stale_bet", project_id, str(v.target_id), v.reasoning)
                    applied.append(f"bet #{v.target_id} flagged stale")

            elif v.target_type == "decision":
                if v.verdict == "contradicted":
                    _write_warning("contradicted_decision", project_id,
                                   str(v.target_id), v.reasoning)
                    applied.append(f"decision #{v.target_id} flagged contradicted")

            elif v.target_type == "experiment":
                if v.verdict == "resolved":
                    exps = store.load_experiments(project_id)
                    exp  = next((e for e in exps if str(e.id) == str(v.target_id)), None)
                    if exp:
                        exp.status = ExperimentStatus.completed
                        exp.completed = date.today()
                        store.save_experiment(project_id, exp)
                        applied.append(f"experiment #{v.target_id} closed")

        except Exception as e:
            applied.append(f"[error applying {v.target_type} #{v.target_id}: {e}]")

    return applied


# ── Public API ────────────────────────────────────────────────────────────────

def run_project(project_id: str) -> OutcomeReport | None:
    """Run the outcome loop for one project. Returns None if nothing to review."""
    cfg = store.load_config()
    ctx = _build_context(project_id, cfg)
    if not ctx.strip():
        return None

    # Nothing actionable — skip Sonnet call
    has_bets  = bool([b for b in store.load_bets(project_id)
                      if b.status == BetStatus.active])
    has_exps  = bool([e for e in store.load_experiments(project_id)
                      if e.status == ExperimentStatus.running])
    today     = date.today()
    has_olddec = any(
        d.logged and (today - d.logged).days >= cfg.outcomes.decision_check_after_days
        for d in store.load_decisions(project_id)
    )
    if not (has_bets or has_exps or has_olddec):
        return None

    try:
        report = extract(
            system_prompt=_SYSTEM_PROMPT,
            schema=OutcomeReport,
            context=ctx,
            model=Model.smart,
        )
    except LLMExtractionError:
        return None

    _apply_verdicts(project_id, report)
    return report


def run_all() -> dict[str, OutcomeReport]:
    """Run outcome loop across all active projects. Returns {project_id: report}."""
    results: dict[str, OutcomeReport] = {}
    for p in store.load_projects():
        if p.status != "active":
            continue
        try:
            report = run_project(p.id)
            if report:
                results[p.id] = report
        except Exception:
            pass  # fail-open per project
    return results
