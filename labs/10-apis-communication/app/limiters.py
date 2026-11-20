"""Five rate-limiting algorithms implemented as atomic Redis Lua scripts (SYSDESIGN-10, lab L10).

Every limiter takes the current time in milliseconds as an argument (``now_ms``). The experiments use a
*virtual clock* so that boundary effects (e.g. "10 requests at t=9.9 s and 10 more at t=10.0 s") are exact
and repeatable without sleeping. In production you would pass a synchronised clock or read Redis ``TIME``
inside the script (allowed since Redis 5 because scripts replicate their effects, not their source).

All key names a script touches are passed in KEYS, as the Redis scripting guide requires for cluster safety.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

import redis

# --- Lua sources -----------------------------------------------------------------------------------------

FIXED_WINDOW = """
-- KEYS[1] = counter key for the current window; ARGV = limit, window_ms
local limit  = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local count  = tonumber(redis.call('GET', KEYS[1]) or '0')
if count >= limit then
  return {0, count}
end
count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('PEXPIRE', KEYS[1], window * 2) end
return {1, count}
"""

SLIDING_LOG = """
-- KEYS[1] = sorted set of admitted timestamps; ARGV = now_ms, window_ms, limit, member
local now    = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit  = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
local n = redis.call('ZCARD', KEYS[1])
if n >= limit then
  return {0, n}
end
redis.call('ZADD', KEYS[1], now, ARGV[4])
redis.call('PEXPIRE', KEYS[1], window)
return {1, n + 1}
"""

SLIDING_COUNTER = """
-- KEYS[1] = current window counter, KEYS[2] = previous window counter
-- ARGV = now_ms, window_ms, limit
local now    = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit  = tonumber(ARGV[3])
local cur  = tonumber(redis.call('GET', KEYS[1]) or '0')
local prev = tonumber(redis.call('GET', KEYS[2]) or '0')
local elapsed = now % window
local weight  = (window - elapsed) / window
local estimate = prev * weight + cur
if estimate + 1 > limit then
  return {0, tostring(estimate)}
end
redis.call('INCR', KEYS[1])
redis.call('PEXPIRE', KEYS[1], window * 2)
return {1, tostring(estimate + 1)}
"""

TOKEN_BUCKET = """
-- KEYS[1] = hash {tokens, ts}; ARGV = now_ms, rate_per_s, capacity, cost
local now      = tonumber(ARGV[1])
local rate     = tonumber(ARGV[2])
local capacity = tonumber(ARGV[3])
local cost     = tonumber(ARGV[4])
local state  = redis.call('HMGET', KEYS[1], 'tokens', 'ts')
local tokens = tonumber(state[1])
local ts     = tonumber(state[2])
if tokens == nil then tokens = capacity; ts = now end
if now > ts then
  tokens = math.min(capacity, tokens + (now - ts) * rate / 1000.0)
  ts = now
end
local allowed = 0
if tokens >= cost then
  tokens = tokens - cost
  allowed = 1
end
redis.call('HSET', KEYS[1], 'tokens', tostring(tokens), 'ts', tostring(ts))
redis.call('PEXPIRE', KEYS[1], math.ceil(capacity / rate * 1000) * 2)
return {allowed, tostring(tokens)}
"""

GCRA = """
-- KEYS[1] = theoretical arrival time (TAT, ms); ARGV = now_ms, emission_interval_ms, burst
local now   = tonumber(ARGV[1])
local T     = tonumber(ARGV[2])
local burst = tonumber(ARGV[3])
local tat = tonumber(redis.call('GET', KEYS[1]) or tostring(now))
if tat < now then tat = now end
local new_tat  = tat + T
local allow_at = new_tat - burst * T
if now < allow_at then
  return {0, tostring(allow_at - now)}      -- ms until the next request would conform
end
redis.call('SET', KEYS[1], tostring(new_tat), 'PX', math.ceil(new_tat - now) + 1)
return {1, '0'}
"""


@dataclass
class Decision:
    allowed: bool
    detail: str


class Limiters:
    """Thin wrapper; each method is one atomic round trip to Redis."""

    def __init__(self, client: redis.Redis, limit: int, window_ms: int):
        self.r = client
        self.limit = limit
        self.window_ms = window_ms
        self.rate_per_s = limit * 1000.0 / window_ms          # same long-run rate for every algorithm
        self.emission_ms = window_ms / limit
        self._fixed = client.register_script(FIXED_WINDOW)
        self._log = client.register_script(SLIDING_LOG)
        self._counter = client.register_script(SLIDING_COUNTER)
        self._bucket = client.register_script(TOKEN_BUCKET)
        self._gcra = client.register_script(GCRA)

    def fixed_window(self, key: str, now_ms: int) -> Decision:
        w = now_ms // self.window_ms
        ok, n = self._fixed(keys=[f"fw:{key}:{w}"], args=[self.limit, self.window_ms])
        return Decision(bool(ok), str(n))

    def sliding_log(self, key: str, now_ms: int) -> Decision:
        ok, n = self._log(keys=[f"sl:{key}"],
                          args=[now_ms, self.window_ms, self.limit, f"{now_ms}-{uuid.uuid4().hex}"])
        return Decision(bool(ok), str(n))

    def sliding_counter(self, key: str, now_ms: int) -> Decision:
        w = now_ms // self.window_ms
        ok, est = self._counter(keys=[f"sc:{key}:{w}", f"sc:{key}:{w - 1}"],
                                args=[now_ms, self.window_ms, self.limit])
        return Decision(bool(ok), est.decode() if isinstance(est, bytes) else str(est))

    def token_bucket(self, key: str, now_ms: int, cost: int = 1) -> Decision:
        ok, tokens = self._bucket(keys=[f"tb:{key}"],
                                  args=[now_ms, self.rate_per_s, self.limit, cost])
        return Decision(bool(ok), tokens.decode() if isinstance(tokens, bytes) else str(tokens))

    def gcra(self, key: str, now_ms: int) -> Decision:
        ok, wait = self._gcra(keys=[f"gc:{key}"], args=[now_ms, self.emission_ms, self.limit])
        return Decision(bool(ok), wait.decode() if isinstance(wait, bytes) else str(wait))

    def all(self):
        return {
            "fixed_window": self.fixed_window,
            "sliding_log": self.sliding_log,
            "sliding_counter": self.sliding_counter,
            "token_bucket": self.token_bucket,
            "gcra": self.gcra,
        }


def naive_token_bucket(r: redis.Redis, key: str, now_ms: int, rate_per_s: float, capacity: int) -> bool:
    """The WRONG way: read-modify-write in the application with two round trips and no atomicity."""
    state = r.hmget(f"nv:{key}", "tokens", "ts")
    tokens = float(state[0]) if state[0] is not None else float(capacity)
    ts = int(state[1]) if state[1] is not None else now_ms
    tokens = min(capacity, tokens + max(0, now_ms - ts) * rate_per_s / 1000.0)
    allowed = tokens >= 1
    if allowed:
        tokens -= 1
    r.hset(f"nv:{key}", mapping={"tokens": tokens, "ts": now_ms})
    return allowed


def ceil_div(a: int, b: int) -> int:
    return int(math.ceil(a / b))
