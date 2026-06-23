# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Customer tech stack preference takes priority over company defaults
- Choose simplest solution by default; complexity only justified by measured perf issue, regulatory requirement, or proven bottleneck

## Constraints
- WCAG 2.1 AA compliance is non-negotiable
- Security, data integrity, observability, and disaster recovery are non-negotiable
- Never store passwords in plain text, never use weak hashing (MD5, SHA1), never put secrets in code
- Never mock the database in integration tests; use a test database instead
- Test behavior, not implementation; assert on what users see or APIs return
- No TODO/FIXME comments in committed code
- OpenAPI/Swagger specification is mandatory for all REST APIs
- API versioning required from day one (/api/v1/...)
- Authorization model: use permissions OR roles, never both simultaneously
- Never roll your own auth; use identity provider (Auth0, Azure AD, Okta)
- Design for horizontal scalability; keep applications stateless
- Structured JSON logging only in production; no console.log/println/print
- Fail fast on missing config; validate all required environment variables at startup

## Eliminations / rejected
- Do not use unvetted or unknown third-party packages due to supply-chain risk
- Company engineering heuristics are non-negotiable regardless of deadline pressure
