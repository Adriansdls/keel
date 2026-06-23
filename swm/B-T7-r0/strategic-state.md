# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Database default is PostgreSQL unless NoSQL clearly justified by data model
- Architecture default is Monolith unless clear bounded contexts, large team, and independent deploy needs exist
- API style default is REST unless multiple consumers need flexible queries across deeply nested data
- Auth default is Identity provider (Auth0, Azure AD, Okta); never roll your own
- UI library default is PrimeReact/PrimeNG/PrimeVue unless client already uses different library
- Toast notifications: Success (green, auto-dismiss 3s), Info (blue, auto-dismiss 5s), Warning (orange, manual dismiss), Error (red, manual dismiss + retry action)
- Caching default is None unless measured performance bottleneck exists
- Message queue default is None unless clear async workflow need
- API gateway default is None unless 5+ services

## Constraints
- WCAG 2.1 AA compliance is non-negotiable
- Function max 50 lines
- File max 300-400 lines
- No TODO/FIXME comments in committed code
- OpenAPI/Swagger specification is mandatory for all REST APIs
- Never store passwords in plain text or use weak hashing (MD5, SHA1)
- Design for horizontal scalability; keep applications stateless
- Regulatory compliance must be addressed at architecture level, not retroactively
- API response (p95) target < 200ms; database query (p95) < 50ms; page load < 3s
- On PR: all tests pass (block merge on failure), coverage must not drop

## Premises (provisional)
- Start simple, scale smart; choose simplest solution unless measured performance issue, regulatory requirement, or proven bottleneck
- Design for 10x, build for today; architecture should accommodate growth without over-engineering for hypothetical scale
- Optimize for team skill level, maintainability, time to market, simplicity (in that order)
- Customer preference takes priority; if client has tech stack, respect it
- Delegate exploration not orchestration; subagents handle research, lead agent owns sequencing and user communication
