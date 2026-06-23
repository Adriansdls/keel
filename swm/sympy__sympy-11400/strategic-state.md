# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- sinc should be converted to Piecewise form in ccode output instead of 'Not supported in C' message

## Constraints
- Do NOT edit or add test files

## Premises (provisional)
- math.h does not have a sinc function; sinc(x) should be represented as sin(x)/x when x≠0, else 1
