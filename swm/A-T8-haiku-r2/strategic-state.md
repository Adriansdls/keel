# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Test behavior not implementation; assert on user-visible outcomes or API returns, never internal state
- Default database: PostgreSQL (deviate only when NoSQL clearly justified by data model)
- Default architecture: Monolith (split only with clear bounded contexts and independent deploy needs)
- Default API style: REST (use GraphQL only for multiple consumers needing flexible nested queries)
- Use identity provider (Auth0, Azure AD, Okta) for auth; never roll your own
- Customer preference takes priority for tech stack

## Constraints
- WCAG 2.1 AA compliance is non-negotiable
- Never mock the database in integration tests; use a real test database
- Never store passwords in plain text; never use weak hashing (MD5, SHA1)
- Never put secrets in code
- No TODO/FIXME comments in committed code
- OpenAPI/Swagger specification is mandatory for all REST APIs
- Version APIs from day one: /api/v1/resources
- Authorization model: permissions OR roles, never both simultaneously
- Function max 50 lines; file max 300-400 lines
- Comprehensive error handling with centralized error handler mandatory for backends
- Validate all inputs, sanitize user data, use parameterized queries
- On PR: all tests pass and coverage must not drop; on merge to main: full suite including E2E, staging-only deploy
- Never compromise on security, data integrity, observability, disaster recovery
- Design for horizontal scalability; keep applications stateless
- Structured JSON logging only in production code

## Premises (provisional)
- Start simple, scale smart; choose simplest solution unless measured performance issue, regulatory requirement, or proven bottleneck exists
- Design for 10x, build for today
- Optimize for: team skill level, maintainability, time to market, simplicity (in priority order)
