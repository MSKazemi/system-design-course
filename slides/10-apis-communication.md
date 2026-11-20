# 10 — APIs & communication (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/10-apis-communication.md](../course/01-foundations/10-apis-communication.md)

## Slide 1 — The requirement

- 3,000 tenant apps call Lumen's chat and document APIs
- LLM answers stream token by token; first text in under a second
- Mobile clients retry aggressively; no double charges allowed
- One tenant must not starve the rest; admission control ≤ 2 ms p99

**Visual:** Lumen logo-free sketch: many client icons → gateway → services. Icons: `arch-users`, `arch-api-gateway`, `arch-microservice`.

**Speaker notes:** Every line of this requirement is an API decision. We will take them one at a time: protocol,
streaming, safe retries, rate limiting, and evolution.

## Slide 2 — Three boundaries, three defaults

- Public (north–south): REST/JSON + SSE
- Internal (east–west): gRPC + protobuf, deadlines
- Asynchronous: events and queues (SYSDESIGN-08)
- The gateway and the mesh enforce policy at the edges of each

**Visual:** The lesson's boundary flowchart (client → edge → gateway → mesh services; Redis on the side). Icons: `arch-api-gateway`, `arch-service-mesh`, `cache-redis`, `protocol-grpc`.

**Speaker notes:** Locate the boundary before choosing a protocol. Who are the clients, how long does the contract
live, and who can cache what?

## Slide 3 — REST is HTTP semantics you get for free

- Fielding's constraints: client–server, stateless, cache, uniform interface, layered, code-on-demand [1]
- Safe: GET, HEAD, OPTIONS, TRACE; idempotent: those plus PUT, DELETE [2]
- POST and PATCH are not idempotent [2][34]
- Idempotent ⇒ intermediaries may retry automatically

**Visual:** Table of methods with two check columns (safe / idempotent), checks also written as "yes/no" text. Icons: `pattern-api`, `protocol-openapi`.

**Speaker notes:** The idempotency column is the most practical line in RFC 9110. It decides which requests your
mesh and client libraries are allowed to retry on their own.

## Slide 4 — gRPC and GraphQL

- gRPC: protobuf contracts, HTTP/2 multiplexing, 4 method shapes, deadlines, cancellation [5]
- HTTP/2 fixes application HOL blocking, not TCP HOL blocking [3]
- Long-lived connections need L7 or client-side balancing
- GraphQL: client chooses the shape; server pays in N+1 and cost control [7][8]
- GitHub GraphQL: 5,000 points/hour, max 500,000 nodes per call [9]

**Visual:** Side-by-side: REST (5 round trips for one screen) vs GraphQL (1 query) vs gRPC (typed stub). Icons: `protocol-grpc`, `protocol-graphql`, `protocol-json`.

**Speaker notes:** GraphQL does not remove work; it moves it to the server. That is why serious GraphQL APIs rate
limit by query cost, not request count.

## Slide 5 — Why SSE carries LLM tokens

- One direction: prompt once, tokens stream back
- Plain HTTP: passes proxies, gateways, auth headers
- `text/event-stream`, `id:` + `Last-Event-ID` reconnect [10]
- Anthropic and OpenAI stream over SSE (as of 2026-11) [12][13]
- WebSockets for true two-way: chat presence, collaboration [11]

**Visual:** Sequence: browser → gateway → chat → inference; events with ids; drop at id 17; resume with Last-Event-ID. Icons: `domain-chat`, `domain-ai`, `pattern-push`, `protocol-websocket`.

**Speaker notes:** The design question is not "which is newer" but "which direction does data flow and what does
every hop already understand". For one-way token streams, that is SSE.

## Slide 6 — Streams change capacity planning

- Capacity = concurrent connections × duration, not requests/s
- 20k streams × 40 tok/s × ~120 B ≈ 0.8 Gbit/s (assumptions)
- Disable proxy buffering; align idle timeouts; send pings
- Deploys wait for the longest stream to drain

**Visual:** Bar: "new requests/s" small vs "open connections" large. Icons: `ops-throughput`, `arch-load-balancer`, `ops-latency`.

**Speaker notes:** The numbers are labelled assumptions in the lesson; the point is that the stream tier is sized by
concurrency. Buffering proxies and short idle timeouts are the most common streaming bugs.

## Slide 7 — Making POST safe to retry

- Client names the operation: `Idempotency-Key` (IETF draft -08, not yet an RFC) [18]
- 400 missing key · 409 still in progress · 422 same key, different body [18]
- Store key + request hash + response; same transaction as the effect
- Pass a derived key to external systems [20]
- Stripe v1: ≤ 255 chars, response replayed incl. 500s, keys prunable after 24 h [19]

**Visual:** Sequence: POST with k1 → store → charge → response lost → retry with k1 → replay. Icons: `pattern-idempotency`, `domain-payment`, `pattern-retry`.

**Speaker notes:** The network can fail after the commit. Without a key, the client must choose between a duplicate
and a lost write. With a key, the server answers "already done, here is the result".

## Slide 8 — Six rate-limiting algorithms

- Fixed window: 1 counter; up to 2× at boundaries
- Sliding log: exact; memory ∝ limit
- Sliding counter: 2 counters; Cloudflare measured ~0.003% wrong decisions [23]
- Token bucket: bursts up to b, average r; variable cost [22]
- Leaky bucket (queue): smooth output; GCRA: one timestamp (TAT) [24]

**Visual:** Six small timelines, each with the same request pattern and admitted ticks marked by shape (✓ / ✗), not color. Icons: `pattern-rate-limiter`, `ops-clock`.

**Speaker notes:** Algorithms differ in three things: state per key, burst behavior, and how exact they are. Most
production systems pick token bucket or sliding window counter.

## Slide 9 — The boundary burst, measured

- Policy: 10 per 10 s; 10 requests at t=9.9 s, 10 at t=10.0 s
- Fixed window admits 20; sliding log, sliding counter, token bucket, GCRA admit 10
- Reproduced in lab L10, Experiment 1
- Same lab: naive read-then-write bucket over-admits under 50 concurrent clients; Lua does not

**Visual:** Two windows side by side, 20 ticks clustered at the boundary; the fixed-window row marks all 20 admitted. Icons: `pattern-rate-limiter`, `cache-redis`.

**Speaker notes:** This is the observed lab result, not a theoretical claim. Run it yourself; then look at the race
experiment, which is the bug that actually ships.

## Slide 10 — Distributed rate limiting

- Central store + atomic Lua script (Redis runs scripts atomically) [25]
- Two-stage: local token bucket, then global limit (Envoy) [26]
- Quota leasing: fewer round trips, less accuracy
- Decide per endpoint: fail open (cheap reads) or closed (GPU, login) [22]
- Return 429 + Retry-After [21]; advertise `RateLimit` fields (draft -11) [28]

**Visual:** The lesson's decision flowchart: local bucket → Redis → allow / 429 / store-timeout branch. Icons: `pattern-rate-limiter`, `cache-redis`, `proxy-envoy`, `arch-api-gateway`.

**Speaker notes:** The interview question behind every rate limiter is "what happens when the limiter is down?".
Have an answer per endpoint.

## Slide 11 — Gateways and meshes

- Gateway: authN, quotas, rate limits, routing, transcoding at the edge
- Mesh: mTLS, retries, timeouts, telemetry between services
- Linkerd: Rust sidecar proxy [31]
- Istio ambient: per-node ztunnel (L4) + optional waypoints (L7); GA in 1.24 [29][30]

**Visual:** Sidecar mode (proxy per pod) vs ambient (one ztunnel per node + a waypoint). Icons: `proxy-istio`, `proxy-linkerd`, `proxy-envoy`, `arch-service-mesh`.

**Speaker notes:** The mesh question is where cross-cutting network policy lives and what it costs per pod or per
node. Keep business logic out of the gateway.

## Slide 12 — Evolving without breaking

- Additive changes only; new fields optional; tolerate unknown fields
- Protobuf: never reuse numbers; reserve deleted numbers and names; 1–15 = one byte [32]
- AIP-180: source, wire, semantic compatibility [33]
- Versioning: path `/v1`, date versions pinned per account (Stripe) [14], header + 24-month window (GitHub) [15]
- Pagination: cursor/keyset over offset [16][17]

**Visual:** A protobuf message before/after with `reserved` lines highlighted by a bracket. Icons: `protocol-grpc`, `pattern-pagination`.

**Speaker notes:** You will change the API many more times than you design it. The rules are simple; the discipline
is enforcing them in review.

## Slide 13 — Interview angle

- CLARIFY key, unit, burst, failure policy
- QUANTIFY calls/s, keys, memory, latency budget
- SKETCH gateway → local bucket → Redis (Lua) → 429
- DEEPEN algorithm, atomicity, clock, hot keys
- STRESS store down, retry storms, multi-region → WRAP

**Visual:** Six-step strip CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP. Icons: `pattern-rate-limiter`, `ops-check`.

**Speaker notes:** Red flags: fixed window without the boundary caveat, read-then-write limiters, no failure policy,
WebSockets by reflex for one-way streams, POST retries without keys.
