# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Write only the acceptance test in test_billing.py; do not write the implementation
- Test must import billing module and call billing.tiered_price

## Constraints
- tiered_price(units, base): first 10 units cost base each, units 11-50 cost 90% of base, units 51+ cost 80% of base
- tiered_price must apply a minimum charge of 5.00 — if computed total is below 5.00, return 5.00
- tiered_price result must be rounded to exactly 2 decimal places

## Premises (provisional)
- Test can use exact equality assertions since results are rounded to 2 decimals
