# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Risk rating labels (Low/Medium/High/Critical) eliminated — no scoring rubric exists; judgment without rubric is forbidden.
- Executive recommendation verdicts (APPROVE/APPROVE WITH CONDITIONS/REJECT) eliminated and replaced by deterministic READY/NOT-READY derived from open questions and unmet conditions.

## Constraints
- READY/NOT-READY must be derived deterministically from count of unresolved questions and unmet approval conditions, never from a subjective verdict label.
- Final go/no-go decision remains human-only; AI must not simulate authority or accountability.
- Output must not contain literal '...' placeholder sections; write one explanatory sentence instead if a section has nothing meaningful.
- Include only active committee members whose focus area is materially affected; drop tangential concerns.
- Concerns and approval conditions must stay at strategic level (risk, tradeoff, dependency) not implementation detail.

## Premises (provisional)
- Default posture is scrutiny and risk-surfacing, not approval validation; review exists to find what will break, not validate what has been decided.
