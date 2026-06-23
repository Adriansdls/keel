# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- test_billing.py must explicitly pin tier boundaries at unit counts 10/11 and 50/51
- test_billing.py must explicitly pin minimum-charge floor behavior with small inputs (0 and a few units)
- test_billing.py must explicitly pin 2-decimal rounding behavior

## Constraints
- Test definitions of done must pass on correct implementations before being considered valid

## Eliminations / rejected
- First definition of done attempt was rejected by GATE as unfit

## Premises (provisional)
- Zero base cost still triggers the minimum charge (incorrect prior assumption that it did not)
