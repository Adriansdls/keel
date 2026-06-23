# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Add a mode parameter to flask.Config.from_file() to allow binary mode, enabling simple expressions like app.config.from_file('config.toml', tomllib.load, mode='b')

## Constraints
- tomllib.load() requires files opened in binary mode, not text mode
- flask.Config.from_file() currently opens files in text mode

## Eliminations / rejected
- Verbose workaround exists (using open() with binary mode + from_mapping()), but should be replaced with simpler mode parameter

## Premises (provisional)
- Fix is complete and working
