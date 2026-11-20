# 11 — Exercises

Lesson: [course/01-foundations/11-reliability-engineering.md](../course/01-foundations/11-reliability-engineering.md) ·
Lab: [labs/11-reliability-engineering/](../labs/11-reliability-engineering/README.md)

## 1. Classify the failure [Core]

For each, name the failure class (crash, omission, timing, arbitrary/Byzantine, gray) and one detection method:
(a) a VM loses power; (b) a load balancer silently drops 2% of packets; (c) a database replica answers in 4 s
during compaction; (d) a cache node returns another tenant's data after a memory error; (e) a service's `/healthz`
returns `200` while its request handler thread pool is deadlocked.

<details><summary>Answer</summary>

(a) **Crash** — heartbeats or connection failures detect it quickly. (b) **Omission** — visible as elevated
retransmits/timeouts from callers; a heartbeat would usually still pass. (c) **Timing** — tail-latency SLIs (p99 per
replica) and timeouts at callers. (d) **Arbitrary** — only end-to-end validation detects it (checksums, tenant-ID
assertions on responses); it cannot be detected by liveness checks at all. (e) **Gray failure**, the textbook case of
differential observability [Huang et al. 2017]: the observer (health check) sees healthy, callers see failure. Fix by
making the health check exercise the real request path (or a synthetic request through the same pool) and by
alerting on caller-observed errors. Note that (b) and (c) are also gray failures in practice if your detector misses
them — "gray" is about the observation gap, the classic classes are about the behaviour.
</details>

## 2. Error budget and dependencies [Core]

Lumen promises 99.95% monthly availability. The answer path has five hard dependencies at 99.99% and two at 99.9%.
(a) What is the expected availability of the path? (b) How many minutes per 30-day month is that? (c) Which two
changes would you make first?

<details><summary>Answer</summary>

(a) 0.9999⁵ × 0.999² ≈ 0.99950 × 0.99800 ≈ **0.99750** (99.75%). (b) Unavailability 0.0025 × 43,200 ≈ **108 min**,
against a budget of 21.6 min. (c) The two 99.9% dependencies dominate: each alone contributes ~43 min. Make them
**soft** (cache their results, serve a degraded answer when they fail, call them asynchronously if the response does
not need them) or add **independent** redundancy for them. Raising the 99.99% ones further barely helps. Acceptable
alternatives: moving a dependency off the critical path entirely (precompute) is often the best answer.
</details>

## 3. Retry amplification [Core]

A request crosses gateway → answer service → retrieval → vector DB. Every layer retries up to two times (three
attempts) on timeout. (a) Worst-case attempts at the vector DB per user request? (b) Redesign the retry policy and
state the new worst case.

<details><summary>Answer</summary>

(a) Three retrying layers above the DB: 3 × 3 × 3 = **27 attempts**. (If the vector DB client inside retrieval also
retries, it is the third factor; count layers that issue calls to the next.) (b) Retry at **one** layer — usually
the one closest to the failing dependency (retrieval → vector DB) or end-to-end at the client — with capped
exponential backoff, full jitter and a retry budget (e.g. retries ≤ 10% of requests). All other layers fail fast and
propagate the deadline. Worst case per request is 3 attempts, and the *aggregate* is bounded at ≈ 1.1× normal load by
the budget [Google SRE book, ch. 21]. Mention idempotency: the vector query is a read, so safe to retry.
</details>

## 4. Pick a timeout [Core]

A dependency's latency over the last week: p50 = 12 ms, p99 = 60 ms, p99.9 = 140 ms, p99.99 = 900 ms. The calling
service has a 1 s end-to-end deadline and typically spends 250 ms before this call and 300 ms after it. Choose a
timeout and say whether a retry fits.

<details><summary>Answer</summary>

With a target false-timeout rate of 0.1%, start at p99.9 = 140 ms and add padding (connection setup, distant
clients), giving **~150–200 ms** [Amazon Builders' Library]. The remaining deadline when the call starts is
1,000 − 250 − 300 = **450 ms**. One attempt at 200 ms plus a jittered backoff (say up to 50 ms) plus a second attempt
at 200 ms = 450 ms — it just fits, so allow **at most one retry and only if the remaining deadline is ≥ timeout** at
the moment of retrying. Do *not* pick p99.99 (900 ms): it would consume the whole budget for 0.01% of calls and
create bimodal latency. Alternative: a hedged request (send a second copy at ~p95 if the first has not returned) is
acceptable for idempotent reads, but it also needs a budget.
</details>

## 5. Why backoff is not enough [Deep]

Your client already uses exponential backoff with full jitter and up to 3 retries. During a 10-minute partial outage
of a dependency (50% of calls time out), backend load still rises sharply. Explain why, estimate the steady-state
amplification, and propose a fix.

<details><summary>Answer</summary>

Users keep arriving (an **open** system), so backoff only *delays* retries; it does not reduce how many happen
[Brooker, "What is Backoff For?"]. With failure probability p = 0.5 per attempt and up to 4 attempts, expected
attempts per request = 1 + p + p² + p³ = 1 + 0.5 + 0.25 + 0.125 = **1.875×**. Worse, the extra load raises latency,
which raises p, which raises amplification (toward 4× as p → 1) — a feedback loop. Fix: a **retry budget** (token
bucket: first attempts deposit 0.1 token, retries spend 1) caps amplification near 1.1×; add a per-endpoint
**circuit breaker** with a fallback for the hard-down case; and have the server **shed** requests whose deadlines
cannot be met. Backoff and jitter remain useful for desynchronising bursts.
</details>

## 6. Static stability [Core]

Lumen's retrieval tier runs in 3 AZs. Peak load is 30,000 req/s; one instance handles 500 req/s at its safe
utilisation. (a) How many instances must run at all times so that losing any one AZ needs no scale-up? (b) What
changes with 2 AZs? (c) Why not rely on autoscaling?

<details><summary>Answer</summary>

(a) Peak needs 30,000 / 500 = 60 instances. After losing one AZ, the remaining two must hold 60, so each AZ needs 30;
total **90 instances** (1.5× = N/(N−1) for N = 3). (b) With 2 AZs each must carry the full 60: **120 instances** (2×).
More AZs reduce the overhead (4 AZs → 80, 1.33×). (c) Scaling up is a **control-plane** action — launching instances,
pulling images, warming caches — that may be impaired during the very event (the October 2025 AWS event impaired EC2
launches for hours) and is slow relative to the failure. Static stability means the data plane keeps working with no
control-plane action [Furr, "Static stability using Availability Zones"; AWS DR whitepaper].
</details>

## 7. Diagnose a metastable failure [Deep]

Read the summary of the Google Cloud incident of 12 June 2025 (lesson reference [23]). Identify (a) the trigger,
(b) the sustaining effect that prolonged recovery in us-central1, and (c) two design changes that would have shortened
it.

<details><summary>Answer</summary>

(a) Trigger: a policy change with blank fields, replicated globally within seconds, hit a new, unflagged code path
with no error handling (null pointer) and crash-looped Service Control everywhere. (b) Sustaining effect in
us-central1: restarting Service Control tasks all at once overloaded the backing Spanner table — the report says the
service lacked "appropriate randomized exponential backoff" — a herd on recovery that took ~2 h 40 min to work
through with throttled task creation. (c) Any two of: feature-flag the new code path (bug caught in staging, or
disabled instantly); fail open for quota checks; randomized exponential backoff on startup reads; rate-limit task
restarts (recovery velocity control); validate replicated policy data before use; stage global data propagation by
region. Answers naming "add more Spanner capacity" miss the point — the load was self-inflicted by recovery.
</details>

## 8. Breaker or budget? [Deep]

Dependency A sometimes goes fully down for minutes. Dependency B frequently runs at 70–90% success for long periods.
Which protection fits each, and what is the fallback?

<details><summary>Answer</summary>

**A (hard down):** a **circuit breaker** — after the failure ratio crosses the threshold, fail fast, stop wasting
threads and give A room to restart; half-open probes detect recovery. Fallback: cached/stale data or a degraded
feature. **B (partial):** a breaker would flap or, when open, reject the 70–90% of calls that would have succeeded.
Use a **retry budget** (proportional: first attempts always go, retries rationed) plus possibly **adaptive
throttling** (reject a fraction proportional to observed rejections). Keep a breaker on B too, but with a high
threshold so it trips only on near-total failure. In both cases, bulkhead the pools so A's or B's slowness cannot
consume the shared thread pool.
</details>

## 9. Choose a DR strategy [Interview]

Lumen's conversation store: losing more than 5 minutes of writes is unacceptable (RPO); a regional disaster may cause
at most 1 hour of downtime (RTO); the budget does not allow full duplicate capacity. Pick a DR strategy, describe the
failover, and name two traps.

<details><summary>Answer</summary>

**Pilot light or warm standby.** Continuously replicate the store asynchronously to a second region (RPO ≈ replication
lag, comfortably < 5 min if monitored), keep core infrastructure deployed there, and either keep app servers off
(pilot light — must switch on and scale within the hour) or run a small fully functional copy (warm standby — can take
traffic immediately and scales up). Given a 1-hour RTO and the cost limit, warm standby is the safer choice if the
budget allows a small always-on footprint. Failover: a **manually initiated, scripted** switch using data-plane
operations (e.g. DNS/traffic-dial changes already provisioned), promote the replica, scale out. Traps: (1)
replication is not backup — keep point-in-time backups for corruption/deletion; (2) automatic failover on a noisy
health check can cause an unnecessary failover with its own data loss; (3) untested DR — drill it and measure the
achieved RPO/RTO; (4) service quotas in the DR region too low to scale.
</details>

## 10. Design the STRESS answer [Interview]

In an interview you designed a URL shortener. The interviewer asks: "Your database slows to 2 s per query for
5 minutes at peak, then recovers. Walk me through what happens and how the system gets back to normal." Write the
answer as 6–8 bullet points.

<details><summary>Answer</summary>

A strong answer covers both *during* and *after*:
- Redirect reads hit the cache first; most traffic is unaffected (hit ratio stated, e.g. 95%).
- Cache misses call the DB with a timeout from its p99.9 (e.g. 100 ms) inside the request deadline — they time out
  fast instead of holding threads for 2 s.
- No retries at the app layer for misses beyond one, with jitter and a 10% retry budget; the client is told to retry
  later (`503` + `Retry-After`).
- Circuit breaker on the DB opens after the failure ratio crosses the threshold; fallback for unknown short codes is a
  friendly "try again" page; creation requests are queued (or rejected with `503`) rather than piled up.
- Bulkhead: writes and reads use separate pools so a slow write path can't starve redirects.
- Request coalescing on cache misses prevents a stampede when the DB returns.
- After recovery: breaker half-opens, probes succeed, closes; the retry budget prevents a surge; caches refill
  gradually; queued creations drain at a throttled rate.
- Signals: retry ratio, breaker state, DB queue age, goodput; postmortem names the trigger and checks for any
  sustaining effect.
</details>

## 11. Run and explain the lab [Lab]

Run lab L11. (a) Which scenarios recover within 5 seconds after the trigger is removed, and which do not? (b) Explain
the `naive` result using the terms trigger, vulnerable state and sustaining effect. (c) Change `RPS` to 40 and rerun
`naive`. What changes, and why?

<details><summary>Answer</summary>

(a) Compare the `after0-5` column of your own table. In the recorded run (lab README) `none` (100%) and `budget`
(93.6%) are back within 5 s; `shed` needs the 5-15 s window (84.1% in `after5-15`); `naive` and `backoff` stay at 0%
for all 15 s. Your numbers may differ; the README records the outcome observed when the lab was tested.
(b) The backend's capacity (~200 req/s) exceeds normal load (125 req/s), so the system is stable — but with up to 4
attempts per request it is **vulnerable**: any trigger that makes most attempts fail drives offered attempts toward
4 × 125 = 500 req/s. The latency toxic is the **trigger**. Once queued work exceeds what can be served within the
200 ms timeout, every attempt times out, so every request keeps making 4 attempts even after the toxic is gone — the
**sustaining effect** is retry amplification plus the server finishing work nobody is waiting for (the `wasted`
counter). (c) At 40 req/s, 4× amplification is 160 req/s — below the ~200 req/s capacity — so even if every attempt fails, the
backlog cannot grow and the system recovers once the trigger ends: it is no longer in the vulnerable region. At
60 req/s (240 req/s amplified) it is just above capacity, so the backlog grows slowly. Your observed numbers decide;
the point is that vulnerability depends on load × amplification relative to capacity [Bronson et al. 2021].
</details>

## 12. Plan a chaos experiment [Lab]

Write a chaos-experiment plan for Lumen's retrieval dependency using the Principles of Chaos Engineering: steady
state, hypothesis, injected variable, blast radius, abort condition, and what you will learn.

<details><summary>Answer</summary>

- **Steady state:** answer API success rate ≥ 99.9% and p99 ≤ 1.5 s, measured per minute.
- **Hypothesis:** with +300 ms latency on retrieval for 5% of answer-service instances, the steady state holds in the
  experimental group as in the control group (breaker opens or degraded answers are served; no retry amplification
  > 1.1×).
- **Variable:** latency toxic (Toxiproxy or mesh fault injection) between the experimental instances and retrieval.
- **Blast radius:** 5% of instances, one AZ, internal/beta tenants first; 10-minute window.
- **Abort:** automatic rollback if experimental success rate drops below 99.5% for 2 consecutive minutes or retry
  ratio exceeds 1.3.
- **Learn:** whether timeouts, budgets and fallbacks behave as designed; whether dashboards show the injected fault
  (gray-failure detection); whether recovery after removal is immediate. Graduate to production and automation only
  after it passes in staging [principlesofchaos.org; Basiri et al. 2016].
</details>
