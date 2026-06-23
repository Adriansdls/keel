"""Entropy Manager — actor on top of the ra-pm store.

Manages project entropy as a value-creation engine:
  capture  — lose nothing (guaranteed persist)
  promote  — idea → tracked issue with lineage
  decide   — the one gate (halts on contradiction / missing alternatives)
  brief    — render the field + leverage metrics

Identity/purpose text is generic so this works for any team, not just one person.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shared import store
from shared.llm import LLMExtractionError, Model, extract
from shared.models import (
    Bet, ContradictionCheck, Decision, EntropyReport,
    IdeaPromotionScore, InboxIdea, Issue, IssueStatus,
    PromotionBatch,
)
from entropy.ra_graph import build_ra_graph
from entropy.vault_anchor import unanchored

DORMANT_DAYS = 7
WINDOW_DAYS  = 90


# ── Contradiction check (LLM — no heuristics) ─────────────────────────────────

def _contradicts_llm(new_decision: str, prior_decisions: list) -> tuple[bool, dict | None, str]:
    """Return (contradicts, clashing_prior_or_None, reasoning). Fail-open."""
    if not prior_decisions:
        return False, None, ""
    try:
        prior_text = "\n".join(
            f"[#{p.id}] {p.decision}" for p in prior_decisions[-20:]
        )
        result = extract(
            system_prompt=(
                "Determine whether the NEW DECISION directly contradicts any PRIOR DECISIONS. "
                "A contradiction means both cannot simultaneously be honored. "
                "Be conservative: flag only clear logical conflicts, not stylistic differences. "
                "If contradicts=true, set prior_decision to the exact text of the conflicting prior."
            ),
            schema=ContradictionCheck,
            context=f"NEW DECISION:\n{new_decision}\n\nPRIOR DECISIONS:\n{prior_text}",
            model=Model.fast,
        )
        if result.contradicts:
            clash = next(
                (p for p in prior_decisions
                 if result.prior_decision and
                 result.prior_decision[:40].lower() in p.decision.lower()),
                prior_decisions[-1],
            )
            return True, clash, result.reasoning
        return False, None, result.reasoning
    except (LLMExtractionError, Exception) as e:
        return False, None, f"contradiction check unavailable ({e}) — proceeding"


# ── Field report (metrics engine) ─────────────────────────────────────────────

def field_report() -> dict:
    today    = date.today()
    ideas    = store.load_ideas()
    projects = [p for p in store.load_projects() if p.status == "active"]

    def age(d) -> int | None:
        if not d:
            return None
        try:
            dt = datetime.fromisoformat(str(d)).date() if not isinstance(d, date) else d
            return (today - dt).days
        except Exception:
            return None

    # lineage: idea indices that have a descendant issue
    converted_idx: set[int] = set()
    for p in projects:
        for iss in store.load_issues(p.id):
            if iss.from_idea is not None:
                converted_idx.add(iss.from_idea)

    # flow metrics over window
    in_window = [
        (i, idea) for i, idea in enumerate(ideas)
        if (a := age(idea.created)) is not None and a <= WINDOW_DAYS
    ]
    total = len(in_window) or 1

    leaked = [
        i for i, idea in in_window
        if (idea.project or "inbox") == "inbox"
        and i not in converted_idx
        and (age(idea.created) or 0) > DORMANT_DAYS
    ]
    converted = [
        i for i, idea in in_window
        if i in converted_idx or (idea.project or "inbox") != "inbox"
    ]

    leakage_rate    = round(len(leaked) / total, 3)
    conversion_rate = round(len(converted) / total, 3)

    # dormant items (surface for harvest-or-kill — never auto-prune)
    dormant_ideas = [
        i for i, idea in enumerate(ideas)
        if (idea.project or "inbox") == "inbox"
        and (age(idea.created) or 0) > DORMANT_DAYS
        and i not in converted_idx
    ]
    dormant_projects = [
        p.id for p in projects
        if (age(p.last_touched) or 0) > DORMANT_DAYS
    ]

    # legibility: project with no handoff AND no issue = black hole
    illegible = [
        p.id for p in projects
        if not store.latest_handoff_text(p.id) and not store.load_issues(p.id)
    ]

    # anchor integrity (optional — requires vault_path in config)
    unanchored_ids = unanchored()

    # graph connectivity
    _, g, _ = build_ra_graph()
    connectivity = g.connectivity()

    return {
        "leaked": leaked, "leakage_rate": leakage_rate,
        "converted": converted, "conversion_rate": conversion_rate,
        "window_days": WINDOW_DAYS,
        "dormant_ideas": dormant_ideas, "dormant_projects": dormant_projects,
        "illegible": illegible, "unanchored": unanchored_ids,
        "connectivity": connectivity,
        "n_ideas": len(ideas), "n_projects": len(projects),
    }


def make_report(f: dict) -> EntropyReport:
    narrative = (
        f"Field: {f['n_projects']} projects, {f['n_ideas']} ideas, "
        f"connectivity {f['connectivity']}. "
        f"Leakage {f['leakage_rate']} | conversion {f['conversion_rate']} "
        f"(window {f['window_days']}d). "
        f"Dormant: {len(f['dormant_ideas'])} ideas, {len(f['dormant_projects'])} projects. "
        f"Illegible: {len(f['illegible'])}. Unanchored: {len(f['unanchored'])}."
    )
    return EntropyReport(
        leakage_rate=f["leakage_rate"],
        conversion_rate=f["conversion_rate"],
        n_ideas=f["n_ideas"],
        n_projects=f["n_projects"],
        dormant_idea_count=len(f["dormant_ideas"]),
        dormant_project_ids=f["dormant_projects"],
        illegible_ids=f["illegible"],
        unanchored_ids=f["unanchored"],
        connectivity=f["connectivity"],
        narrative=narrative,
    )


# ── Promotion scoring (LLM — Haiku) ────────────────────────────────────────────

_PROMPT_SCORE = (
    "You are a project-triage assistant. Score each inbox idea for promotion readiness.\n\n"
    "For each idea, judge:\n"
    "  - confidence (0.0–1.0): how ready is this idea to become a tracked issue?\n"
    "    Consider: specificity of title+why, actionability, strategic fit.\n"
    "  - suggested_project: which existing project should own this? Use project id "
    "from the project list. Empty string if unclear.\n"
    "  - suggested_priority: p0 / p1 / p2 / p3\n"
    "  - action: promote (confidence >= threshold), recommend (>= 0.4), or skip\n"
    "  - reasoning: one sentence explaining the score\n\n"
    "Return a JSON object matching the PromotionBatch schema."
)


def _score_ideas(
    ideas: list[InboxIdea],
    projects: list,
    field: dict,
    max_candidates: int = 10,
    threshold: float = 0.7,
) -> PromotionBatch:
    """Score inbox ideas via Haiku. Returns PromotionBatch with scored ideas."""
    candidates = []
    converted_idx = field.get("converted", set()) or set()
    for i, idea in enumerate(ideas):
        if (idea.project or "inbox") != "inbox":
            continue
        if i in converted_idx:
            continue
        candidates.append((i, idea))
        if len(candidates) >= max_candidates:
            break
    if not candidates:
        return PromotionBatch()

    project_summary = "\n".join(
        f"  {p.id}: {p.name} ({p.area or 'no area'})" for p in projects
    )
    idea_lines = "\n".join(
        f"  [{i}] {idea.title} — why: {idea.why}  (area: {idea.area or 'none'})"
        for i, idea in candidates
    )
    context = (
        f"Projects:\n{project_summary}\n\n"
        f"Inbox ideas to score:\n{idea_lines}\n\n"
        f"Threshold for auto-promote: {threshold}"
    )
    try:
        result = extract(
            system_prompt=_PROMPT_SCORE,
            schema=PromotionBatch,
            context=context,
            model=Model.fast,
        )
    except LLMExtractionError:
        return PromotionBatch()

    for score in result.scored:
        score.confidence = round(score.confidence, 2)
        if score.confidence >= threshold:
            score.action = "promote"
        elif score.confidence >= 0.4:
            score.action = "recommend"
        else:
            score.action = "skip"
    return result


def _auto_promote(
    batch: PromotionBatch,
    ideas: list[InboxIdea],
    max_promotions: int = 3,
) -> list[str]:
    """Auto-promote ideas with action='promote'. Returns list of promoted titles."""
    promoted_titles: list[str] = []
    count = 0
    for score in batch.scored:
        if score.action != "promote":
            continue
        if count >= max_promotions:
            break
        if score.idea_idx >= len(ideas):
            continue
        idea = ideas[score.idea_idx]
        target_project = score.suggested_project or idea.project or "inbox"
        new_id = store.next_issue_id(target_project)
        issue = Issue(
            id=new_id,
            title=idea.title,
            area=idea.area or "engineering",
            why=idea.why,
            from_idea=str(score.idea_idx),
            status=IssueStatus.planned,
            priority=score.suggested_priority or "p2",
            source="entropy-auto-promote",
        )
        try:
            store.save_issue(target_project, issue)
            idea.project = target_project
            ideas[score.idea_idx] = idea
            promoted_titles.append(idea.title)
            count += 1
        except Exception:
            continue
    if promoted_titles:
        store.save_ideas(ideas)
    return promoted_titles


def _enrich_narrative(report: EntropyReport, batch: PromotionBatch) -> str:
    """Append promotion results to the report narrative."""
    parts = [report.narrative]
    if batch.promoted:
        titles = ", ".join(batch.promoted)
        parts.append(f"Auto-promoted: {titles}.")
    recommends = [s for s in batch.scored if s.action == "recommend"]
    if recommends:
        lines = [f"  [{s.idea_idx}] {s.title} (conf {s.confidence}) → {s.suggested_project or '?'}" for s in recommends[:5]]
        parts.append("Recommendations:\n" + "\n".join(lines))
    return "\n".join(parts)


def _log_action(action: str, details: dict) -> None:
    """Append one action to the entropy actions audit trail."""
    d = store.root() / "entropy"
    d.mkdir(parents=True, exist_ok=True)
    path = d / "actions.jsonl"
    entry = {"action": action, "timestamp": datetime.now().isoformat(), **details}
    path.open("a", encoding="utf-8").write(json.dumps(entry, default=str) + "\n")


# ── Actions ────────────────────────────────────────────────────────────────────

def handle(task: dict) -> dict:
    action = task.get("action", "brief")

    # ── capture ───────────────────────────────────────────────────────────────
    if action == "capture":
        idea_data = task.get("idea") or {}
        title = (idea_data.get("title") or "").strip()
        why   = (idea_data.get("why") or "").strip()
        if not title or not why:
            return {"answer": "rejected: needs title + why", "commit_ok": False,
                    "block_reason": "capture missing title/why"}
        idea = InboxIdea(
            title=title, why=why,
            area=idea_data.get("area", "engineering"),
            source="entropy-manager",
        )
        store.append_idea(idea)
        return {"answer": f"captured: {title!r}", "commit_ok": True}

    # ── promote ───────────────────────────────────────────────────────────────
    if action == "promote":
        idea_idx   = task.get("idea_idx")
        to_project = task.get("to_project") or task.get("project")
        ideas      = store.load_ideas()
        if not isinstance(idea_idx, int) or idea_idx >= len(ideas) or not to_project:
            return {"answer": "promote needs idea_idx (int) + to_project",
                    "commit_ok": False, "block_reason": "bad promote args"}
        idea  = ideas[idea_idx]
        new_id = store.next_issue_id(to_project)
        issue = Issue(
            id=new_id, title=idea.title,
            area=idea.area or "engineering",
            why=idea.why,
            from_idea=str(idea_idx),
            status=IssueStatus.planned,
            source="entropy-manager",
        )
        store.save_issue(to_project, issue)
        # Route the idea (mark it as no longer inbox)
        idea.project = to_project
        ideas_updated = list(store.load_ideas())
        ideas_updated[idea_idx] = idea
        store.save_ideas(ideas_updated)
        return {"answer": f"promoted idea {idea_idx} → {to_project!r} (lineage stamped)",
                "commit_ok": True}

    # ── decide ────────────────────────────────────────────────────────────────
    if action == "decide":
        dec_data   = task.get("decision") or {}
        project    = dec_data.get("project") or task.get("project") or "inbox"
        text       = (dec_data.get("decision") or "").strip()
        rationale  = (dec_data.get("rationale") or "").strip()
        alts       = dec_data.get("alternatives_rejected") or []

        if not alts:
            return {"answer": "HALT: a decision must carry the field (alternatives_rejected required)",
                    "commit_ok": False, "block_reason": "missing alternatives_rejected"}

        priors = store.load_decisions(project)
        contradicts, clash, reasoning = _contradicts_llm(text, priors)
        if contradicts and clash:
            return {"answer": f"HALT: contradicts decision #{clash.id}: {clash.decision[:60]}",
                    "reasoning": reasoning, "commit_ok": False,
                    "block_reason": f"contradicts prior decision {clash.id}"}

        new_id = store.next_decision_id(project)
        decision = Decision(
            id=new_id, decision=text, rationale=rationale,
            alternatives_rejected=alts, source="entropy-manager",
        )
        store.save_decision(project, decision)
        return {"answer": f"decided: {text[:60]!r}", "commit_ok": True}

    # ── brief (default) ───────────────────────────────────────────────────────
    f      = field_report()
    report = make_report(f)
    return {"answer": report.narrative, "report": report, "field": f, "commit_ok": True}


# ── Post-brief promotion phase ────────────────────────────────────────────────

def run_promotion_phase(cfg=None) -> PromotionBatch:
    """Score inbox ideas and auto-promote high-confidence ones.

    Called by cadence.run_now() after the brief is generated.
    Uses HealthConfig.auto_promote_ideas as the kill switch.
    """
    if cfg is None:
        cfg = store.load_config()
    if not cfg.health.auto_promote_ideas:
        return PromotionBatch()

    ideas = store.load_ideas()
    projects = [p for p in store.load_projects() if p.status == "active"]
    f = field_report()

    batch = _score_ideas(
        ideas=ideas,
        projects=projects,
        field=f,
        max_candidates=cfg.health.promotion_candidates_per_run,
        threshold=cfg.health.promotion_confidence_threshold,
    )

    promoted = _auto_promote(
        batch=batch,
        ideas=ideas,
        max_promotions=cfg.health.max_auto_promotions_per_run,
    )
    batch.promoted = promoted

    _log_action("promotion_phase", {
        "scored": len(batch.scored),
        "promoted": len(promoted),
        "titles": promoted,
    })

    return batch
