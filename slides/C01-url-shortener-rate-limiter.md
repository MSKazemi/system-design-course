# C01 — URL shortener + distributed rate limiter (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C01-url-shortener-rate-limiter.md](../course/04-case-studies/C01-url-shortener-rate-limiter.md)

## Slide 1 — The requirement

- 100 M new links/month; 10 B redirects/month
- p99 redirect < 50 ms at the edge
- Per-API-key quotas that hold across three regions
- Phishing campaigns from week one

**Visual:** A short link card expanding into a long URL; three region pins with a quota gauge above them.
Icons: `domain-link`, `arch-cdn`, `pattern-rate-limiter`, `arch-region`.

**Speaker notes:** Two classic interview questions in one. The shortener is the simplest real system that needs a
limiter, and the limiter is the simplest real system whose correctness depends on where its state lives.

## Slide 2 — The numbers say "skew", not "size"

- ≈ 39 creates/s average, ≈ 3,860 redirects/s average, 100 : 1
- 5 years: 6 B links × 500 B ≈ 3 TB
- Peak ≈ 19,300 redirects/s — one viral link at 50,000 /s exceeds it
- Peak egress ≈ 77 Mbit/s

**Visual:** Bar chart: fleet peak vs one viral link; a tiny "3 TB" box next to a large "skew" arrow.
Icons: `ops-throughput`, `ops-metrics`.

**Speaker notes:** All of these are labelled assumptions in the lesson. The point is what they rule out: you do not
need to shard 3 TB, you do need to survive one key that is hotter than everything else combined.

## Slide 3 — Seven characters, and why

- 62^6 ≈ 5.7 × 10^10 → ≈ 10.6 % full after 5 years
- 62^7 ≈ 3.52 × 10^12 → ≈ 0.17 % full
- Random code collides with probability ≈ occupancy → ≈ 1 retry per 600 creates
- Occupancy argument beats "7 sounds right"

**Visual:** Two jars of marbles: one 10 % full, one barely filled.
Icons: `pattern-partitioning`.

**Speaker notes:** Do the arithmetic aloud. It also justifies the random-code scheme: retries are rare enough to
ignore at this occupancy.

## Slide 4 — Sketch

- Edge PoP: cache + edge rate limit
- Redirect service → regional cache → replicated KV link store
- API gateway → rate limiter → create service → code generator + URL safety check
- Edge logs → analytics, off the critical path

**Visual:** The lesson's flowchart (≤ 15 nodes): read path left, write path right.
Icons: `arch-cdn`, `arch-cache`, `arch-database`, `arch-api-gateway`, `pattern-rate-limiter`, `arch-event-stream`.

**Speaker notes:** For each box, say why it exists. The edge exists because 50 ms p99 is less than a transatlantic
round trip, and because the edge sees abusive traffic first.

## Slide 5 — 301 or 302?

- RFC 9110: 301/308 permanent and heuristically cacheable; 302/307 temporary
- Browser-cached 301 → lost clicks, no edits, no takedown for repeat visitors
- Choice: 302 + `Cache-Control: public, s-maxage=60, max-age=0`
- CDN absorbs load; browsers revalidate; takedown bounded to ≈ 60 s

**Visual:** Two timelines of a repeat click: 301 never reaches the edge; 302 reaches the edge and is logged.
Icons: `arch-client`, `arch-cdn`, `ops-logs`.

**Speaker notes:** Method preservation (307/308) is irrelevant for GET redirects; caching is the real difference.

## Slide 6 — Generating codes without a global lock

- Hash-and-truncate: collisions, and shared codes for shared URLs
- Global counter: enumerable — anyone can crawl every link
- Random + conditional insert: default; ≈ 0.17 % retries
- Counter blocks + keyed permutation: zero retries, non-guessable

**Visual:** Table with four rows and three columns: collisions, coordination, enumerable.
Icons: `pattern-idempotency`, `security-key`.

**Speaker notes:** The keyed permutation is a bijection, so no collisions; without the key, consecutive counters look
unrelated. Mention Snowflake only to say why 64-bit IDs are too long here.

## Slide 7 — The viral link

- Stampede on expiry → request coalescing + stale-while-revalidate
- Hot cache shard → small in-process LRU (5 s TTL)
- Scanners → cache 404s, limit 404-heavy clients
- Takedown: store + invalidation event + CDN purge

**Visual:** 200 PoPs each sending 20 requests at expiry (4,000) vs one per PoP (200) with coalescing.
Icons: `arch-cache`, `pattern-cache-invalidation`.

**Speaker notes:** The 4,000-vs-200 example is exercise 5. Every viral-link fix is a caching pattern from SYSDESIGN-04.

## Slide 8 — Rate limiting in three layers

- Edge: IP / ASN / TLS fingerprint — drop floods
- Gateway: API key — enforce paid quotas
- Service: in-flight requests — shed load
- Stripe runs request-rate, concurrency, and two load-shedding limiters

**Visual:** Three concentric rings around the origin, labelled with keys and example limits.
Icons: `pattern-rate-limiter`, `arch-firewall`, `pattern-bulkhead`.

**Speaker notes:** Different layers use different keys and different algorithms. Concurrency limits matter for
expensive endpoints where request rate says little about load.

## Slide 9 — Algorithms and atomic state

- Token bucket: burst + rate, two numbers per key (Stripe, Envoy, DynamoDB GAC)
- Sliding window counter: Cloudflare measured 0.003 % wrong decisions over 400 M requests
- Read-modify-write must be atomic → Lua script, not INCR then EXPIRE
- Lab: labs/10-apis-communication

**Visual:** Bucket with tokens dripping in; a two-window weighted counter diagram.
Icons: `pattern-rate-limiter`, `cache-redis`.

**Speaker notes:** The Redis docs show the INCR/EXPIRE race themselves; the lab implements five algorithms as atomic
scripts with a virtual clock.

## Slide 10 — Global quotas across regions

- Home region: exact, but a cross-region round trip per call
- Static split: unfair to skewed customers
- Adaptive shares, sync every second: bounded overshoot
- 6,000/min, 3 regions, 1 s sync → ≤ ≈ 200 extra per interval ≈ 3 %

**Visual:** Three gauges sharing one quota; arrows exchanging consumption every second.
Icons: `arch-region`, `pattern-consistency`, `ops-clock`.

**Speaker notes:** State the bound. It converts "eventually consistent limiter" into a product contract the customer
can be told.

## Slide 11 — When the limiter fails

- API quotas: fail open with conservative local limits
- Login / safety limits: fail closed
- Always: 429 + Retry-After + RateLimit fields (IETF draft-11)
- Jitter in SDK retries, or the 429s become a retry storm

**Visual:** Decision tree: store unreachable → which limit? → open or closed.
Icons: `pattern-circuit-breaker`, `pattern-retry`, `ops-alert`.

**Speaker notes:** Measure fallback decisions as an SLI. The RateLimit and Idempotency-Key headers are still drafts as
of 2026-11; pin the version you implement.

## Slide 12 — Modern twist: the adversary

- Check destinations at creation and re-check later (Web Risk Update API: local hashed lists)
- Safe Browsing API is non-commercial only
- Edge limits key on JA3/JA4 fingerprints, ASN, headers — counted per data center
- Interstitials instead of hard blocks for uncertain cases

**Visual:** A short link opening onto a warning interstitial; an edge PoP with a fingerprint icon.
Icons: `security-ddos`, `security-bug`, `ops-warning`.

**Speaker notes:** Per-data-center counting is the same trade-off as our multi-region quota, made by a vendor: no
cross-PoP coordination, at the price of some overshoot from distributed attackers.

## Slide 13 — WRAP

- Junior: API, data model, base-62 math, cache, one limiter algorithm
- Senior: code scheme defended, viral-link fixes, async analytics, atomic two-stage limiter
- Staff: overshoot bound, takedown SLO, abuse and privacy as requirements, cost at the edge
- Red flags: sharding 3 TB first, MD5-truncate with no collision story, synchronous click counting

**Visual:** Three-step staircase labelled junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** The staff signal is turning vague properties into numbers and contracts: overshoot ≤ 5 %, takedown
≤ 60 s, cost per 10,000 redirects.
