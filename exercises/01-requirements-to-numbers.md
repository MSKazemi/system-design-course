# 01 — Exercises

Lesson: [course/00-orientation/01-requirements-to-numbers.md](../course/00-orientation/01-requirements-to-numbers.md)

### 1. [Core] Error budget

A request-based SLO of 99.95% over 30 days, with 2 million requests/day. How many failed requests may you have
in the window? If an outage fails *every* request, how many minutes does that budget buy?

<details><summary>Answer</summary>

Requests in 30 days = 2 × 10⁶ × 30 = 60 million. Budget = 0.05% = 0.0005 × 60 × 10⁶ = **30,000 failed
requests**. As full outage time: 0.0005 × 43,200 min = **21.6 minutes**. This assumes traffic is uniform. An
outage at peak burns the request budget faster than its share of minutes, which is why request-based and
time-based budgets differ.
</details>

### 2. [Core] Burn rate

With a 99.9% / 30-day SLO, the error rate over the last hour was 1.44%. What is the burn rate, and what fraction
of the monthly budget did that hour consume? Should it page?

<details><summary>Answer</summary>

Allowed error rate = 0.1%. Burn rate = 1.44% / 0.1% = **14.4×**. One hour is 1/720 of 30 days, so the
consumption = 14.4 / 720 = **2%** of the budget. That is exactly the SRE Workbook's page-level threshold (14.4×
over one hour, confirmed over the last five minutes). Page, if the short window also shows the burn is still
happening.
</details>

### 3. [Core] Availability arithmetic

A request passes through an API gateway (99.95%), an auth service (99.9%) and an application service (99.9%) in
series. (a) What is the best-case availability, assuming independent failures? (b) The application service is
deployed as two independent replicas, each 99.9%, either of which can serve. Recompute.

<details><summary>Answer</summary>

(a) 0.9995 × 0.999 × 0.999 ≈ **0.9975 (99.75%)**: lower than any single component.

(b) The replicated application tier is down only when both replicas are down: 1 − (0.001)² = 0.999999. Total ≈
0.9995 × 0.999 × 0.999999 ≈ **0.9985 (99.85%)**. The auth service is now the weakest link. The caveat is
independence. Two replicas fed by the same bad configuration push fail together, and the real number is closer
to (a).
</details>

### 4. [Core] Little's law, pool sizing

A service handles 2,000 requests/s at peak with a mean latency of 150 ms. Each request holds a database
connection for 12 ms. (a) How many requests are in flight? (b) How many database connections are busy on
average? (c) The service has 200 worker threads. What happens?

<details><summary>Answer</summary>

(a) L = λW = 2,000 × 0.150 = **300 in flight**.
(b) L = 2,000 × 0.012 = **24 connections** busy on average. Size the pool at perhaps 2–3× for variance and
peaks, so about 50–75, and check that the database can take that many connections from every instance.
(c) Only 200 requests can be served at once, so about 100 wait in a queue (accept backlog or executor queue).
Queueing adds latency, which raises W, which by Little's law raises L further. The service is at saturation. Add
threads (if CPU allows), go asynchronous, or add instances. Watching L climb while λ is flat is the early-warning
signal.
</details>

### 5. [Core] Utilisation and latency

A single-worker service has a mean service time of 20 ms. Using M/M/1, compute the mean and p99 latency at 50%,
80% and 95% utilisation. At which utilisation does p99 exceed a 300 ms SLO?

<details><summary>Answer</summary>

W = S / (1 − ρ); p99 = ln(100) × W ≈ 4.6 W.

| ρ | W | p99 |
|---|---|---|
| 0.5 | 40 ms | 184 ms |
| 0.8 | 100 ms | 460 ms |
| 0.95 | 400 ms | 1,840 ms |

p99 = 300 ms when W = 300 / 4.605 ≈ 65 ms, that is when 20 / (1 − ρ) = 65, so ρ ≈ **0.69**. Above roughly 70%
utilisation this service breaks its p99 SLO, even though it is "only" 70% busy. That is the hockey stick in
action. Smoother arrivals (lower c_a) or less variable service (lower c_s) move the threshold up, as Kingman's
formula shows.
</details>

### 6. [Core] Fan-out

A page fans out to 50 backends in parallel and waits for all. Each backend's p99 is 200 ms. (a) What fraction of
page loads wait 200 ms or more? (b) What per-backend percentile must you hit for only 1% of page loads to wait
that long?

<details><summary>Answer</summary>

(a) P(all fast) = 0.99⁵⁰ ≈ 0.605, so about **39.5%** of page loads include at least one slow backend.
(b) We need p⁵⁰ = 0.99, so p = 0.99^(1/50) ≈ 0.99980. Each backend must be under 200 ms **99.98%** of the time,
roughly a p99.98 target. Alternatives: reduce fan-out, hedge requests, or accept partial results after a
deadline.
</details>

### 7. [Core] Launch-day estimate

Redo the lesson's launch-day estimate with 2 million DAU, 40 requests per user per day, a busiest-hour share of
10% and a minute burst factor of 1.5. CPU is 15 ms per request. How many cores at 60% target utilisation?

<details><summary>Answer</summary>

Requests/day = 2 × 10⁶ × 40 = 80 M. Busiest hour = 0.10 × 80 M / 3,600 ≈ 2,222/s. Peak minute ≈ 3,333/s, call it
**3,500/s**. CPU = 3,500 × 0.015 = 52.5 cores busy, so at 60%: 52.5 / 0.6 ≈ **88 cores**. That is several
servers before any redundancy. With N+1 or zone redundancy (SYSDESIGN-03), plan for perhaps 6–8 servers of
16–24 cores. State the assumptions, because the busiest-hour share is the one most worth challenging.
</details>

### 8. [Deep] Pooling

Two servers, each with mean service time 10 ms, receive 160 requests/s in total. Compare the mean latency of
(a) random assignment to two separate queues and (b) one shared queue (M/M/2). What does this suggest for load
balancer design?

<details><summary>Answer</summary>

Per server capacity = 100/s, so ρ = 160 / 200 = 0.8.
(a) Each server is an M/M/1 at 80 requests/s: W = 10 / (1 − 0.8) = **50 ms**.
(b) M/M/2: W = S / (1 − ρ²) = 10 / 0.36 ≈ **27.8 ms**.
A shared queue nearly halves latency at the same utilisation, because no request waits behind a busy server while
another is idle. Balancers approximate this by sending work to the less busy server (least-outstanding requests,
power of two choices) instead of blindly at random or in turn (SYSDESIGN-03).
</details>

### 9. [Deep] Kingman and variability

A service at ρ = 0.8 with S = 10 ms has c_s = 1 (exponential service). Compare the approximate mean queueing delay
for (a) Poisson arrivals (c_a = 1), (b) perfectly regular arrivals (c_a = 0), and (c) bursty arrivals (c_a = 2).

<details><summary>Answer</summary>

W_q ≈ (ρ / (1 − ρ)) × ((c_a² + c_s²) / 2) × S = 4 × ((c_a² + 1) / 2) × 10 ms.
(a) 4 × 1 × 10 = **40 ms**. (b) 4 × 0.5 × 10 = **20 ms**. (c) 4 × 2.5 × 10 = **100 ms**.
The same utilisation gives 2.5× more queueing with bursty traffic than with Poisson. Kingman's formula is an
approximation that is most accurate in heavy traffic, so treat these as estimates. Lab L01 uses regular arrivals,
so expect measured delays below the M/M/1 prediction.
</details>

### 10. [Core] Tokens

Lumen expects 100,000 chat generations per hour at peak. Each has 1,500 input and 500 output tokens. Streams run
at 25 output tokens/s after a 0.8 s time to first token. Compute (a) prefill and decode tokens/s, (b) concurrent
streams, (c) daily tokens if the peak hour is 12% of the day.

<details><summary>Answer</summary>

Rate = 100,000 / 3,600 ≈ 27.8 generations/s.
(a) Prefill = 27.8 × 1,500 ≈ **41,700 tokens/s**. Decode = 27.8 × 500 ≈ **13,900 tokens/s**.
(b) Stream duration = 0.8 + 500 / 25 = 20.8 s, so L = 27.8 × 20.8 ≈ **578 concurrent streams**.
(c) Daily generations = 100,000 / 0.12 ≈ 833,000. Tokens = 833,000 × 2,000 ≈ **1.7 billion tokens/day**.
The number of GPUs needs a measured tokens/s per GPU *at the latency targets* for your model and engine
(SYSDESIGN-21, SYSDESIGN-22). Don't guess it.
</details>

### 11. [Interview] Will one server survive?

The interviewer says: "We expect 50 million requests a day. Can one server handle it?" Give a two-minute answer.

<details><summary>Answer</summary>

"50 M/day is about 580/s on average. With a peak-to-average ratio of perhaps 3–4×, call it **2,000/s at peak**.
Whether one server can serve that depends on per-request cost. At 5 ms of CPU it's 10 cores busy, which fits one
big box at a healthy utilisation. At 50 ms it's 100 cores, so no. But even when it fits, I wouldn't run one
server: one failure or deploy is a full outage, and a 99.9% SLO allows 43 minutes a month. So I'd run at least
three instances across zones, each sized so that two can carry the peak below about 70% utilisation. Then I'd
confirm the per-instance knee with an open-model load test." Strong answers state the assumption (CPU per
request, peak factor) and separate *capacity* from *availability*.
</details>

### 12. [Lab] Predict, then measure

Before running lab L01, run `python3 predict.py 10 50 80 90 95` and write down the D/M/1 p99 at 90 requests/s.
After the sweep, compare it with the measured p99. List three reasons the measurement may differ.

<details><summary>Answer</summary>

`predict.py` gives a D/M/1 mean of about 52 ms and p99 of about 239 ms at 90 requests/s (S = 10 ms). The
measurement will differ because of: (1) HTTP, Docker networking and Python overhead adding roughly a millisecond
or more per request, and sometimes more under load; (2) the finite test (30 s at high utilisation is short, so
the queue may not reach steady state and percentiles are noisy); (3) timer and scheduling granularity in
`time.sleep` and thread wake-ups, which make the real service-time distribution not exactly exponential;
(4) k6's own scheduling jitter making arrivals slightly less regular than D. The *shape* (flat, then a sharp rise
near ρ = 1) is the result to look for. Agreement within tens of percent is good. See the lab README's Test status
for what was observed.
</details>
