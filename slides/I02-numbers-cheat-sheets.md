# I02 — Numbers & cheat sheets (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — Why numbers
- Estimates rule designs in or out ("≈ 15k writes/s, so a single primary is out")
- Constants you memorize vs throughput you label as assumptions
- Every number on this deck is sourced [S], derived [D] or an assumption [A]
**Visual:** three badges S / D / A. Icons: `ops-metrics`.
**Speaker notes:** The label key is the habit to copy into interviews: say which kind of number you are using.

## Slide 2 — Time and rate conversions
- 86,400 s/day ≈ 10⁵; year ≈ π × 10⁷ s
- 1 M/day ≈ 12/s; 1 B/day ≈ 12k/s; 100/s ≈ 8.6 M/day
- Powers of two: KiB vs KB gap is 2.4 % at kilo, 10 % at tera
**Visual:** conversion ladder. Icons: `ops-clock`.
**Speaker notes:** GPU vendors list GB, while tools often report GiB. At GPU scale that is a 7 % difference.

## Slide 3 — The 2009 latency table and its drift
- Dean, LADIS 2009: memory 100 ns, DC round trip 500 µs, disk seek 10 ms, CA–NL–CA 150 ms
- Flat: DRAM latency, cross-continent RTT (physics)
- Changed: NIC bandwidth, SSD tier (≈ 16–100 µs random read), faster fabrics
**Visual:** log-scale bar chart of 2009 values with arrows showing drift direction.
**Speaker notes:** Colin Scott's interactive page extrapolates by year from stated growth assumptions. It is a model,
not a measurement.

## Slide 4 — Speed of light in fiber
- ≈ 5 µs per km one way; ≈ 1 ms RTT per 100 km
- New York–London ≈ 56 ms RTT floor; California–Netherlands ≈ 89 ms (5 µs/km rule)
- AWS says its AZs are within 100 km of each other, so zone hops are ≤ 1 ms of propagation
**Visual:** world map arc with distance and RTT floor labels. Icons: `arch-region`, `pattern-geo-distribution`.
**Speaker notes:** No engineering removes the floor. Only moving data closer does.

## Slide 5 — Throughput rules of thumb (labelled)
- Redis ≈ 10⁵ ops/s per instance unpipelined; ≈ 10⁶ pipelined (Redis docs examples)
- Kafka 2014: ≈ 2 M records/s on 3 HDD brokers, async 3× replication
- Relational writes ≈ 10³–10⁴/s per primary [A]; NIC Gbps ÷ 8 = GB/s
**Visual:** table with a label column. Icons: `cache-redis`, `messaging-kafka`, `sql-postgresql`.
**Speaker notes:** A throughput number without its hardware and access pattern is an assumption. Say "I'd load-test
to confirm".

## Slide 6 — Nines and downtime
- 99.9 % = 43.8 min/month; 99.99 % = 4.4 min; 99.999 % = 26 s
- Serial: multiply (three 99.9 % → 99.7 %)
- Parallel: 1 − Π(1 − A), only if failures are independent
**Visual:** downtime table; serial and parallel block diagrams. Icons: `ops-slo`, `pattern-failover`.
**Speaker notes:** Answer "five nines" with the budget: 26 seconds a month is shorter than most failovers.

## Slide 7 — QPS, concurrency, bandwidth
- avg QPS = DAU × actions ÷ 86,400; × peak factor (2–5× diurnal, more for bursts)
- Little's law: in-flight = rate × duration
- 1 Gbps = 125 MB/s; 1 TB/day ≈ 93 Mbps
**Visual:** DAU → QPS funnel; Little's law triangle. Icons: `arch-users`, `ops-throughput`.
**Speaker notes:** Token streaming at 1.4 M tokens/s is only about 1 Gbps. For LLM services the network is rarely the
bottleneck.

## Slide 8 — Cost formulas
- cost per request = monthly cost ÷ monthly requests
- $/M tokens = $/GPU-h ÷ (tokens/s × 3,600) × 10⁶
- Example: $3/h [A, low end of 2026-11 prices] at 1,400 tokens/s ≈ $0.60/M; at 50 % utilization ≈ $1.20
**Visual:** formula card with one worked line. Icons: `ops-cost`.
**Speaker notes:** Prices are indicative and dated (checked 2026-11-20): H100 list prices ran ≈ $3–7 per GPU-hour on
demand. Other prices are assumptions except where checked (R2 lists $0.015/GB-month and no egress fee).
Utilization is the biggest lever on self-hosted token cost.

## Slide 9 — Model weight memory
- params × {2, 1, 0.5} bytes for {BF16, FP8, INT4}
- 8B: 16 / 8 / ≈ 4 GB · 70B: 140 / 70 / ≈ 36 GB · 405B: 810 / 405 / ≈ 209 GB
- MoE: memory scales with total params (gpt-oss-120b: 117 B total, 5.1 B active)
**Visual:** stacked bars per model and precision. Icons: `arch-memory`, `domain-ai`.
**Speaker notes:** Weights are only the start. The KV cache usually caps concurrency.

## Slide 10 — KV cache per token
- 2 × layers × KV heads × head dim × bytes
- Llama 3: 8B 128 KiB · 70B 320 KiB · 405B 504 KiB per token (BF16)
- H200 + 70B FP8: ≈ 54 GB KV → ≈ 165k tokens → ≈ 40 conversations of 4k tokens
**Visual:** formula with each factor labelled; H200 memory bar split into weights / KV / overhead.
**Speaker notes:** Grouped-query attention (8 KV heads vs 64 query heads) is why these numbers are small. MLA and
sliding windows change the formula, so read the config.

## Slide 11 — GPU memory and bandwidth (as of 2026-11)
- H100 SXM 80 GB @ 3.35 TB/s · H100 NVL 94 GB @ 3.9 TB/s · H200 141 GB @ 4.8 TB/s
- B200 ≈ 180 GB @ ≈ 8 TB/s and GB200 ≈ 186 GB @ ≈ 8 TB/s (derived from system totals)
- B300 up to 288 GB per GPU (NVIDIA system pages: 2.1 TB per 8-GPU node) · L40S 48 GB @ 864 GB/s · L4 24 GB @ 300 GB/s
**Visual:** scatter of capacity vs bandwidth with labels. Icons: `arch-servers-cluster`.
**Speaker notes:** NVIDIA's tensor TFLOPS are listed with sparsity, and dense is half. NVIDIA's two B300 figures do not
match exactly, so plan an 8-GPU node with the 2.1 TB system figure. Bandwidth decides decode speed; capacity decides
concurrency.

## Slide 12 — Compute rules for AI
- Prefill ≈ 2N FLOPs/token; training ≈ 6N FLOPs/token (Kaplan et al.)
- Mixed-precision Adam ≈ 16 bytes/param (ZeRO), so a 70B full fine-tune needs ≈ 1.1 TB of model state
- Decode step ≥ bytes read ÷ HBM bandwidth
**Visual:** three formula cards.
**Speaker notes:** These three formulas answer most GPU-sizing follow-ups in an interview.

## Slide 13 — The one-page card
- Time, latency, bandwidth, nines, Little, weights, KV, GPUs, compute, cost
- Use ratios rather than absolute values
- Say what you would measure
**Visual:** the memorization card from the lesson, as a single slide.
**Speaker notes:** If you remember one slide from this unit, remember this one.
