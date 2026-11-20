# 02 — Anatomy of a request (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Lesson: [course/01-foundations/02-anatomy-of-a-request.md](../course/01-foundations/02-anatomy-of-a-request.md)

## Slide 1 — Latency is round trips

- Requirement: first byte < 200 ms (p75) for first-time EU visitors
- Before `GET /`: DNS, transport handshake, TLS
- Each step costs ≥ 1 RTT; light in fibre ≈ 200 km per ms

**Visual:** A timeline bar split into DNS / TCP / TLS / request segments; icons `arch-client`, `arch-internet`.

**Speaker notes:** The bottleneck is not CPU. The lever is fewer round trips over shorter distances.

## Slide 2 — The whole journey

- Browser → recursive resolver → authoritative DNS
- Browser → CDN edge: handshake, then request
- Edge → origin on a warm, reused connection

**Visual:** The lesson's sequence diagram; icons `arch-dns`, `arch-cdn`, `arch-load-balancer`, `arch-server`.

**Speaker notes:** Keep this picture. Every later slide zooms into one arrow.

## Slide 3 — DNS and TTLs

- Long TTL: fast lookups, slow changes. Short TTL: agile, more cold lookups
- Negative answers are cached too (RFC 2308)
- Serve-stale (RFC 8767): resilience, and outdated answers
- GeoDNS sees the resolver, not the user

**Visual:** A record moving through caches, each with a countdown timer; icons `arch-dns`, `ops-clock`.

**Speaker notes:** DNS is a poor fast-failover tool because you don't own the caches. Lower TTLs one old TTL
before a migration.

## Slide 4 — TCP costs

- Three-way handshake: 1 RTT before data
- Slow start: about 14.6 KB in the first flight (10 × 1,460 B; RFC 6928)
- A 100 KB response needs 3 rounds of data on a new connection
- Head-of-line blocking: one loss stalls everything behind it

**Visual:** Congestion window doubling per RTT: 14.6 → 29.2 → 58.4 KB; icon `arch-network`.

**Speaker notes:** This is why the first response should be small, and why warm connections matter.

## Slide 5 — TLS 1.3

- Full handshake in 1 RTT (TLS 1.2: 2)
- 0-RTT resumption: "no guarantees of non-replay between connections" (RFC 8446 §2.3)
- Only idempotent requests as early data; else `425 Too Early` (RFC 8470)
- ECH (RFC 9849, 2026) hides the hostname

**Visual:** Two handshake ladders side by side, TLS 1.2 vs 1.3; icons `security-lock`, `security-encryption`.

**Speaker notes:** 0-RTT saves a round trip and adds a replay risk. Never use it for state-changing requests.

## Slide 6 — HTTP/1.1 → HTTP/2 → HTTP/3

- 1.1: one request at a time per connection; about six connections per host
- 2: many streams over one TCP connection; TCP head-of-line blocking remains
- 3: QUIC streams independent; handshake merged; UDP

**Visual:** Three lanes: six thin pipes; one pipe with interleaved frames; one pipe with independent streams; icons `arch-network`, `protocol-grpc`.

**Speaker notes:** Semantics are identical (RFC 9110). Only the wire changes.

## Slide 7 — QUIC in three properties

- 1-RTT combined transport + TLS handshake; 0-RTT on resumption
- Per-stream loss recovery
- Connection IDs: survive Wi-Fi → cellular (RFC 9000 §9)
- Load balancers must route on connection ID

**Visual:** A phone switching networks while the connection continues; icons `arch-mobile-client`, `arch-load-balancer`.

**Speaker notes:** A 4-tuple hash breaks migration. That is why HTTP/3 lives behind purpose-built edges.

## Slide 8 — Reuse connections, nest timeouts

- Pay handshakes once: keep-alive, pools, multiplexing
- New connection per call: handshakes, slow start, `TIME_WAIT`
- Upstream idle timeout > proxy idle timeout, or random 502s (AWS ALB default: 60 s)

**Visual:** Proxy and upstream with two idle timers; the shorter one on the wrong side, marked with a warning; icons `arch-reverse-proxy`, `ops-warning`.

**Speaker notes:** This is one of the most common production 502 causes, and it is documented by AWS for ALB.

## Slide 9 — Proxies and the edge

- Reverse proxy: TLS termination, routing, buffering, pooling, retries
- `Forwarded` / `X-Forwarded-For` / PROXY protocol carry the client IP; trust only your own proxies
- CDN: cache, terminate near the user, warm connections to the origin

**Visual:** User → edge PoP → shield → origin; icons `arch-cdn`, `arch-reverse-proxy`, `network-cloudflare`.

**Speaker notes:** Even uncacheable responses benefit from edge termination, because the handshakes run over a short
path.

## Slide 10 — Anycast vs GeoDNS

- Anycast: one prefix, many PoPs, BGP picks the "closest"; fast failover
- GeoDNS: per-country control; bounded by caches
- Common combination: anycast to the edge, logic at the edge picks the origin

**Visual:** World map with one IP announced from many points vs DNS answering per country; icons `pattern-geo-distribution`, `arch-region`.

**Speaker notes:** Anycast follows routing, not borders. Residency needs explicit origin selection.

## Slide 11 — The budget, worked

- Direct, TCP + TLS 1.3: 225 ms (cached DNS); fails 200 ms
- QUIC direct or edge-terminated: ≈ 165 ms; HTTP/3 at the edge: 145 ms
- Returning user with an open connection: 110 ms; fails 100 ms
- Shell cached at the edge: ≈ 21 ms

**Visual:** Horizontal stacked bars for scenarios A–G from the lesson, with the 200 ms and 100 ms targets as labelled lines; icon `ops-latency`.

**Speaker notes:** The returning-user target forces a caching decision, not a protocol decision. Assumptions:
20 ms to the edge, 60 ms to the origin.

## Slide 12 — When DNS takes you down

- Meta, 4 Oct 2021: DNS servers withdrew BGP routes; "unreachable even though they were still operational"
- AWS, 19–20 Oct 2025: race condition left an empty DNS record for DynamoDB in us-east-1
- Lessons: guardrails on DNS automation; "never withdraw the last one"; serve-stale

**Visual:** Two incident cards with dates and one-line causes; icons `ops-incident`, `arch-dns`.

**Speaker notes:** Both are public postmortems. The pattern is automation acting everywhere at once.

## Slide 13 — Interview: "what happens when you type a URL?"

- Count round trips per phase; name what removes each
- Edge + HTTP/3 + warm origin connections + edge caching
- Failures: DNS automation, keep-alive mismatch, UDP blocked, certificate expiry
- Red flags: "use a CDN" without saying why; 0-RTT for POST

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip; icon `arch-user`.

**Speaker notes:** Interviewers listen for round trips and distances. Close with what you'd measure: phase-level
timings from real users.
