# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- The traceback for unrecognized options should be removed; only the error message should be shown (e.g., 'Unrecognized option found: Q')

## Constraints
- Do NOT edit or add test files when fixing this bug

## Premises (provisional)
- Current behavior prints both an error message and a traceback when an unrecognized option is passed; desired behavior matches mypy's approach of showing just the error without traceback
- The _UnrecognizedOptionError is raised in pylint.config.config_initialization._config_initialization and propagates with a traceback
