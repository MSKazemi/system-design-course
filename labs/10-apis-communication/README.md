# L10 — Rate limiter: five algorithms in Redis

Lab for [SYSDESIGN-10 — APIs & communication](../../course/01-foundations/10-apis-communication.md).

## Goal

Implement fixed window, sliding window log, sliding window counter, token bucket and GCRA as **atomic Redis Lua
scripts**, then fire scripted bursts at them and compare what each admits. Break a naive (non-atomic) limiter under
concurrency and see why atomicity is the whole game.

## What you will observe

1. **Boundary burst.** The fixed window admits twice its limit for requests straddling a window boundary; the other
   four do not.
2. **Sustained overload.** Long-run admitted rates converge to the limit; token bucket and GCRA additionally admit
   their initial burst; the sliding window counter admits slightly fewer because of its approximation.
3. **Refill after a burst.** Half a window after a burst, the token bucket and GCRA have refilled half their
   capacity, the sliding log and sliding counter still remember the burst, and the fixed window has reset.
4. **The race.** A token bucket implemented as read-then-write in Python admits far more than its capacity when 50
   clients arrive together; the same algorithm as one Lua script admits exactly its capacity.
5. **Memory.** The sliding window log stores one sorted-set member per admitted request; the others store a few
   bytes per key.

## Prerequisites

- Docker Engine with Compose v2+ (tested with Docker 29.10.0, Compose v5.8.0)
- Images (pinned; current stable tags checked against `docker-library/official-images` on 2026-11-19):
  - `redis:8.10.3-alpine`
  - `python:3.15.2-slim` + `redis` (redis-py) `8.1.0` from PyPI, installed at build time
- Free host port `11079` (bound to 127.0.0.1, optional, for `redis-cli` exploration)
- No GPU, no cloud account

Files:

| File | Purpose |
|---|---|
| `compose.yaml` | project `sd-10`: `redis` + `driver` |
| `app/limiters.py` | the five Lua scripts and a deliberately naive Python token bucket |
| `app/run_experiments.py` | the driver: experiments 1–5, prints tables |
| `app/Dockerfile` | driver image |

**Virtual clock.** Each script receives `now_ms` as an argument. Experiments 1, 2, 3 and 5 drive a *virtual* clock
so boundary effects are exact and the run takes seconds, not minutes. Experiment 4 uses real wall-clock time. In
production, pass a disciplined clock or read Redis `TIME` inside the script (see the lesson's Deep dive).

## Run

```bash
cd labs/10-apis-communication
docker compose -p sd-10 up --build --abort-on-container-exit --exit-code-from driver
```

Run a single experiment or change the policy:

```bash
docker compose -p sd-10 up -d redis
docker compose -p sd-10 run --rm driver python run_experiments.py --exp boundary --limit 100 --window-ms 60000
docker compose -p sd-10 run --rm driver python run_experiments.py --exp race --threads 200
```

Look at the keys while Redis is up (optional; needs `redis-cli` on the host):

```bash
redis-cli -p 11079 --scan --pattern 'sl:*' | head
redis-cli -p 11079 ZRANGE "$(redis-cli -p 11079 --scan --pattern 'sl:*' | head -1)" 0 -1 WITHSCORES | head
```

## Experiments

1. **Boundary burst** (`--exp boundary`). Policy *L* per *W* ms (default 10 per 10,000 ms). *L* requests at
   `window_end − 100 ms`, *L* more at the next `window_start`. Count admitted per algorithm.
2. **Sustained overload** (`--exp sustained`). Offer 2× the allowed rate, evenly spaced, for 60 virtual seconds.
3. **Bursts after idle** (`--exp burst`). 3*L* requests at one instant mid-window, then *L* more exactly half a window
   later.
4. **Race** (`--exp race`). 50 threads, each with its own Redis connection, pass a barrier and request one token from
   a fresh bucket of capacity *L*. Three trials each for the naive Python implementation and the Lua script.
5. **Memory** (`--exp memory`). After 1,000 admitted requests for one client (limit raised to 1,000), sum
   `MEMORY USAGE` over that client's keys.

Things to try next:

- `--limit 100 --window-ms 60000` and repeat Experiment 1: the fixed window still admits 2×.
- `--threads 200` for Experiment 4.
- Edit `TOKEN_BUCKET` to read `redis.call('TIME')` instead of `ARGV[1]` and rerun Experiment 4.
- Give the token bucket a variable `cost` (the lesson's LLM-token use case).

## Expected results

Look for these patterns (exact counts can differ by an off-by-one with other parameters):

- Exp 1: `fixed_window` total = 2 × limit; every other algorithm total = limit.
- Exp 2: `fixed_window` and `sliding_log` ≈ limit rate; `token_bucket` and `gcra` ≈ limit rate plus the initial burst;
  `sliding_counter` slightly below the limit rate.
- Exp 3: second burst — `fixed_window` admits a full limit (new window); `sliding_log` and `sliding_counter` admit 0;
  `token_bucket` and `gcra` admit about half the limit (refill).
- Exp 4: `naive_get_then_set` admits more than the capacity (verdict `OVER-ADMITTED`); `lua_token_bucket` admits
  exactly the capacity.
- Exp 5: `sliding_log` bytes are orders of magnitude larger than the others.

## Clean up

```bash
docker compose -p sd-10 down -v --rmi local
```

`--rmi local` removes the locally built driver image; the pulled `redis` and `python` images stay cached (remove with
`docker image rm redis:8.10.3-alpine python:3.15.2-slim` if you want the space back).

## Cost

€0. Everything runs locally; no cloud resources.

## Test status

**runtime-tested** — 2026-11-20 (run started 2026-11-20T00:18:48+01:00).

- Host: Ubuntu 24.04, Linux kernel 7.0.0-43-generic, x86_64
- Docker Engine 29.10.0, Docker Compose v5.8.0
- Images: `redis:8.10.3-alpine` (server reported `redis_version` 8.10.3), `python:3.15.2-slim`, redis-py 8.1.0
- Command: `docker compose -p sd-10 up --build --abort-on-container-exit --exit-code-from driver` → exit code 0;
  then `docker compose -p sd-10 down -v --rmi local`.

Observed output (default policy: 10 requests per 10,000 ms):

| Experiment | fixed_window | sliding_log | sliding_counter | token_bucket | gcra |
|---|---|---|---|---|---|
| 1. Boundary burst: admitted before + after boundary | 10 + 10 = **20** | 10 + 0 = 10 | 10 + 0 = 10 | 10 + 0 = 10 | 10 + 0 = 10 |
| 2. Sustained 2× overload, 60 s: admitted of 120 | 60 | 60 | 55 | 69 | 69 |
| 3. Second burst half a window later: admitted of 10 | 10 | 0 | 0 | 5 | 5 |
| 5. Memory after 1,000 admitted requests (bytes, `MEMORY USAGE`) | 46 | 109,850 | 46 | 72 | 42 |

Experiment 4 (50 concurrent clients, capacity 10, three trials each): `naive_get_then_set` admitted **50, 50, 50**
(`OVER-ADMITTED` every trial); `lua_token_bucket` admitted **10, 10, 10**.

A pre-test of the same scripts against a local `valkey/valkey:9.1.3-alpine` container (which reports Redis
compatibility version 7.2.4) produced the same admission counts; memory figures differed slightly (48 / 100,896 /
48 / 80 / 48 bytes). The race result depends on timing and may differ on other machines (see Troubleshooting).

## Troubleshooting

- **`port is already allocated` on 11079.** Another process uses the port. Remove the `ports:` block from
  `compose.yaml` (the driver talks to Redis over the compose network and does not need it).
- **Experiment 4 shows `ok` for the naive implementation.** The race depends on timing; increase `--threads`, or run
  on a busier machine. It never makes the naive version *correct* — only lucky.
- **`NOSCRIPT` errors.** redis-py's `register_script` reloads scripts automatically; if you call `EVALSHA` yourself
  after a Redis restart you must `SCRIPT LOAD` again (the script cache is not persisted).
- **Build hangs on `pip install`.** The driver image needs PyPI access at build time. Behind a proxy, set
  `HTTP_PROXY`/`HTTPS_PROXY` as build args.
