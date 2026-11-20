---
id: SYSDESIGN-01
title: "Requirements to numbers: SLIs/SLOs, estimation, latency numbers, Little's law, queueing"
part: "0 — Orientation"
level: [core, deep, frontier]
status: DRAFT
prerequisites: [SYSDESIGN-00]
estimated_time: "3h reading + 1.5h lab"
requirement: "Decide, before launch day, whether one server survives 500,000 daily active users with 99.9% of requests succeeding and p99 latency under 300 ms"
learning_objectives:
  - "Turn vague requirements (fast, reliable, scalable) into SLIs, SLOs and error budgets"
  - "Estimate requests/s, concurrency, storage and bandwidth from user numbers, stating every assumption"
  - "Apply Little's law and the M/M/1 utilisation–latency curve to size servers, pools and queues"
  - "Explain why tail latency dominates fan-out systems and how hedging and headroom address it"
  - "Estimate an LLM workload in tokens/s and concurrent streams instead of requests/s"
last_reviewed: 2026-11-20
---

# 01 — Requirements to numbers

> **The requirement.** Lumen launches on Monday. Marketing expects **500,000 daily active users** on day one.
> Product wants it to be "fast and reliable". The CTO asks one question: *will one server survive launch day?*
> You can't answer with adjectives. You can answer only after turning "fast" and "reliable" into measurable
> targets, turning "500,000 users" into requests per second at the busiest minute, and knowing how a server
> behaves as it approaches its limit. Here is the uncomfortable part: a server at 95% utilisation is not "5%
> away from trouble". By the arithmetic of queues, its average latency is already **20 times** its unloaded
> latency.

## In one minute

Every design starts as words: fast, reliable, scales. This chapter turns words into numbers in four moves.
First, define *what you measure* (a **service level indicator**, for example the fraction of requests answered
successfully within 300 ms) and *what target you promise yourself* (a **service level objective**, for example
99.9% of them over 30 days). The gap between 100% and the target is an **error budget** you are allowed to spend.
Second, **estimate** with round numbers. A day has about 100,000 seconds, so a million requests a day is about 12
per second on average, and several times that at the peak. Third, use **Little's law**: requests in flight =
arrival rate × time each spends inside. It tells you how many threads, connections and GPUs you need. Fourth,
respect the **utilisation curve**. Queueing makes latency explode as a server nears 100% busy, so you plan to
run well below it. Then, because users wait for the *slowest* part of their request, you design for the
**tail** (p99), not the average.

## Why this matters now

- **Requirements now arrive with a bill attached.** In the cloud every request has a marginal cost. "Make it
  99.99%" is now a budget conversation as much as a technical one. SLOs, popularised by Google's SRE books
  [1][2], have become the common language between product, engineering and finance.
- **The classic latency table is old.** The "numbers everyone should know" most engineers learned were published
  by Jeff Dean in 2009 [6]. Disks, SSDs and networks have changed by orders of magnitude since then, and the
  speed of light has not. Knowing *which* numbers drift and which don't is a skill in its own right.
- **AI workloads are measured in tokens, not requests.** One LLM chat request can cost a thousand times more
  compute than a page view, and its latency has two parts: time to first token, and time per output token.
  Estimating them takes the same tools (Little's law, utilisation, tails) applied to a new unit. The last part
  of this chapter previews that, and SYSDESIGN-21 develops it.

## Core ideas [Core]

### From adjectives to requirements

Split requirements into two kinds.

- **Functional:** what the system does. "A user can ask a question about their documents and get an answer with
  citations."
- **Non-functional:** how well it does it. Latency, availability, durability, throughput, cost, security,
  compliance, energy.

Non-functional requirements are where designs differ, and they are the ones people state as adjectives. The
conversion pattern is always the same: **metric, threshold, population, window.**

| Adjective | Requirement |
|---|---|
| "Fast" | 99% of `GET /answer` requests from EU users get the first byte within 300 ms, measured over 30 days |
| "Reliable" | 99.9% of API requests succeed (non-5xx), over a rolling 30 days |
| "Durable" | Once a document is acknowledged as uploaded, the probability of losing it is below 10⁻¹¹ per year |
| "Scales" | Sustains 3× the forecast peak for 1 hour without breaching the latency target |

### SLIs, SLOs, SLAs and error budgets

The Google SRE book defines these terms crisply [1]:

- An **SLI** (service level indicator) is "a carefully defined quantitative measure of some aspect of the level
  of service that is provided". Good SLIs are ratios of good events to valid events: successful requests ÷ all
  requests, or requests faster than 300 ms ÷ all requests.
- An **SLO** (service level objective) is "a target value or range of values for a service level that is
  measured by an SLI": 99.9% of requests good over 30 days.
- An **SLA** (service level agreement) is a *contract* with consequences, usually credits, if it is missed. Set
  SLAs looser than internal SLOs, so the SLO warns you before the contract is breached.

The **error budget** is 1 − SLO. The SRE book presents it as a tool that "aligns incentives and emphasizes joint
ownership between SRE and product development" [2]. While budget remains, ship features and take risks. When it
runs out, slow releases and spend effort on reliability. The decision rule is agreed *in advance*, so nobody
argues about it during an incident.

What a budget means in practice:

| SLO (30-day window) | Error budget | As downtime, if every request fails | As failed requests at 15 M requests/day |
|---|---|---|---|
| 99% | 1% | 7.2 hours | 4.5 million |
| 99.9% | 0.1% | 43.2 minutes | 450,000 |
| 99.95% | 0.05% | 21.6 minutes | 225,000 |
| 99.99% | 0.01% | 4.3 minutes | 45,000 |

(30 days = 43,200 minutes. 0.1% of that is 43.2 minutes.)

Two subtleties catch people out.

1. **Request-based versus time-based.** "99.9% of requests" and "99.9% of minutes" differ. An outage at 3 a.m.
   costs few requests but many minutes. Choose the one that matches user harm. For most user-facing APIs that is
   request-based.
2. **Alert on burn rate, not on budget left.** Burn rate is how fast you are consuming budget relative to the
   rate that would use exactly 100% in the window. The SRE Workbook's recommended page for a 99.9%, 30-day SLO
   fires at a **14.4× burn rate** sustained over both the last hour and the last five minutes. That condition
   means 2% of the month's budget has gone in one hour (14.4 × 1 h / 720 h = 0.02) [3]. SYSDESIGN-12 builds this
   alert.

### Availability arithmetic: dependencies multiply

If a request must pass through three services that are each available 99.9% of the time, and their failures are
independent, the chance that all three work is 0.999³ ≈ **99.7%**. Serial dependencies *multiply*
availabilities, so a chain of "three nines" components is not three nines. Redundancy works the other way. Two
independent replicas that are each 99% available are both down only 0.01² = 0.01% of the time, so the pair is
available **99.99%**. The word doing the work is *independent*. Replicas that share a power feed, a
configuration push or a software bug fail together, and the formula then flatters you (SYSDESIGN-11).

### Percentiles, not averages

Latency distributions are skewed: most requests are fast, a few are very slow. The **mean** hides the slow ones.
The **median (p50)** says what a typical request sees. The **p99** says what the slowest 1% see, and a user who
makes 100 requests in a session will, on average, see one of them. Three rules:

- **Report percentiles of the distribution you care about** (client-observed, not server-internal, where you can).
- **Percentiles do not average.** The mean of ten servers' p99s is not the fleet's p99. Aggregate histograms,
  then compute percentiles.
- **Pick the percentile that matches user harm.** p99 for interactive APIs. p99.9 when one request fans out to
  many backends (see tail latency below).

### Back-of-envelope estimation

Estimation is not guessing. It is **stating assumptions explicitly and propagating them with simple
arithmetic**, so a reviewer can disagree with an assumption rather than with your conclusion. The working
constants:

| Constant | Value | Rounded for mental arithmetic |
|---|---|---|
| Seconds per day | 86,400 | ≈ 10⁵ |
| Seconds per month (30 d) | 2,592,000 | ≈ 2.6 × 10⁶ |
| Seconds per year | ≈ 3.15 × 10⁷ | ≈ π × 10⁷ |
| 1 million requests/day | ≈ 11.6 requests/s average | ≈ 12/s |
| 1 KB × 1 billion | 1 TB | — |
| 1 Gbit/s | 125 MB/s | — |

The method:

1. Write the **users → actions → requests** chain with one assumption per arrow.
2. Compute the **average** rate, then apply a **peak factor** (busiest hour and busiest minute). Systems fail at
   the peak, not at the average.
3. Convert to **resources**: CPU-seconds, concurrency (Little's law), storage, bandwidth.
4. Add **headroom** for utilisation (queueing), failures (N+1, zone loss) and growth.
5. **Sanity-check** each result against a known reference: "1,000 requests/s is a lot for one Python process
   and trivial for a fleet."

### Latency numbers, and how they drift

Dean's LADIS 2009 keynote listed "Numbers Everyone Should Know" [6]:

| Operation (Dean, 2009) | Latency | What changed since (as of 2026-11) |
|---|---|---|
| L1 cache reference | 0.5 ns | About the same: clock speeds stopped rising in the mid-2000s [7] |
| Branch mispredict | 5 ns | About the same |
| L2 cache reference | 7 ns | About the same |
| Mutex lock/unlock | 25 ns | Uncontended, similar. Contended, it can be microseconds |
| Main memory reference | 100 ns | About the same: DRAM latency has barely improved [7] |
| Compress 1 KB with a fast compressor | 3,000 ns (3 µs) | Codec- and CPU-dependent; benchmark your own |
| Send 2 KB over a 1 Gbit/s network | 20,000 ns (20 µs) | Scales with NIC bandwidth: about 25–125× less at 25–100 Gbit/s |
| Read 1 MB sequentially from memory | 250,000 ns (250 µs) | Lower: memory bandwidth has grown; measure on your hardware |
| Round trip within the same datacenter | 500,000 ns (500 µs) | Depends on fabric and software stack; Scott's extrapolation holds it constant [7]. Measure it |
| Disk seek | 10,000,000 ns (10 ms) | Unchanged for spinning disks; NVMe flash has no seek |
| Read 1 MB sequentially from disk | 20,000,000 ns (20 ms) | NVMe SSD: about 0.13 ms at 7,450 MB/s [9] |
| Packet California → Netherlands → California | 150,000,000 ns (150 ms) | Unchanged: bounded by the speed of light in fibre |

Two modern reference points with sources:

- A current consumer NVMe SSD (Samsung 990 PRO) is specified at **7,450 MB/s sequential read** and **22,000
  random 4 KB read IOPS at queue depth 1** [9]. At queue depth 1 that implies about **45 µs per random read**
  (1 / 22,000 s). That is roughly 200× faster than a disk seek, and still about 450× slower than a DRAM access.
- Light in fibre travels at about 2/3 c, about **204,000 km/s** [8]. Measured London ↔ New York round trips
  averaged about **70 ms** in WonderNetwork's ping data from November 2026 [10]. The great-circle distance is
  about 5,570 km, so the physical floor over a perfect straight fibre would be about 55 ms. Real cable routes are
  longer, and routers add delay.

**How to use the table without being fooled by it.** Colin Scott's interactive version extrapolates each number
by year, using explicit growth assumptions: bandwidths that double every two to three years, memory latency
held flat, and network round trips held constant because physics bounds them [7]. Its lesson is not any one
value. It is the *ratios* and *which ones move*. Memory is about 100× faster than an SSD read, which is about
100× faster than a cross-continent round trip. Bandwidth keeps improving and latency mostly doesn't. **Date
every number you quote, and measure the ones your design depends on.**

### Little's law: the most useful equation in capacity planning

For any stable system observed over a long period, John Little proved in 1961 that

> **L = λ W**

where **L** is the average number of items in the system, **λ** the average arrival rate, and **W** the average
time an item spends in the system [4]. It holds regardless of the arrival distribution, the service
distribution, or the scheduling order. It applies to a CPU run queue, a thread pool, a database connection
pool, a Kafka consumer group, a GPU's batch of sequences, or a whole data centre. Little's own retrospective on
its 50th anniversary surveys how widely it applies [5].

Three ways to use it:

- **Size a pool.** 1,000 requests/s, each holding a database connection for 8 ms: on average L = 1,000 × 0.008
  = **8 connections** are busy. Size the pool for peak and variance (2–3× that), not for the average.
- **Find concurrency.** 1,000 requests/s with a 200 ms average latency means **200 requests in flight**. A
  server with 64 worker threads will queue the rest.
- **Detect a problem.** If λ is steady and L (in flight, or queue depth) is climbing, W is climbing. You are
  near or past saturation.

### Utilisation vs latency: why 95% busy is not 5% from trouble

Little's law tells you *how many* requests are in the system. Queueing theory tells you *how long* they wait.
The simplest model, **M/M/1**, has random (Poisson) arrivals, exponentially distributed service times with mean
S, and one server. With utilisation **ρ = λ S** (the fraction of time the server is busy), the mean time in
system is

> **W = S / (1 − ρ)**

| Utilisation ρ | Mean time in system W | p99 time in system (M/M/1) |
|---|---|---|
| 50% | 2 S | 9.2 S |
| 70% | 3.3 S | 15.4 S |
| 80% | 5 S | 23 S |
| 90% | 10 S | 46 S |
| 95% | 20 S | 92 S |
| 99% | 100 S | 460 S |

In M/M/1 the time in system is itself exponentially distributed with rate (1 − ρ)/S, so **p99 = ln(100) × W ≈
4.6 W** [11]. With S = 10 ms, a server at 90% utilisation has a mean latency of 100 ms and a p99 of about 460 ms.
That is already outside a 300 ms SLO, while the server is still "only" 90% busy.

The curve is a hockey stick. Latency barely moves until about 60–70% utilisation, then turns sharply upward,
heading to infinity at 100%. That is why capacity planners **target 50–70% utilisation for latency-sensitive
services**: not out of waste, but because the last 30% of capacity can be used only by accepting much worse
latency.

**Variability is the other half.** Kingman's heavy-traffic approximation for a single-server queue with general
arrival and service distributions (G/G/1) [12] says the mean wait in the queue is approximately

> W_q ≈ (ρ / (1 − ρ)) × ((c_a² + c_s²) / 2) × S

where c_a and c_s are the coefficients of variation (standard deviation ÷ mean) of inter-arrival and service
times. For M/M/1 both are 1, and you recover W_q = ρS/(1 − ρ). If arrivals were perfectly regular and service
perfectly constant (both 0), there would be no queue at all until 100%. **Queueing comes from utilisation
multiplied by variability.** Bursty traffic and occasional slow requests (garbage collection, cache misses, a
huge prompt) make it worse. Smoothing either one helps.

### Tail latency at scale

Dean and Barroso's *The Tail at Scale* (CACM, 2013) makes the fan-out problem concrete. Suppose a server
typically responds in 10 ms, but with a 99th-percentile latency of one second. If a user request must collect
responses from 100 such servers in parallel, "63% of user requests will take more than one second" [13]. The
arithmetic: the request is fast only if *all* 100 leaves are fast, and 0.99¹⁰⁰ ≈ 0.366, so 1 − 0.366 ≈ 63% of
requests see at least one slow leaf.

Two consequences:

- **Fan-out raises the percentile you must engineer.** For the *overall* request to be slow at most 1% of the
  time with fan-out 100, each leaf must be slow at most about 0.01% of the time (1 − 0.9999¹⁰⁰ ≈ 1%). Leaves
  need p99.99 targets, not p99.
- **You can't eliminate variability, but you can tolerate it.** Their techniques include hedged requests
  (send a second copy after a short delay, use whichever answer arrives first), tied requests, micro-partitions
  and selective replication. In one Google benchmark, reading 1,000 keys spread over 100 servers, hedging after
  10 ms reduced the 99.9th-percentile latency from 1,800 ms to 74 ms while sending just 2% more requests [13].

### Capacity planning

Capacity planning combines everything above into one repeatable procedure:

1. **Forecast demand at the peak**, with explicit assumptions and a range (expected, high).
2. **Measure per-instance capacity at the SLO.** Find the "knee": the highest load at which one instance still
   meets the latency target. Don't use the theoretical maximum. This is lab L01.
3. **Divide**, then add **redundancy** (N+1, or Z/(Z−1) for zone loss), **growth during lead time** (how long it
   takes to get more capacity: seconds for autoscaling, weeks for hardware or GPU quota), and **burst headroom**.
4. **Validate with a load test** that uses an **open** workload model. Arrivals must keep coming at the target
   rate even when the system slows down, as real users do. A closed model, where each virtual user waits for its
   previous response, quietly lowers its own request rate as latency rises. That hides the knee. k6's
   documentation names this effect *coordinated omission* and implements the open model in its arrival-rate
   executors [14].
5. **Re-plan on a schedule** and whenever the workload changes shape (a new feature, a new model, a new customer).

## Numbers that matter

### Worked example: will one server survive Lumen's launch day?

**Assumptions** (every one is labelled and can be challenged):

| # | Assumption | Value |
|---|---|---|
| A1 | Daily active users on launch day | 500,000 |
| A2 | API requests per active user per day (pages, search, history, polling) | 30 |
| A3 | Share of the day's traffic in the busiest hour | 15% (launch-day spike; a mature product is often lower) |
| A4 | Busiest minute ÷ busiest-hour average | 1.5 |
| A5 | CPU time per request (measured on a dev box) | 20 ms of one core |
| A6 | Mean latency per request, including database time | 80 ms |
| A7 | Average response size | 20 KB |

**Step 1 — requests per second.**
- Requests/day = 500,000 × 30 = **15 million**.
- Average = 15 × 10⁶ / 86,400 ≈ **174 requests/s**.
- Busiest hour = 0.15 × 15 × 10⁶ / 3,600 ≈ **625 requests/s**.
- Busiest minute = 625 × 1.5 ≈ **940 requests/s**. Round up to **1,000 requests/s** as the design peak.

**Step 2 — CPU.** 1,000 requests/s × 0.020 core-seconds = **20 cores busy** at peak. To stay at about 60%
utilisation, which keeps queueing delay small, you need about 20 / 0.6 ≈ **34 cores**.

**Step 3 — concurrency (Little's law).** L = 1,000 × 0.080 = **80 requests in flight**. The server needs at
least 80 concurrent workers or an asynchronous runtime, plus margin.

**Step 4 — bandwidth.** 1,000 × 20 KB = 20 MB/s ≈ **160 Mbit/s** at peak. A 1 Gbit/s link is not the
constraint.

**Step 5 — the answer.** On *capacity*, one large server (a 48- or 64-core machine) could carry the launch peak at
a comfortable utilisation. On *availability*, it cannot. One machine is one failure, one kernel patch or one bad
deploy away from 100% downtime, and the 99.9% SLO allows only 43 minutes of that per month. The defensible
answer is: **"Three smaller servers across two or more zones, each sized so that any two carry the peak at under
70% utilisation."** That is 34 / 0.7 ≈ 49 cores' worth across two servers, so three servers of 24–32 cores each.
SYSDESIGN-03 refines this with zone-loss arithmetic.

### Worked example: storage for a year of chat history

**Assumptions:** 500,000 DAU × 8 questions/day. Each stored exchange is a 300-byte question, a 2 KB answer and
200 bytes of metadata, about 2.5 KB in total. Kept for one year. Three replicas.

- Per day: 500,000 × 8 × 2.5 KB = **10 GB/day**.
- Per year: 10 GB × 365 ≈ **3.65 TB** of raw data. With 3 replicas ≈ **11 TB**, before indexes, embeddings and
  backups. Embeddings for retrieval can be larger than the text itself: SYSDESIGN-24 does that arithmetic.

### Worked example: queue length at the knee

One instance has a mean service time S = 10 ms (capacity 100 requests/s) and receives 90 requests/s. Then
ρ = 0.9, M/M/1 gives W = 10 / (1 − 0.9) = **100 ms** and p99 ≈ 4.6 × 100 = **460 ms**, and Little's law gives
L = 90 × 0.1 = **9 requests in the system**. At 95 requests/s: W = 200 ms, L = 19. Five percent more load
doubles both. Lab L01 reproduces this curve with a real service and measures how closely it follows theory.

### Token-based estimation preview (LLM workloads)

For an LLM feature, "requests per second" is the wrong unit, because cost and latency scale with **tokens**. As a
rule of thumb for English text with GPT-style tokenisers, one token is about four characters, or about ¾ of a
word, so 100 tokens ≈ 75 words. Exact counts depend on the model's tokenizer [15]. Count with the real tokenizer
before you commit to numbers.

**Assumptions:** 500,000 DAU × 8 questions/day = 4 million generations/day. Busiest-hour share 15%. Each request
has **2,000 input tokens** (question + retrieved context + conversation history) and **350 output tokens**
(≈ 260 words). The service targets **30 output tokens/s per user** while streaming, plus about 1 s to the first
token.

- Peak generation rate = 0.15 × 4 × 10⁶ / 3,600 ≈ **167 requests/s**.
- **Prefill** (input) tokens at peak = 167 × 2,000 ≈ **334,000 tokens/s**.
- **Decode** (output) tokens at peak = 167 × 350 ≈ **58,000 tokens/s**.
- Each stream lasts about 1 s + 350 / 30 ≈ **12.7 s**, so by Little's law the system holds about 167 × 12.7 ≈
  **2,100 concurrent streams** at peak.
- Daily volume ≈ 4 × 10⁶ × 2,350 ≈ **9.4 billion tokens/day**.

How many GPUs that needs depends on a number you must *measure*: tokens/s per GPU *while meeting* the latency
targets (time to first token and time per output token) for your model and serving engine. If a benchmark shows
X decode tokens/s per GPU at your latency targets, decode needs about 58,000 / X GPUs before headroom. Prefill,
memory for 2,100 concurrent KV caches, and the fact that input tokens and output tokens cost very different
amounts of compute are the subject of SYSDESIGN-21 and SYSDESIGN-22. The point here is the method: **users →
requests → tokens → concurrency**, with Little's law in the middle, exactly as for a web API.

## Design choices and trade-offs

| Choice | Option | Wins when | Costs |
|---|---|---|---|
| SLI type | Request-based (good requests ÷ total) | User-facing APIs with steady traffic | Low-traffic hours carry little weight |
| | Time-based (good minutes ÷ total) | Low or bursty traffic; contractual uptime | One bad minute counts the same at 3 a.m. and at peak |
| SLO strictness | 99.9% | Most user-facing products | 43 min/month of budget; most teams can afford the work |
| | 99.99% | Payments, auth, core platforms others depend on | Multi-zone or region redundancy, slower releases, much higher cost |
| Latency target | p99 | Interactive APIs | Needs enough traffic for a stable estimate |
| | p99.9 / p99.99 | Leaves of fan-out systems | Expensive; hedging and replication required |
| Load-test model | Open (arrival rate) | Finding the knee; user-facing traffic | Can overwhelm a fragile system quickly |
| | Closed (fixed users) | Systems with a hard concurrency cap (batch, worker pools) | Hides queueing (coordinated omission) |
| Estimation | Top-down (users → requests) | New products, interviews | Assumptions dominate |
| | Bottom-up (measured per-request cost × forecast) | Existing systems with telemetry | Needs good measurements |

## Deep dive [Deep]

### Why Little's law needs no assumptions

The proof idea fits on a napkin. Plot the number of items in the system, N(t), over a long interval T. The area
under the curve, ∫N(t)dt, can be computed two ways: as average height × width (L × T), or as the sum of each
item's time in the system (number of items × average stay = λT × W). Equate them and you get L = λW. Nothing in
the argument cares *how* items arrive or are served, only that the system is stable and the interval long
enough that items in transit at the edges don't matter [4][5]. Lab L01's service measures the area directly
(it integrates N(t)) and compares it with λ × W computed from completed requests, so you can watch the law hold
on a real system.

### Pooling: why one queue for many servers beats many queues

Compare two ways of using two servers, each with mean service time S, at total utilisation ρ = 0.8:

- **Two separate M/M/1 queues** (requests are assigned at random and can't move): each has W = S / (1 − 0.8)
  = **5 S**.
- **One shared queue feeding both (M/M/2)**: W = S / (1 − ρ²) = S / 0.36 ≈ **2.8 S** [11].

The shared queue nearly halves latency at the same hardware and utilisation, because a request never waits behind
a busy server while the other one is idle. This is the theoretical case for **work-conserving** designs: a
shared worker pool, least-outstanding-requests balancing, work stealing. It is also why "power of two choices"
works so well (SYSDESIGN-03): it recovers much of the pooling benefit without a shared queue.

### Evenly spaced arrivals: the D/M/1 case

Load generators often produce *evenly spaced* arrivals rather than Poisson ones. k6's `constant-arrival-rate`
executor starts iterations on a fixed schedule [14]. With constant inter-arrival times and exponential service,
the system is D/M/1, a special case of G/M/1. Its time in system is still exponential, with rate μ(1 − σ), where
σ ∈ (0, 1) solves σ = e^(−(1−σ)/ρ) [16]. At ρ = 0.9 this gives a mean of about 52 ms for S = 10 ms, roughly half
the M/M/1 value. Regular arrivals remove the arrival half of Kingman's variability term. The lab ships a
`predict.py` that prints both models, so you can compare your measurements with the right one. Real user traffic
is usually *burstier* than Poisson, so production queues tend to be worse than both.

### Coordinated omission, in one paragraph

If a load generator sends the next request only after the previous one returns, a 2-second stall produces *one*
slow sample, not the hundreds that real users arriving during those 2 seconds would have experienced. The
measured p99 then looks excellent exactly when the system is failing. The fixes: use an **open model**
(arrival-rate executors) [14], or correct the recorded latencies by the intended start times. When someone shows
you a latency report, ask first which model produced it.

### The tail compounds with depth as well as width

Fan-out width multiplies tail exposure (1 − p^N). So does depth: a request that passes through five services in
series has five chances to hit a slow instance. Each layer that adds a timeout-and-retry also adds load exactly
when the system is slowest (SYSDESIGN-11). The arithmetic of the tail is why mature systems cap fan-out, keep
critical paths short, and give leaves stricter latency targets than the front end.

## Frontier [Frontier]

*(as of 2026-11)*

- **SLOs for generative AI** are stated per phase, not per request. The usual metrics are **time to first token
  (TTFT)** and **time per output token (TPOT)** or inter-token latency, often combined into **goodput**: requests
  per second that meet *both* targets. DistServe (OSDI 2024) made goodput under TTFT and TPOT constraints its
  optimisation target and reported serving up to 7.4× more requests or meeting 12.6× tighter SLOs than the
  systems it compared against [17]. SYSDESIGN-21 defines these metrics properly.
- **Token budgets are error budgets' cousins.** Rate limits and quotas for LLM APIs are commonly expressed in
  tokens per minute as well as requests per minute, because one request can be 100 tokens or 100,000.
  Capacity planning follows the same unit (SYSDESIGN-26).
- **Energy is becoming a stated non-functional requirement.** The IEA estimates that data centres used about
  **415 TWh in 2024, around 1.5% of the world's electricity**, and projects about **945 TWh by 2030** [18].
  "Joules per request" or "watt-hours per 1,000 tokens" is starting to appear next to latency and cost in
  requirements (SYSDESIGN-17).

## Failure modes and operations

| Failure | What it looks like | Detect with | Mitigate |
|---|---|---|---|
| Wrong SLI (measures the server, not the user) | Dashboards green, users complaining | Compare server-side SLI with client or synthetic probes | Measure as close to the user as practical |
| Averaged percentiles | Fleet "p99" looks fine while some hosts are terrible | Per-host histograms | Aggregate histograms, never percentiles |
| Planning for the average, not the peak | Fine all day, falls over at 9 a.m. or on launch day | Peak-to-average ratio from history | Peak factors in every estimate; load-test at the peak |
| Running hot | p99 creeps up long before CPU hits 100% | Utilisation vs latency curve per service | Target 50–70%; autoscale on demand |
| Coordinated omission in load tests | Load test passes, production fails | Check the test's workload model | Open-model (arrival-rate) tests |
| Budget exhausted silently | Month ends with the SLO missed and no one was paged | Burn-rate alerts | Multi-window burn-rate alerting [3] |
| Retries counted as traffic | Load doubles during incidents | Attempts ÷ unique requests | Retry budgets (SYSDESIGN-03, SYSDESIGN-11) |

## Cost and energy

- **Every nine costs more than the last.** Moving from 99.9% to 99.99% shrinks the budget from 43 to 4.3 minutes
  a month. That usually means multi-zone or multi-region redundancy, automated failover, slower and more careful
  releases, and on-call staffing. Set the SLO from user harm and business value, not from pride.
- **Headroom is a cost you choose.** Running at 60% instead of 90% utilisation buys a 4× lower mean latency (in
  M/M/1 terms, 2.5 S instead of 10 S) and costs 50% more servers. The utilisation curve tells you exactly what
  you are buying.
- **Energy per request** = average power × time ÷ requests served. An idle server still draws a large share of
  its peak power (SYSDESIGN-03, SYSDESIGN-17), so energy per request falls as utilisation rises. That is the
  opposite direction from latency. The design question is where on the curve both are acceptable.

## Interview angle

**How it is asked.** Rarely by itself. Almost every system-design interview has a **QUANTIFY** phase ("how much
traffic, how much storage?"), and strong candidates do it in two minutes without being asked. Follow-ups test
understanding: "Why not run at 90% CPU?" "How many database connections do you need?"

**Model answer outline** (CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP):

1. **CLARIFY:** users, actions per user, read/write mix, latency and availability targets (offer numbers:
   "Shall we say 99.9% and p99 under 300 ms?").
2. **QUANTIFY:** requests/day → average → peak (state the factor) → cores (at 60–70%) → concurrency (L = λW) →
   storage per year → bandwidth. Round aggressively and say so.
3. **SKETCH:** let the numbers pick the architecture. "1,000 requests/s fits on three modest servers. 100,000
   requests/s needs sharding."
4. **DEEPEN:** the utilisation curve (why headroom), or tail amplification (why leaves need p99.9).
5. **STRESS and WRAP:** what happens at 3× the forecast; which number you are least sure of, and how you'd
   measure it (load test with an open model).

**Red flags.** Designing before quantifying. Averages instead of percentiles. Using the theoretical maximum
throughput as capacity. "100% availability". Numbers with false precision ("we need 37.4 servers").

**Likely follow-ups.** How does the answer change if the service is 10× more read-heavy? What if p99 must be
50 ms? How many GPUs for the chat feature? (Answer with the method, and name the benchmark you would need.)

## Common mistakes

- Promising a nine without pricing it.
- Quoting Dean's 2009 table as current fact. Date your numbers, and measure what matters.
- Treating 80–90% utilisation as efficient for latency-sensitive services.
- Forgetting that availability multiplies across serial dependencies.
- Load-testing with a closed model and reporting the result as capacity.
- Estimating LLM workloads in requests instead of tokens.
- Treating assumptions as facts. Write them down so someone can disagree.

## Check yourself

1. A 99.95% request-based SLO over 30 days, at 2 million requests/day: how many failed requests may you have?
2. A service receives 2,000 requests/s and its mean latency is 150 ms. How many requests are in flight? What
   happens if the thread pool has 200 threads?
3. In M/M/1, what are the mean and p99 latency at 80% utilisation if the service time is 20 ms?
4. A page fans out to 50 backends, each with p99 = 200 ms. Roughly what fraction of page loads see at least one
   200 ms+ backend?
5. 100,000 LLM generations per hour with 500 output tokens each: what decode token rate must the fleet sustain?

The full set, with answers, is in [exercises/01-requirements-to-numbers.md](../../exercises/01-requirements-to-numbers.md).

## Lab

**Lab L01 — saturation point** ([labs/01-requirements-to-numbers/](../../labs/01-requirements-to-numbers/README.md)).
You run a deliberately simple Lumen service whose capacity you can compute in advance: one worker, 10 ms mean
service time, so 100 requests/s. You predict its latency curve with `predict.py`, then drive it with k6 at
fixed arrival rates from 20 to 110 requests/s and watch p50 and p99 bend upwards as utilisation approaches 1.
You also check Little's law against the service's own measurement of the average number of requests in the
system. An optional profile adds Prometheus and Grafana to watch the same curves live. In the recorded run
(2026-11-20, on a shared, busy host), the measured mean latency stayed within about 6% of the D/M/1
prediction up to 80% utilisation, Little's law held to three decimal places at every step, and two identical
runs at 90 requests/s (about 92% measured utilisation) differed by 2.7× in mean latency. That last result is a reminder that near saturation,
a single short load test is not a capacity measurement. The full table is in the lab README.

## Further reading

- *Site Reliability Engineering* (Google, 2016), ch. 3 *Embracing Risk* and ch. 4 *Service Level Objectives*:
  the origin of the error-budget idea as most teams practise it [1][2].
- *The Site Reliability Workbook* (2018), ch. 2 *Implementing SLOs* and ch. 5 *Alerting on SLOs*: worked burn-rate
  alerting [3].
- J. D. C. Little, *Little's Law as Viewed on Its 50th Anniversary* (Operations Research, 2011): the law, its
  proof and its uses, from its author [5].
- M. Harchol-Balter, *Performance Modeling and Design of Computer Systems* (Cambridge University Press, 2013): the
  best modern textbook on queueing for computer systems [11].
- J. Dean, L. A. Barroso, *The Tail at Scale* (CACM, 2013): short, practical, and still the reference on tail
  latency [13].
- Google SRE Workbook, *Non-Abstract Large System Design*: estimation done with real hardware numbers.
  https://sre.google/workbook/non-abstract-design/

## References

[1] B. Beyer, C. Jones, J. Petoff, N. R. Murphy (eds.), *Site Reliability Engineering*, O'Reilly, 2016, ch. 4 *Service Level Objectives* (SLI and SLO definitions). https://sre.google/sre-book/service-level-objectives/ (accessed 2026-11)
[2] Ibid., ch. 3 *Embracing Risk* (error budgets). https://sre.google/sre-book/embracing-risk/ (accessed 2026-11)
[3] B. Beyer, N. R. Murphy, D. K. Rensin, K. Kawahara, S. Thorne (eds.), *The Site Reliability Workbook*, O'Reilly, 2018, ch. 2 *Implementing SLOs*, https://sre.google/workbook/implementing-slos/ ; ch. 5 *Alerting on SLOs* (14.4× burn rate = 2% of a 30-day budget in 1 hour), https://sre.google/workbook/alerting-on-slos/ (accessed 2026-11)
[4] J. D. C. Little, *A Proof for the Queuing Formula: L = λW*, Operations Research 9(3):383–387, 1961. https://doi.org/10.1287/opre.9.3.383 (accessed 2026-11)
[5] J. D. C. Little, *Little's Law as Viewed on Its 50th Anniversary*, Operations Research 59(3):536–549, 2011. https://doi.org/10.1287/opre.1110.0940 (accessed 2026-11)
[6] J. Dean, *Designs, Lessons and Advice from Building Large Distributed Systems*, keynote, LADIS 2009 ("Numbers Everyone Should Know"). https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf (accessed 2026-11)
[7] C. Scott, *Latency Numbers Every Programmer Should Know* (interactive, with per-year extrapolation; based on P. Norvig's 2002 numbers). https://colin-scott.github.io/personal_website/research/interactive_latency.html (accessed 2026-11)
[8] I. N. Bozkurt, W. Aqeel, D. Bhattacherjee, B. Chandrasekaran, P. B. Godfrey, G. Laughlin, B. M. Maggs, A. Singla, *Dissecting Latency in the Internet's Fiber Infrastructure*, arXiv:1811.10737, 2018 (speed of light in fibre ≈ 204,000 km/s). https://arxiv.org/abs/1811.10737 (accessed 2026-11)
[9] Samsung Electronics, *Samsung NVMe SSD 990 PRO Data Sheet*, Rev. 2.0 (sequential read 7,450 MB/s; random read QD1 22K IOPS). https://download.semiconductor.samsung.com/resources/data-sheet/samsung_nvme_ssd_990_pro_datasheet_rev.2.0.pdf (accessed 2026-11)
[10] WonderNetwork, *Global Ping Statistics: London to New York* (daily averages ≈ 70–71 ms, 5–19 Nov 2026). https://wondernetwork.com/pings/London/New%20York (accessed 2026-11)
[11] M. Harchol-Balter, *Performance Modeling and Design of Computer Systems: Queueing Theory in Action*, Cambridge University Press, 2013 (M/M/1 response-time distribution; M/M/k). https://doi.org/10.1017/CBO9781139226424 (accessed 2026-11)
[12] J. F. C. Kingman, *The single server queue in heavy traffic*, Mathematical Proceedings of the Cambridge Philosophical Society 57(4):902–904, 1961. https://doi.org/10.1017/S0305004100036094 (accessed 2026-11)
[13] J. Dean, L. A. Barroso, *The Tail at Scale*, Communications of the ACM 56(2):74–80, February 2013. https://www.barroso.org/publications/TheTailAtScale.pdf (accessed 2026-11)
[14] Grafana Labs, *Open and closed models*, k6 documentation (coordinated omission; `constant-arrival-rate` and `ramping-arrival-rate` executors). https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/ (accessed 2026-11)
[15] OpenAI, *What are tokens and how to count them?*, OpenAI Help Center (1 token ≈ 4 characters ≈ ¾ word in English). https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them (accessed 2026-11; the page blocked automated fetching, so its wording was checked through search-engine extracts only)
[16] L. Kleinrock, *Queueing Systems, Volume 1: Theory*, Wiley, 1975 (the G/M/1 queue; D/M/1 as a special case). https://www.wiley.com/en-us/Queueing+Systems%2C+Volume+1%3A+Theory-p-9780471491101 (accessed 2026-11)
[17] Y. Zhong, S. Liu, J. Chen, J. Hu, Y. Zhu, X. Liu, X. Jin, H. Zhang, *DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving*, Proc. USENIX OSDI 2024. https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin (accessed 2026-11)
[18] International Energy Agency, *Energy and AI*, April 2025, Executive summary. https://www.iea.org/reports/energy-and-ai/executive-summary (accessed 2026-11)
