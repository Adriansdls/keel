# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Load secrets from environment variables (approved solution to satisfy GATE requirement)

## Constraints
- GATE rejects plaintext secrets/tokens/passwords in files - must load from environment variables or secrets manager

## Premises (provisional)
- Missing env var correctly results in KeyError fast-fail - this behavior is expected and sufficient
