# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Add a Domain column to the routes output showing full domain for each route
- Domain is constructed as {subdomain}.{SERVER_NAME} for subdomain routes, or just {SERVER_NAME} for non-subdomain routes
- Only show Domain column when SERVER_NAME is configured, to maintain backward compatibility
- Modified src/flask/cli.py in the routes_command function to implement the feature

## Constraints
- Flask routes command currently doesn't display which routes are assigned to which subdomain
- SERVER_NAME configured as 'test.local' with subdomains: admin.test.local, test.test.local, test.local
- Do NOT edit or add test files
