# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Add early return for empty inputs: if len(y) == 0, return np.array([], dtype=np.int64)

## Constraints
- Cannot run full test suite due to environment limitations: Cython .pyx to .so compilation incompatible with current setuptools/numpy/Python 3.12; verification limited to code inspection and system sklearn testing
- Must not edit or add test files
- Empty list transformation should return empty array consistently regardless of class dtype

## Premises (provisional)
- column_or_1d converts empty sequences to empty float64 arrays by default
- np.searchsorted fails when casting float64 arrays to string class dtypes
