# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Tool named wc_tool.py

## Constraints
- Reads from file path given as last argument, or from stdin if no path
- Prints three numbers separated by single spaces: line count, word count, byte count (default with no flags)
- Flags -l, -w, -c restrict output to lines, words, bytes respectively
- When multiple flags given, output appears in fixed order: -l, -w, -c
- Results printed to stdout
