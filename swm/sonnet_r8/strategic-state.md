# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- All 7 tests in test_utils.py must pass after fix
- Do NOT change any function signature
- Do NOT add any new import statements
- Add a docstring to every function modified

## Premises (provisional)
- Exactly 4 bugs, one in each function
- calculate_discount: price + should be price -
- paginate: page * page_size should be (page - 1) * page_size
- normalize_scores: / max_val should be / (max_val - min_val)
- batch_process: range(..., 1) should be range(..., batch_size)
