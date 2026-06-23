# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Fixed xarray/core/dataarray.py:1964 in to_unstacked_dataset by adding .drop(dim, errors='ignore') after squeeze to remove retained scalar coordinate

## Constraints
- to_unstacked_dataset must support roundtrip stacking/unstacking for single-dimension variables without raising MergeError

## Premises (provisional)
- Single-dimension variables retain the stacked coordinate as a scalar after selection by MultiIndex level, causing merge conflicts
