# 21 — Exercises

Lesson: [course/03-ai-systems/21-llm-inference-anatomy.md](../course/03-ai-systems/21-llm-inference-anatomy.md).
Model and hardware facts used below are from the lesson's cited sources; anything else is a stated assumption.

## 1. [Core] Prefill or decode?

For each symptom, say which phase is responsible and which hardware resource limits it:
(a) a 20,000-token document summary takes 1.5 s before the first word appears;
(b) once text starts, it streams at 30 tokens/s regardless of whether 1 or 10 people use the server;
(c) after enabling FP8 weights, streaming speed nearly doubles but the time to first token barely changes.

<details><summary>Answer</summary>

(a) **Prefill**, compute-bound: 20,000 tokens × 2 × parameters FLOPs, plus attention that grows with length.
(b) **Decode**, memory-bandwidth-bound: each step streams all weights once whatever the batch size, so up to the
point where KV reads or compute start to matter, 1 and 10 users see similar step times. (That is the whole argument
for batching.)
(c) FP8 halves the **bytes** of weights that every decode step reads, so decode (bandwidth-bound) speeds up close to
2×. Prefill is compute-bound; it speeds up only if the matrix multiplies run on FP8 tensor cores *and* prefill was not
dominated by other costs (attention at long context, queueing). A W8A8 FP8 scheme can speed up prefill too; INT4
weight-only usually does not. Acceptable alternative: "prefill sped up a little" if the learner notes W8A8.
</details>

## 2. [Core] KV cache arithmetic

Qwen3-32B: 64 layers, 64 query heads, 8 KV heads, head dimension 128. Compute (a) KV bytes per token in BF16;
(b) KV for one 8,192-token conversation; (c) how many such conversations fit in 40 GB of KV budget; (d) the same three
numbers if the model had used full multi-head attention.

<details><summary>Answer</summary>

(a) 64 × 2 × 8 × 128 × 2 B = **262,144 B = 256 KiB/token**.
(b) 256 KiB × 8,192 = **2 GiB** (2,147,483,648 B).
(c) 40 × 10⁹ ÷ 2,147,483,648 ≈ **18 conversations**.
(d) MHA has 64 KV heads → 8× more: **2 MiB/token**, **16 GiB per conversation**, **2 conversations**. GQA is the
difference between a usable chat server and a toy.
</details>

## 3. [Core] Weights at different precisions

How much memory do the weights of an 8.2 B-parameter model take at BF16, FP8 and INT4 with one FP16 scale per group of
128 weights? Which of these fit, with at least 20 GB left for KV, on a 24 GB GPU, an 80 GB GPU and a 141 GB GPU?

<details><summary>Answer</summary>

BF16 = 16.4 GB; FP8 = 8.2 GB; INT4 = 4.1 GB + 8.2 × 10⁹ / 128 × 2 B ≈ 0.13 GB of scales ≈ **4.2 GB**.
24 GB GPU: none leaves a full 20 GB (INT4 leaves ≈ 19.8 GB before runtime overhead; BF16 and FP8 leave 7.6 and
15.8 GB) — INT4 comes closest, and saying so is the right answer. 80 GB and 141 GB: all three fit with ample KV room. The point: precision choice is often forced by
the *smallest* GPU you must support.
</details>

## 4. [Deep] Roofline for decode

A GPU offers 1,000 TFLOP/s (dense, BF16) and 4 TB/s. A dense model with BF16 weights runs decode at batch size *B*.
(a) What is the arithmetic intensity of the weight matrix multiplies as a function of *B*? (b) At which *B* do they
become compute-bound? (c) Why does attention over the KV cache not become compute-bound at that *B*?

<details><summary>Answer</summary>

(a) Each 2-byte weight is used for 2 FLOPs per sequence → AI ≈ 2*B* / 2 = ***B* FLOP/byte**.
(b) Ridge = 10¹⁵ / 4 × 10¹² = **250 FLOP/byte** → *B* ≈ 250 (ignoring KV traffic, which pushes it higher).
(c) KV is per sequence: no two sequences share it, so batching does not increase reuse. Attention's AI ≈ query
heads ÷ KV heads (the GQA group size), e.g. ≈ 4 — far below 250 at any batch size.
</details>

## 5. [Core] Metrics from a trace

A streamed response has: request sent at t = 0 ms; first token at 420 ms; 101 output tokens in total; last token at
4,420 ms. One gap between tokens was 900 ms; the rest were roughly equal. Compute TTFT, TPOT and E2E. What does the
900 ms gap tell you, and which metric exposes it?

<details><summary>Answer</summary>

TTFT = **420 ms**. E2E = **4,420 ms**. TPOT = (4,420 − 420) ÷ (101 − 1) = **40 ms**.
The 900 ms gap is a **stall** — typically another request's long prefill scheduled into this request's decode, or a
preemption. TPOT (an average) hides it; **ITL p99** (the distribution of individual gaps) exposes it. Mitigation:
chunked prefill with a smaller token budget, or disaggregated prefill (chapter 22).
</details>

## 6. [Core] Why p99?

Lumen's research assistant makes 8 sequential LLM calls per user question. Each call independently has a 1 % chance of
exceeding its p99 latency. What fraction of user questions experiences at least one p99-or-worse call? What if
calls are made in parallel and the answer waits for all of them?

<details><summary>Answer</summary>

1 − 0.99⁸ ≈ **7.7 %** of questions. In parallel the probability is the same (at least one of 8 is slow), but now
the slow call sets the end-to-end latency directly — the "tail at scale" effect. Sequential chains also add the
latencies, so the *expected* end-to-end grows with the chain length. Design implication: per-call p99 targets must be
much stricter than the product-level target.
</details>

## 7. [Deep] Capacity on one GPU

Using the lesson's H100 numbers (80 GB, 3.35 TB/s; 70 % of bandwidth achievable — assumption) and Qwen3-8B in BF16
(16.4 GB weights; 144 KiB KV per token), Lumen's chats average 3,000 tokens of context. (a) Max concurrent sequences
with a 53.6 GB KV budget? (b) Step time at that batch? (c) Does it meet a 20 tokens/s per-user target?

<details><summary>Answer</summary>

(a) 3,000 × 147,456 B = 442 MB per sequence → 53.6 × 10⁹ ÷ 4.42 × 10⁸ ≈ **121 sequences**.
(b) Bytes per step = 16.4 GB + 121 × 0.442 GB ≈ 69.9 GB → ÷ (0.7 × 3.35 TB/s = 2.345 TB/s) ≈ **29.8 ms**.
(c) 1 ÷ 0.0298 ≈ **33.6 tokens/s per user** > 20, so the binding constraint is **KV memory**, not speed. Options to raise
concurrency: FP8 KV (≈ 2×), FP8 weights (+8.2 GB of KV budget), shorter context via summarisation. Always confirm with a
load test; this ignores compute, scheduler overhead and interleaved prefill.
</details>

## 8. [Interview] Debug a slow endpoint

"After a product launch, Lumen's TTFT p99 went from 600 ms to 6 s. TPOT p50 is unchanged at 35 ms." Give a structured
answer in under two minutes.

<details><summary>Answer</summary>

Outline: (1) **Localise the phase:** TPOT unchanged → decode healthy; TTFT up → queueing, tokenisation or prefill.
(2) **Check queue metrics:** `vllm:num_requests_waiting` and `vllm:request_queue_time_seconds`; if queue time ≈ the
increase, the system is saturated (arrival rate above capacity) — a queueing problem, not a model problem.
(3) **Check prompt length distribution:** did the launch add long prompts (RAG documents, longer history)? Prefill
time grows with length. (4) **Check prefix-cache hit rate:** a new system prompt or routing change can collapse it.
(5) **Mitigate:** scale replicas (autoscale on queue depth), admission control/load shedding for low-priority traffic,
per-tenant token rate limits, prompt trimming; protect the SLO first, then optimise. Red flag answer: "add GPUs" with
no diagnosis, or blaming decode.
</details>

## 9. [Lab] Predict, then measure

Before running Lab L21, predict: (a) how TTFT changes when prompt length goes from 50 to 1,500 words; (b) how TPOT
changes; (c) whether aggregate output tokens/s at concurrency 8 is closer to 1× or 8× that at concurrency 1 on a CPU.
Then run the lab and explain any surprises.

<details><summary>Answer</summary>

Expected direction: (a) TTFT rises roughly linearly with prompt tokens (prefill work); (b) TPOT rises only slightly
(more KV to read per step); (c) aggregate throughput rises **well above 1×** but **below 8×** — on a CPU, compute is
scarcer relative to bandwidth than on a GPU, so batching gains saturate sooner. Record your measured numbers with your
CPU model and core count; surprises usually come from thread pinning, other load on the laptop, or early stopping
(use `--ignore-eos`).
</details>

## 10. [Interview] One-GPU sizing question

"How many users can one H100 serve for our 8B chat model?" What do you ask, and what is the shape of your answer?

<details><summary>Answer</summary>

Ask: model architecture (layers, KV heads), precision, context and output length distributions, SLOs (TTFT p95, TPOT
p95), "users" meaning concurrent streams vs daily users, think time. Compute: weights → KV budget → max concurrent
sequences; decode step time at that batch → per-user tokens/s vs SLO; prefill time → TTFT budget left for queueing.
Answer as a **range with the binding constraint named** ("≈ 100–150 concurrent 2k-token streams, KV-limited; TTFT holds
below ≈ 80 % utilisation; confirm with a load test"), and convert concurrent streams to daily users via think time
and Little's law.
</details>
