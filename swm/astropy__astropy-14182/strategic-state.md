# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Modified RST.__init__() to accept header_rows=None parameter and forward it to parent FixedWidth class

## Constraints
- RestructuredText (RST) format must support header_rows parameter for flexible documentation generation
- RST class __init__() overrides parent without accepting keyword arguments, causing TypeError when header_rows is passed

## Premises (provisional)
- Parent FixedWidth class properly handles header_rows parameter when provided to __init__()
