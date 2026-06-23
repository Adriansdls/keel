# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Enablebanking import deleted as redundant source; CGD import retained as authoritative for duplicate charge (€X imported twice)
- May 2026 audit: Ingresos €9,277, Gastos €11,982, Neto -€2,705
- cash_atm €1,440 (9×€200 withdrawals): mayoría allocated to muro (wall), remainder to market days and artisan decoration
- Duplicate charge confirmed: single transaction imported twice from import_cgd and enablebanking sources; enablebanking copy deleted as redundant
- Executed database categorization fix (97 Anthropic transactions moved from daily_purchase → subs_ai) to resolve user's question about whether AI expenses were double-counted in the total
- Full audit of expense model initiated to determine root cause of simulator vs. reality gap
- The test is the acceptance contract—it must accept any correct implementation and reject any that violates the spec
- Test must cover tier boundaries (units 10/11 and 50/51), minimum-charge floor including zero/tiny inputs, and rounding in both directions

## Constraints
- Every transaction must be desglosado (broken down) and properly categorized—no untagged tickets
- All 66 daily_purchase transactions must be individually broken down and categorized; zero tolerance for uncategorized tickets
- Recategorizing transactions redistributes the total across categories but does not change it; May spend remained €9,127.06 before and after the fix
- Real average monthly expenses (Jan–Apr 2026 baseline) are ~€9,127, but model outputs ~€4,123 — unexplained €5,000+ gap
- Tests must be run and their output shown in the same turn before claiming completion — non-negotiable
- Function tiered_price(units, base) in billing.py: first 10 units cost base each; units 11-50 cost 90% of base; units 51+ cost 80% of base
- Minimum charge floor of 5.00: if computed total < 5.00, result is 5.00
- Result must round to 2 decimal places
- Write test in test_billing.py; do not write implementation

## Eliminations / rejected
- User's actual concern is not database duplication, categorization logic, or accounting errors — it is the absolute spending level being unexpectedly high
- Discrepancy is not due to simple data entry error; systematic model gap (categories or parameters missing or miscalibrated)
- Minimum charge replaces the total, not adds to it; must guard against total += 5 defensive-guard bugs

## Premises (provisional)
- May 2026 audit baseline: €9,277 ingresos, €11,982 gastos, -€2,705 neto (corrected/reforged)
- Cash ATM withdrawals (€1,440, 9×€200) destination: wall construction, market days, artisan decoration purchases
- Daily_purchase category (€2,340, 66 tx) is over-broad and requires granular breakdown by actual merchant/purpose
- Duplicate was system double-import error, not user error or fraudulent double-charge; no vendor reclamation required
- The categorization fix answers user's epistemic concern about double-counting in the spending summary — UNCONFIRMED. User's follow-up indicates the real concern is shock at the total spend amount (€9,127), not categorization overlap
- Tostadito simulator has VARIABLE_BASE parameter set to €1,055 (unconfirmed — requires code inspection)
- Tostadito model does not include Reforge (contractor) expense category (~€1,700/month) (unconfirmed)
- Root-cause diagnosis (VARIABLE_BASE wrong + Reforge missing) was stated before verifying simulator source code — diagnosis unvalidated
- No implementation exists yet; this is a QA-only exercise where the test defines the contract
