"""Haiku semantic extractor for strategic-fact capture (replaces rule-based as primary).

The n=20 experiment showed the rule-based detector misses facts stated in natural prose
(it keys on "Hard constraint:"-style labels real strategic talk doesn't use): +0.19 SDT
vs the Haiku extractor's +0.52. So capture now extracts SEMANTICALLY via Haiku,
using shared.llm.extract() — no regex, no subprocess boilerplate, subscription-native.

Falls back to the rule detector only if LLM is unavailable. Fail-open.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
COWORK_ROOT = HERE.parent
sys.path.insert(0, str(COWORK_ROOT))

import capture_patterns as cp                           # rule fallback  # noqa: E402
from shared.llm import extract, Model, LLMExtractionError  # noqa: E402
from shared.models import ExtractedFacts                # noqa: E402

_KINDS = ("constraint", "decision", "elimination", "premise")  # must match swm_store.KINDS

_SYSTEM_PROMPT = (
    "From this conversation excerpt, extract any strategic facts the team must NOT lose across "
    "a long session: hard constraints, decisions (with their rationale and any rejected alternative), "
    "options that were considered and dropped, and provisional/unconfirmed premises. "
    "Capture genuine commitments stated in the conversation — including ones phrased casually, not labeled. "
    "IGNORE system reminders, tool/command output, instructions about how the assistant should behave, and meta-text. "
    "Emit ATOMIC facts: one self-contained claim per item. Do NOT also emit a combined/compound version "
    "of facts you already split out, and do NOT split one fact into overlapping fragments. "
    "No item should restate or contain another. "
    "Empty facts list if nothing genuine."
)


def extract_facts(text: str, committed_state_text: str = "") -> list[dict]:
    """Return strategic facts [{kind, text}] from a transcript excerpt via Haiku,
    falling back to the rule detector if LLM is unavailable.

    committed_state_text is the already-known durable state, passed as additional context
    so Haiku skips re-extracting already-committed facts.

    Fail-open: returns [] on any error so a capture failure never breaks the turn.
    Filters to the canonical kinds so a hallucinated kind never reaches the store.
    """
    context = text[-6000:]
    if committed_state_text.strip():
        context = (
            "ALREADY CAPTURED — do NOT repeat these or trivial rephrasings:\n"
            + committed_state_text.strip()[-1500:]
            + "\n\nEXCERPT:\n"
            + context
        )

    try:
        result = extract(
            system_prompt=_SYSTEM_PROMPT,
            schema=ExtractedFacts,
            context=context,
            model=Model.fast,
        )
        raw = [{"kind": f.kind, "text": f.text.strip()} for f in result.facts]
    except LLMExtractionError:
        # Primary path unavailable — fall back to rule-based detector
        try:
            raw = [{"kind": kind, "text": span.strip()} for kind, span in cp.detect_in_text(text)]
        except Exception:
            return []
    except Exception:
        return []

    return [f for f in raw if f["kind"] in _KINDS and f["text"]]


def extract_and_record(text: str, candidates_path: Path, committed_state_text: str = "",
                       priority: str = "continuous") -> int:
    """Legacy candidate-file path (kept for the manual review/dismiss flow in swm cli)."""
    try:
        facts_result = extract(
            system_prompt=_SYSTEM_PROMPT,
            schema=ExtractedFacts,
            context=text[-6000:],
            model=Model.fast,
        )
        facts = [{"kind": f.kind, "text": f.text} for f in facts_result.facts]
        cands = [cp.build_candidate(f["kind"], f["text"].strip(), priority=priority) for f in facts]
        return cp.append_candidates(candidates_path, cands, committed_state_text)
    except Exception:
        return cp.detect_and_record(text, candidates_path,
                                    committed_state_text=committed_state_text,
                                    priority=priority)
