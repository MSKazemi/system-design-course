# 04 — Exercises

Lesson: [course/01-foundations/04-caching.md](../course/01-foundations/04-caching.md) · Lab:
[labs/04-caching](../labs/04-caching/README.md) · Bracketed numbers such as [1] refer to the lesson's References.

## 1. [Core] Required hit ratio

Lumen's search-suggestion API receives 30,000 requests/s. The backing service safely handles 2,000 requests/s and
you want 25 % headroom on it. What is the minimum cache hit ratio? What happens to the p99 if the hit ratio is exactly
that value and a miss takes 80 ms while a hit takes 2 ms?

<details><summary>Answer</summary>

Headroom of 25 % leaves a miss budget of 0.75 × 2,000 = 1,500 requests/s. `(1 − h) × 30,000 ≤ 1,500` → `h ≥ 95 %`.

At h = 95 %, 5 % of requests are misses. The p99 is therefore inside the miss population: about 80 ms (plus whatever
queueing the backend adds at 75 % utilisation). The mean is `0.95 × 2 + 0.05 × 80 = 5.9 ms`, which looks great on a
dashboard and hides the tail. To bring the p99 down you need either h > 99 % for the traffic that matters, or a faster
miss path (cheaper query, precomputation, stale-while-revalidate so users rarely wait for a miss). Acceptable variant:
compute p99 as "slightly above 80 ms" to account for queueing.
</details>

## 2. [Core] Pick the write pattern

For each, choose cache-aside, write-through, write-back or write-around, and justify: (a) per-video view counters;
(b) user profile shown on every page; (c) uploaded PDF files, rarely re-read in the first hour; (d) account balance.

<details><summary>Answer</summary>

(a) **Write-back**: increments are absorbed in the cache (e.g. Redis `INCR`) and flushed periodically; losing a few
seconds of views on a cache crash is acceptable, and per-increment DB writes would be wasteful.
(b) **Cache-aside with delete-on-write** (or write-through if a just-edited profile must be served from cache): read
heavy, small, tolerates seconds of staleness for *other* viewers; the editor should read their own profile from the
source (read-your-writes).
(c) **Write-around**: write to object storage/DB only; filling the cache with data nobody reads soon evicts useful
entries.
(d) **No write caching**: write to the database transactionally. Reads may use a cache for display, but every decision
(can this payment proceed?) reads the source. Write-back here can lose acknowledged money movements.
</details>

## 3. [Deep] The stale-set race

Write out the interleaving that leaves a stale value in a cache-aside cache despite delete-on-write. Then show how
(a) a lease token and (b) a version check each prevent it. Which of the two requires the database to expose something?

<details><summary>Answer</summary>

Reader: GET k → miss; reads DB (v = 10); pauses. Writer: UPDATE DB (v = 20); DEL k. Reader: SET k = 10. Cache holds 10
until TTL while DB holds 20.

(a) **Lease**: on the miss, the cache issues token T to the reader and remembers it for k. The writer's DEL invalidates
outstanding tokens for k. The reader's later SET presents T, which is no longer valid, so the set is rejected; the next
read misses and loads 20. This needs nothing from the database (Facebook's leases [1]; lab L04 implements it with a
Lua script).

(b) **Version check**: rows carry a version (a version column or the commit LSN), and the cache only accepts a set
whose version is newer than the version it already knows for that key (compare-and-set in a Lua script). A plain DEL
erases that knowledge, so the writer must instead leave a small **tombstone** carrying the new version
(`SET k {version: 2, deleted: true}`). The reader's later set carries version 1 and is rejected; the next read sees the
tombstone, treats it as a miss and loads version 2. This requires the **database** to expose versions. Both are valid; leases are simpler to retrofit.
</details>

## 4. [Deep] XFetch by hand

A cached report took Δ = 2 s to compute and expires at t = 600 s. With β = 1, what is the probability that a single
read at t = 596 s triggers an early recomputation? At t = 599 s? If 50 reads/s arrive, roughly when will the first early
recomputation happen?

<details><summary>Answer</summary>

A read at time `t` recomputes if `t − Δβ ln(U) ≥ expiry`, i.e. `−ln(U) ≥ (expiry − t)/(Δβ)`, i.e. `U ≤ e^{−(expiry−t)/(Δβ)}`.
So `P = e^{−(expiry − t)/(Δβ)}`.

- t = 596: gap 4 s, P = e^{−2} ≈ 13.5 %.
- t = 599: gap 1 s, P = e^{−0.5} ≈ 60.7 %.

At 50 reads/s, the expected number of triggers between gap g and expiry is ∫ 50 e^{−g/2} dg; setting the cumulative
expectation to 1: `50 × 2 × e^{−g/2} = 1` → `e^{−g/2} = 0.01` → g ≈ 9.2 s. So the first early refresh happens around
9 s before expiry, comfortably more than the 2 s recompute time, so readers keep getting hits. Vattani et al. show the
expected early-expiration gap scales with Δβ·log(n) [2]. Note that a few more readers may also trigger during the 2 s
refresh; pair with a lock if duplicates are expensive.
</details>

## 5. [Core] Negative caching

An attacker requests `/products/<random id>` at 5,000 requests/s; none of the ids exist. Describe what happens with
plain cache-aside and two mitigations, with one risk of each.

<details><summary>Answer</summary>

Every request misses, queries the DB, finds nothing, caches nothing: 5,000 DB queries/s bypassing the cache
(penetration).

1. **Negative cache** entries (`product:123 → NOT_FOUND`, TTL 30–60 s): the risk is that a product created just after
   being looked up stays "not found" until the tombstone expires; delete the tombstone on create, keep TTLs short.
   Random ids rarely repeat, so negative caching alone may not help against *random* ids.
2. **Bloom filter of existing ids** checked before the cache: random ids are rejected with ~1 % false positives at
   10 bits/id; the risk is staleness of the filter (must be updated on insert; deletions need a counting filter or
   periodic rebuild).
3. Also valid: per-client rate limiting ([SYSDESIGN-10](../course/01-foundations/10-apis-communication.md)) and input
   validation (ids outside the allocated range).
</details>

## 6. [Core] CDN headers

Write the `Cache-Control` header for: (a) a public product page that may be 60 s stale at the CDN and 0 s in browsers;
(b) a logged-in dashboard; (c) a fingerprinted JS bundle `app.3f2a9c.js`; (d) a public page that should stay up for 10
minutes even if the origin is down.

<details><summary>Answer</summary>

(a) `Cache-Control: public, max-age=0, s-maxage=60` (browsers revalidate, CDN keeps 60 s). Optionally
`stale-while-revalidate=30` for smoother refreshes, accepting up to 90 s worst-case staleness, which would break a
strict 60 s promise unless `s-maxage` is lowered to 30.
(b) `Cache-Control: private, no-store` if it contains sensitive data; `private, max-age=0` (with `ETag`) if browser
revalidation is acceptable. Never cache at the CDN.
(c) `Cache-Control: public, max-age=31536000, immutable`: the fingerprint changes with content, so versioned keys
replace invalidation.
(d) `Cache-Control: public, s-maxage=60, stale-if-error=600` (RFC 5861).
</details>

## 7. [Deep] Hot key

One Redis shard holds `product:launch-day`, which receives 120,000 GET/s during a launch, more than one Redis process
serves comfortably for that value size in your measurements. Propose three mitigations and the consistency cost of
each.

<details><summary>Answer</summary>

1. **In-process L1 cache** in each app instance with a 1–2 s TTL: the shard sees ~1 request per instance per TTL.
   Cost: up to 2 s of staleness, different instances may briefly disagree.
2. **Replicate the key** as `product:launch-day#0..#15` across shards; readers pick one at random; writers delete all
   16. Cost: a write must touch 16 keys; a reader can see an old copy until all deletes land.
3. **Read replicas** of the shard (Redis replication) and spread reads. Cost: replica lag.
Also valid: serve the launch page from the CDN with `s-maxage` of a few seconds, making the cache tier irrelevant for
anonymous traffic.
</details>

## 8. [Interview] Facebook-style invalidation

Your interviewer asks: "Many services write to the products table. How do you make sure the cache is invalidated on
every write?" Answer in five sentences.

<details><summary>Answer</summary>

Do not rely on every writer remembering to delete the key. Tail the database's change stream (logical replication /
CDC, e.g. Debezium) and have an invalidation service translate each committed row change into cache deletes, as
Facebook's mcsqueal daemons did from the MySQL commit log [1]. Deletes are idempotent, so at-least-once delivery from
the stream is fine, and they arrive in commit order. Keep TTLs as a safety net for anything the pipeline misses, and
monitor its lag as an SLI. For the stale-set race on refill, add leases or versioned sets.
</details>

## 9. [Frontier] Prefix caching

Two Lumen features call the same model. Feature A sends `[system prompt (2,000 tokens)][user question]`. Feature B
sends `[user name and date][system prompt (2,000 tokens)][user question]`. Which benefits from vLLM's automatic prefix
caching, and why? How would you fix the other, and what isolation concern applies across tenants?

<details><summary>Answer</summary>

vLLM hashes each full KV block together with its parent block's hash [16], so a block is reused only if *every*
preceding token matches. Feature A's 2,000-token system prompt is an identical prefix across users → its blocks are
reused and prefill for those tokens is skipped. Feature B starts with per-user tokens, so the system-prompt blocks have
different parent hashes and never match. Fix: move variable content after the stable part. Isolation: shared prefix
blocks across tenants can leak information through timing (a cache hit is faster); vLLM supports a per-request
`cache_salt` mixed into the first block's hash so only requests with the same salt share blocks [16]. Use one salt per
tenant.
</details>

## 10. [Lab] Read the stampede table

Run `docker compose -p sd-04 run --rm bench stampede`. Explain the `recomputes`, `max parallel` and `p99` columns for
the three strategies. Then rerun with `--beta 3` and explain what changes for XFetch.

<details><summary>Answer</summary>

Expected pattern (your numbers will differ): **naive** shows many recomputations per TTL and `max parallel` well above
1, because every client arriving during the recompute window misses and recomputes. **lock** shows about one recompute
per TTL and `max parallel` = 1, but the p99 rises toward the recompute cost because waiting clients block. **xfetch**
shows few hard misses (the value is refreshed before it expires), so p50 and p99 stay near hit latency; recomputations
per TTL can exceed 1 at high request rates, because several readers may draw an early refresh during the same recompute
window. With `--beta 3` early refreshes happen earlier (larger head start), hard misses drop further, and recomputation
count rises slightly. The combination XFetch + lock gives early *and* single refreshes.
</details>
