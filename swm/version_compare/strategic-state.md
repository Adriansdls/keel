# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Implementation splits by '.', converts parts to integers, pads shorter versions with zeros, then compares

## Constraints
- compare_versions(a, b) must return -1 if a < b, 0 if equal, 1 if a > b
- Versions are dot-separated numbers like '1.2.10'
