# 03 — Scaling compute (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Lesson: [course/01-foundations/03-scaling-compute.md](../course/01-foundations/03-scaling-compute.md)

## Slide 1 — The requirement

- 6,000 req/s at peak, p99 < 300 ms
- Lose any instance or zone without visible errors
- 20 deploys a day without dropping a request

**Visual:** A fleet of servers across three zones, one zone crossed out; icons `arch-servers-cluster`, `arch-region`.

**Speaker notes:** One server can't meet this, and even a big one is a single point of failure. So many servers,
and a decision per request.

## Slide 2 — Scale up vs scale out

- Up: simple, limited, steep price, one failure domain
- Out: needs statelessness; capacity grows with N until coordination bites
- USL: C(N) = N / (1 + α(N − 1) + βN(N − 1))

**Visual:** Two curves: linear ideal vs USL peaking then falling; icons `pattern-vertical-scaling`, `pattern-horizontal-scaling`.

**Speaker notes:** β > 0 means adding nodes can reduce throughput. Measure at 1, 2, 4 and 8 instances.

## Slide 3 — Stateless means "kill any instance, lose nothing"

- Sessions → shared store or signed tokens
- Uploads → object storage; jobs → queue
- Local cache is fine (soft state)
- Sticky sessions: uneven load, lost sessions, slow drains

**Visual:** An instance being removed while its state lives in Redis and object storage; icons `cache-redis`, `arch-object-storage`, `arch-server`.

**Speaker notes:** Tokens move the problem to revocation, which brings shared state back.

## Slide 4 — L4 vs L7

- L4: per connection, no HTTP parsing, fast; Maglev-style consistent hashing
- L7: per request, routing, retries, observability; terminates TLS
- Trap: gRPC/HTTP/2 over L4 balances connections, not load

**Visual:** Two-tier diagram: L4 → L7 proxies → apps (from the lesson); icons `arch-load-balancer`, `proxy-envoy`, `proxy-haproxy`.

**Speaker notes:** Ten long-lived gRPC connections over three replicas can split 6/3/1 (an illustrative split) and stay that way.

## Slide 5 — Algorithms

- Round robin: fair only for uniform work
- Least outstanding requests: adapts to slow servers
- Hash: affinity, but `mod N` reshuffles almost everything
- Power of two choices: two random picks, take the less loaded

**Visual:** Decision tree from the lesson; icons `arch-load-balancer`, `pattern-consistent-hashing`.

**Speaker notes:** Each algorithm answers "which backend?" with different information. The choice depends on what
the balancer knows.

## Slide 6 — Why two choices is magic

- One random choice: max load ≈ ln n / ln ln n
- Two choices: ≈ ln ln n / ln 2 + O(1) (Azar et al. 1999; Mitzenmacher 2001)
- Robust to stale information; no shared state
- Envoy default `choice_count` 2; HAProxy `random(2)`; NGINX `random two least_conn`

**Visual:** Histogram of bin loads: random (long tail) vs two-choice (tight); icon `pattern-horizontal-scaling`.

**Speaker notes:** The second sample gives an exponential improvement. More samples add only a constant factor.

## Slide 7 — "Least loaded" stampedes

- Many balancers, one stale report, same choice
- The minimum becomes the maximum, and the herd moves on
- Randomness keeps independent deciders apart (Mitzenmacher 2000)

**Visual:** Ten arrows converging on one server, then on the next; icons `arch-load-balancer`, `ops-warning`.

**Speaker notes:** This is the deep reason P2C appears in every modern proxy.

## Slide 8 — Consistent hashing, bounded

- Remove 1 of N: ≈ 1/N of keys move (vs ≈ (N − 1)/N with `mod N`)
- Virtual nodes even out the arcs
- Bounded loads: cap at (1 + ε) × average; HAProxy `hash-balance-factor`

**Visual:** Hash ring with three servers; one removed, only its arc reassigned; icon `pattern-consistent-hashing`.

**Speaker notes:** With 300 backends, a modulo hash moves about 99.7% of keys and consistent hashing about 0.3%.
Lab experiment 5 measures it.

## Slide 9 — Health checks

- Active probes (detection ≈ inter × fall) + passive outlier ejection
- Readiness ≠ liveness
- Never make health depend on a shared dependency
- Fail open: Envoy panic threshold, default 50%

**Visual:** Three probes with a heart-beat line, one flat; icons `pattern-health-check`, `ops-check`.

**Speaker notes:** A deep `SELECT 1` check removes the whole fleet during a database failover.

## Slide 10 — Draining

- SIGTERM → fail readiness → keep serving → LB stops sending → finish in flight → exit
- Kubernetes grace: 30 s default; endpoint removal races SIGTERM → preStop delay
- AWS ELB deregistration delay: 300 s default
- Long-lived connections: `Connection: close`, `GOAWAY`

**Visual:** The drain sequence diagram from the lesson; icons `ops-deploy`, `devops-kubernetes`.

**Speaker notes:** New instances need the opposite: slow start, or least-connections floods them.

## Slide 11 — Autoscaling

- HPA: ceil(current × metric / target); 15 s period; 0.1 tolerance; 300 s downscale window
- Predictive (AWS: ≥ 24 h data, 48 h forecast; GCP: 3 days of history, CPU only)
- Scale on demand per instance, not on latency
- Scale-up lag sets the headroom you need

**Visual:** Replica count vs load over a day: reactive lagging, predictive leading; icons `pattern-autoscaling`, `devops-kubernetes`.

**Speaker notes:** Per-HPA tolerance is stable since Kubernetes v1.37. A latency-based scaler removes instances
when latency improves, which makes latency worse.

## Slide 12 — Thundering herds

- Synchronised retries, reconnect storms, cache expiry, cold starts, cron at :00
- Jittered exponential backoff (Brooker 2015)
- Retry budgets: 3 attempts, 10% per client → ≈ 1.1× instead of ≈ 3× (SRE book)
- Retry at one layer only: 3 attempts at each of 5 layers → 3⁵ = 243 at the failing service (our arithmetic; SRE book example: 4³ = 64)

**Visual:** A wave of requests hitting one server at the same instant, then the same requests spread out by jitter; icons `pattern-retry`, `pattern-backpressure`.

**Speaker notes:** The balancer and the autoscaler are where herds land.

## Slide 13 — Sizing, worked

- 6,000 / 400 per instance = 15
- Zone loss, 3 zones: × 3/2 → 24 (8 per zone)
- Scale-up lag 90 s at 2× per 10 min → 11% headroom (covered only while all zones are up)
- Zone down + rolling deploy → 14 × 400 = 5,600 < 6,000: pause deploys, or 27 (9 per zone)
- 63% of knee at normal peak; that is the price of zone tolerance

**Visual:** The step-by-step table with the final "24 instances"; icons `ops-cost`, `arch-region`.

**Speaker notes:** Make the cost of redundancy explicit: four zones would need 1.33× instead of 1.5×.

## Slide 14 — Lab L03

- HAProxy 3.4 with five frontends: RR, leastconn, P2C, consistent hash, modulo hash
- One slow replica: compare p99 across algorithms
- Kill vs graceful stop; retries on vs off
- Count keys that move when a replica goes

**Visual:** Lab topology: k6 → HAProxy → app1/app2/app3; icons `proxy-haproxy`, `devops-docker`, `arch-servers-cluster`.

**Speaker notes:** The lab README records what was actually run and observed.
