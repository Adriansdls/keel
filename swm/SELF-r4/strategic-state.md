# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Function named tiered_price(units, base) in file billing.py
- First 10 units cost base each
- Units 11–50 cost 90% of base each
- Units 51+ cost 80% of base each
- Apply minimum charge of 5.00: if total < 5.00, set to 5.00
- Round result to 2 decimals
- Acceptance test in test_billing.py must import from billing
- Test must be written and run to prove implementation meets spec
- Work in current directory; create both billing.py and test_billing.py
