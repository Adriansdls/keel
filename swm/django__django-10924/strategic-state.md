# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- FilePathField path parameter must support callables to allow runtime path resolution instead of migration-time evaluation

## Premises (provisional)
- Current behavior: os.path.join() in path parameter is evaluated at makemigrations time, hardcoding the path and breaking on other machines
- Use case: support different file paths across dev/production environments without manual migration editing
