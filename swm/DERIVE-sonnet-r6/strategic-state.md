# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Test-first approach: write acceptance test before implementation to define the contract
- Tests in test_billing.py; must use `import billing` and call `billing.tiered_price`

## Constraints
- First 10 units cost base each (Tier 1: 100%)
- Units 11-50 cost 90% of base each (Tier 2)
- Units beyond 50 cost 80% of base each (Tier 3)
- Minimum charge of 5.00: if computed total is below 5.00, use 5.00
- Round result to 2 decimal places
- Function: tiered_price(units, base) in billing.py module

## Premises (provisional)
- Common implementation mistakes to catch: off-by-one errors on tier boundaries (units 10/11 and 50/51), miscount tier 2 units as 39 or 41 instead of 40, apply 90% to unit 10, start 80% at unit 50 instead of 51, truncate instead of round, return string instead of numeric, ignore minimum when base is zero
