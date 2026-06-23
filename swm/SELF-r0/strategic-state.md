# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- tiered_price returns total cost for given units at base price with tiered discounts

## Constraints
- Create file named billing.py in current directory
- Implement function tiered_price(units, base)
- First 10 units cost base each
- Units 11-50 cost 90% of base
- Units beyond 50 cost 80% of base
- Apply minimum charge of 5.00 (if total < 5.00, return 5.00)
- Round final result to 2 decimals
- Test must import from billing module
