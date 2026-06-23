# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Fixed percentage() crash by adding guard: whole == 0 returns 0.0 instead of crashing

## Constraints
- Users report percentage() in calc.py crashes sometimes
