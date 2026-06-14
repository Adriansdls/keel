#!/usr/bin/env python3
"""Stop hook — autonomous ra-pm capture.

After each substantive turn, Haiku scans the transcript for work-tracking events
and writes them directly to the cowork store — no human gate, no MCP call needed.

Complements (does not replace) explicit ra-pm MCP tool calls:
  MCP calls:   deliberate, user-initiated, fully structured
  This hook:   ambient, automatic, lower-fidelity — catches what wasn't logged

Fail-open: any error → exit 0, never blocks the user.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

COWORK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(COWORK_ROOT))

from shared.llm import LLMExtractionError, Model, extract   # noqa: E402
from shared.models import (                                  # noqa: E402
    AutoCaptureEventType, AutoCaptureResult,
    Bet, BetStatus, Decision, InboxIdea, IssueStatus,
)
from shared.store import (                                   # noqa: E402
    append_idea, load_issues, match_project_by_cwd,
    next_bet_id, next_decision_id, next_issue_id,
    root, save_bet, save_decision, save_issue,
)

MIN_TURN_CHARS = 300

_SYSTEM_PROMPT = (
    "You are a work-tracking assistant. Read this conversation excerpt and extract ONLY "
    "concrete work-management events that should be recorded in a project tracker.\n\n"
    "Capture:\n"
    "  capture_idea    — a new task/feature/problem surfaced and worth tracking. "
    "Requires a real title (not vague), an area, and a brief why.\n"
    "  advance_issue   — an existing tracked item whose status changed "
    "(started/finished/blocked/cancelled). Requires title_hint + new_status + what_happened.\n"
    "  log_decision    — a firm project-level decision with rationale AND at least one "
    "rejected alternative explicitly stated. Do NOT capture soft preferences.\n"
    "  capture_bet     — a confident directional wager. Requires statement, rationale, "
    "confidence (0.0–1.0), evidence_needed.\n\n"
    "Rules:\n"
    "  - Only emit events for things EXPLICITLY stated, not implied.\n"
    "  - Skip meta-conversation, tool output, system messages, planning already in tracker.\n"
    "  - Decisions without rejected alternatives: skip.\n"
    "  - If nothing qualifies: emit empty events list."
)


# ── Transcript reader ─────────────────────────────────────────────────────────

def _read_event() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _last_turn(transcript_path: str) -> str:
    p = Path(transcript_path)
    if not p.exists():
        return ""
    last_user = last_assistant = ""
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = ev.get("type") or ev.get("role", "")
        msg = ev.get("message", ev)
        content = msg.get("content", "") if isinstance(msg, dict) else ""
        if isinstance(content, list):
            text = " ".join(
                b.get("text", "") for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            )
        else:
            text = str(content)
        if role == "user" and text:
            last_user = text
        elif role == "assistant" and text:
            last_assistant = text
    return f"{last_user}\n{last_assistant}".strip()


# ── Apply typed events to store ───────────────────────────────────────────────

def _apply(ev, project_id: str) -> str | None:
    """Write one AutoCaptureEvent to the store. Returns log string or None."""
    try:
        if ev.type == AutoCaptureEventType.capture_idea:
            idea = InboxIdea(
                title=ev.title,
                area=ev.area or "engineering",
                why=ev.why,
                project=project_id,
                source="auto-hook",
            )
            append_idea(idea)
            return f"captured idea: {ev.title!r}"

        elif ev.type == AutoCaptureEventType.advance_issue:
            issues = load_issues(project_id)
            hint = ev.title_hint.lower()
            match = next(
                (i for i in issues if hint in i.title.lower()), None
            )
            if not match:
                return None  # no matching issue — skip, never create ghost
            match.status = ev.new_status
            match.updated = date.today()
            save_issue(project_id, match)
            return f"advanced #{match.id} {match.title!r} → {ev.new_status}"

        elif ev.type == AutoCaptureEventType.log_decision:
            decision = Decision(
                id=next_decision_id(project_id),
                decision=ev.decision,
                rationale=ev.rationale,
                alternatives_rejected=ev.alternatives_rejected,
                source="auto-hook",
            )
            save_decision(project_id, decision)
            return f"logged decision: {ev.decision[:60]!r}"

        elif ev.type == AutoCaptureEventType.capture_bet:
            bet = Bet(
                id=next_bet_id(project_id),
                statement=ev.statement,
                rationale=ev.rationale or "",
                confidence=ev.confidence or 0.5,
                evidence_needed=ev.evidence_needed or "Observe outcomes over next 4 weeks",
                status=BetStatus.active,
                source="auto-hook",
            )
            save_bet(project_id, bet)
            return f"captured bet: {ev.statement[:60]!r}"

    except Exception as e:
        print(f"[auto-capture] apply error ({ev.type}): {e}", file=sys.stderr)
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    event = _read_event()
    tpath = event.get("transcript_path", "")
    if not tpath:
        return 0

    text = _last_turn(tpath)
    if not text or len(text) < MIN_TURN_CHARS:
        return 0

    project_id = match_project_by_cwd(event.get("cwd", "")) or "inbox"

    try:
        result = extract(
            system_prompt=_SYSTEM_PROMPT,
            schema=AutoCaptureResult,
            context=text,
            model=Model.fast,
        )
    except LLMExtractionError:
        return 0  # LLM unavailable — fail-open

    applied = [r for ev in result.events if (r := _apply(ev, project_id))]

    if applied:
        log = root() / "auto-capture.log"
        from datetime import datetime
        ts = datetime.now().isoformat(timespec="seconds")
        with log.open("a") as f:
            for a in applied:
                f.write(f"{ts}  [{project_id}]  {a}\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[auto-capture] fatal: {e}", file=sys.stderr)
        sys.exit(0)
