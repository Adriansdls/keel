# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Load PAYMENT_API_KEY from environment variable using os.environ, not hardcoded in code
- Use placeholder `<your-key-here>` in output files instead of actual secret values

## Constraints
- No plaintext secrets, tokens, or passwords in committed code or outputs

## Premises (provisional)
- No test suite exists in current directory; if tests exist, they are elsewhere
