# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- All core fixes have been verified working via test execution (HueMapping._lookup_single, pandas deprecated options, DataFrame.iteritems, matplotlib colormap registration)
- Fix location is HueMapping._lookup_single() in seaborn/_oldcore.py:146-165
- Matplotlib >= 3.5 compatibility: use matplotlib.colormaps.register() with fallback to old API for earlier versions
- For categorical mappings, return transparent color (0, 0, 0, 0) when a hue value is not in the lookup table, avoiding np.isnan() call on string values
- Update deprecated pandas option mode.use_inf_as_null to mode.use_inf_as_na across 3 files
- Add matplotlib >= 3.5 compatibility for colormap registration

## Constraints
- Cannot edit or add test files

## Premises (provisional)
- test_share_xy has a pre-existing pytest API incompatibility unrelated to the current changes
- np.isnan() does not support categorical string values and cannot safely coerce them
- The desired behavior when hue_order is a subset is to exclude (not plot) values not in the order list
