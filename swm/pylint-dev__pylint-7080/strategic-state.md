# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Root cause is in _discover_files() method in pylint/lint/pylinter.py - code checks if directories are ignored but not individual files
- Fix by adding ignore-check for individual files before yielding them in the file discovery generator

## Constraints
- src/gen/* files should not be checked by pylint

## Premises (provisional)
- Bug present: --recursive=y ignores ignore-paths configuration
