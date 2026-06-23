# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Support outer join semantics when concatenating datasets with different variables (matching pandas.concat behavior)
- Fill missing data variables with NaN instead of raising errors
- Promote integer types to float64 to accommodate NaN
- Preserve validation of structural coordinates (dimension-related coordinates still raise errors if missing)

## Eliminations / rejected
- Rejected requiring users to create dummy variables filled with NaN
- Rejected dropping mismatched variables as a solution

## Premises (provisional)
- Test results claimed as passing without evidence shown
