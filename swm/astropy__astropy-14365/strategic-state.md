# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Fix the QDP parser case-sensitivity issue by updating the regex pattern to accept case-insensitive commands

## Constraints
- Do not edit or add test files

## Eliminations / rejected
- Output generation code at lines 460 and 463 correctly writes uppercase and should not be modified

## Premises (provisional)
- QDP format itself is case-insensitive for commands, but astropy's parser was incorrectly enforcing uppercase
