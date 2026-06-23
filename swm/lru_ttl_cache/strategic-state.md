# Strategic State

_Durable world-model — auto-maintained by SWM, re-injected each turn._

## Decisions
- Expiration is based on put-time only, not on last access/get time
- Expired entries are cleaned lazily (on access), not proactively
- Use OrderedDict to track access order with first item as LRU
- Store each entry as (value, put_time) tuple for TTL calculation

## Constraints
- LRUCache constructor takes capacity and ttl_seconds parameters
- At most `capacity` live entries allowed; LRU entry evicted when full
- Entries expire `ttl_seconds` after their last put() call
- Both get() and put() operations count as 'use' for recency tracking

## Premises (provisional)
- Implementation is complete and verified with 15 passing tests
