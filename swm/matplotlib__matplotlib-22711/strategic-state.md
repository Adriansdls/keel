# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Removed lines 906 and 912 from RangeSlider.set_val() that assigned to xy[4], which was out of bounds for the 4-vertex polygon

## Constraints
- Fixing RangeSlider widget initialization bug in matplotlib where valinit parameter causes IndexError

## Premises (provisional)
- Matplotlib polygons created by axvspan/axhspan automatically close with exactly 4 vertices (indices 0-3)
