# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- tiered_price(units, base) function must be implemented in billing.py
- Pricing tiers: first 10 units at base price, units 11–50 at 90% of base, units beyond 50 at 80% of base
- Minimum charge of 5.00 applies; if computed total is below 5.00, return 5.00
- Result must be rounded to 2 decimals
- Acceptance test in test_billing.py must import from billing module and prove implementation meets spec, then be run
