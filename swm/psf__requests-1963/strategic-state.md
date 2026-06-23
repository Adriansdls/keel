# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Preserve method changes across redirect iterations by tracking the modified request separately using a previous_request variable, rather than always copying the original request

## Constraints
- HTTP 307 Temporary Redirect must preserve the request method; 303 See Other/301/302 must change it per HTTP standards

## Premises (provisional)
- The critical bug scenario is a redirect chain: POST request receives 303 See Other (correctly changes to GET), then 307 Temporary Redirect (should preserve GET but was reverting to POST)
