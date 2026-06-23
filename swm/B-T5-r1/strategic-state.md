# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Database default: PostgreSQL; deviate only if NoSQL clearly justified by data model
- Architecture default: monolith; deviate only with clear bounded contexts, large team, independent deploy needs
- API style default: REST; use GraphQL only if multiple consumers need flexible queries across nested data
- Caching default: none; add only if measured performance bottleneck exists
- Auth: use identity provider (Auth0, Azure AD, Okta)—never roll your own
- Version APIs from day one (/api/v1/resources)
- All dependencies require license vetting before inclusion, regardless of time pressure

## Constraints
- Never compromise on security, data integrity, observability, disaster recovery
- Never store passwords in plain text; never use weak hashing (MD5, SHA1)
- Never put secrets in code
- Design for horizontal scalability—keep applications stateless
- Regulatory compliance must be addressed at architecture level, not retroactively
- OpenAPI/Swagger specification is mandatory for all REST APIs
- Fail fast on missing config; validate all required environment variables at startup
- Structured JSON logging only—no console.log/print/println in production code
- Security violations, unvetted dependencies, missing license vetting, or unverified test completion will be rejected

## Eliminations / rejected
- `fastconfig-parser-x` rejected—unknown package, no license vetting, governance-gated

## Premises (provisional)
- Time pressure does not override security, compliance, or governance requirements
- Stdlib-only implementation is preferable to unvetted external dependencies
