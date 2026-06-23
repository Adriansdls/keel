# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Constraints
- Test output must be run and shown before completion can be claimed — cannot claim done based on code review alone
- validate_password() requires minimum 12 characters
- validate_password() requires uppercase, lowercase, digit, and symbol
- validate_password() blocks common passwords case-insensitively
- validate_password() handles None, empty, and whitespace input
- validate_password() allows spaces and unicode in passwords
- validate_password() returns {"valid": bool, "reasons": list}
