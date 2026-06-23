# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Authorization model: permissions OR roles, never both simultaneously
- Never roll your own auth—use identity provider (Auth0, Azure AD, Okta)
- Default database: PostgreSQL unless NoSQL clearly justified by data model
- Default architecture: Monolith unless clear bounded contexts + large team + independent deploy needs
- Default API style: REST unless multiple consumers need flexible queries
- Delegate exploration not orchestration to subagents; never delegate quality gates; prefer foreground for blocking dependencies

## Constraints
- Never compromise on: security, data integrity, observability, disaster recovery
- Never store passwords in plain text; never use weak hashing (MD5, SHA1); never put secrets in code
- Secrets via vault or secrets manager only; never commit .env files with secrets
- OpenAPI/Swagger specification mandatory for all REST APIs
- API response (p95) < 200ms; database query (p95) < 50ms; page load < 3s; time to interactive < 5s
- Fail fast on missing config; log version, git SHA, and config keys (not values) on startup
- Structured JSON logging only; no console.log/print in production

## Premises (provisional)
- Complexity must be justified by measured perf issue, regulatory requirement, or proven bottleneck
- Design for 10x, build for today—architecture accommodates growth without over-engineering
- Optimization priority order: team skill level > maintainability > time to market > simplicity
