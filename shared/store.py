"""
shared/store.py — Unified, typed, atomic file store for the cowork stack.

Single module. All packages read/write through here.
Returns Pydantic models — never raw dicts.
All writes are atomic: tmp file → rename (POSIX-safe).

Store root: $KEEL_HOME (default ~/.keel)

Layout:
  ~/.keel/
    config.yaml
    ra/
      projects.yaml
      focus.yaml
      ideas.yaml
      issues/{project_id}/          ← YAML files, one per issue
      bets/{project_id}/
      decisions/{project_id}/
      experiments/{project_id}/
      findings/{project_id}/
      handoffs/{project_id}/        ← markdown files
      thesis/{project_id}/thesis.yaml
      northstar/{project_id}/northstar.yaml
      theory/{project_id}/theory.yaml
    swm/
      {project_id}/
        committed.jsonl
        strategic-state.md
        premise-findings.jsonl
        .turn-counter
    entropy/
      findings.jsonl
      last-run.json
    outcome-loop/
      verdicts.jsonl
    auto-capture.log
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import yaml

from pydantic import BaseModel

from shared.models import (
    Bet, KeelConfig, Decision, Experiment, Fact,
    Finding, Focus, InboxIdea, Issue, NorthStar, OutcomeVerdict,
    PremiseFinding, Project, Thesis, TheoryOfChange,
)

# ── Root ─────────────────────────────────────────────────────────────────────

def _keel_home() -> Path:
    return Path(os.environ.get("KEEL_HOME", "~/.keel")).expanduser()


def root() -> Path:
    return _keel_home()


def ra_root() -> Path:
    return _keel_home() / "ra"


def swm_root() -> Path:
    return _keel_home() / "swm"


# ── Atomic write ─────────────────────────────────────────────────────────────

def _atomic_write(path: Path, content: str) -> None:
    """Write content to path atomically via tmp-file + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)   # atomic on POSIX/macOS
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_yaml(path: Path, data: object) -> None:
    _atomic_write(path, yaml.safe_dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))


def _atomic_jsonl_append(path: Path, record: dict) -> None:
    """Append one JSON line atomically (read → append → rewrite)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    _atomic_write(path, existing + json.dumps(record, ensure_ascii=False, default=str) + "\n")


# ── Config ───────────────────────────────────────────────────────────────────

_config_cache: Optional[KeelConfig] = None


def load_config(force_reload: bool = False) -> KeelConfig:
    global _config_cache
    if _config_cache is not None and not force_reload:
        return _config_cache
    path = _keel_home() / "config.yaml"
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _config_cache = KeelConfig.model_validate(raw)
    else:
        _config_cache = KeelConfig()
    return _config_cache


def write_default_config() -> None:
    """Write config.yaml with defaults if it doesn't exist."""
    path = _keel_home() / "config.yaml"
    if path.exists():
        return
    template = """\
# keel configuration
# You probably don't need to change anything here.

# ── How cowork thinks ─────────────────────────────────────────────────────────
llm:
  # "subscription" uses your Claude subscription. No extra setup needed. (default)
  # "api"          uses an Anthropic API key. For advanced users.
  mode: subscription
  fast_model:  claude-haiku-4-5
  smart_model: claude-sonnet-4-5
  # api_key_env: ANTHROPIC_API_KEY   # uncomment if using mode: api

# ── What cowork remembers ─────────────────────────────────────────────────────
memory:
  check_assumptions_every: 5
  max_inject_size: 12000
  share_global_decisions: true

# ── Project health ────────────────────────────────────────────────────────────
health:
  check_every_days: 7
  warn_if_idea_leakage_above: 0.40

# ── Outcome tracking ──────────────────────────────────────────────────────────
outcomes:
  check_every_days: 7
  flag_stale_bets_after_days: 60
  decision_check_after_days: 30
"""
    _atomic_write(path, template)


# ── Projects ─────────────────────────────────────────────────────────────────

def load_projects() -> list[Project]:
    path = ra_root() / "projects.yaml"
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [Project.model_validate(p) for p in raw]


def save_projects(projects: list[Project]) -> None:
    data = [p.model_dump(mode="json") for p in projects]
    _atomic_yaml(ra_root() / "projects.yaml", data)


def save_project(p: Project) -> None:
    projects = load_projects()
    idx = next((i for i, x in enumerate(projects) if x.id == p.id), None)
    if idx is not None:
        projects[idx] = p
    else:
        projects.append(p)
    p.last_touched = date.today()
    save_projects(projects)


def match_project_by_cwd(cwd: str) -> Optional[str]:
    """
    Match a filesystem path against registered project workspace_paths.
    Returns project id or None.
    No LLM — pure path comparison (exact → prefix).
    """
    if not cwd:
        return None
    cwd_path = Path(cwd).resolve()
    projects = load_projects()
    # 1. exact match
    for p in projects:
        if p.workspace_path:
            try:
                if Path(p.workspace_path).expanduser().resolve() == cwd_path:
                    return p.id
            except Exception:
                pass
    # 2. prefix match (cwd is inside a project dir)
    for p in projects:
        if p.workspace_path:
            try:
                cwd_path.relative_to(Path(p.workspace_path).expanduser().resolve())
                return p.id
            except ValueError:
                pass
    return None


# ── Generic record helpers ────────────────────────────────────────────────────

def _records_dir(kind: str, project_id: str) -> Path:
    return ra_root() / kind / project_id


def _load_records(kind: str, project_id: str) -> list[dict]:
    d = _records_dir(kind, project_id)
    if not d.exists():
        return []
    records = []
    for f in sorted(d.glob("*.yaml")):
        try:
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            if data:
                records.append(data)
        except Exception:
            pass
    return records


def _next_id(existing_ids: list[int]) -> int:
    return max(existing_ids, default=0) + 1


def _save_record(kind: str, project_id: str, record_id: int, data: dict) -> Path:
    d = _records_dir(kind, project_id)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{record_id:04d}.yaml"
    _atomic_yaml(path, data)
    return path


# ── Issues ────────────────────────────────────────────────────────────────────

def load_issues(project_id: str) -> list[Issue]:
    return [Issue.model_validate(r) for r in _load_records("issues", project_id)]


def save_issue(project_id: str, issue: Issue) -> None:
    issue.updated = date.today()
    _save_record("issues", project_id, issue.id, issue.model_dump(mode="json"))


def next_issue_id(project_id: str) -> int:
    return _next_id([i.id for i in load_issues(project_id)])


# ── Bets ─────────────────────────────────────────────────────────────────────

def load_bets(project_id: str) -> list[Bet]:
    return [Bet.model_validate(r) for r in _load_records("bets", project_id)]


def save_bet(project_id: str, bet: Bet) -> None:
    bet.updated = date.today()
    _save_record("bets", project_id, bet.id, bet.model_dump(mode="json"))


def next_bet_id(project_id: str) -> int:
    return _next_id([b.id for b in load_bets(project_id)])


# ── Decisions ─────────────────────────────────────────────────────────────────

def load_decisions(project_id: str) -> list[Decision]:
    return [Decision.model_validate(r) for r in _load_records("decisions", project_id)]


def save_decision(project_id: str, decision: Decision) -> None:
    _save_record("decisions", project_id, decision.id, decision.model_dump(mode="json"))


def next_decision_id(project_id: str) -> int:
    return _next_id([d.id for d in load_decisions(project_id)])


# ── Experiments ───────────────────────────────────────────────────────────────

def load_experiments(project_id: str) -> list[Experiment]:
    return [Experiment.model_validate(r) for r in _load_records("experiments", project_id)]


def save_experiment(project_id: str, exp: Experiment) -> None:
    _save_record("experiments", project_id, exp.id, exp.model_dump(mode="json"))


def next_experiment_id(project_id: str) -> int:
    return _next_id([e.id for e in load_experiments(project_id)])


# ── Findings ──────────────────────────────────────────────────────────────────

def load_findings(project_id: str) -> list[Finding]:
    return [Finding.model_validate(r) for r in _load_records("findings", project_id)]


def save_finding(project_id: str, finding: Finding) -> None:
    _save_record("findings", project_id, finding.id, finding.model_dump(mode="json"))


def next_finding_id(project_id: str) -> int:
    return _next_id([f.id for f in load_findings(project_id)])


# ── Thesis / NorthStar / Theory of Change ────────────────────────────────────

def load_thesis(project_id: str) -> Optional[Thesis]:
    path = ra_root() / "thesis" / project_id / "thesis.yaml"
    if not path.exists():
        return None
    return Thesis.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def save_thesis(project_id: str, thesis: Thesis) -> None:
    path = ra_root() / "thesis" / project_id / "thesis.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_yaml(path, thesis.model_dump(mode="json"))


def load_northstar(project_id: str) -> Optional[NorthStar]:
    path = ra_root() / "northstar" / project_id / "northstar.yaml"
    if not path.exists():
        return None
    return NorthStar.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def save_northstar(project_id: str, ns: NorthStar) -> None:
    path = ra_root() / "northstar" / project_id / "northstar.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_yaml(path, ns.model_dump(mode="json"))


def load_theory(project_id: str) -> Optional[TheoryOfChange]:
    path = ra_root() / "theory" / project_id / "theory.yaml"
    if not path.exists():
        return None
    return TheoryOfChange.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def save_theory(project_id: str, theory: TheoryOfChange) -> None:
    path = ra_root() / "theory" / project_id / "theory.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_yaml(path, theory.model_dump(mode="json"))


# ── Ideas (inbox) ─────────────────────────────────────────────────────────────

def load_ideas() -> list[InboxIdea]:
    path = ra_root() / "ideas.yaml"
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [InboxIdea.model_validate(i) for i in raw]


def save_ideas(ideas: list[InboxIdea]) -> None:
    _atomic_yaml(ra_root() / "ideas.yaml", [i.model_dump(mode="json") for i in ideas])


def append_idea(idea: InboxIdea) -> None:
    ideas = load_ideas()
    ideas.append(idea)
    save_ideas(ideas)


# ── Focus ─────────────────────────────────────────────────────────────────────

def load_focus() -> Optional[Focus]:
    path = ra_root() / "focus.yaml"
    if not path.exists():
        return None
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Focus.model_validate(raw) if raw else None


def save_focus(focus: Focus) -> None:
    _atomic_yaml(ra_root() / "focus.yaml", focus.model_dump(mode="json"))


# ── Handoffs ──────────────────────────────────────────────────────────────────

def latest_handoff_text(project_id: str) -> Optional[str]:
    d = ra_root() / "handoffs" / project_id
    if not d.exists():
        return None
    files = sorted(d.glob("*.md"), reverse=True)
    return files[0].read_text(encoding="utf-8") if files else None


def save_handoff(project_id: str, text: str) -> Path:
    d = ra_root() / "handoffs" / project_id
    d.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = d / f"{ts}.md"
    _atomic_write(path, text)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# SWM — Facts & Premise Findings
# ══════════════════════════════════════════════════════════════════════════════

def _swm_dir(project_id: str) -> Path:
    return swm_root() / project_id


def load_facts(
    project_id: Optional[str],
    kinds: Optional[list] = None,
) -> list[Fact]:
    """
    project_id=None → global facts only (project field is None in the record).
    project_id="x"  → project-specific facts + global facts.
    kinds           → filter by FactKind; None means all kinds.
    """
    paths: list[Path] = []

    if project_id:
        paths.append(_swm_dir(project_id) / "committed.jsonl")

    # Always include global facts (stored in swm/_global/committed.jsonl)
    global_path = swm_root() / "_global" / "committed.jsonl"
    if global_path not in paths:
        paths.append(global_path)

    facts: list[Fact] = []
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                fact = Fact.model_validate_json(line)
                if kinds and fact.kind not in kinds:
                    continue
                facts.append(fact)
            except Exception:
                pass
    return facts


def save_fact(fact: Fact) -> None:
    if fact.id is None:
        fact.id = str(uuid.uuid4())
    # Global facts go to _global dir
    if fact.project is None:
        project_key = "_global"
    else:
        project_key = fact.project
    path = _swm_dir(project_key) / "committed.jsonl"
    _atomic_jsonl_append(path, fact.model_dump(mode="json"))


def load_premise_findings(project_id: str) -> list[PremiseFinding]:
    path = _swm_dir(project_id) / "premise-findings.jsonl"
    if not path.exists():
        return []
    findings = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            findings.append(PremiseFinding.model_validate_json(line))
        except Exception:
            pass
    return findings


def save_premise_finding(project_id: str, finding: PremiseFinding) -> None:
    path = _swm_dir(project_id) / "premise-findings.jsonl"
    _atomic_jsonl_append(path, finding.model_dump(mode="json"))


def load_turn_counter(project_id: str) -> int:
    path = _swm_dir(project_id) / ".turn-counter"
    if not path.exists():
        return 0
    try:
        return int(path.read_text().strip())
    except Exception:
        return 0


def save_turn_counter(project_id: str, n: int) -> None:
    path = _swm_dir(project_id) / ".turn-counter"
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, str(n))


def load_strategic_state(project_id: str) -> str:
    path = _swm_dir(project_id) / "strategic-state.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def save_strategic_state(project_id: str, text: str) -> None:
    _atomic_write(_swm_dir(project_id) / "strategic-state.md", text)


# ══════════════════════════════════════════════════════════════════════════════
# Outcome Loop
# ══════════════════════════════════════════════════════════════════════════════

def load_verdicts() -> list[OutcomeVerdict]:
    path = _keel_home() / "outcome-loop" / "verdicts.jsonl"
    if not path.exists():
        return []
    verdicts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            verdicts.append(OutcomeVerdict.model_validate_json(line))
        except Exception:
            pass
    return verdicts


def save_verdict(v: OutcomeVerdict) -> None:
    path = _keel_home() / "outcome-loop" / "verdicts.jsonl"
    _atomic_jsonl_append(path, v.model_dump(mode="json"))


# ══════════════════════════════════════════════════════════════════════════════
# Migration: ~/.ra/ → ~/.keel/ra/
# ══════════════════════════════════════════════════════════════════════════════

class MigrationReport(BaseModel):
    n_migrated:  int         = 0
    n_skipped:   int         = 0
    warnings:    list[str]   = []
    errors:      list[str]   = []


def migrate_from_legacy(legacy_root: Path = Path.home() / ".ra") -> MigrationReport:
    """
    One-time migration from ~/.ra/ to ~/.keel/ra/.
    Non-destructive: never deletes ~/.ra/.
    Validates each record through Pydantic before writing.
    """
    report = MigrationReport()

    if not legacy_root.exists():
        report.warnings.append(f"Legacy root {legacy_root} not found — nothing to migrate")
        return report

    # ── Projects ──────────────────────────────────────────────────────────────
    proj_path = legacy_root / "projects.yaml"
    if proj_path.exists():
        raw = yaml.safe_load(proj_path.read_text(encoding="utf-8")) or []
        for item in raw:
            try:
                p = Project.model_validate(item)
                save_project(p)
                report.n_migrated += 1
            except Exception as e:
                report.n_skipped += 1
                report.errors.append(f"project {item.get('id','?')}: {e}")

    # ── Ideas ─────────────────────────────────────────────────────────────────
    ideas_path = legacy_root / "ideas.yaml"
    if ideas_path.exists():
        raw = yaml.safe_load(ideas_path.read_text(encoding="utf-8")) or []
        migrated_ideas = []
        for item in raw:
            try:
                idea = InboxIdea.model_validate(item)
                migrated_ideas.append(idea)
                report.n_migrated += 1
            except Exception as e:
                report.n_skipped += 1
                report.errors.append(f"idea {item.get('title','?')}: {e}")
        if migrated_ideas:
            save_ideas(migrated_ideas)

    # ── Per-project records ───────────────────────────────────────────────────
    _record_kinds = {
        "issues":      (Issue, save_issue),
        "bets":        (Bet, save_bet),
        "decisions":   (Decision, save_decision),
        "experiments": (Experiment, save_experiment),
        "findings":    (Finding, save_finding),
    }
    for kind, (Model, saver) in _record_kinds.items():
        kind_dir = legacy_root / kind
        if not kind_dir.exists():
            continue
        for proj_dir in kind_dir.iterdir():
            if not proj_dir.is_dir():
                continue
            project_id = proj_dir.name
            for yaml_file in proj_dir.glob("*.yaml"):
                try:
                    data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                    if not data:
                        continue
                    record = Model.model_validate(data)
                    saver(project_id, record)
                    report.n_migrated += 1
                except Exception as e:
                    report.n_skipped += 1
                    report.errors.append(f"{kind}/{project_id}/{yaml_file.name}: {e}")

    # ── SWM committed.jsonl (per project) ────────────────────────────────────
    # Legacy SWM lives in ~/.claude/hooks/swm/{project_id}/committed.jsonl
    legacy_swm = Path.home() / ".claude" / "hooks" / "swm"
    for proj_dir in (legacy_swm.iterdir() if legacy_swm.exists() else []):
        if not proj_dir.is_dir():
            continue
        project_id = proj_dir.name
        committed = proj_dir / "committed.jsonl"
        if committed.exists():
            for line in committed.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    raw_fact = json.loads(line)
                    # Legacy format has 'kind' as string — model_validate handles it
                    fact = Fact.model_validate(raw_fact)
                    if fact.project is None:
                        fact.project = project_id
                    save_fact(fact)
                    report.n_migrated += 1
                except Exception as e:
                    report.n_skipped += 1
                    report.errors.append(f"swm/{project_id}: {e}")

    return report
