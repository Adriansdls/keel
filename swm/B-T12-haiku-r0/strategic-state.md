# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Tier calculation replaced with closed-form logic: units per tier (0–10 @ base, 10–50 @ 90%, 50+ @ 80%), summed, min 5.0 charge applied, rounded—improves from O(n) to O(1) while preserving behavior
