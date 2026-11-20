# C01 — Exercises

Lesson: [course/04-case-studies/C01-url-shortener-rate-limiter.md](../course/04-case-studies/C01-url-shortener-rate-limiter.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Key-space sizing

A shortener expects 400 M new links per year for 10 years. Using base-62 codes, what is the shortest code length that
keeps occupancy under 1 %? What is the expected number of insert attempts per link at the end of year 10 with random
codes?

<details><summary>Answer</summary>

Total links = 4 B. Length 6: 62^6 ≈ 5.7 × 10^10 → occupancy ≈ 7 % (too high). Length 7: 62^7 ≈ 3.52 × 10^12 →
occupancy ≈ 0.11 %. So **7 characters**. Expected attempts = 1 / (1 − p) ≈ 1 / 0.9989 ≈ 1.001 — about one retry per
900 creates. Acceptable variants: base-58 (drops look-alike characters 0/O/I/l) needs 58^7 ≈ 2.2 × 10^12, still under
1 % at 7 characters. The point is to show the occupancy calculation, not just "7 is enough".
</details>

## 2. [Core] Storage and bandwidth

Using the lesson's assumptions (500 B per stored link including overhead, 500 B per redirect response), compute
5-year primary storage and peak redirect egress for 50 M creates/month and 5 B redirects/month with a 5× peak factor.

<details><summary>Answer</summary>

Links = 50 M × 60 = 3 B → 3 B × 500 B = 1.5 TB (4.5 TB with 3 replicas). Redirects average = 5 B / 2.59 M s ≈ 1,930 /s →
peak ≈ 9,650 /s → × 500 B ≈ 4.8 MB/s ≈ 39 Mbit/s. Conclusion: neither storage nor bandwidth is the design driver; skew
and latency are. A candidate who proposes 64 shards here has not done the arithmetic.
</details>

## 3. [Core] Redirect status codes

A marketing customer asks for 301 redirects "because they are faster". List what they gain and what they lose, citing
RFC 9110 semantics, and propose a header set that gets most of the speed without the losses.

<details><summary>Answer</summary>

RFC 9110 makes 301 (and 308) heuristically cacheable, so browsers may cache them without explicit freshness; repeat
clicks then skip the shortener entirely. **Gain:** one fewer round trip for repeat visitors. **Lose:** click counts for
repeat visits, the ability to change the destination, and — critically — the ability to take down a link the victim
already visited. Proposal: `302 Found` with `Cache-Control: public, s-maxage=60, max-age=0`. The CDN caches for 60 s
(most of the speed: the redirect is answered at a nearby PoP), browsers revalidate every time (analytics and takedown
keep working). Note that `s-maxage=60` bounds only *passive* CDN staleness (plus any stale-while-revalidate window);
a 60 s takedown still needs an active CDN purge that bypasses stale-while-revalidate and stale-if-error. If the customer insists, offer 301 per link with documented trade-offs.
</details>

## 4. [Deep] Choosing a code generator

Compare "global counter → base 62" with "counter blocks → keyed permutation → base 62". Why does the second remove the
enumeration problem without adding collisions? What happens to unused IDs when a node crashes holding a block?

<details><summary>Answer</summary>

A keyed permutation is a bijection on [0, 62^7): distinct inputs map to distinct outputs, so no collisions, and without
the key consecutive counter values map to unrelated-looking codes, so an attacker cannot walk the space by
incrementing. (Format-preserving encryption or a small Feistel network over the 7-character domain are ways to build
it.) Unused IDs in a crashed node's block are simply never issued — gaps are harmless because nothing depends on
density. The cost is operating the block coordinator and protecting the permutation key; if the key leaks, codes become
predictable again, so rotate by starting a new key for new blocks (old codes stay valid because they are stored, not
recomputed).
</details>

## 5. [Deep] The viral link

A link receives 50,000 /s for 10 minutes. The edge TTL is 60 s, there are 200 PoPs, and each PoP sees on average 20
concurrent requests for the link at the moment its entry expires. Without coalescing, how many origin requests arrive
per expiry cycle? With coalescing per PoP? With stale-while-revalidate?

<details><summary>Answer</summary>

Without coalescing: up to 200 × 20 = **4,000** origin requests in a burst every 60 s (and more if origin latency rises
and requests pile up — a positive feedback loop). With per-PoP coalescing: one in-flight fetch per PoP → **≤ 200** per
cycle. With stale-while-revalidate: still ≤ 200 refreshes, but they are background requests, so users see no miss
latency and a slow origin does not cause a user-visible stall. Adding a tiered cache (PoPs → regional shield) reduces
origin fetches to roughly one per shield. Try the stampede experiment in [labs/04-caching](../labs/04-caching/) to see
the effect on p99.
</details>

## 6. [Core] Limiter algorithm per layer

For each limit, pick an algorithm and justify it: (a) 600 redirects/min per IP at the edge; (b) business API quota of
6,000 creates/min with bursts allowed; (c) 5 password-reset emails per account per day.

<details><summary>Answer</summary>

(a) **Sliding window counter** — two counters per key, no per-request state, and Cloudflare measured only 0.003 % wrong
decisions over 400 M requests with this approximation [lesson ref 4]. (b) **Token bucket** — "burst *b*, sustained *r*"
matches the commercial contract; two numbers of state per key; used by Stripe and Envoy. (c) **Sliding window log** —
volume is tiny, the action is security-sensitive, and exactness matters more than memory. A fixed window is acceptable
for (c) only if you accept up to 2× at the day boundary.
</details>

## 7. [Deep] Multi-region overshoot bound

A key has a 1,200 /min quota (20 /s). Three regions enforce adaptive shares, re-synchronized every 2 s. A client
suddenly sends at full speed to all three regions. Estimate the worst-case excess per sync interval and as a fraction of
the per-minute quota. What change halves it?

<details><summary>Answer</summary>

Using the lesson's worst-case burst bound (it assumes a region admits at most the full per-second rate for one
interval): excess ≈ (regions − 1) × rate × interval = 2 × 20 /s × 2 s = **80 requests per interval**.
Over a minute's quota of 1,200 that is ≈ 6.7 % — above a 5 % accuracy target. Halving the interval to 1 s halves the
bound to 40 (≈ 3.3 %). Alternatives: a cheap "burst detector" that triggers an immediate sync when a region's local
consumption jumps, or pinning very small quotas to a home region (exact but adds a cross-region round trip). The skill
being tested is turning "eventually consistent limiter" into a number.
</details>

## 8. [Interview] Fail open or fail closed?

The Redis cluster holding quota counters becomes unreachable in one region. Decide per limit type (API quota, login
attempts, edge flood protection) whether to fail open or closed, and say what you monitor.

<details><summary>Answer</summary>

API quota → **fail open with a conservative local limit** per gateway instance (e.g. the key's share divided by
instance count): briefly over-serving paid quota costs little; blocking every customer is an outage. Login attempts →
**fail closed or degrade to a strict local limit**: the limit protects accounts against credential stuffing. Edge flood
protection → unaffected (counts are per PoP at the CDN). Monitor the fallback-decision counter, alert if fallback lasts
more than a few minutes, and include fallback time in the incident review. A good answer also notes that Redis
`TIME` inside the Lua script avoids gateway clock skew once the store returns.
</details>

## 9. [Lab] Boundary bursts

In [labs/10-apis-communication](../labs/10-apis-communication/), run Experiment 1 (`--exp boundary`, default 10 per
10,000 ms): 10 requests 100 ms before a window ends and 10 more at the next window start. Record how many each
algorithm admits (fixed window, sliding log, sliding counter, token bucket, GCRA) and explain the differences.

<details><summary>Answer</summary>

Expected behavior (verify against your own run): the fixed window admits all 20, because the second 10 fall into a new
window — the classic 2× boundary burst. A sliding-window log admits 10; the sliding-window counter admits close to 10
(its weighted estimate counts most of the previous window). The token bucket admits 10 at t = 9.9 s and almost none at
t = 10.0 s (only ≈ 0.1 token has refilled). Report the numbers you observed, not these expectations; the lab uses a
virtual clock so results are repeatable.
</details>

## 10. [Interview] Takedown in 60 seconds

A phishing link is reported. Walk through every cache layer between the browser and the store and show how a takedown
reaches all of them within 60 s, including a browser that visited the link 10 minutes ago.

<details><summary>Answer</summary>

Browser: with `max-age=0` on a 302 the browser revalidates on every click, so it asks the edge again. (With a 301 it
might not ask at all — this is why the lesson rejects 301 by default.) Edge: TTL 60 s bounds staleness; an explicit
purge call removes the entry immediately. Regional cache: invalidation event on takedown. In-process LRU: 5 s TTL (or
subscribe to the same event). Store: status set to `flagged`, so a fresh lookup returns an interstitial or 410.
Worst case without purge ≈ 65 s (more if stale-while-revalidate or stale-if-error serve the old entry); with a purge
that bypasses those stale windows, seconds. Make it an SLO with a synthetic probe from several PoPs.
</details>
