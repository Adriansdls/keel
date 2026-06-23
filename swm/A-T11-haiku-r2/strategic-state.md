# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- PostgreSQL is default database; deviate only if NoSQL clearly justified by data model
- Monolith is default architecture; deviate if clear bounded contexts + large team + independent deploy needs
- REST is default API style; deviate if multiple consumers need flexible queries across deeply nested data
- Never roll your own auth; always use identity provider (Auth0, Azure AD, Okta)
- PrimeReact/PrimeNG/PrimeVue is default UI library; deviate only if client already uses different

## Constraints
- E2E tests only for critical business paths (auth, payment, core workflows); everything else gets unit + integration
- Never mock the database in integration tests; use a test database instead
- Test behavior, not implementation; assert on what user sees or API returns, never on internal state
- WCAG 2.1 AA compliance is non-negotiable
- Function max 50 lines; file max 300-400 lines
- No TODO/FIXME comments in committed code
- Comprehensive error handling mandatory; centralized error handler mandatory for backends
- All tests must pass on PR (blocks merge); coverage must not drop
- OpenAPI/Swagger specification is mandatory for all REST APIs
- Version APIs from day one: /api/v1/resources
- Non-CRUD operations use command pattern: POST /commands/verb-noun (kebab-case)
- Permissions OR roles, never both simultaneously
- Never store passwords in plain text; never use weak hashing (MD5, SHA1); never put secrets in code
- Validate required environment variables at startup before accepting traffic
- Structured JSON logging only in production code; no console.log/println/print
- API response p95 < 200ms; database query p95 < 50ms; page load < 3s; time to interactive < 5s

## Premises (provisional)
- Customer preference takes priority; respect client tech stack
- Start simple, scale smart; choose simplest solution unless measured perf issue, regulatory requirement, or proven bottleneck
- Optimize for team skill level, maintainability, time to market, simplicity (in that order)
- Delegate exploration, not orchestration; subagents handle research, lead agent owns sequencing and quality gates
- Security, data integrity, observability, and disaster recovery are non-negotiable—never compromise
- Design for horizontal scalability; keep applications stateless
