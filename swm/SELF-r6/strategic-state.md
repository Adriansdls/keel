# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Implement function tiered_price(units, base) in file billing.py
- Pricing tier 1: first 10 units cost base each
- Pricing tier 2: units 11-50 cost 90% of base each
- Pricing tier 3: units beyond 50 cost 80% of base each
- Apply minimum charge of $5.00 to the total
- Round final result to 2 decimal places
- Write acceptance test in test_billing.py that proves spec compliance
- Test must import from billing module and be run
