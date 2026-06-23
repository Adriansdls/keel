# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Security gate rejects plaintext secrets/tokens/passwords in code—must load from environment variables or secrets manager

## Premises (provisional)
- `config.py` validates env var usage by raising `KeyError` if the required secret env var is missing
