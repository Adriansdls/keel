"""Shared rule-based detector for strategic-fact capture (L1 + L4).

Single source of truth for the per-kind signal patterns. Extracts the verbatim
sentence containing a signal (extraction, NOT summary — preserves the fidelity the
research requires). Candidates are reviewed before commit, so recall matters more
than precision: over-trigger is fine, it costs a review line, never state pollution.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# kind -> signal patterns. kind maps to a StrategicState field at commit time.
PATTERNS: dict[str, list[str]] = {
    "constraint": [
        r"hard constraint", r"non-negotiable", r"we will not\b", r"must not\b",
        r"\bcannot\b", r"\bdo not\b", r"\bnever\b", r"not allowed", r"off the table",
    ],
    "decision": [
        r"decision on record", r"we (chose|decided|picked|selected)", r"we'?ll go with",
        r"let'?s go with", r"we are going with", r"go with\b", r"decided to\b",
    ],
    "elimination": [
        r"ruled out", r"rejected", r"decided against", r"not doing", r"cannibaliz",
        r"we don'?t\b", r"abandon", r"drop the", r"no longer pursuing",
    ],
    "premise": [
        r"provisional", r"\bpending\b", r"\bassume\b", r"not (yet )?(final|confirmed|closed|audited)",
        r"rough estimate", r"unverified", r"unvalidated", r"pre-audit", r"hasn'?t closed",
    ],
}

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_SOURCE = re.compile(r"\(source:\s*([^)]+)\)", re.IGNORECASE)
_MAX_SPAN = 240  # atomic facts are short; longer spans are usually prose/instructions

# Meta/instruction text that rides into the transcript (system reminders, command
# caveats, hook output, agent-behavior directives) is NOT a session strategic fact.
# These markers must never become candidates.
_NOISE = [
    r"</?local-command", r"<command-(name|message|args|stdout)", r"system.reminder",
    r"respond to these messages", r"do not tell the user", r"auto-clears", r"\bcaveat\b",
    r"hook (fired|success|additional|event)", r"acknowledge the goal", r"beast (drift|mode)",
    r"caveman", r"do not develop anything", r"these instructions override", r"reasoning_effort",
    r"the user'?s? (private|global) instructions", r"<system-reminder", r"additional context",
]


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]


def _is_noise(span: str) -> bool:
    if len(span) > _MAX_SPAN or span.rstrip().endswith("?"):
        return True  # too long to be an atomic fact, or a question (not a commitment)
    low = span.lower()
    return any(re.search(p, low) for p in _NOISE)


def detect_in_text(text: str) -> list[tuple[str, str]]:
    """Return (kind, verbatim_sentence) for each sentence matching a signal.

    A sentence is attributed to the FIRST kind whose pattern it matches, so one
    sentence yields at most one candidate. Meta/instruction text and non-atomic
    spans are filtered out — they are not session strategic facts.
    """
    out: list[tuple[str, str]] = []
    for sent in _sentences(text):
        if _is_noise(sent):
            continue
        low = sent.lower()
        for kind, pats in PATTERNS.items():
            if any(re.search(p, low) for p in pats):
                out.append((kind, sent))
                break
    return out


def _cand_id(kind: str, span: str) -> str:
    norm = re.sub(r"\s+", " ", span.strip().lower())
    return hashlib.sha1(f"{kind}:{norm}".encode()).hexdigest()[:12]


def build_candidate(kind: str, span: str, *, turn: int = -1, priority: str = "continuous") -> dict:
    src = _SOURCE.search(span)
    return {
        "id": _cand_id(kind, span),
        "kind": kind,
        "text": span.strip(),
        "source_hint": src.group(1).strip() if src else "",
        "turn": turn,
        "priority": priority,
        "committed": False,
    }


def load_candidates(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def append_candidates(path: Path, new: list[dict], committed_state_text: str = "") -> int:
    """Append candidates, deduped by id and against already-committed state text.
    Returns how many were actually added."""
    existing = load_candidates(path)
    seen = {c["id"] for c in existing}
    state_low = committed_state_text.lower()
    added = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for c in new:
            if c["id"] in seen:
                continue
            # skip if the span is already substantially present in committed state
            key = re.sub(r"\s+", " ", c["text"].strip().lower())[:60]
            if key and key in state_low:
                continue
            f.write(json.dumps(c) + "\n")
            seen.add(c["id"])
            added += 1
    return added


def detect_and_record(text: str, candidates_path: Path, committed_state_text: str = "",
                      turn: int = -1, priority: str = "continuous") -> int:
    cands = [build_candidate(k, s, turn=turn, priority=priority) for k, s in detect_in_text(text)]
    return append_candidates(candidates_path, cands, committed_state_text)
