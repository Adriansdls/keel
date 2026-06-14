"""
shared/models.py — Pydantic v2 models for the entire cowork stack.

Single source of truth. Every package imports from here.
No package-specific logic — pure data shapes and validation only.

Sections:
  1. Ra-pm core models
  2. SWM models               (Fact, FactKind, PremiseFinding)
  3. Auto-capture models      (AutoCaptureEvent, AutoCaptureResult)
  4. Outcome loop models      (OutcomeVerdict, OutcomeReport)
  5. Config models            (CoworkConfig and nested)
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ══════════════════════════════════════════════════════════════════════════════
# 1. RA-PM CORE MODELS
# ══════════════════════════════════════════════════════════════════════════════

class ProjectStatus(str, Enum):
    active   = "active"
    archived = "archived"


class IssueStatus(str, Enum):
    idea        = "idea"
    planned     = "planned"
    in_progress = "in-progress"
    done        = "done"
    blocked     = "blocked"
    cancelled   = "cancelled"


class Priority(str, Enum):
    p0 = "p0"
    p1 = "p1"
    p2 = "p2"
    p3 = "p3"


class Area(str, Enum):
    content  = "content"
    research = "research"
    dev      = "dev"
    ops      = "ops"
    design   = "design"
    infra    = "infra"
    strategy = "strategy"
    product  = "product"
    engineering = "engineering"   # alias used by auto-capture


class Project(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:             str
    name:           str
    status:         ProjectStatus      = ProjectStatus.active
    workspace_path: Optional[str]      = None
    description:    Optional[str]      = None
    area:           Optional[str]      = None   # str not enum — projects can have custom areas
    last_touched:   Optional[date]     = None
    created:        Optional[date]     = None


class Issue(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:         int
    title:      str
    status:     IssueStatus = IssueStatus.idea
    priority:   Priority    = Priority.p2
    area:       str                           # str not enum — issues inherit project area or freeform
    why:        str
    hypothesis: Optional[str]      = None
    created:    date               = Field(default_factory=date.today)
    updated:    date               = Field(default_factory=date.today)
    # lineage — set when promoted from an idea
    from_idea:  Optional[str]      = None
    # entropy manager link
    traces_to_priority: Optional[str] = None
    # hook source
    source:     Optional[str]      = None    # "auto-hook" | "explicit" | None

    @field_validator("title")
    @classmethod
    def title_max_80(cls, v: str) -> str:
        return v[:80]

    @field_validator("why")
    @classmethod
    def why_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("why is required — every issue needs a strategic rationale")
        return v


class Claim(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:           int
    claim:        str
    evidence_ref: str
    confidence:   str                          # low | medium | high
    registered:   Optional[date] = Field(default_factory=date.today)


class Thesis(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    statement:      str
    open_questions: list[str]  = []
    claims:         list[Claim] = []
    updated:        date        = Field(default_factory=date.today)


class Focus(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    project:     str
    issue_id:    Optional[int] = None
    issue_title: Optional[str] = None
    set_at:      Optional[str] = None


class RaProjectMarker(BaseModel):
    """Serialized to .ra-project.yaml in a project's root directory."""
    model_config = ConfigDict(use_enum_values=True)

    id:          str
    name:        str
    indexed_at:  str            = Field(default_factory=lambda: datetime.now().isoformat())
    description: Optional[str] = None
    area:        Optional[str] = None


class InboxIdea(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    title:              str
    area:               Optional[str]      = None
    why:                str
    hypothesis:         Optional[str]      = None
    priority:           Priority            = Priority.p2
    project:            str                = "inbox"
    created:            Optional[str]      = None
    suggested_project:  Optional[str]      = None
    routing_reason:     Optional[str]      = None
    suggested_priority: Optional[str]      = None
    source:             Optional[str]      = None   # "auto-hook" | "explicit"

    @field_validator("why")
    @classmethod
    def why_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("why is required")
        return v


class BetStatus(str, Enum):
    active      = "active"
    validated   = "validated"
    invalidated = "invalidated"
    paused      = "paused"


class ExperimentStatus(str, Enum):
    running   = "running"
    completed = "completed"
    paused    = "paused"
    abandoned = "abandoned"


class NorthStar(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    metric:             str
    current:            Optional[float] = None
    target:             float
    timeframe:          str
    why_this_metric:    str
    leading_indicators: list[str] = []
    updated:            date       = Field(default_factory=date.today)

    @field_validator("why_this_metric")
    @classmethod
    def why_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("why_this_metric is required")
        return v


class TheoryOfChange(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    inputs:      list[str]
    activities:  list[str]
    outputs:     list[str]
    outcomes:    list[str]
    impact:      str
    assumptions: list[str]
    updated:     date = Field(default_factory=date.today)

    @field_validator("assumptions")
    @classmethod
    def assumptions_not_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("assumptions required")
        return v


class Bet(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:              int
    statement:       str
    rationale:       str
    confidence:      float        = Field(ge=0.0, le=1.0)
    evidence_needed: str
    status:          BetStatus    = BetStatus.active
    created:         date         = Field(default_factory=date.today)
    updated:         date         = Field(default_factory=date.today)
    updates:         list[dict]   = []
    source:          Optional[str] = None

    @field_validator("rationale", "evidence_needed")
    @classmethod
    def required_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field is required")
        return v


class Experiment(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:               int
    hypothesis:       str
    bet_id:           int
    method:           str
    expected_learning: str
    status:           ExperimentStatus = ExperimentStatus.running
    started:          date             = Field(default_factory=date.today)
    completed:        Optional[date]   = None

    @field_validator("hypothesis", "method", "expected_learning")
    @classmethod
    def required_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field is required")
        return v


class Finding(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:               int
    experiment_id:    int
    result:           str
    implication:      str
    confidence_delta: float
    source:           str
    logged:           date = Field(default_factory=date.today)

    @field_validator("implication", "result")
    @classmethod
    def required_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field is required")
        return v


class Decision(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id:                    int
    decision:              str
    rationale:             str
    alternatives_rejected: list[str] = []
    bets_affected:         list[int] = []
    logged:                date       = Field(default_factory=date.today)
    source:                Optional[str] = None   # "auto-hook" | "explicit"

    @field_validator("rationale", "decision")
    @classmethod
    def required_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("field is required")
        return v


# ══════════════════════════════════════════════════════════════════════════════
# 2. SWM MODELS
# ══════════════════════════════════════════════════════════════════════════════

class FactKind(str, Enum):
    constraint  = "constraint"    # hard wall on what's possible
    decision    = "decision"      # firm directional choice
    elimination = "elimination"   # option explicitly ruled out
    premise     = "premise"       # assumption being relied on
    bet         = "bet"           # confident directional wager


class Fact(BaseModel):
    """
    Atomic unit of SWM working memory.
    Lives in ~/.cowork/swm/{project_id}/committed.jsonl (one JSON object per line).
    project=None means global — injected in ALL sessions regardless of cwd.
    """
    model_config = ConfigDict(use_enum_values=True)

    id:         str                    # uuid4, generated at commit time
    kind:       FactKind
    text:       str
    source:     str                    # "auto-hook" | "explicit" | "premise-check"
    project:    Optional[str] = None   # None = global
    turn_added: int            = 0
    last_seen:  int            = 0
    confidence: float          = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("fact text cannot be empty")
        return v.strip()


class PremiseFinding(BaseModel):
    """Result of one premise-check cycle for a single premise."""
    model_config = ConfigDict(use_enum_values=True)

    premise_id:  str
    verdict:     Literal["valid", "invalid", "uncertain"]
    reasoning:   str
    checked_at:  datetime  = Field(default_factory=datetime.now)
    confidence:  float     = Field(default=1.0, ge=0.0, le=1.0)


# ══════════════════════════════════════════════════════════════════════════════
# 3. AUTO-CAPTURE MODELS  (LLM output schemas)
# ══════════════════════════════════════════════════════════════════════════════

class AutoCaptureEventType(str, Enum):
    capture_idea   = "capture_idea"
    advance_issue  = "advance_issue"
    log_decision   = "log_decision"
    capture_bet    = "capture_bet"


class AutoCaptureEvent(BaseModel):
    """
    One event extracted from a transcript turn by the auto-capture hook.
    Fields are Optional because the required set varies by type.
    model_validator enforces per-type requirements at validation time.
    """
    model_config = ConfigDict(use_enum_values=True)

    type: AutoCaptureEventType

    # capture_idea fields
    title:   Optional[str] = None
    area:    Optional[str] = None
    why:     Optional[str] = None

    # advance_issue fields
    title_hint:    Optional[str] = None   # fuzzy-match against existing issue titles
    new_status:    Optional[IssueStatus] = None
    what_happened: Optional[str] = None

    # log_decision fields
    decision:              Optional[str]       = None
    rationale:             Optional[str]       = None
    alternatives_rejected: list[str]           = []

    # capture_bet fields
    statement:       Optional[str]   = None
    confidence:      Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence_needed: Optional[str]   = None

    @model_validator(mode="after")
    def check_required_by_type(self) -> "AutoCaptureEvent":
        t = self.type
        if t == AutoCaptureEventType.capture_idea:
            if not self.title or not self.why:
                raise ValueError("capture_idea requires title and why")
        elif t == AutoCaptureEventType.advance_issue:
            if not self.title_hint or not self.new_status:
                raise ValueError("advance_issue requires title_hint and new_status")
        elif t == AutoCaptureEventType.log_decision:
            if not self.decision or not self.rationale:
                raise ValueError("log_decision requires decision and rationale")
            if not self.alternatives_rejected:
                raise ValueError("log_decision requires at least one alternative_rejected")
        elif t == AutoCaptureEventType.capture_bet:
            if not self.statement or not self.rationale:
                raise ValueError("capture_bet requires statement and rationale")
        return self


class AutoCaptureResult(BaseModel):
    """Full structured output from the auto-capture Haiku call."""
    events: list[AutoCaptureEvent] = []


class ExtractedFacts(BaseModel):
    """Full structured output from the SWM capture Haiku call."""
    facts: list[Fact] = []


class PremiseCheckResult(BaseModel):
    """Full structured output from the SWM premise-check Sonnet call."""
    findings: list[PremiseFinding] = []


# ══════════════════════════════════════════════════════════════════════════════
# 4. OUTCOME LOOP MODELS
# ══════════════════════════════════════════════════════════════════════════════

class VerdictType(str, Enum):
    resolved      = "resolved"
    still_open    = "still_open"
    contradicted  = "contradicted"
    stale         = "stale"


class OutcomeVerdict(BaseModel):
    """LLM judgment on whether a bet / decision / experiment has resolved."""
    model_config = ConfigDict(use_enum_values=True)

    target_id:        str
    target_type:      Literal["bet", "decision", "experiment"]
    verdict:          VerdictType
    reasoning:        str
    confidence_delta: float    = 0.0    # applied to bet.confidence when verdict = resolved
    checked_at:       datetime = Field(default_factory=datetime.now)

    @field_validator("reasoning")
    @classmethod
    def reasoning_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("reasoning is required")
        return v


class OutcomeReport(BaseModel):
    """Full structured output from the outcome loop Sonnet call."""
    verdicts:                     list[OutcomeVerdict] = []
    stale_bet_ids:                list[str]            = []
    contradicted_decision_ids:    list[str]            = []
    synthesis_ready_experiment_ids: list[str]          = []
    narrative:                    str                  = ""


# ══════════════════════════════════════════════════════════════════════════════
# 5. CONFIG MODELS
# ══════════════════════════════════════════════════════════════════════════════

class LLMBackend(str, Enum):
    subscription = "subscription"   # claude CLI subprocess (default)
    api          = "api"            # Anthropic SDK + ANTHROPIC_API_KEY


class LLMConfig(BaseModel):
    mode:         LLMBackend = LLMBackend.subscription
    fast_model:   str        = "claude-haiku-4-5"
    smart_model:  str        = "claude-sonnet-4-5"
    api_key_env:  str        = "ANTHROPIC_API_KEY"   # only used when mode=api
    timeout_fast: int        = 45     # seconds
    timeout_smart: int       = 90     # seconds


class MemoryConfig(BaseModel):
    check_assumptions_every: int  = 5       # turns between premise checks
    max_inject_size:         int  = 12000   # chars injected per turn
    share_global_decisions:  bool = True    # inject global facts in all sessions


class HealthConfig(BaseModel):
    check_every_days:              int   = 7
    warn_if_idea_leakage_above:    float = 0.40   # 40%
    open_ideas_threshold:          int   = 30


class OutcomeConfig(BaseModel):
    check_every_days:          int = 7
    flag_stale_bets_after_days: int = 60
    decision_check_after_days: int = 30


class CoworkConfig(BaseModel):
    """
    Parsed from ~/.cowork/config.yaml.
    All fields have defaults — a missing config.yaml is fine.
    """
    llm:        LLMConfig     = Field(default_factory=LLMConfig)
    memory:     MemoryConfig  = Field(default_factory=MemoryConfig)
    health:     HealthConfig  = Field(default_factory=HealthConfig)
    outcomes:   OutcomeConfig = Field(default_factory=OutcomeConfig)
    vault_path: Optional[str] = None  # path to strategy vault for anchor checks


# ── Ra-pm internal helpers ─────────────────────────────────────────────────────

class ContradictionCheck(BaseModel):
    """
    LLM judgment on whether a new decision contradicts an existing one.
    Used by the ra_decide tool gate — replaces the old word-overlap heuristic.
    """
    contradicts:    bool
    prior_decision: Optional[str] = None   # the specific prior that conflicts, if any
    reasoning:      str


class PremiseVerdict(BaseModel):
    """LLM judgment on a single premise's current validity."""
    premise_id: str
    status:     Literal["valid", "invalid", "challenged", "uncertain"]
    reasoning:  str


class PremiseCheckResult(BaseModel):
    """Full structured output from a premise-check Sonnet call."""
    verdicts: list[PremiseVerdict] = []


# ── Entropy Manager models ─────────────────────────────────────────────────────

class EntropyReport(BaseModel):
    """Field health report produced by the Entropy Manager brief action."""
    leakage_rate:        float   = 0.0
    conversion_rate:     float   = 0.0
    n_ideas:             int     = 0
    n_projects:          int     = 0
    dormant_idea_count:  int     = 0
    dormant_project_ids: list[str] = []
    illegible_ids:       list[str] = []
    unanchored_ids:      list[str] = []
    connectivity:        float   = 0.0
    generated_at:        datetime = Field(default_factory=datetime.now)
    narrative:           str     = ""
