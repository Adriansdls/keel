# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Do NOT invoke for architecture decisions (use system-architect), test-only work (use qa-specialist), or discovery/requirements (use product-manager).
- Non-negotiable across all projects.
- Never ship below this.
- Never put secrets in code.
- Key is never in code — set it via env or a secrets manager (Azure Key Vault, AWS Secrets Manager, etc.) at deploy time.
