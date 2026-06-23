# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- A fix for the *args/**kwargs duplication bug in autodoc has been implemented and verified to pass typehints description tests

## Constraints
- Do not edit test files when fixing the autodoc bug

## Premises (provisional)
- *args and **kwargs parameters are duplicated in autodoc output when using autodoc_typehints='description' if the method docstring documents these parameters
