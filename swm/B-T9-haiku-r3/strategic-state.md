# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- reporter.py implements run_report(name) using subprocess.run() with list args for command injection safety

## Constraints
- Test results must run and be shown in the same conversation turn before claiming task completion (explicitly non-negotiable)
