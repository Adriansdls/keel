# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Test will guard against off-by-one errors at tier boundaries (units 10→11 and 50→51)
- Test will verify incremental costs: unit 11 must cost exactly 0.9*base (not base), unit 51 must cost exactly 0.8*base (not 0.9*base)
- Test will validate minimum charge with zero units, zero base, and boundary cases: 4.99→5.00, 5.00→5.00, 5.01→5.01
- Test will use parametrized rounding validation with fractional bases (e.g., base=1/3) to verify both round-up and round-down cases

## Constraints
- Tiered pricing structure: units 1–10 cost base each, units 11–50 cost 90% of base, units 51+ cost 80% of base
- Minimum charge floor of 5.00: if computed total is below 5.00, the result is 5.00
- Minimum charge is a floor replacement, not an additive fee
- Result must be rounded to 2 decimal places

## Premises (provisional)
- The test is the contract — it must accept any correct implementation and reject any that violates the spec
