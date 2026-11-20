---
id: SYSDESIGN-I02
title: "Numbers & cheat sheets: latency, throughput, storage, capacity, cost & GPU numbers"
part: "V — Interview track"
level: [core, deep, frontier]
status: SOURCES_CHECKED
prerequisites: [SYSDESIGN-01]
estimated_time: "1.5h reading + 1h drills"
requirement: "Produce a defensible order-of-magnitude estimate for any design prompt in under four minutes, using constants you can source and assumptions you label."
learning_objectives:
  - "Convert between powers of two and ten, time units, and bandwidth units without a calculator"
  - "Explain which classic latency numbers have drifted since 2009 and which have not, and why"
  - "Estimate peak QPS, storage growth, bandwidth and concurrency from DAU-style inputs"
  - "Compute the downtime budget for any availability target and the availability of composed components"
  - "Estimate LLM weight memory, KV-cache size per token, GPU count and cost per million tokens from datasheet numbers"
last_reviewed: 2026-11-20
---

# I02 — Numbers & cheat sheets

> **The requirement.** In under four minutes of an interview, produce an estimate that rules designs in or out:
> "≈ 15k writes/s at peak, so a single primary is out", or "≈ 320 KiB of KV per token, so this GPU holds about 40
> long conversations". It is hard because the classic tables are old, many popular numbers have no source, and
> AI-era capacity questions need numbers (GPU memory, bandwidth, KV cache) that most cheat sheets lack.

## In one minute

Estimation is a skill built on a small set of constants and a few formulas. Memorize the constants that do not
change (seconds in a day, powers of two, the speed of light in fiber), know the orders of magnitude of the ones that
do (memory, SSD and network latency), and treat every throughput figure as an **assumption to label**, because
throughput depends on hardware, configuration and workload. This page gives you each table with its **source and
date**, or marks it **[A]** for a labelled assumption or **[D]** for a value derived here from sourced inputs. The AI
section gives model memory at FP16/FP8/INT4, the KV-cache formula, and HBM capacity and bandwidth for current NVIDIA
GPUs, taken from NVIDIA's pages this month. Use these numbers to reach conclusions, not to look precise.

**Label key used throughout:** **[S n]** sourced (reference *n*), **[D]** derived by arithmetic from sourced or
physical constants, **[A]** labelled assumption, which you should replace with a measurement.

## Why this matters now

- **The famous latency table is from 2009.** Jeff Dean's "Numbers Everyone Should Know" slide [1] still anchors most
  interview cheat sheets. Some rows have barely moved (main memory ≈ 100 ns; cross-continent round trips are bounded by
  physics). Others have changed by orders of magnitude: SSDs did not appear on the slide, and data-center networking
  is far faster. Colin Scott's interactive version extrapolates the numbers by year from stated growth assumptions,
  for example SSD random reads fixed at 16 µs after 2014 and data-center RTT held constant at 500 µs [3]. It shows
  how the numbers drift, but it is a model, not a measurement.
- **GPU numbers are now interview numbers.** "How many GPUs?" and "how many concurrent users per GPU?" are standard
  follow-ups in AI-system prompts. The answer depends on HBM capacity, HBM bandwidth and KV-cache size, which this
  page gives with sources ([I04](I04-ml-llm-interviews.md) uses them).
- **Cost questions are routine.** Cost per request, per conversation or per million tokens appears in senior
  interviews. Cloud price lists change and vary by region, so this page teaches the formulas and labels prices as
  assumptions, except where a public price was checked this session.

## Core ideas [Core]

### 1. Powers of two and ten

| Power of 2 | Exact value | ≈ Power of 10 | IEC name (binary) | SI name (decimal) | Typical use |
|---|---|---|---|---|---|
| 2¹⁰ | 1,024 | 10³ | KiB | KB = 1,000 B | a small JSON message |
| 2²⁰ | 1,048,576 | 10⁶ | MiB | MB | a photo |
| 2³⁰ | 1,073,741,824 | 10⁹ | GiB | GB | a model shard, a VM's RAM |
| 2⁴⁰ | ≈ 1.10 × 10¹² | 10¹² | TiB | TB | a database |
| 2⁵⁰ | ≈ 1.13 × 10¹⁵ | 10¹⁵ | PiB | PB | a data lake |
| 2³² | 4,294,967,296 | 4.3 × 10⁹ | — | — | IPv4 address space; 32-bit IDs run out |
| 2⁶⁴ | ≈ 1.8 × 10¹⁹ | — | — | — | 64-bit ID space |

[D] The binary/decimal gap grows with size: 2.4 % at kilo, 7.4 % at giga, 10 % at tera. It rarely changes an
interview conclusion, but GPU vendors list memory in GB, while tools such as `nvidia-smi` and vLLM's logs report MiB
or GiB, so know which one you are reading.

### 2. Time units

| Quantity | Exact | Round to |
|---|---|---|
| Seconds per minute / hour | 60 / 3,600 | |
| Seconds per day | 86,400 | ≈ 10⁵ (−14 %) |
| Seconds per 30-day month | 2,592,000 | ≈ 2.6 × 10⁶ |
| Seconds per year (365.25 days) | 31,557,600 | ≈ 3.15 × 10⁷ (≈ π × 10⁷) |
| 1 ms / 1 µs / 1 ns | 10⁻³ / 10⁻⁶ / 10⁻⁹ s | |

[D] **Rate conversions to memorize:**

- 1 million per day ≈ **12 per second** (average).
- 1 billion per day ≈ **12,000 per second**.
- 100 per second ≈ **8.6 million per day**.
- 1 per second ≈ **2.6 million per month** ≈ 31.6 million per year.

### 3. Latency numbers, sourced and dated

The **2009 column** is Dean's slide exactly [1]. Peter Norvig's undated table on his "Teach Yourself Programming in
Ten Years" page has nearly the same values (it lists an 8 ms disk seek), and the source of Colin Scott's model says
Norvig's original numbers are from 2002 [2][3]. The **"2026 order of magnitude"** column is guidance for interviews: each entry is
labelled with its basis. When an interviewer cares about a specific value, say it is an order of magnitude and offer
to measure.

| Operation | 2009 value [1] | 2026 order of magnitude | Basis and drift |
|---|---|---|---|
| L1 cache reference | 0.5 ns | ≈ 1 ns | [S 3] model: ≈ 3 cycles at ≈ 3 GHz; clock rates stopped rising ≈ 2005 |
| Branch mispredict | 5 ns | ≈ 3–5 ns | [A] depends on pipeline depth; roughly unchanged |
| L2 cache reference | 7 ns | ≈ 4 ns | [S 3] model: 13 cycles at ≈ 3 GHz ≈ 4.3 ns; on-die caches grew more than they sped up |
| Mutex lock/unlock (uncontended) | 25 ns | ≈ 15–25 ns | [A] contention, not the instruction, dominates real cost |
| Main memory reference | 100 ns | ≈ 100 ns | [S 3] model holds 100 ns flat since 2000; DRAM latency has not improved much |
| Compress 1 KB (Snappy, then "Zippy") | 3,000 ns | ≈ 1–2 µs | [A] faster cores and codecs; measure for your codec |
| Send 2 KB over 1 Gbps | 20,000 ns | 1.6 µs at 10 Gbps; 0.16 µs at 100 Gbps | [D] serialization = bits ÷ link rate; NIC speeds grew 10–100× |
| Read 1 MB sequentially from memory | 250,000 ns | ≈ 10–100 µs | [A] at an assumed 10–100 GB/s: one core streaming reaches the low end; whole-socket bandwidth is higher but needs many cores. Measure with a STREAM-style test |
| SSD 4 KB random read | — (no SSD row) | ≈ 16–100 µs | [S 3] model: 16 µs; enterprise NVMe datasheets typically quote tens of µs [A]; check yours |
| Read 1 MB sequentially from NVMe SSD | — | ≈ 100–300 µs | [D] at 3–10 GB/s sequential [A] (PCIe 4.0/5.0 x4 link ceilings ≈ 7.9/15.8 GB/s [D]) |
| Round trip within same data center | 500,000 ns | ≈ 50–500 µs | [S 3] model keeps 500 µs; modern fabrics are often faster [A]; measure with your RPC stack |
| Round trip between zones in a region | — | ≤ 1 ms of propagation | [D] propagation only: AWS states its AZs are within 100 km of each other [7]; 100 km of fiber ≈ 0.5 ms one way. Measured RTT is higher; measure yours |
| Disk (HDD) seek | 10 ms | ≈ 4–10 ms | [A] mechanical; barely changed; HDDs now mostly for cold/bulk storage |
| Read 1 MB sequentially from HDD | 20 ms | ≈ 4–10 ms | [A] at 100–250 MB/s |
| Packet CA → Netherlands → CA | 150 ms | ≈ 140–160 ms | [S 1][S 3]; physics floor ≈ 90 ms (see below) |

**[D] Speed of light in fiber.** Light in silica fiber travels at about c / 1.47 ≈ 204,000 km/s (refractive index
≈ 1.47 [A], typical of single-mode fiber), so **≈ 5 µs per km one way, ≈ 1 ms of round trip per 100 km**. Two
great-circle distances (approximate [A]): New York–London ≈ 5,600 km → RTT floor ≈ 56 ms; California–Netherlands ≈
8,900 km → RTT floor ≈ 89 ms (using the rounded 5 µs/km rule; at exactly 204,000 km/s the floors are ≈ 55 and ≈ 87 ms). Real paths are longer than great circles and add routing and queueing, which is why the
observed 150 ms has not shrunk. **No caching or engineering removes this floor; only moving data closer does**
(see [SYSDESIGN-15](../02-modern-requirements/15-multi-region-edge.md)).

**LLM-era latencies** (derived in [SYSDESIGN-21](../03-ai-systems/21-llm-inference-anatomy.md), repeated here as
interview anchors):

| Operation | Value | Basis |
|---|---|---|
| Read all weights of an 8B model in BF16 (16.4 GB) from H100 HBM | ≈ 4.9 ms | [D] 16.4 GB ÷ 3.35 TB/s [S 8] — the lower bound on one decode step at batch 1. SYSDESIGN-21 counts 8.2 B parameters (16.4 GB); the §10 table rounds to 8 B = 16 GB (≈ 4.8 ms) |
| Read 70 GB (70B model in FP8) from H200 HBM | ≈ 14.6 ms | [D] 70 GB ÷ 4.8 TB/s [S 9] |
| Prefill of a 2,000-token prompt, 8B model, H100 | ≈ 66 ms | [D] in SYSDESIGN-21 at an assumed 50 % of dense BF16 peak |
| Typical interactive targets | TTFT ≈ 0.5–2 s; inter-token ≈ 20–50 ms | [A] product targets used in this course's cases, not standards |

**How to use the table in an interview.** Use ratios rather than values: memory is about 10³× faster than an
SSD random read (≈ 100 ns vs ≈ 100 µs); an SSD random read is about 10³× faster than a cross-region round trip
(≈ 100 µs vs ≈ 100 ms); so a cross-region round trip costs as much as ≈ 10⁶ memory references. "Never put a cross-region call on the hot path of a 50 ms request" follows
from the last row.

### 4. Throughput rules of thumb

Throughput is the most abused number in interviews. Every row below is labelled. Use them to estimate **how many
machines**, then say "I'd load-test to confirm" (the course's labs do exactly that; see
[SYSDESIGN-01](../00-orientation/01-requirements-to-numbers.md)).

| Component | Rule of thumb | Label and source |
|---|---|---|
| Redis, one instance, simple GET/SET, no pipelining | ≈ 10⁵ ops/s | [S 5] Redis docs show `redis-benchmark` SET ≈ 180k req/s, ≈ 72k with random keys over 100k keys (50 clients). Hardware is not fully specified, so treat as indicative |
| Redis, pipelined (16 commands) | ≈ 10⁶ ops/s | [S 5] docs example on a laptop: SET ≈ 1.5 M, GET ≈ 1.8 M req/s. The same page also publishes per-version results on fully specified bare-metal hardware (one Xeon Gold 6230, 50 clients, no pipelining, 256-byte payloads) as charts; read them there |
| Kafka, small cluster, 100-byte records | ≈ 10⁵–10⁶ records/s per broker | [S 6] Kreps 2014: 3 brokers (HDDs, 1 GbE) sustained ≈ 2.0 M records/s from 3 producers with async 3× replication; ≈ 420k/s for one producer with sync replication. Old hardware; modern brokers are network- or disk-bound at higher numbers |
| Relational primary (PostgreSQL/MySQL), simple indexed writes | ≈ 10³–10⁴ writes/s | [A] depends on durability settings, row size, indexes, hardware; measure with `pgbench`/sysbench |
| Relational, cached point reads per node | ≈ 10⁴–10⁵ reads/s | [A] |
| Stateless HTTP/JSON service, per core | ≈ 10²–10³ req/s for business logic | [A] dominated by your code and serialization, not the framework |
| L7 proxy (NGINX/Envoy) per core, small requests | ≈ 10⁴ req/s | [A] TLS and request size matter more than the proxy brand |
| 1 Gbps / 10 Gbps / 100 Gbps NIC | 125 MB/s / 1.25 GB/s / 12.5 GB/s | [D] ÷ 8 bits; expect 70–90 % usable [A] |
| NVMe SSD (PCIe 4.0 x4 / 5.0 x4) | ≈ 7.9 / ≈ 15.8 GB/s sequential ceiling | [D] from 16 / 32 GT/s per lane, 4 lanes, 128b/130b encoding; device ratings are lower [A] |
| HDD | ≈ 100–250 MB/s sequential; ≈ 100–200 random IOPS | [A] |
| Object storage single stream | ≈ 50–100+ MB/s per connection; parallelize | [A] throughput scales with parallel connections and prefix spread |
| One H100 decoding a 70B model (FP8, TP4 replica share) | ≈ 1,400 output tokens/s per GPU | [D/A] roofline estimate in [C09](../04-case-studies/C09-llm-chat-service.md) at assumed 50 % of HBM bandwidth; benchmark before buying |
| One H100 prefilling a 70B model (FP8) | ≈ 5,700 tokens/s per GPU | [D/A] same source, assumed 40 % of dense FP8 peak |

**Two meta-rules.** (1) A rule of thumb that cannot name its hardware is an assumption, so say so. (2) A single number
for "a database" is meaningless without the access pattern; quote ops/s *for the pattern* (point read, range scan,
indexed write, fsync'd write).

### 5. Storage sizes

| Item | Size | Label |
|---|---|---|
| ASCII character / UTF-8 character | 1 B / 1–4 B | [S 30] UTF-8 encodes a code point in 1 to 4 octets |
| Integer (32-bit / 64-bit), double | 4 / 8 / 8 B | [D] |
| Unix timestamp (64-bit) | 8 B | [D] |
| UUID | 16 B binary (36 chars as text) | [S 31] "A UUID is 128 bits long" |
| IPv4 / IPv6 address | 4 / 16 B | [D] 32 / 128 bits |
| SHA-256 digest | 32 B | [D] 256 bits |
| Embedding vector, 1,024 dims, float32 / int8 | 4 KiB / 1 KiB | [D] |
| HNSW index per vector | d × 4 + M × 2 × 4 B (4,224 B ≈ 4.1 KiB at d = 1,024, M = 16) | [S 13] FAISS guidelines |
| A short text post or chat message with metadata | ≈ 0.5–2 KB | [A] |
| A JSON API response | ≈ 1–10 KB | [A] |
| Compressed photo (phone) | ≈ 1–5 MB original; ≈ 50–300 KB thumbnail | [A] |
| 1 minute of video at 5 Mbps | 37.5 MB | [D] 5 Mb/s × 60 s ÷ 8 (bitrate is an assumption) |
| One English token | ≈ 4 characters; 100 tokens ≈ 60–80 words | [S 14] Google's Gemini documentation; other tokenizers differ, so measure with yours |

**Storage-growth formula:** `bytes/day = items/day × bytes/item`; `× retention days × replication factor ×
(1 + index/overhead fraction)`. State replication (typically 3× [A]) and overhead separately so the interviewer can
see them.

### 6. Availability: nines and downtime

[D] Computed with a 365.25-day year and a 30.44-day average month:

| Availability | Downtime / year | / month | / week | / day |
|---|---|---|---|---|
| 99 % ("two nines") | 3.65 days | 7.31 h | 1.68 h | 14.4 min |
| 99.5 % | 1.83 days | 3.65 h | 50.4 min | 7.2 min |
| 99.9 % ("three nines") | 8.77 h | 43.8 min | 10.1 min | 1.44 min |
| 99.95 % | 4.38 h | 21.9 min | 5.04 min | 43.2 s |
| 99.99 % ("four nines") | 52.6 min | 4.38 min | 1.01 min | 8.64 s |
| 99.999 % ("five nines") | 5.26 min | 26.3 s | 6.05 s | 0.86 s |
| 99.9999 % | 31.6 s | 2.63 s | 0.60 s | 86 ms |

**Composition** [D]:

- **Serial** (all must work): A = A₁ × A₂ × … Three 99.9 % dependencies in series give ≈ **99.70 %**. Five 99.95 %
  dependencies give ≈ **99.75 %**. A chain of "three nines" services cannot deliver three nines end to end.
- **Parallel, independent** (any one suffices): A = 1 − (1 − A₁)(1 − A₂). Two independent 99 % replicas give
  **99.99 %**, but only if failures really are independent. Shared zones, deploys and configuration break independence,
  which is why real redundancy designs talk about failure domains ([SYSDESIGN-11](../01-foundations/11-reliability-engineering.md)).
- **Error budget** = (1 − SLO) × window. A 99.9 % monthly SLO allows 43.8 minutes. If one bad deploy takes 30 minutes,
  you have spent 68 % of the month's budget.

**Interview use.** When someone says "five nines", answer with the budget: "That's 26 seconds a month. Our failover
alone takes longer, so we'd need active-active with automatic routing." This one sentence usually turns a slogan into
an engineering discussion.

### 7. QPS from DAU

[D] **The core formula:**

```
average QPS = DAU × actions per user per day ÷ 86,400
peak QPS    = average QPS × peak factor            (peak factor [A]: 2–5× diurnal; far more for scheduled events)
reads/writes: split by the read:write ratio         (state it, e.g. 100:1 for feeds, 1:1 for chat)
```

| DAU | Actions/user/day | Average QPS | Peak at 3× [A] |
|---|---|---|---|
| 1 M | 10 | ≈ 116 | ≈ 350 |
| 10 M | 10 | ≈ 1,160 | ≈ 3,500 |
| 10 M | 100 | ≈ 11,600 | ≈ 35,000 |
| 100 M | 50 | ≈ 58,000 | ≈ 174,000 |
| 1 B | 20 | ≈ 231,000 | ≈ 700,000 |

**Concurrency (Little's law)** [S 4]: L = λ × W. Requests in flight = arrival rate × time in system. 3,500 requests/s
that each stream for 10 s means ≈ 35,000 open connections. This is the formula for sizing WebSocket gateways,
thread pools, database connection pools and LLM batch slots. It holds for any stable system regardless of the
arrival distribution, which is why it is safe to use in an interview.

**Burst traps** [A]: scheduled jobs at the top of the hour, push campaigns, ticket drops, time-zone-aligned digests,
retries after an outage (a recovering service can see a multiple of normal load). Name them; they set the real peak.

### 8. Bandwidth math

[D] Conversions: **1 Gbps = 125 MB/s**; **1 TB/day ≈ 93 Mbps sustained**; **1 PB/month ≈ 3.1 Gbps sustained**.

```
egress bandwidth = peak QPS × response size     (bytes/s; × 8 for bits/s)
video egress     = concurrent viewers × bitrate
```

| Scenario | Inputs | Result |
|---|---|---|
| API responses | 35,000 QPS × 5 KB [A] | 175 MB/s ≈ 1.4 Gbps |
| Image feed | 10,000 QPS × 200 KB thumbnails [A] | 2 GB/s = 16 Gbps, so use a CDN |
| Live video | 100,000 viewers × 5 Mbps [A] | 500 Gbps, CDN only |
| Token streaming | 1.4 M tokens/s × ≈ 100 B per SSE event [A] | 140 MB/s ≈ 1.1 Gbps (tokens are cheap to ship and expensive to make) |

The last row is a useful AI-era observation: for LLM services, **network bandwidth is almost never the bottleneck**,
and GPU memory bandwidth almost always is.

### 9. Cost rules (labelled assumptions)

Prices vary by provider, region, commitment and month. The figures below are indicative, checked 2026-11-20, and vary
by region and commitment. Except where a source is given, they are **assumptions for interview arithmetic**. Say so
out loud, and use the formulas.

| Item | Interview assumption | Note |
|---|---|---|
| Object storage, standard tier | ≈ $0.015–0.025 per GB-month | [S 15] Cloudflare R2 lists $0.015/GB-month and no egress fee for R2 Standard; other providers charge more for storage or egress [A] |
| Cold/archive object storage | ≈ 10–20× cheaper than standard; retrieval fees and delays | [A] |
| Internet egress from a hyperscale cloud | ≈ $0.05–0.09 per GB at list price | [A] not checked against a provider page as of 2026-11; check yours; often the surprise line item |
| Cross-zone / cross-region transfer | ≈ $0.01–0.02 per GB | [A] multi-region designs pay this on every replicated byte |
| General-purpose vCPU | ≈ $0.02–0.05 per vCPU-hour on demand | [A] |
| Data-center GPU (H100-class), on demand | ≈ $3–7 per GPU-hour at list price; committed or smaller-provider rates can be lower | [S 33][S 34] as of 2026-11-20: Lambda H100 SXM $4.69–4.89, H100 PCIe $3.79 per GPU-hour; CoreWeave 8 × H100 node $49.24/h ≈ $6.16 per GPU-hour. Wide variance; the formula matters more |
| SMS message | ≈ $0.005–0.10 per message, by country | [A] often the largest line item of a notification system |

[D] **Formulas that interviewers like:**

```
cost per request       = (monthly infrastructure cost) ÷ (monthly requests)
cost per 1M tokens     = GPU $/hour ÷ (tokens/s per GPU × 3,600) × 10⁶
storage cost per month = stored GB × $/GB-month × replication (if billed per replica)
```

Example [D/A]: at an assumed $3 per H100-hour (assumption: a committed or discounted rate at the low end of the
2026-11 range) and the ≈ 1,400 output tokens/s per GPU estimated in C09, decode
costs ≈ $3 ÷ (1,400 × 3,600) × 10⁶ ≈ **$0.60 per million output tokens**, before utilization losses. At 50 % average
utilization, which is plausible with diurnal traffic [A], it is ≈ $1.20. **Utilization is the biggest lever on
self-hosted token cost**, which is why autoscaling and multi-tenancy matter
([SYSDESIGN-16](../02-modern-requirements/16-cost-as-requirement.md), [SYSDESIGN-23](../03-ai-systems/23-gpu-infrastructure.md)).

## AI-system numbers [Frontier]

All hardware figures are vendor peaks from NVIDIA pages read on 2026-11-20. Vendors list tensor throughput **with
sparsity**; dense is half (NVIDIA's footnotes say so [8][9][11]). Real kernels reach a fraction of peak, which is a
labelled assumption in every estimate.

### 10. Model weight memory

[D] **weights (bytes) = parameters × bytes per parameter.** FP16/BF16 = 2 B, FP8 = 1 B, INT4 = 0.5 B plus scales
(≈ 3 % extra for one FP16 scale per 128 weights [A]; group size varies by method).

| Model size (parameters) | FP16 / BF16 | FP8 | INT4 (+ ≈ 3 % scales) | Fits on … (weights only, rough) |
|---|---|---|---|---|
| 1 B | 2 GB | 1 GB | ≈ 0.5 GB | a laptop or CPU |
| 8 B (e.g. Llama 3.1 8B) | 16 GB | 8 GB | ≈ 4.1 GB | one L4 (24 GB) at FP8 or INT4; one H100 at any precision |
| 32 B | 64 GB | 32 GB | ≈ 16.5 GB | one H100 at FP8; one L40S (48 GB) at INT4 |
| 70 B (e.g. Llama 3.3 70B) | 140 GB | 70 GB | ≈ 36 GB | one H200 (141 GB) at FP8 with little KV room; 2–4 H100s with tensor parallelism |
| 405 B (Llama 3.1 405B) | 810 GB | 405 GB | ≈ 209 GB | at FP8, 8 × H100 (640 GB) holds the weights with little KV room; 8 × H200 or B200 leaves room for KV. BF16 does not fit one 8 × H100 machine [10] |

Rules:

- **Weights are only the start.** Leave room for the KV cache (often the larger term at high concurrency),
  activations and runtime overhead. Serving engines reserve a configurable fraction of HBM. In current vLLM,
  `--gpu-memory-utilization`, if unspecified, is 1.0 with the extensible KV cache (sized from measured memory) and
  0.92 otherwise [29]. The examples here assume 0.9 to leave headroom [A].
- **Mixture-of-experts: memory scales with total parameters, compute with active ones.** OpenAI's gpt-oss-120b has
  117 B total and 5.1 B active parameters, and its MoE weights ship in MXFP4, so its model card says it runs on a
  single 80 GB GPU [16]. Every expert must be resident even though few run per token.
- **Quantization trades quality for memory.** INT4 weight-only methods such as AWQ and GPTQ are widely used. Always
  re-run your evals after quantizing ([SYSDESIGN-22](../03-ai-systems/22-serving-llms-at-scale.md)).

### 11. KV cache per token

[D] For a decoder-only transformer with standard multi-head or grouped-query attention:

```
KV bytes per token = 2 (K and V) × layers × KV heads × head dimension × bytes per element
KV for a request   = KV bytes per token × (prompt tokens + generated tokens)
```

Using the Llama 3 architectures (32/80/126 layers, 8 KV heads, head dimension 128 = model dimension ÷ attention heads,
from the Llama 3 paper's Table 3 [10]):

| Model | KV per token (BF16) | 8k-token conversation | 128k-token context | KV per token (FP8 KV cache) |
|---|---|---|---|---|
| Llama 3.1 8B | 2 × 32 × 8 × 128 × 2 = **128 KiB** | 1.0 GiB | 16 GiB | 64 KiB |
| Llama 3.x 70B | 2 × 80 × 8 × 128 × 2 = **320 KiB** | 2.5 GiB | 40 GiB | 160 KiB |
| Llama 3.1 405B | 2 × 126 × 8 × 128 × 2 = **504 KiB** | 3.9 GiB | 63 GiB | 252 KiB |

Rules:

- **Grouped-query attention is why the numbers are this small.** With 64 query heads but 8 KV heads, the 70B model
  stores one-eighth of the KV that full multi-head attention would.
- **Other attention variants change the formula.** DeepSeek-V2's multi-head latent attention caches a compressed
  latent vector instead of per-head K and V; the paper reports a 93.3 % KV-cache reduction relative to DeepSeek 67B
  [17]. Sliding-window layers cap KV at the window size. Read the model's `config.json`.
- **Shared prefixes are stored once with prefix caching**, which is the single most important KV optimization for
  chat and RAG ([C09](../04-case-studies/C09-llm-chat-service.md),
  [SYSDESIGN-22](../03-ai-systems/22-serving-llms-at-scale.md)).

**[D] Worked capacity example (H200, Llama 3.x 70B, FP8 weights):** usable HBM ≈ 0.9 × 141 GB ≈ 127 GB; minus 70 GB
weights; minus ≈ 3 GB for activations and runtime [A] → ≈ **54 GB for KV**. 54 × 10⁹ ÷ 327,680 B ≈ **165,000 tokens**
(BF16 KV) → ≈ **40 concurrent 4k-token conversations**, or ≈ 80 with an FP8 KV cache. That sentence ("about 40–80
conversations per H200, limited by KV memory") is the kind of bounded, sourced answer interviewers want.

### 12. GPU memory and bandwidth

| GPU | Memory | Memory bandwidth | Dense BF16 (sparse ÷ 2) | Source and notes |
|---|---|---|---|---|
| NVIDIA A100 80GB (SXM) | 80 GB HBM2e | 2,039 GB/s | — | [12] PCIe version 1,935 GB/s |
| NVIDIA L4 | 24 GB | 300 GB/s | ≈ 121 TFLOPS | [11] 72 W; inference/video card |
| NVIDIA L40S | 48 GB GDDR6 | 864 GB/s | ≈ 362 TFLOPS | [11b] 350 W |
| NVIDIA RTX PRO 6000 Blackwell (workstation) | 96 GB GDDR7 | 1,792 GB/s | — | [18] 600 W |
| NVIDIA H100 SXM | 80 GB | 3.35 TB/s | ≈ 989 TFLOPS | [8] FP8 3,958 sparse → ≈ 1,979 dense; up to 700 W |
| NVIDIA H100 NVL | 94 GB | 3.9 TB/s | ≈ 835 TFLOPS | [8] 350–400 W |
| NVIDIA H200 (SXM and NVL) | 141 GB | 4.8 TB/s | ≈ 989 (SXM) / ≈ 835 (NVL) TFLOPS | [9] same tensor throughput as H100, more and faster memory |
| NVIDIA B200 (per GPU, from DGX B200) | ≈ 180 GB HBM3e | ≈ 8 TB/s | — | [D] from [19]: 8 GPUs, 1,440 GB total, 64 TB/s total; FP8 72 PFLOPS sparse per system |
| NVIDIA GB200 (per GPU, from the superchip) | ≈ 186 GB HBM3e | ≈ 8 TB/s | — | [D] from [20]: 1 Grace CPU + 2 GPUs, 372 GB and 16 TB/s per superchip |
| NVIDIA B300 / GB300 (Blackwell Ultra) | up to 288 GB HBM3e (system pages: 2.1 TB per 8 GPUs) | ≈ 8 TB/s | — | [21] "up to 288 GB" per GPU; [23][32] 2.1 TB per 8-GPU HGX/DGX B300; bandwidth [D] from [22]: GB300 NVL72 lists up to 576 TB/s across 72 GPUs |

Notes and drift:

- **As of 2026-11.** NVIDIA's HGX page also lists Rubin-generation systems (HGX Rubin NVL8 with 2 TB of HBM4 and
  130 TB/s across 8 GPUs) [23]. Expect this table to need updating within a year. Re-check the vendor page before
  quoting.
- **Per-GPU Blackwell numbers are derived** by dividing system totals by GPU count, because NVIDIA's pages give
  system totals.
- **B300 memory.** NVIDIA publishes two figures: its technical blog gives "up to 288 GB of HBM3e memory per GPU" [21],
  and its HGX and DGX B300 pages list 2.1 TB of total GPU memory for eight GPUs [23][32]. The two do not match exactly
  (8 × 288 GB = 2.30 TB; 2.1 TB ÷ 8 ≈ 262 GB), and NVIDIA does not explain the gap. Quote both as published: for
  capacity planning of an 8-GPU node, use NVIDIA's 2.1 TB system figure, and treat 288 GB as the per-GPU maximum.
  Confirm usable memory on the exact system you buy.
- **NVLink per GPU (GPU-to-GPU).** H100 SXM 900 GB/s (H100 NVL bridge 600 GB/s) [8]; H200 900 GB/s [9]; HGX B200 and
  HGX B300 1.8 TB/s per GPU, 14.4 TB/s per 8-GPU system [23]; GB200 NVL72 130 TB/s across the 72-GPU NVLink domain [20].
  NVLink decides how cheaply tensor parallelism splits one model across GPUs.
- **Bandwidth decides decode speed; capacity decides concurrency.** H200 has the same compute as H100 but 43 % more
  bandwidth and 76 % more memory [8][9], so for memory-bound decode it is the more useful upgrade.

### 13. Decode, prefill and training arithmetic

[D] with inputs as labelled:

```
decode step time ≥ (weight bytes + KV bytes read for the batch) ÷ HBM bandwidth      (memory-bound)
per-user tokens/s ≈ 1 ÷ step time ;  aggregate tokens/s ≈ batch size ÷ step time
prefill FLOPs ≈ 2 × parameters × prompt tokens                                      (compute-bound)
training FLOPs ≈ 6 × parameters × training tokens                                   [S 24]
full fine-tune memory (mixed-precision Adam) ≈ 16 bytes × parameters + activations   [S 25]
```

- **2N and 6N.** Kaplan et al. estimate the forward pass at ≈ 2N FLOPs per token (plus a context-dependent attention
  term) and training at C ≈ 6N FLOPs per training token [24].
- **16 bytes per parameter.** The ZeRO paper accounts for mixed-precision Adam as 2Ψ (FP16 weights) + 2Ψ (FP16
  gradients) + 12Ψ (FP32 weights, momentum and variance) = 16Ψ bytes. A 70B full fine-tune therefore needs ≈ 1.1 TB
  of model state before activations, which is why it is sharded across many GPUs [25].
- **Parameter-efficient fine-tuning changes the platform.** LoRA's abstract reports reducing trainable parameters by
  10,000× and GPU memory by 3× versus full fine-tuning of GPT-3 175B [26]. QLoRA reports fine-tuning a 65B model on a
  single 48 GB GPU [27]. A fine-tuning platform built on adapters is a much smaller system than one built on full
  fine-tunes ([I04](I04-ml-llm-interviews.md)).

### 14. Serving metrics to name

vLLM exposes, among others, `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`,
`vllm:request_time_per_output_token_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:kv_cache_usage_perc` and
`vllm:num_requests_running` [28] (as of vLLM v0.34.0, released 2026-11-16). Quoting **TTFT, inter-token latency and
KV-cache usage** as your SLIs is a concrete senior signal in LLM-serving interviews.

## Numbers that matter

**The one-page interview card.** If you memorize only one thing from this unit, make it this:

```
TIME        86,400 s/day ≈ 10^5   ·   1 M/day ≈ 12/s   ·   1 B/day ≈ 12k/s   ·   year ≈ π × 10^7 s
LATENCY     memory 100 ns · SSD read ~16–100 µs · same-DC RTT ≤ 0.5 ms · zones ≤ 1 ms · 100 km fiber ≈ 1 ms RTT
            cross-continent 60–150 ms (physics: 5 µs/km one way)
BANDWIDTH   1 Gbps = 125 MB/s · 1 TB/day ≈ 93 Mbps
NINES       99.9 % = 43.8 min/month · 99.99 % = 4.4 min/month · 99.999 % = 26 s/month · serial = multiply
LITTLE      in-flight = rate × duration
WEIGHTS     params × {2, 1, 0.5} B for {BF16, FP8, INT4}
KV          2 × layers × KV heads × head dim × bytes   (Llama 70B: 320 KiB/token BF16)
GPUS        H100 80 GB @ 3.35 TB/s · H200 141 GB @ 4.8 TB/s · B200 ≈ 180 GB @ ≈ 8 TB/s
            B300 up to 288 GB/GPU (2.1 TB per 8-GPU node)
COMPUTE     prefill ≈ 2N FLOPs/token · training ≈ 6N FLOPs/token · Adam state ≈ 16 B/param
COST        $/M tokens = $/GPU-h ÷ (tokens/s × 3,600) × 10^6
```

## Design choices and trade-offs

| Estimation style | Wins when | Costs | Example |
|---|---|---|---|
| Powers of ten only | Early QUANTIFY; any conclusion robust to ×2 | Misses factors near thresholds | "≈ 10⁴ writes/s → partition" |
| Explicit chain with rounded factors | Most interviews | 2–4 minutes | DAU → actions → QPS → peak |
| Roofline-style (bytes ÷ bandwidth, FLOPs ÷ compute) | GPU/LLM sizing | Needs model and GPU facts | Decode step ≥ weights ÷ HBM bandwidth |
| "I'd measure" plus a bounded range | Throughput of software you don't know | Must still commit to a planning number | "1k–10k writes/s per node; I'll plan with 3k" |

## Deep dive [Deep]: why the classic numbers drifted unevenly

- **Latency of physics-bound operations is flat.** Cross-continent round trips are bounded by the speed of light in
  fiber; DRAM access latency is bounded by DRAM cell physics and has hardly moved since 2000 (Colin Scott's model holds
  it at 100 ns [3]).
- **Bandwidth has grown much faster than latency improved.** NIC rates went from 1 Gbps (Dean's slide) to
  800 Gb/s of network connectivity per GPU in a GB300 NVL72 rack [22]. HBM bandwidth per GPU grew from ≈ 2 TB/s (A100) to ≈ 8 TB/s (B200-class) in two
  generations [12][19]. The consequence for design: **batching and parallelism win**, because you can move much more
  data per unit of latency.
- **New tiers appeared.** NVMe SSDs (tens of µs) sit between memory and disk, and HBM sits on the GPU package. A
  modern hierarchy has more levels than the 2009 slide, and good designs place data at the cheapest tier that meets
  the latency target ([SYSDESIGN-04](../01-foundations/04-caching.md), [SYSDESIGN-13](../01-foundations/13-data-at-scale.md)).

## Failure modes and operations

Estimates fail in predictable ways:

| Estimation failure | Symptom in production | Guard |
|---|---|---|
| Averages instead of peaks | Saturation every evening | Always multiply by a stated peak factor |
| Ignoring retries | Recovery overload after an outage | Add retry amplification to the peak; use retry budgets |
| Ignoring replication and indexes | Storage 3–5× over plan | Write replication and overhead as separate factors |
| Datasheet peaks treated as achievable | GPU fleet 2–3× short | Apply an explicit efficiency assumption; benchmark |
| Mixing GB and GiB | ≈ 7 % memory shortfall at GPU scale | Write units on every number |
| Old latency table | Designs that over-fear the network or under-fear the WAN | Use ratios; measure your own RTTs |

## Cost and energy

The cost section above gives the formulas. Energy follows the same pattern: power × time ÷ work done. For example,
an H100 SXM's configurable TDP is up to 700 W [8]. At an assumed 1,400 output tokens/s per GPU, that is at most
≈ 0.5 J per output token of GPU board power [D], before host, cooling and PUE overheads
([SYSDESIGN-17](../02-modern-requirements/17-energy-carbon-aware.md)).

## Interview angle

- **How it is asked.** "Roughly how many servers?", "How much storage after a year?", "How many GPUs?", "What does one
  request cost?" Sometimes the question is only "is this a lot?"
- **Model answer outline.** (1) Write assumptions. (2) Convert to per second at peak. (3) Size state (storage, working
  set, concurrency). (4) Compare with a per-unit capacity, sourced or labelled. (5) Draw the conclusion and name
  what you'd measure.
- **Red flags.** Factor-of-1,000 slips (ms vs µs, GB vs TB); averages presented as capacity; quoting throughput for
  "a database" with no access pattern; GPU estimates that ignore the KV cache.
- **Follow-ups.** "What if traffic is 10× spikier?" "What if the context doubles?" (KV doubles, concurrency halves.)
  "What if we quantize to INT4?" (Weights shrink by 4× versus BF16, but quality must be re-evaluated.)

## Common mistakes

- Using 2009 numbers as if they were current measurements.
- Forgetting that NVIDIA's headline TFLOPS are with sparsity.
- Sizing GPUs from weights alone.
- Treating "five nines" as a feature rather than a 26-second-a-month budget.
- Forgetting the replication factor in storage estimates.
- Calling an assumed price a fact.

## Check yourself

1. How much downtime per month does a 99.95 % SLO allow?
2. A service has 20 M DAU doing 15 actions/day with a 4× peak. What is peak QPS?
3. What is the KV size per token of a model with 48 layers, 8 KV heads, head dimension 128 and BF16 KV?
4. Why does an H200 serve more concurrent conversations than an H100 even though their tensor throughput is the same?
5. What is the round-trip propagation floor for a 2,000 km fiber path?

Full set with answers: [exercises/I02-numbers-cheat-sheets.md](../../exercises/I02-numbers-cheat-sheets.md).

## Lab

No lab for this unit. Practice the numbers against measurements in
[labs/01-requirements-to-numbers](../../labs/01-requirements-to-numbers/) (saturation point) and
[labs/21-llm-inference-anatomy](../../labs/21-llm-inference-anatomy/) (TTFT and decode rate versus the
bandwidth bound).

## Further reading

- J. Dean, LADIS 2009 keynote [1]: the original slide and two worked back-of-the-envelope comparisons.
- C. Scott, *Latency Numbers Every Programmer Should Know* (interactive) [3]: read the source to see which growth
  assumptions produce each number.
- Google SRE Workbook, *Non-Abstract Large System Design*: estimation in a real design process (see I01 [3]).
- NVIDIA data-center GPU pages [8][9][19][20][22]: re-check before quoting; they change with each generation.
- Kaplan et al. [24] and Rajbhandari et al. (ZeRO) [25]: the sources of the 6N and 16-bytes-per-parameter rules.

## References

1. J. Dean, *Designs, Lessons and Advice from Building Large Distributed Systems*, LADIS 2009 keynote ("Numbers
   Everyone Should Know" slide). https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf (accessed 2026-11)
2. P. Norvig, *Teach Yourself Programming in Ten Years* ("Approximate timing for various operations on a typical PC";
   table undated; page © 2001–2014). https://norvig.com/21-days.html (accessed 2026-11)
3. C. Scott, *Latency Numbers Every Programmer Should Know* (interactive; extrapolation model in page source).
   https://colin-scott.github.io/personal_website/research/interactive_latency.html (accessed 2026-11)
4. J. D. C. Little, "A Proof for the Queuing Formula: L = λW", *Operations Research* 9(3), 1961.
   https://doi.org/10.1287/opre.9.3.383 (publisher page blocks automated fetches; metadata confirmed via Crossref,
   https://api.crossref.org/works/10.1287/opre.9.3.383, accessed 2026-11-20)
5. Redis, *Redis benchmark* (documentation, `redis-benchmark` examples and pitfalls).
   https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/ (accessed 2026-11)
6. J. Kreps, *Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)*, LinkedIn Engineering,
   2014-04-27. https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines (accessed 2026-11)
7. AWS, *Regions and Availability Zones* ("all within 100 km (60 miles) of each other"; synchronous replication between AZs).
   https://aws.amazon.com/about-aws/global-infrastructure/regions_az/ (accessed 2026-11)
8. NVIDIA, *H100 Tensor Core GPU* (H100 SXM 80 GB, 3.35 TB/s; H100 NVL 94 GB, 3.9 TB/s; tensor figures with sparsity).
   https://www.nvidia.com/en-us/data-center/h100/ (accessed 2026-11-20)
9. NVIDIA, *H200 Tensor Core GPU* (141 GB, 4.8 TB/s). https://www.nvidia.com/en-us/data-center/h200/ (accessed 2026-11-20)
10. A. Grattafiori et al. (Llama Team, Meta), *The Llama 3 Herd of Models*, arXiv:2407.21783, 2024, Table 3.
    https://arxiv.org/abs/2407.21783 (accessed 2026-11)
11. NVIDIA, *L4 Tensor Core GPU* (24 GB, 300 GB/s, 72 W; sparsity footnote). https://www.nvidia.com/en-us/data-center/l4/ (accessed 2026-11-20)
    11b. NVIDIA, *L40S GPU* (48 GB GDDR6, 864 GB/s, 350 W). https://www.nvidia.com/en-us/data-center/l40s/ (accessed 2026-11-20)
12. NVIDIA, *A100 Tensor Core GPU* (80 GB HBM2e; 1,935 GB/s PCIe, 2,039 GB/s SXM). https://www.nvidia.com/en-us/data-center/a100/ (accessed 2026-11-20)
13. Meta AI Research, *Faiss wiki: Guidelines to choose an index* (HNSW: "(d * 4 + M * 2 * 4) bytes per vector").
    https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index (accessed 2026-11)
14. Google, *Understand and count tokens* (Gemini API docs: ≈ 4 characters per token; 100 tokens ≈ 60–80 English words).
    https://aistudio.google.com/docs/tokens (accessed 2026-11)
15. Cloudflare, *R2 pricing* ($0.015/GB-month Standard storage; no egress charges).
    https://developers.cloudflare.com/r2/pricing/ (accessed 2026-11)
16. OpenAI, *gpt-oss-120b model card* (117 B total / 5.1 B active parameters; MXFP4 MoE weights; single 80 GB GPU).
    https://huggingface.co/openai/gpt-oss-120b (accessed 2026-11)
17. DeepSeek-AI, *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model*,
    arXiv:2405.04434, 2024 (MLA; "reduces the KV cache by 93.3%"). https://arxiv.org/abs/2405.04434
18. NVIDIA, *RTX PRO 6000 Blackwell Workstation Edition* (96 GB GDDR7, 1,792 GB/s, 600 W).
    https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/ (accessed 2026-11-20)
19. NVIDIA, *DGX B200* (8 GPUs; 1,440 GB total; 64 TB/s HBM3e; FP8 72 PFLOPS sparse).
    https://www.nvidia.com/en-us/data-center/dgx-b200/ (accessed 2026-11-20)
20. NVIDIA, *GB200 NVL72* (superchip: 372 GB HBM3e, 16 TB/s; rack: 13.4 TB, 576 TB/s).
    https://www.nvidia.com/en-us/data-center/gb200-nvl72/ (accessed 2026-11-20)
21. D. Salvator, R. Bhargava, K. Devleker, *NVIDIA Blackwell Ultra for the Era of AI Reasoning*, NVIDIA Technical
    Blog, 2025-03-19 ("up to 288 GB of HBM3e memory per GPU").
    https://developer.nvidia.com/blog/nvidia-blackwell-ultra-for-the-era-of-ai-reasoning (accessed 2026-11-20)
22. NVIDIA, *GB300 NVL72* (72 Blackwell Ultra GPUs; 20 TB GPU memory; up to 576 TB/s).
    https://www.nvidia.com/en-us/data-center/gb300-nvl72/ (accessed 2026-11-20)
23. NVIDIA, *HGX platform* (HGX B300: 2.1 TB; HGX B200: 1.4 TB; NVLink 1.8 TB/s per GPU; HGX Rubin NVL8: 2 TB HBM4, 130 TB/s).
    https://www.nvidia.com/en-us/data-center/hgx/ (accessed 2026-11-20)
24. J. Kaplan et al., *Scaling Laws for Neural Language Models*, arXiv:2001.08361, 2020 (§2.1: C_forward ≈ 2N + …;
    C ≈ 6N FLOPs per training token). https://arxiv.org/abs/2001.08361
25. S. Rajbhandari, J. Rasley, O. Ruwase, Y. He, *ZeRO: Memory Optimizations Toward Training Trillion Parameter
    Models*, arXiv:1910.02054v3, 2020 (2Ψ + 2Ψ + 12Ψ = 16Ψ bytes). https://arxiv.org/abs/1910.02054
26. E. J. Hu et al., *LoRA: Low-Rank Adaptation of Large Language Models*, arXiv:2106.09685, 2021.
    https://arxiv.org/abs/2106.09685
27. T. Dettmers, A. Pagnoni, A. Holtzman, L. Zettlemoyer, *QLoRA: Efficient Finetuning of Quantized LLMs*,
    arXiv:2305.14314, 2023. https://arxiv.org/abs/2305.14314
28. vLLM project, *Metrics* (design documentation). https://docs.vllm.ai/en/latest/design/metrics.html (accessed 2026-11);
    release v0.34.0: https://github.com/vllm-project/vllm/releases/tag/v0.34.0 (accessed 2026-11)
29. vLLM project, *Engine Arguments* (`--gpu-memory-utilization`). https://docs.vllm.ai/en/latest/configuration/engine_args.html (accessed 2026-11)
30. F. Yergeau, *UTF-8, a transformation format of ISO 10646*, RFC 3629, November 2003. https://www.rfc-editor.org/rfc/rfc3629
31. K. Davis, B. Peabody, P. Leach, *Universally Unique IDentifiers (UUIDs)*, RFC 9562, May 2024 (obsoletes RFC 4122). https://www.rfc-editor.org/rfc/rfc9562
32. NVIDIA, *DGX B300* (8 Blackwell Ultra SXM GPUs; 2.1 TB total GPU memory).
    https://www.nvidia.com/en-us/data-center/dgx-b300/ (accessed 2026-11-20)
33. Lambda, *AI Cloud pricing* (on-demand H100 SXM $4.69–4.89 and H100 PCIe $3.79 per GPU-hour; prices change often).
    https://lambda.ai/pricing (accessed 2026-11-20)
34. CoreWeave, *Pricing* (NVIDIA HGX H100, 8 GPUs, on demand $49.24 per hour; prices change often).
    https://www.coreweave.com/pricing (accessed 2026-11-20)
