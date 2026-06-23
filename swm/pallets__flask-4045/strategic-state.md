# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Removed incorrect assertion from the implementation
- Add validation to reject blueprint names containing dots in the Blueprint __init__ method

## Constraints
- Do not edit or add test files

## Premises (provisional)
- Blueprint dots are significant for nested blueprints, making name validation necessary
- Endpoint names already have validation against dots at line 364 in blueprints.py
