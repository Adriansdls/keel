# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Socket errors that occur during response content reading must be caught and wrapped as requests.exceptions.ConnectionError, not propagated as raw socket.error
- Exception handling pattern should follow the existing approach in adapters.py: catch socket.error and re-raise as ConnectionError(e, request=self.request)

## Constraints
- collections.MutableMapping and collections.Mapping must be imported from collections.abc for Python 3.12 compatibility (cookies.py, sessions.py, structures.py, utils.py, urllib3/_collections.py)
- Do NOT edit or add test files when fixing this bug

## Premises (provisional)
- Users expect requests exceptions when using the requests library, not raw socket errors from the underlying layers
