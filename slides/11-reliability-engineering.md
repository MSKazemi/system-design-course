# 11 — Reliability engineering (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/11-reliability-engineering.md](../course/01-foundations/11-reliability-engineering.md)

## Slide 1 — The requirement

- Lumen's answer API: 99.95% monthly availability
- Survive the loss of one availability zone with no human action
- Recover on its own within 5 minutes after a dependency brownout ends
- The third line is the hard one: outages are often sustained by how the system *reacts*

**Visual:** Three requirement cards; the third highlighted. Icons: `ops-slo`, `arch-region`, `ops-incident`.

**Speaker notes:** Redundancy handles the first two requirements. The third is about feedback loops — retries,
failovers and restarts that keep a system down after the trigger has gone. That is the thread through this unit.

## Slide 2 — A vocabulary of failure

- Crash (fail-stop) ⊂ omission ⊂ timing ⊂ arbitrary (Byzantine) — Cristian's hierarchy
- Byzantine agreement with unsigned messages needs > 2/3 correct participants (Lamport, Shostak, Pease)
- Cloud services assume crash faults; corruption is handled by validation and staged rollout
- Most real incidents are *partial*: slow, flaky, wrong for some callers

**Visual:** Nested boxes, crash innermost, Byzantine outermost. Icons: `ops-error`, `arch-server`.

**Speaker notes:** Name the failure before choosing the defence. Each class includes the ones inside it, so a defence
for timing failures must also handle crashes.

## Slide 3 — Gray failure and differential observability

- Gray failure: degradation, packet loss, flaky I/O, non-fatal exceptions (Huang et al., HotOS '17)
- Differential observability: the detector says "healthy", a caller sees "broken"
- Example: stuck request handler next to a working heartbeat thread
- Fan-out makes it worse: P(touch a given switch) = 1 − ((n−1)/n)^m ≈ 0.99999 for n = 4, m = 40

**Visual:** Observer box reporting green while an app box reports red against the same system core. Icons:
`pattern-health-check`, `ops-warning`.

**Speaker notes:** Health checks must exercise the user path, and caller-observed error rates are the most honest
signal. More redundancy can make a gray failure touch more requests, not fewer.

## Slide 4 — Availability arithmetic

- Serial hard dependencies multiply: 0.9995⁶ ≈ 99.70% ≈ 129 min/month
- Lumen's whole budget at 99.95% is 21.6 min/month
- Parallel redundancy, 1 − Π(1 − Aᵢ), only holds for independent failures
- Two levers: make dependencies soft, and decorrelate replicas

**Visual:** Chain of six boxes with the product written under it; next to it two replicas sharing a "config push"
arrow that breaks independence. Icons: `ops-slo`, `pattern-replication`.

**Speaker notes:** Six dependencies at the product's own target already blow the budget sixfold. Everything else in
the unit is either making dependencies optional or keeping replicas from failing together.

## Slide 5 — Timeouts and deadlines

- Timeout = dependency latency at your accepted false-timeout rate (e.g. p99.9 for 0.1%)
- One end-to-end deadline, pass the *remaining* budget down (30 s − 7 s spent → 23 s)
- Bimodal latency: 5% of requests hanging 100 s on 1,000 threads → 80.4% errors (SRE book)
- Little's law: slow dependency × arrival rate = exhausted pools upstream

**Visual:** Timeline bar shrinking hop by hop as the deadline propagates. Icons: `pattern-timeout`, `ops-clock`.

**Speaker notes:** Timeouts come from measured percentiles, not intuition, and they must nest inside one deadline.
The bimodal example shows why a deadline far above mean latency is harmful.

## Slide 6 — Retries multiply

- Retry only idempotent operations; honour `429`/`503` + `Retry-After`
- Retry at one layer: 4 attempts × 3 layers = 64× (SRE book); 5 layers, 3 retries = 243× (Builders' Library)
- Capped exponential backoff with full jitter: `sleep = U(0, min(cap, base·2^n))`
- Backoff delays work; it does not remove it in an open system

**Visual:** Call tree fanning out 4 → 16 → 64 at the database. Icons: `pattern-retry`, `arch-database`.

**Speaker notes:** Jitter desynchronises clients; backoff spreads retries in time. Neither bounds total work when new
users keep arriving, which is why the next slide matters.

## Slide 7 — Retry budgets

- Per request: ≤ 3 attempts; per client: retry only while retries < 10% of requests (Google)
- Worst case drops from "just below 3X" to about 1.1× (SRE book)
- Envoy `RetryBudget`: `budget_percent` default 20%, `min_retry_concurrency` default 3
- AWS SDKs: local token bucket for retries since 2016

**Visual:** Token bucket refilled by successes/first attempts, drained by retries. Icons: `pattern-retry`,
`pattern-rate-limiter`.

**Speaker notes:** A budget makes amplification proportional and bounded. It is the single most effective change
against retry storms, and the lab demonstrates it.

## Slide 8 — Circuit breakers and bulkheads

- Breaker: closed → open on failure ratio → half-open trial → closed or open again
- Gives callers a fast signal to fall back; relieves the dependency
- Bulkhead: a bounded pool per dependency or tenant so one hang cannot take every thread
- Cells are bulkheads at deployment scale

**Visual:** State machine (closed/open/half-open) beside a ship hull with compartments. Icons:
`pattern-circuit-breaker`, `pattern-bulkhead`.

**Speaker notes:** Breakers are binary per dependency; budgets are proportional. Use both, and make "open" mean
"degraded", not "error".

## Slide 9 — Load shedding, admission control, degradation

- Goodput ≠ throughput: late answers are wasted work (Yanacek)
- Bound queues by length and age; reject cheaply and early; shed by priority
- Shed by deadline: if the caller will have given up, don't start
- Client-side adaptive throttling: reject locally with p = max(0, (req − K·acc)/(req + 1)), K = 2
- Degrade on purpose: cached answer, skip re-ranker, smaller model

**Visual:** Throughput line rising while goodput collapses past the knee; a second goodput line that plateaus with
shedding. Icons: `pattern-backpressure`, `ops-throughput`.

**Speaker notes:** Overload always drops something; the choice is whether you drop it deliberately. Degradation modes
are product states that must be designed and exercised.

## Slide 10 — Metastable failures

- Stable → vulnerable (load past a hidden threshold) → trigger → metastable, held by a sustaining effect
- Bronson et al.: DB fine at 280 QPS; after a 10 s outage, retries push it to 560 QPS and it never recovers
- 90% cache hit-rate lost → 10× DB load → cache never refills
- Huang et al. (OSDI '22): 22 cases, 11 organisations; ≥ 4 of 15 major AWS outages

**Visual:** State diagram stable/vulnerable/metastable with a self-loop labelled "retries". Icons: `ops-incident`,
`pattern-retry`.

**Speaker notes:** The outage is blamed on the trigger, but the root cause is the sustaining effect. Recovery needs a
strong push: shed load, cut retries, then ramp back up.

## Slide 11 — Postmortems through this lens

- AWS 2021-12-07: connection surge + retries; clients failed to back off; monitoring impaired
- Google Cloud 2025-06-12: unflagged code path crashed globally; restart herd hit Spanner without backoff
- AWS 2025-10-20: empty DynamoDB DNS record → EC2 lease manager "congestive collapse"; NLB failover removed capacity
- Cloudflare 2025-11-18 / CrowdStrike 2024-07-19: global propagation of a bad file

**Visual:** Four timeline strips, each marking trigger and sustaining effect. Icons: `ops-incident`, `cloud-aws`,
`cloud-gcp`, `network-cloudflare`.

**Speaker notes:** Read each vendor report for two things: what tipped it, and what kept it down. Recovery itself is
a load event that needs throttling and backoff.

## Slide 12 — Multi-AZ, static stability, DR

- Static stability: pre-provision N/(N−1) of peak — 1.5× for 3 AZs, 2× for 2
- DR ladder: backup & restore → pilot light → warm standby → active/active
- RTO = max acceptable downtime; RPO = max acceptable data-loss window
- Fail over with data-plane actions; automatic failover needs caution and velocity limits

**Visual:** Ladder of four DR strategies with cost rising and RTO/RPO falling. Icons: `arch-region`,
`pattern-failover`, `pattern-backup`.

**Speaker notes:** Scaling up during a zone loss is a control-plane action that may be impaired, so the spare must
already be running. Replication is not backup: it copies deletions too.

## Slide 13 — Operate it: signals and chaos

- Alert on retry ratio, goodput, queue age, shed rate by priority, breaker flips
- Caller-observed errors per dependency catch gray failure
- Chaos experiment: steady state → hypothesis → inject → try to disprove; minimise blast radius
- Drill DR and measure the RPO/RTO you actually achieve

**Visual:** Dashboard mock with the five signals; chaos loop diagram. Icons: `ops-dashboard`, `ops-alert`.

**Speaker notes:** Pre-build the incident controls — retry kill switch, manual breaker, priority shedding — so they
are flags, not code changes, when you need them.

## Slide 14 — Interview angle and lab

- STRESS question: "dependency slows to 2 s for 5 min — how does it recover?"
- Model answer: timeout in a deadline; one-layer retries with jitter + budget; breaker + fallback; bulkheads + shedding; verify with fault injection
- Red flags: retries at every layer; "add replicas" for correlated failures; no recovery story
- Lab L11: Toxiproxy trigger, five policies, watch which ones recover

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip with STRESS highlighted. Icons:
`pattern-retry`, `pattern-circuit-breaker`.

**Speaker notes:** Interviewers listen for the recovery story. The lab gives you a concrete result to cite: which
retry policy kept the system down after the trigger was removed.
