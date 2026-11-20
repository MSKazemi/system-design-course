# 04 — Caching everywhere (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/04-caching.md](../course/01-foundations/04-caching.md)

## Slide 1 — The requirement

- 50,000 reads/s; the database saturates near 5,000 queries/s
- p99 < 50 ms, and a price never more than 60 s stale
- A 10× capacity gap, a tail-latency target, a freshness bound

**Visual:** Lumen product page → app → database bar chart (demand 50k vs capacity 5k). Icons: `arch-users`, `arch-database`, `ops-latency`.

**Speaker notes:** Every caching design trades these three forces. We will size the cache from the gap, protect the
tail, and keep the copy honest.

## Slide 2 — Caches live at every layer

- Browser, CDN edge, reverse proxy, in-process L1, distributed cache, DB buffer pool
- Lower layers are coherent by construction; upper layers are copies
- Each copy needs an owner, a key and an invalidation story

**Visual:** Left-to-right request path with a cache box at each hop. Icons: `client-chrome`, `arch-cdn`, `arch-reverse-proxy`, `arch-cache`, `cache-redis`, `arch-database`.

**Speaker notes:** The buffer pool is the database, so it is never stale. Everything above it is a copy that someone
must invalidate.

## Slide 3 — The arithmetic of a hit ratio

- Backend load = (1 − h) × λ; required h ≥ 95 % for 50 % headroom
- Mean latency = h·t_hit + (1 − h)·t_miss
- If more than 1 % of requests miss, the p99 is a miss

**Visual:** Two latency histograms: mean moves left, p99 marker stays on the miss hump.

**Speaker notes:** This is the most common misunderstanding about caches. A 95 % hit ratio transforms the mean and
does nothing for the p99.

## Slide 4 — Five patterns

- Cache-aside: app reads cache, fills on miss, deletes on write
- Read-through and write-through: the cache library talks to the DB
- Write-back: fast, but acknowledged writes can be lost
- Write-around: skip the cache for write-once data

**Visual:** 5-row table, cache-aside highlighted. Icons: `arch-cache`, `arch-database`.

**Speaker notes:** Cache-aside is the default because a dead cache makes the system slower, not wrong. Facebook deletes
rather than updates because deletes are idempotent.

## Slide 5 — TTLs and eviction

- TTL = freshness budget and safety net; add jitter against mass expiry
- LRU (recency), LFU (frequency), ARC (adaptive), W-TinyLFU (admission), SIEVE/S3-FIFO (quick demotion)
- Eviction decides who leaves; admission decides who gets in

**Visual:** Timeline of keys with TTL bars; a scan wiping an LRU list vs an LFU list keeping hot keys. Icon: `pattern-eviction`.

**Speaker notes:** Most LRU problems in production are admission problems: a crawler or batch job floods the cache with
keys that will never be read again.

## Slide 6 — The stale-set race

- Reader misses and reads 10; writer updates to 20 and deletes; reader sets 10
- Stale until TTL: delete-on-write did not help
- Fixes: short TTL, leases (token invalidated by delete), versioned sets, invalidate from the commit log

**Visual:** Sequence diagram with four lifelines (reader, cache, DB, writer). Icons: `pattern-cache-invalidation`, `arch-database`.

**Speaker notes:** Lab L04 reproduces this exact interleaving and shows the lease rejecting the stale set.

## Slide 7 — Stampedes

- A hot key expires; every request in the refill window hits the database
- Locks/leases: one refill, others wait or get stale data
- Coalescing and stale-while-revalidate
- Facebook leases: peak DB query rate 17K/s → 1.3K/s on herd-prone keys

**Visual:** Spike chart aligned with TTL expiries. Icons: `arch-database`, `ops-alert`.

**Speaker notes:** The lease mechanism also throttles: one token per key every 10 seconds, other clients wait briefly
and usually find the value already set.

## Slide 8 — XFetch: refresh before expiry

- Recompute if now − Δ·β·ln(rand()) ≥ expiry
- Probability rises as expiry nears; no coordination needed
- Optimal in Vattani et al.'s model (VLDB 2015)
- Lab: zero hard misses; a few overlapping refreshes at high rates

**Visual:** Probability curve rising toward the expiry line; one reader's dot crossing it early. Icon: `ops-clock`.

**Speaker notes:** Δ is how long the last recomputation took; β above 1 refreshes earlier. Combine with a lock when
duplicate recomputation is expensive.

## Slide 9 — Penetration, negative caching, hot keys

- Absent keys bypass cache-aside: cache "not found" briefly, or a Bloom filter
- Never cache errors for long
- Hot key: L1 cache, replicate the key, read replicas of the shard

**Visual:** Random-id attacker arrows passing the cache to the DB; a Bloom filter gate. Icons: `security-ddos`, `arch-cache`.

**Speaker notes:** Negative caching is old: DNS standardised it in RFC 2308.

## Slide 10 — CDN caching and the cache key

- `s-maxage`, `private`, `no-store`, `stale-while-revalidate`, `stale-if-error`
- The key is the design: too broad leaks or poisons; too narrow kills the hit ratio
- Surrogate keys for purge; origin shield for miss collapse

**Visual:** Cache key builder: method + host + path + normalised query + selected headers. Icons: `arch-cdn`, `network-fastly`, `network-cloudflare`.

**Speaker notes:** Every CDN mistake is either a correctness bug (wrong user's page) or a hit-ratio bug (`Vary:
User-Agent`).

## Slide 11 — The cache that became the database

- After a year at 95 % hits, the DB is sized for 5 % of reads
- Cold restart = 20× load on the database
- Warm from a peer cache, roll restarts, admission control on the DB

**Visual:** Before/after load bars on the DB when the cache cluster restarts. Icons: `cache-memcached`, `ops-incident`.

**Speaker notes:** Facebook describes cold-cluster warmup from a warm cluster's caches. Load-test with the cache
flushed.

## Slide 12 — Frontier: KV cache, prefix caching, semantic caching

- vLLM hashes each KV block with its parent's hash; LRU eviction; per-tenant salt
- Put the stable prompt prefix first
- Semantic caching: the similarity threshold is a correctness knob

**Visual:** Two prompts sharing prefix blocks (same colour plus pattern), diverging at the user question. Icons: `domain-ai`, `arch-cache`.

**Speaker notes:** The classical questions return on the GPU: cache key, eviction, isolation. Details in units 22 and
26.

## Slide 13 — Interview wrap

- CLARIFY freshness → QUANTIFY hit ratio → SKETCH cache-aside + TTL
- DEEPEN stampede or stale set → STRESS cold cache, hot key
- WRAP: eventual consistency bounded by TTL, alert on hit ratio by keyspace

**Visual:** The six-step framework strip with caching prompts under each step.

**Speaker notes:** Red flags: no TTL, write-back for money, no answer to "what if the cache is empty?".
