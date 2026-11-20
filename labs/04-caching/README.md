# L04 — Cache in front of Postgres

Lab for [SYSDESIGN-04 Caching everywhere](../../course/01-foundations/04-caching.md).

## Goal

See, on your own machine, the four caching behaviours the lesson argues from first principles: what a hit ratio does
to mean and tail latency, why LFU beats LRU when one-touch traffic pollutes the cache, what a stampede on one hot key
looks like (and how a lock and XFetch change it), and the stale-set race that delete-on-write does not prevent.

## What you will observe

- Cache-aside on a Zipf(0.99) workload: database calls fall several-fold, median latency drops to the hit latency,
  and the **p99 stays at the miss latency** while more than 1 % of requests miss.
- `allkeys-lfu` keeping a higher hit ratio than `allkeys-lru` once half the traffic is one-touch writes.
- One hot key expiring under 50 concurrent clients: dozens of duplicate recomputations per expiry (naive), exactly
  one but with blocked waiters (lock), or refreshes before expiry with almost no misses (XFetch).
- The stale-set race leaving the cache wrong until its TTL, and a lease token rejecting the stale set.

## Prerequisites

- Docker Engine with Compose v2+ (tested: Docker 29.10.0, Compose v5.8.0).
- About 1 GB of free disk for images: `postgres:18.7-alpine`, `redis:8.10.3-alpine`, `python:3.15.2-slim` (plus
  `psycopg[binary]==3.3.9` and `redis==8.1.0` from PyPI at build time).
- Free localhost ports **10432** (Postgres) and **10479** (Redis). Nothing else is exposed.

## Run

```bash
cd labs/04-caching
docker compose -p sd-04 up -d --build --wait        # db + cache, healthy
docker compose -p sd-04 run --rm bench all           # all four experiments, ~4 minutes
```

Each experiment can be run alone: `aside`, `policy`, `stampede`, `race`. `docker compose -p sd-04 run --rm bench
--help` lists the knobs (`--zipf`, `--threads`, `--ttl`, `--cost`, `--beta`, `--think`, `--policy-mem` …).

You can also poke at the services directly: `redis-cli -p 10479 INFO stats` or
`psql postgresql://lumen:lumen-lab-only@localhost:10432/catalog` (local lab credentials only).

## Experiments

1. **`aside`** — 20,000 requests from 16 threads, Zipf(0.99) over 100,000 product ids. The database call is a primary-key
   lookup plus a fixed 20 ms `pg_sleep` standing in for an expensive query (a labelled assumption in `init.sql`). One
   no-cache run, then three cache-aside runs with fresh request sequences (the cache keeps what earlier runs loaded).
2. **`policy`** — Redis capped at `maxmemory 3mb`, 20,000 keys with 300-byte values, 40,000 warm-up and 40,000 measured
   iterations; `allkeys-lru` vs `allkeys-lfu`, first with Zipf reads only, then with 50 % of iterations writing
   one-touch keys that are never read again (a crawler or export job).
3. **`stampede`** — one hot key, TTL 2 s, recomputation cost 100 ms, 50 clients for 20 s (about 10 expiries). Strategies:
   `naive` (every misser recomputes), `lock` (`SET NX PX` + re-check after acquiring), `xfetch` (probabilistic early
   expiration, Vattani et al. 2015, β = 1). The key is warmed first, so the run measures expiry, not the cold start.
4. **`race`** — a deterministic interleaving: the reader misses and reads the DB, sleeps 300 ms, the writer updates
   the DB and deletes the key, the reader sets its old copy. Then the same with a lease token checked by a Lua script.

Try next: `--zipf 1.2` (more skew, higher hit ratio), `--beta 3` for XFetch, `--policy-mem 2mb,6mb`, and
`--threads 4` to see how much of the latency is client-side contention.

## Expected results

Look for the pattern, not the exact numbers (which depend on CPU, load and Docker networking):

- `aside`: hit ratio rising run over run (the long tail of 100,000 items keeps it well below 100 % for a while);
  database calls dropping by roughly the miss ratio; p50 near the hit latency; **p99 roughly equal to the no-cache
  latency** (it is a miss).
- `policy`: LRU and LFU close on Zipf-only traffic; LFU clearly ahead with one-touch writes.
- `stampede`: naive with tens of recomputes per TTL and `max parallel` near the client count; lock with about 1 per
  TTL, `max parallel` 1 and a p99 near the recompute cost; xfetch with zero or near-zero hard misses, a p99 near hit
  latency, and a few overlapping early refreshes per TTL at this request rate.
- `race`: `STALE until TTL` for plain cache-aside, `REJECTED (lease invalidated) -> consistent` with the lease.

## Clean up

```bash
docker compose -p sd-04 --profile bench down -v
docker image rm sd-04-bench          # the locally built bench image
```

## Cost

€0: everything runs locally. No cloud resources.

## Test status

**runtime-tested** — 2026-11-19 (UTC), Ubuntu Linux (kernel 7.0.0-43-generic, x86_64, 12 cores), Docker 29.10.0,
Compose v5.8.0, PostgreSQL 18.7, Redis 8.10.3, Python 3.15.2. The host was heavily loaded by unrelated workloads during
the run (load average 17–58 on 12 cores), so absolute latencies are inflated and noisy. Observed output of
`bench all` (run time 3 min 54 s):

```text
# Experiment 1 (aside): Zipf 0.99, 100,000 ids, 20,000 requests, 16 threads, DB call = 20 ms + PK lookup
run                    hit ratio  DB calls   p50 ms   p99 ms    req/s
no cache                    0.0%     20000    20.77    23.40      762
cache-aside, run 1         61.3%      7743     1.52    35.14     1528
cache-aside, run 2         72.6%      5482     1.20    32.99     1967
cache-aside, run 3         77.2%      4563     1.18    34.44     2208

# Experiment 2 (policy): maxmemory 3mb, 20,000 keys
workload                       allkeys-lru allkeys-lfu
zipf only                            78.6%       80.6%
zipf + 50% one-touch writes          63.9%       70.5%

# Experiment 3 (stampede): TTL 2 s, recompute 100 ms, 50 clients, 20 s
strategy   requests recomputes  per TTL max parallel hard misses  p50 ms  p99 ms
naive         38555        450     45.0           50         450     1.2   105.2
lock          32186          9      0.9            1           9     2.9   204.5
xfetch        37341         40      4.0            8           0     1.5    33.8

# Experiment 4 (race)
[plain cache-aside] ... DB=20.00 cache=10.00 ttl=300s -> STALE until TTL
[lease] ... reader set REJECTED (lease invalidated); DB=20.00 cache=None -> consistent
```

During development an earlier version of the `lock` strategy recomputed about twice per expiry; the cause was a missing
re-check of the cache after acquiring the lock (a client that saw the miss acquired the lock just after the winner had
released it). The re-check is now in `bench.py`, and is worth copying into real code.

## Troubleshooting

- **Port already in use**: change the left side of `ports:` in `compose.yaml` or stop the conflicting service.
- **`bench` exits with connection errors**: run `docker compose -p sd-04 up -d --wait` first; `bench` waits for health
  checks only when started by `run`, not if the stack was torn down.
- **Very different latencies from the table**: expected on another machine. Rerun with `--threads 4`; check
  `uptime` for host load; compare ratios, not absolutes.
- **`policy` takes long**: lower `--policy-requests` (e.g. 20000); hit ratios get noisier.
