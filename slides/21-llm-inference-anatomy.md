# 21 — Anatomy of LLM inference (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/03-ai-systems/21-llm-inference-anatomy.md](../course/03-ai-systems/21-llm-inference-anatomy.md).
All numbers are from the lesson and carry its citations and labelled assumptions.

## Slide 1 — The requirement

- Lumen chat on an open 8B model: first token < 500 ms p95, ≥ 20 tokens/s per user
- Finance: "how many users per GPU?"
- A web-service mental model ("X ms of CPU per request") cannot answer this
- An LLM request is a loop: one big parallel step, then hundreds of tiny sequential steps

**Visual:** Lumen chat box with a stopwatch on the first word and a speedometer on the stream. Icons: `domain-chat`, `ops-latency`, `domain-ai`.

**Speaker notes:** Start with the three numbers product and finance actually ask for. By the end of the chapter each
one is an estimate with a named bottleneck. The rest of the deck takes the loop apart.

## Slide 2 — Tokens in, tokens out

- Models see integer token IDs from a fixed vocabulary (Qwen3-8B: 151,936 entries)
- Everything is priced and limited in tokens: context, KV cache, rate limits, bills
- Tokenisation is CPU work; detokenisation must be incremental (UTF-8 boundaries)
- Stream chunks are not tokens: count with the usage field

**Visual:** a sentence split into coloured token boxes with IDs underneath. Icons: `ai-tokens`, `domain-document`, `arch-cpu`.

**Speaker notes:** The unit of everything downstream is the token. Measure words-per-token for your own traffic; the lab
does this with vLLM's /tokenize endpoint.

## Slide 3 — Prefill vs decode

- Prefill: all N prompt tokens in one pass → first token (TTFT)
- Decode: one token per step per sequence, strictly sequential (TPOT/ITL)
- Prefill is compute-bound; decode is memory-bandwidth-bound
- Different bottlenecks → different levers and different SLOs

**Visual:** sequence diagram from the lesson: one wide prefill bar, then a row of thin decode ticks. Icons: `arch-server`, `ops-throughput`.

**Speaker notes:** This asymmetry was characterised in Splitwise and is the basis of DistServe's separate TTFT and TPOT
SLOs. If you remember one thing from this chapter, remember which phase is limited by what.

## Slide 4 — Roofline in one picture

- Arithmetic intensity = FLOPs ÷ bytes moved
- Ridge point = peak FLOP/s ÷ bandwidth; H100 BF16 ≈ 295 FLOP/byte
- Decode matmuls at batch B: ≈ B FLOP/byte → memory-bound until B is in the hundreds
- Prefill of 2,000 tokens: ≈ 2,000 FLOP/byte → compute-bound

**Visual:** roofline chart: sloped bandwidth roof, flat compute roof; dots for "decode B=1", "decode B=128", "prefill 2k". Icons: `arch-cpu`, `arch-memory`.

**Speaker notes:** Derive the ridge from the datasheet: 989.5 dense TFLOPS over 3.35 TB/s. Then note the sparsity
footnote — vendor peaks marked "with sparsity" must be halved for dense work.

## Slide 5 — Attention decode never gets compute-bound

- Each sequence reads its own K and V: no sharing across the batch
- Intensity ≈ query heads ÷ KV heads (GQA group size)
- Qwen3-8B: 32 ÷ 8 = 4 FLOP/byte at any batch size
- Long context → slow decode; smaller KV → faster decode

**Visual:** two sequences, each with its own KV stack, arrows to the GPU; a gauge stuck at "4". Icons: `arch-memory`, `ops-latency`.

**Speaker notes:** This is the quantitative reason KV-cache size reductions — GQA, MQA, FP8 KV — matter so much for
serving, and why the next chapter is about managing the KV cache.

## Slide 6 — The KV cache formula

- KV bytes per token = layers × 2 × KV heads × head dim × bytes
- Qwen3-8B (36 × 2 × 8 × 128 × 2 B) = 144 KiB per token
- 4,096-token chat = 576 MiB; 32,768 tokens = 4.5 GiB
- MHA would be 576 KiB per token (4×); MQA 18 KiB

**Visual:** stacked bar per layer growing with each token; side table MHA / GQA / MQA. Icons: `ai-kv-cache`, `arch-memory`.

**Speaker notes:** All values come from the official config.json. Multiply by concurrent sequences to get the server's
KV footprint — this is what usually runs out first.

## Slide 7 — Weights at BF16, FP8, INT4

- Qwen3-8B: 16.4 GB BF16 → 8.2 GB FP8 → ≈ 4.2 GB INT4 (with group scales)
- Fewer weight bytes = faster decode at small batch
- Prefill speeds up only if the matmuls run in low precision (W8A8)
- Quantisation is a model change: evaluate before shipping

**Visual:** three bars shrinking; a speedometer that rises for decode. Icons: `pattern-compression`, `arch-memory`.

**Speaker notes:** INT4 weight-only schemes such as AWQ and GPTQ usually dequantise before multiplying, so they help
memory and decode more than prefill.

## Slide 8 — Batching is the cost lever

- One decode step reads all weights once, whatever the batch size
- B = 1 → 128: aggregate tokens/s ≈ 39× higher; each user only ≈ 3× slower (bandwidth model)
- At B = 128, KV reads dominate step bytes (38.7 of 55.1 GB)
- Static batching wastes slots; continuous batching re-forms the batch every step

**Visual:** the lesson's batch table as a two-line chart: aggregate tokens/s rising, per-user tokens/s falling gently. Icons: `pattern-batching`, `ops-throughput`.

**Speaker notes:** These are roofline estimates with a 70 % bandwidth-efficiency assumption, not benchmarks. The shape is
what matters; the lab shows the same shape on a CPU.

## Slide 9 — Answering Lumen

- KV budget on an H100 ≈ 53.6 GB → ≈ 363k tokens → ≈ 177 concurrent 2k-token chats
- Decode stays above 20 tokens/s per user well past that batch
- Prefill of 2k tokens ≈ 66 ms (assumed 50 % of dense BF16)
- Answer: ~100–150 concurrent streams per GPU, KV-limited; TTFT protected by admission control

**Visual:** a GPU split into weights, KV and overhead; user icons filling the KV area. Icons: `arch-users`, `arch-server`.

**Speaker notes:** The answer is a range with its binding constraint named, plus the load test you would run to confirm.
That is the interview-quality answer.

## Slide 10 — Metrics: TTFT, TPOT, ITL, goodput

- TTFT = queue + tokenise + prefill; TPOT = (E2E − TTFT) ÷ (n − 1)
- ITL = individual gaps; p99 ITL catches stream freezes
- Goodput = completed requests per second that met all SLOs (DistServe; vLLM benchmark)
- Report percentiles, from the client side as well as the server

**Visual:** a timeline of one streamed response annotated with TTFT, gaps and E2E. Icons: `ops-metrics`, `ops-slo`.

**Speaker notes:** A request can have a fine TPOT and a terrible p99 ITL if a long prefill was scheduled into its
stream. Throughput without SLOs is a vanity metric.

## Slide 11 — Why p99 matters for LLM products

- Agents chain calls: 10 calls → 0.99¹⁰ ≈ 90 % chance all under p99
- TTFT includes queueing, which explodes near saturation
- Tail at scale (Dean & Barroso): the tail of parts becomes the median of the whole
- Per-call targets must be stricter than product targets

**Visual:** a chain of 10 boxes, one red. Icons: `domain-bot`, `ops-latency`.

**Speaker notes:** Connect to the queueing material in chapter 01. LLM products fan out sequentially, which makes tails
add up as well as compound.

## Slide 12 — Streaming with SSE

- `text/event-stream`: `data: {...}` events, final `data: [DONE]`
- `stream_options.include_usage` gives exact token counts in the last chunk
- Traps: proxies that buffer, idle timeouts shorter than generations
- SSE vs WebSockets: one-way, plain HTTP, proxy-friendly

**Visual:** HTTP response pipe with discrete event packets flowing to a browser. Icons: `protocol-json`, `proxy-nginx`, `client-chrome`.

**Speaker notes:** Many "the model is slow" tickets are buffering proxies. Disable buffering for event streams and set
timeouts above your longest allowed generation.

## Slide 13 — Interview angle

- CLARIFY: architecture, precision, lengths, SLOs as TTFT/TPOT percentiles
- QUANTIFY: weights, KV per token, KV budget, step time from bandwidth, prefill from FLOPs
- STRESS: long contexts, bursts, preemption, proxy buffering
- Red flags: GPU FLOPs to explain decode; no KV cache; tokens/s without "per user" or "aggregate"

**Visual:** the six-step framework strip with the formulas under QUANTIFY. Icons: `ops-check`.

**Speaker notes:** The most common follow-up is "how do you autoscale it" — the answer (queue depth and KV usage, not
CPU) leads straight into chapter 22.
