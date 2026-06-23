# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Fix the cache bug by invalidating cache on delete, since delete() was clearing underlying data but leaving stale cache entries
- SWM (StrategicPriority) is the authoritative top layer — ra-pm bets execute against SWM spine, not the reverse
- Background hooks maintain SWM fully automatically in every project — no manual per-project install or capture step required
- SWM gates downstream execution — ra-pm work must ladder to active priorities before proceeding

## Constraints
- Keep existing visible tests passing when fixing the bug
- Verify the fix works
- Keep the active priority set short (budget ~7) — if everything is a priority, nothing is

## Premises (provisional)
- Work that does not trace to an active StrategicPriority is drift, flagged for remediation (trace, open new priority, or drop)
