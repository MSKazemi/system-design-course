# 03 — Exercises

Lesson: [course/01-foundations/03-scaling-compute.md](../course/01-foundations/03-scaling-compute.md)

### 1. [Core] Is it stateless?

For each, say whether an instance can be killed at any moment without user impact, and if not, where the state
should go: (a) an in-memory LRU cache of rendered pages; (b) login sessions in a local dictionary; (c) a
multipart upload buffered on local disk; (d) a WebSocket connection.

<details><summary>Answer</summary>

(a) **Yes**, it is soft state. A miss is slower, not wrong. Keep it local, but watch the cold-start herd after
scale-out.
(b) **No**: users are logged out. Use a shared session store, or signed tokens (and plan for revocation).
(c) **No**: the upload is lost. Upload directly to object storage with multipart or resumable uploads.
(d) **Inherently instance-bound**. Keep the subscription and session state in a shared store, design the client to
reconnect with jittered backoff, and send a close or `GOAWAY` during drain.
</details>

### 2. [Core] Universal Scalability Law

With USL parameters α = 0.03 and β = 0.0005, compute the relative capacity C(N) for N = 1, 8, 32, 64. Where is
the peak, roughly?

<details><summary>Answer</summary>

C(N) = N / (1 + α(N − 1) + βN(N − 1)).
- N = 1: 1.
- N = 8: 8 / (1 + 0.21 + 0.028) = 8 / 1.238 ≈ **6.5**.
- N = 32: 32 / (1 + 0.93 + 0.496) = 32 / 2.426 ≈ **13.2**.
- N = 64: 64 / (1 + 1.89 + 2.016) = 64 / 4.906 ≈ **13.0**.

The peak is at N* = √((1 − α)/β) = √(0.97 / 0.0005) ≈ **44**, where C ≈ 13.6. Beyond it, adding nodes *reduces*
capacity. Lesson: fit α and β from measurements at a few N before promising linear scaling, and attack the
coherence cost (β), for example shared locks or chatty synchronisation.
</details>

### 3. [Core] L4 and gRPC

Ten client pods each open one long-lived gRPC (HTTP/2) connection through an L4 load balancer to a 3-replica
service. Describe the load distribution and give two fixes.

<details><summary>Answer</summary>

The L4 balancer chooses a backend **per connection**. Ten connections over three replicas split at best 4/3/3,
and with random or hash placement possibly 6/3/1. Each connection carries all of that client's requests, so load
follows the connection split and stays skewed until connections are re-established, for example at a deploy,
which then reshuffles it. Fixes: (1) balance per request at **L7** (Envoy, a gRPC-aware proxy, a service-mesh
sidecar); (2) **client-side load balancing**, where the gRPC client resolves all endpoints and balances each
call; (3) as a stop-gap, limit connection age (`max connection age`) so connections recycle and rebalance.
</details>

### 4. [Core] Algorithms under a slow replica

Three replicas each serve 200 requests/s at capacity. Replica 3 degrades to 67 requests/s (it is three times
slower). Load is 300 requests/s. Predict the behaviour of round robin, least connections and power of two choices.

<details><summary>Answer</summary>

**Round robin** sends 100 requests/s to each replica. Replica 3 can serve only 67/s, so it is overloaded
(ρ ≈ 1.5). Its queue grows without bound and a third of requests see ever-growing latency, then timeouts. **Least
connections** sees replica 3 accumulate in-flight requests and sends it fewer. Total capacity is 467/s for 300/s
of load, so all replicas can stay below saturation and the p99 stays bounded. **P2C** samples two replicas and
picks the one with fewer in-flight requests. It is nearly as good as least connections and needs no global view.
This is lab L03, experiment 2.
</details>

### 5. [Core] Health-check timing

HAProxy uses `inter 2s fall 3 rise 2`. (a) What is the worst-case time until a crashed backend stops receiving new
requests? (b) At 250 requests/s to that backend, about how many requests are affected? (c) What reduces the
user-visible impact without shortening the interval?

<details><summary>Answer</summary>

(a) Three consecutive failed checks: up to about 3 × 2 = 6 s, plus up to one interval of phase offset, so about
**6–8 s** worst case.
(b) 250 × 6–8 ≈ **1,500–2,000 requests** routed to it.
(c) **Connection retries with redispatch** (a refused or timed-out *connect* is safe to retry on another server),
**passive outlier detection** (eject on real errors immediately), and for in-flight requests, **idempotent
retries** at the client or proxy. Shortening the interval increases check traffic on every backend from every
balancer, which is a real cost at scale.
</details>

### 6. [Core] The deep health check trap

A health check runs `SELECT 1` against the shared database. During a 20-second database failover, what happens to
the fleet, and what should the check do instead?

<details><summary>Answer</summary>

Every instance fails its health check at the same time. The balancer marks the **whole fleet down** and sends all
traffic to errors, or nowhere, even for requests that never touch the database (static assets, cached reads).
Recovery may lag the database's own recovery by `rise × inter`. Instead: readiness should reflect *this
instance's* ability to serve (the process is up, warmed, not draining). Report dependency failures through error
rates and alerts. Configure fail-open behaviour (an Envoy-style panic threshold) so that when most hosts look
unhealthy, traffic is still spread.
</details>

### 7. [Core] Zone-loss sizing

Steady-state peak needs 30 instances. You run in 3 zones and must survive the loss of one. How many instances,
and what is normal peak utilisation relative to the knee? Repeat for 4 zones.

<details><summary>Answer</summary>

3 zones: each surviving pair must carry 30, so 15 per zone and **45 total**. Normal peak = 30/45 ≈ **67%** of the
knee. 4 zones: three must carry 30, so 10 per zone and **40 total**. Normal peak = 30/40 = **75%**. More zones
mean a smaller reserve fraction, Z/(Z − 1), so less idle spend, at the cost of more operational surface and
possibly more cross-zone traffic.
</details>

### 8. [Core] Consistent vs modulo hashing

An affinity-routed cache tier has 10 nodes. One node fails. What fraction of keys change owner under (a) `hash mod N`
and (b) a consistent-hash ring? What does each do to the cache hit ratio?

<details><summary>Answer</summary>

(a) Going from mod 10 to mod 9: a key keeps its owner only if `h mod 10 == h mod 9`, which is true for about 1/10
of keys. So about **90% move**, and nearly every request misses until the caches refill: a stampede on the origin.
(b) Only the failed node's keys move to their ring successors, about **10%**. The hit ratio drops by about 10%,
and only for those keys. Add bounded loads (for example HAProxy's `hash-balance-factor`) so the successor of a hot
arc isn't overwhelmed.
</details>

### 9. [Deep] Why P2C beats "least loaded"

Ten independent proxies each receive a load report from the backends every second and route to the single least
loaded backend. Explain the failure, and why power of two choices avoids it.

<details><summary>Answer</summary>

All ten proxies see the same stale report and all choose the *same* minimum backend for the next second. It
receives ten proxies' worth of traffic, becomes the most loaded, and the herd moves on to the next minimum. Load
oscillates. Mitzenmacher (2000) showed that with stale information, deterministic "pick the minimum" can do worse
than random. P2C samples two backends *at random* per request. Different proxies, and different requests, pick
different pairs, so no single backend attracts the herd. Each proxy can also use its own up-to-date in-flight
counts instead of a shared report. The analysis of Azar et al. and Mitzenmacher shows the maximum load drops from
about ln n / ln ln n (random) to about ln ln n / ln 2, an exponential improvement, with only two samples.
</details>

### 10. [Core] Graceful shutdown sequence

Write the order of events for removing a Kubernetes Pod behind a Service without dropping requests. Include the
default grace period and one race condition.

<details><summary>Answer</summary>

1. Pod deletion. The EndpointSlice marks it `terminating` (`ready` becomes false), *and in parallel* the kubelet
   runs the `preStop` hook, then sends SIGTERM.
2. The `preStop` hook sleeps a few seconds. **Race:** proxies and kube-proxy may not yet have removed the endpoint
   when the app receives SIGTERM, so the app must not stop accepting connections immediately.
3. The app fails readiness, keeps serving in-flight and newly arriving requests, sends `Connection: close` or
   `GOAWAY` on keep-alive connections, and stops accepting connections once traffic has drained.
4. It exits 0 before `terminationGracePeriodSeconds` (**30 s by default**). After that the kubelet sends SIGKILL.

Size the grace period to cover preStop + drain + the longest request (streaming responses may need much longer
than 30 s).
</details>

### 11. [Core] HPA arithmetic

An HPA targets 60% CPU. There are 8 replicas at 90% average CPU. What does it recommend? If the metric then
drops to 40% for two minutes, does it scale down?

<details><summary>Answer</summary>

desired = ceil(8 × 90 / 60) = ceil(12) = **12 replicas**. The ratio 1.5 is far outside the 0.1 tolerance, so it
acts. On the drop to 40% with 12 replicas, the recommendation is ceil(12 × 40 / 60) = 8. But the default
**300 s downscale stabilisation window** uses the *highest* recommendation of the last five minutes, which still
includes 12. So no scale-down happens after two minutes. It happens only if the lower recommendation persists for
the whole window.
</details>

### 12. [Deep] Retry amplification

A request passes through 4 service layers. Each layer retries a failed downstream call up to 2 times (3 attempts
total). The bottom service is failing completely. How many attempts reach it per user request? What does a 10%
retry budget at each client change?

<details><summary>Answer</summary>

Each layer multiplies by 3: 3⁴ = **81 attempts** at the bottom per user request. That amplification lands on the
service that is already failing. With a per-client retry budget that allows retries only while they are under 10%
of requests, the sustained multiplier per layer approaches about 1.1×, so about 1.1⁴ ≈ 1.46× in total. Better
still, retry at **one layer only** (the one directly above the failure), as the SRE book recommends, add jittered
exponential backoff, and fail fast with circuit breakers (SYSDESIGN-11).
</details>

### 13. [Interview] Scale this API to 10×

The interviewer says: "Your API runs on 6 instances at 50% CPU and handles 3,000 requests/s. Traffic will grow
10× next quarter. What do you do?"

<details><summary>Answer</summary>

Outline: (1) **Quantify**: 3,000 requests/s at 50% on 6 instances is about 1,000 requests/s per instance at 100%.
For 30,000 requests/s at a 60% target that is about 50 instances, before zone reserve. With 3 zones, about 75.
(2) **Check the shared dependencies**, because 10× rarely scales linearly (USL). The database, caches, connection
pool limits (50 instances × pool size against the database's connection limit), rate limits of third parties.
(3) **Measure the knee** of one instance with an open-model load test, and test at 2, 4 and 8 instances to fit
α and β. (4) **Balancer and autoscaling**: P2C or least-request, slow start, an HPA on demand per instance, a
scale-up lag budget, a scheduled baseline for known peaks. (5) **Failure plan**: zone loss, retries with
budgets, draining for deploys. The red flag is answering "add 54 more instances" without (2) and (3).
</details>

### 14. [Lab] Draining, measured

In lab L03, compare `docker compose kill app2` with `docker compose stop app2` (with `DRAIN_S=5`) during a k6 run.
What do you expect in the error count, and why?

<details><summary>Answer</summary>

`kill` sends SIGKILL. In-flight requests on app2 fail, and new requests keep reaching it until HAProxy's health
checks mark it down (about `inter × fall` ≈ 2–3 s). With `RETRIES=0` those surface as errors (502/503, or
timeouts). With `RETRIES=2` and `option redispatch`, connection failures are retried elsewhere, but requests
already in flight on app2 still fail. `stop` with `DRAIN_S=5` sends SIGTERM. app2 starts failing `/health` but
keeps serving, HAProxy marks it down after two failed checks and stops routing to it, in-flight requests complete,
and app2 exits after 5 s. You should see **zero or near-zero errors**. See the lab README's Test status for what
was actually observed.
</details>
