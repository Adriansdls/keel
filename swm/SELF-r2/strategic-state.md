# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Implement tiered_price(units, base) function in billing.py
- Pricing: first 10 units at base; units 11-50 at 90% of base; units 51+ at 80% of base
- Apply minimum charge of 5.00 (return 5.00 if computed total is below)
- Round result to 2 decimal places
- Write acceptance test in test_billing.py that proves implementation meets spec
- Test must import from billing module
- Run test and report results and what was done
- Create both files in current directory
