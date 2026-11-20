# I02 — Exercises

Lesson: [course/05-interview/I02-numbers-cheat-sheets.md](../course/05-interview/I02-numbers-cheat-sheets.md).
All inputs are assumptions unless the lesson gives a source. Round as you would in an interview.

## 1. [Core] Downtime budgets

How much downtime per month does a 99.95 % SLO allow? Per week?

<details><summary>Answer</summary>

(1 − 0.9995) × 30.44 days × 1,440 min ≈ **21.9 min/month**; per week 0.0005 × 10,080 min ≈ **5.0 min**. If a single
deploy rollback takes 10 minutes, one bad deploy uses almost half the month's budget, which is why fast automated
rollback matters more than rare manual heroics.
</details>

## 2. [Core] Peak QPS

20 M DAU, 15 actions per user per day, 4× peak factor. Compute average and peak QPS.

<details><summary>Answer</summary>

20 M × 15 = 300 M/day → 300 M ÷ 86,400 ≈ **3,500/s** average → ≈ **14,000/s** at peak. Rounding 86,400 to 10⁵ gives
3,000 and 12,000, which is fine for a conclusion that does not hinge on 15 %.
</details>

## 3. [Core] KV per token

A model has 48 layers, 8 KV heads, head dimension 128 and a BF16 KV cache. KV per token? For a 16k-token context?

<details><summary>Answer</summary>

2 × 48 × 8 × 128 × 2 B = 196,608 B = **192 KiB/token**. 16,384 tokens × 192 KiB = **3 GiB** per sequence. With an FP8
KV cache, half: 96 KiB/token and 1.5 GiB.
</details>

## 4. [Deep] H100 versus H200

NVIDIA lists the same tensor throughput for H100 SXM and H200 SXM. Why does an H200 serve more concurrent LLM
conversations, and roughly how many more for a 70B FP8 model?

<details><summary>Answer</summary>

Concurrency is capped by memory left for the KV cache after weights, and decode speed by HBM bandwidth. H200 has
141 GB at 4.8 TB/s vs 80 GB at 3.35 TB/s. A 70B FP8 model (70 GB) does not usefully fit on one 80 GB H100 with KV
room (≈ 72 GB usable at 90 %), so H100 needs tensor parallelism across several GPUs. On one H200 the lesson's estimate
leaves ≈ 54 GB for KV → ≈ 165 k tokens at 320 KiB/token → ≈ 40 conversations of 4k tokens. Compare per GPU: a 4×H100
replica has ≈ 288 GB usable − 70 GB weights − overhead ≈ 210 GB of KV, about 52 GB per GPU. So per GPU the KV room is
similar, but the H200 does it without tensor-parallel communication and with 43 % more bandwidth per GPU, so each
decode step is faster. The honest answer is a range plus a benchmark.
</details>

## 5. [Core] Fiber latency floor

What is the minimum round-trip propagation time over a 2,000 km fiber path?

<details><summary>Answer</summary>

≈ 5 µs/km one way → 2,000 km × 2 × 5 µs = **20 ms** RTT floor. Real paths add routing detours and queueing, so
measured RTTs are higher.
</details>

## 6. [Core] Storage growth

50 M messages/day at 1 KB each, kept one year, 3× replication, 30 % index overhead. How much storage?

<details><summary>Answer</summary>

50 GB/day × 365 ≈ 18.3 TB/year raw → × 3 ≈ 55 TB → × 1.3 ≈ **71 TB**. Show the factors separately; the interviewer may
challenge the replication factor or the overhead.
</details>

## 7. [Core] Composed availability

A request passes a load balancer (99.99 %), an app tier (99.95 %) and a database (99.9 %) in series. What is the
end-to-end availability and monthly downtime? What one change helps most?

<details><summary>Answer</summary>

0.9999 × 0.9995 × 0.999 ≈ **0.9984 = 99.84 %** → 0.0016 × 43,830 min ≈ **70 min/month**. The database dominates. The
biggest single improvement is to the weakest link: a database with automatic failover across zones, or serving reads
from replicas or a cache when the primary is down (degraded mode). Improving the 99.99 % load balancer changes almost
nothing.
</details>

## 8. [Deep] Will it fit?

A 32B model (64 layers, 8 KV heads, head dimension 128) quantized to INT4 runs on one L40S (48 GB). Assume 90 %
usable memory and 2 GB runtime overhead. How many 4k-token conversations fit with a BF16 KV cache?

<details><summary>Answer</summary>

Weights ≈ 32 × 0.5 GB × 1.03 ≈ 16.5 GB. Usable 43.2 GB → KV budget ≈ 43.2 − 16.5 − 2 ≈ 24.7 GB. KV per token =
2 × 64 × 8 × 128 × 2 = 262,144 B (256 KiB). 24.7 × 10⁹ ÷ 262,144 ≈ 94 k tokens → ≈ **23 conversations** of 4,096
tokens. Decode speed is then limited by 864 GB/s: each step reads ≈ 16.5 GB of weights plus the batch's KV, so
≈ 20+ ms per step at best. Fine for a small internal tool; quality after INT4 quantization must be re-evaluated.
</details>

## 9. [Core] Cost per million tokens

A GPU costs $2.50/hour [A] (an assumed committed rate; 2026-11 on-demand list prices for H100s ran ≈ $3–7, see the
lesson §9), sustains 2,000 output tokens/s at full load, and runs at 60 % average utilization. Cost
per million output tokens?

<details><summary>Answer</summary>

Effective tokens per hour = 2,000 × 3,600 × 0.6 = 4.32 M. $2.50 ÷ 4.32 M × 10⁶ ≈ **$0.58 per M output tokens**. At
100 % utilization it would be ≈ $0.35. Utilization is the lever: autoscaling and sharing GPUs across workloads matter
as much as raw speed.
</details>

## 10. [Core] Bandwidth

5 M DAU each view 20 images of 300 KB per day; peak factor 3×. Average and peak egress?

<details><summary>Answer</summary>

5 M × 20 × 300 KB = 30 TB/day → 30 × 10¹² × 8 ÷ 86,400 ≈ **2.8 Gbps** average → ≈ **8.3 Gbps** at peak. That belongs on
a CDN. At an assumed $0.05/GB of origin egress (an assumption, not a checked price), serving all of it from origin would cost ≈ $1,500/day, which is the
argument for caching at the edge.
</details>

## 11. [Core] Decode lower bound

An 8B model in FP8 runs on an L4 (300 GB/s). What is the best possible single-stream decode speed?

<details><summary>Answer</summary>

Each decode step reads ≈ 8 GB of weights: 8 GB ÷ 300 GB/s ≈ 26.7 ms → at most **≈ 37 tokens/s** for one stream, before
KV reads and inefficiency. Batching raises aggregate throughput, because the weights are read once per step for the
whole batch, but cannot make one stream faster than this bound.
</details>

## 12. [Interview] Little's law

An LLM API receives 500 requests/s at peak. Each response streams for 12 s on average. How many concurrent streams must
the gateway and the GPU fleet hold?

<details><summary>Answer</summary>

L = λ × W = 500 × 12 = **6,000 concurrent streams**. The gateway needs 6,000 open connections plus headroom. The GPU
fleet needs KV memory for 6,000 sequences at their average context length. With 2k-token contexts at 128 KiB/token
(an 8B Llama-3-style model), that is 6,000 × 256 MiB ≈ 1.5 TiB of KV across the fleet, which sets the GPU count more
than compute does.
</details>
