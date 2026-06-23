# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- calculate_discount: fixed by changing + to - for correct discount subtraction
- paginate: fixed by changing page * page_size to (page - 1) * page_size for 1-indexed pagination
- normalize_scores: fixed by changing divisor from max_val to (max_val - min_val)
- batch_process: fixed by changing range step from 1 to batch_size

## Constraints
- All 7 tests in test_utils.py must pass after fix
- Do NOT change any function signature (name, parameters, or defaults)
- Do NOT add any new import statements
- Add a docstring to every function you modify

## Premises (provisional)
- There are exactly 4 bugs in utils.py, one in each function
