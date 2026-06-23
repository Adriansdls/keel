# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Test strategy: validate boundaries via price differences (10→11 must differ by $9, 50→51 by $8) to catch off-by-one mutations
- Test strategy: verify exact discount rates (90%, 80%) and minimum charge as separate concerns to isolate mutation types

## Constraints
- Tier boundaries are exact: units 1–10 cost base each; 11–50 cost 90% of base; 51+ cost 80% of base
- Minimum charge floor: if computed total < $5.00, result is $5.00
- Result must be rounded to 2 decimal places

## Eliminations / rejected
- Single happy-path test is insufficient; must comprehensively pin all spec clauses

## Premises (provisional)
- Acceptance test quality is measured by mutation testing: must fail on off-by-one boundaries, wrong rates, missing minimum, or wrong/missing rounding
