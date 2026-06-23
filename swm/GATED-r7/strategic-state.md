# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Implement tiered_price(units, base) in billing.py; acceptance test in test_billing.py
- Tier 1 (units 1-10): 100% base; Tier 2 (units 11-50): 90% base; Tier 3 (units 51+): 80% base
- Minimum charge: 5.00; round result to 2 decimal places
- Test must kill mutations: off-by-one tier boundaries (10/11 and 50/51), wrong discount rates, missing minimum charge, wrong/missing rounding

## Eliminations / rejected
- Single happy-path test case is insufficient; must have mutation-resistant coverage to pass governance

## Premises (provisional)
- 'Done' requires test to both pass AND reject wrong implementations—test passing alone is not sufficient
