# 22 — Exercises

Lesson: [course/03-ai-systems/22-serving-llms-at-scale.md](../course/03-ai-systems/22-serving-llms-at-scale.md).
Version-specific facts are as of 2026-11 (vLLM v0.34.0). Numbers not from a cited source are labelled assumptions.

## 1. [Core] What PagedAttention actually fixes

A pre-2023 server reserves KV for `max_tokens = 2,048` per request; typical requests use 400 tokens. (a) What fraction
of reserved KV is used? (b) How does paging change this with 64-token blocks? (c) Why does that raise throughput even
though no kernel became faster?

<details><summary>Answer</summary>

(a) 400 ÷ 2,048 ≈ **20 %** — consistent with the 20.4 %–38.2 % utilisation Kwon et al. measured in existing systems.
(b) Blocks are allocated on demand: 400 tokens need ⌈400/64⌉ = 7 blocks = 448 token slots → ≈ **89 %** used; waste is
confined to the last block (and shrinks further with smaller blocks, at the cost of more block-table overhead).
(c) More sequences fit in the same memory → **bigger batches** → each decode step (which reads the weights once)
produces more tokens. Throughput is memory-capacity-limited, and paging frees capacity.
</details>

## 2. [Core] Continuous vs static batching

Four requests arrive together and need 10, 50, 50 and 400 output tokens. A fifth arrives at step 20 needing 30 tokens.
Each step takes the same time. With static batching (batch of 4, then the next batch), and with continuous batching
(max batch 4), when does request 5 finish and how many slot-steps are wasted on finished sequences?

<details><summary>Answer</summary>

**Static:** batch 1 runs 400 steps; request 5 waits, starts at step 400, finishes at **step 430**. Wasted slot-steps
in batch 1: (400 − 10) + (400 − 50) + (400 − 50) = **1,090**.
**Continuous:** request 1 finishes at step 10, freeing a slot; request 5 joins at step 20 (when it arrives) and
finishes at **step 50**. Wasted slot-steps on finished sequences: **0** (idle slots exist only while nothing is
waiting). This is Orca's iteration-level scheduling.
</details>

## 3. [Core] Prefix caching hit maths

Every Lumen request has a 1,200-token system prompt plus 300 unique tokens. vLLM caches only full blocks (64 tokens).
(a) What fraction of prompt tokens can hit the cache on a warm replica? (b) What happens to the hit rate if the system
prompt includes the current timestamp at the top? (c) How should the prompt be structured?

<details><summary>Answer</summary>

(a) 1,200 ÷ 64 = 18.75 → 18 full blocks = 1,152 tokens cached; hit fraction ≈ 1,152 ÷ 1,500 ≈ **77 %**.
(b) Block hashes chain from the first block, so a changing first block changes every hash: hit rate → **≈ 0 %**.
(c) Put **stable content first** (instructions, tools, few-shot examples), variable content (timestamp, user data,
retrieved documents) **last**. Keep stable prefixes byte-identical across requests (same whitespace, same order of tool
definitions).
</details>

## 4. [Deep] vLLM V1 scheduling

Explain what the V1 scheduler emits each step and walk through one step with `max_num_batched_tokens = 2,048`, 100
running decodes and one new 5,000-token prompt waiting.

<details><summary>Answer</summary>

The scheduler emits `{request_id: num_tokens}`. With chunked prefill, decodes are scheduled first: 100 requests × 1
token = 100 tokens. Remaining budget 1,948 tokens → the new prompt gets a **1,948-token chunk** this step (more in
following steps: 1,948 + 1,948 + 1,104). The 100 users see one slightly longer step instead of a stall for a full
5,000-token prefill; the new request's TTFT spans three steps. Raising the budget shortens TTFT for long prompts but
lengthens every step (ITL); lowering it does the opposite.
</details>

## 5. [Core] Router design

Lumen runs 8 vLLM replicas. Compare round-robin, consistent hashing on conversation ID, and a scoring router (prefix
match − load penalty). Which failure does each have?

<details><summary>Answer</summary>

- **Round-robin:** ignores both cost variance and cache locality → low prefix-hit rate and queue imbalance.
- **Consistent hashing on conversation ID:** good multi-turn locality, but hot conversations/tenants overload one
  replica; on scale-out ≈ 1/(N+1) of keys move and their caches go cold; shared system prompts are duplicated on all
  replicas (fine) but cross-conversation reuse (same document) is missed.
- **Scoring router:** best hit rate and balance, but needs fresh load signals (queue depth, KV usage) and prefix state
  (approximate from recent routing, or precise from KV events); stale signals cause herding. Use bounded-load
  hashing or a load penalty to cap skew. This is what the Gateway API Inference Extension's Endpoint Picker and llm-d's
  router implement.
</details>

## 6. [Core] Autoscaling signal

A team autoscales vLLM pods on CPU > 70 %. Under a traffic spike, TTFT p99 hits 20 s and no scale-up happens. Explain
and fix.

<details><summary>Answer</summary>

vLLM's CPU usage is dominated by the API server and engine loop and does not track GPU saturation; the GPU can be
saturated at modest CPU. Scale on **`vllm:num_requests_waiting`** (smoothed, per replica) or queue time, with
**`kv_cache_usage_perc`** plus preemptions as a secondary signal, and an SLO guard-rail on TTFT p95. Add headroom and
scale on leading indicators because cold starts take minutes (image pull, weight load, warm-up). Pair with admission
control so overload degrades gracefully while capacity arrives.
</details>

## 7. [Deep] Disaggregation decision

Workload A: 300-token prompts, 500-token outputs, 4 GPUs total. Workload B: 20,000-token RAG prompts, 200-token outputs,
strict ITL p99 < 60 ms, 64 GPUs on one NVLink/RDMA fabric. Disaggregate which, and why?

<details><summary>Answer</summary>

**A: no.** Prefill is tiny; interference is minor; two pools of 2 GPUs each would waste capacity and add KV-transfer
complexity. Use colocated replicas with chunked prefill.
**B: yes, likely.** Long prefills would repeatedly stall decodes (ITL spikes); separate pools let you size prefill
(compute-heavy, possibly larger TP) and decode (bandwidth-heavy, large batch) independently; the fast fabric makes KV
transfer cheap relative to recompute. Keep in mind vLLM's own warning that disaggregation does not improve
throughput by itself — the win is meeting ITL and TTFT SLOs simultaneously (goodput).
</details>

## 8. [Deep] Speculative decoding

γ = 5 draft tokens, acceptance α = 0.6. Expected tokens per target step? If the target step costs 30 ms and the draft
adds 6 ms, what is the expected speed-up? Why might it vanish at batch 128?

<details><summary>Answer</summary>

(1 − 0.6⁶) ÷ (1 − 0.6) = (1 − 0.0467) ÷ 0.4 ≈ **2.38 tokens per step**. Time per step ≈ 36 ms → 2.38 ÷ 36 ms ≈ 66
tokens/s vs 1 ÷ 30 ms ≈ 33 tokens/s → **≈ 2.0×** (assuming verification costs about one normal decode step, which
holds when decode is bandwidth-bound). At batch 128 the step is closer to compute-bound; verifying 6 tokens per
sequence multiplies compute per step, so the step gets much slower and the gain shrinks or turns negative — hence
vLLM's guidance that it targets medium-to-low QPS, memory-bound workloads.
</details>

## 9. [Interview] Capacity plan variant

Redo the lesson's plan with outputs of 600 tokens (prompts unchanged). How many decode GPUs, and what happens to cost
per 1M output tokens if the fleet scales proportionally?

<details><summary>Answer</summary>

Output tokens/s doubles to 100,000. Average decode context = 1,500 + 300 = 1,800 tokens → 236 MB per sequence (FP8 KV,
128 KiB/token) → KV cap ≈ 35.2 GB ÷ 0.236 GB ≈ 149 sequences. At *B* = 128: bytes = 32.8 + 128 × 0.236 = 63.0 GB →
step ≈ 26.8 ms → ≈ 4,770 tokens/s per GPU → 100,000 ÷ 4,770 ≈ **21 decode GPUs** (prefill unchanged at ≈ 8.3). Base ≈
29.3, × 1.5 peak ≈ 44 → ≈ 48 GPUs (six nodes) after headroom. Cost per 1M output tokens ≈ (48 × $3) ÷ 360 M/h ≈
**$0.40** — lower than before because prefill cost is spread over more output tokens. State that every input to this
is an assumption to validate with a benchmark.
</details>

## 10. [Core] Engine choice

Pick an engine (or layer) and justify in one sentence each: (a) a single developer laptop app; (b) an NVIDIA-only fleet
chasing maximum tokens/s for one model; (c) a multi-model Kubernetes platform with many LoRA adapters; (d) a new
project currently on TGI; (e) a large multi-node MoE deployment with P/D disaggregation.

<details><summary>Answer</summary>

(a) **llama.cpp / Ollama** — CPU/Apple-silicon friendly, GGUF quantisation, single user. (b) **TensorRT-LLM** (or vLLM
— benchmark both) — NVIDIA-tuned kernels. (c) **vLLM** with multi-LoRA behind an inference gateway (Gateway API
Inference Extension / llm-d / KServe) — adapter-aware routing and broad model support. (d) **Migrate** to vLLM or
SGLang — TGI is in maintenance mode and its README recommends them. (e) **vLLM or SGLang under llm-d or NVIDIA
Dynamo** — orchestration layers built for P/D, KV-aware routing and wide expert parallelism. Acceptable alternatives
exist; the justification matters more than the name.
</details>

## 11. [Lab] Interpret your sweep

In Lab L22 your concurrency sweep shows output tokens/s at concurrency 1, 2, 4, 8, 16. Describe what shape you expect,
where the knee is, and how prefix caching changes TTFT for the shared-prefix run.

<details><summary>Answer</summary>

Aggregate tokens/s rises steeply at first (each step's fixed weight-read cost is shared) and then flattens as the CPU's
compute becomes the limit; per-request TPOT rises. The knee is where TPOT starts rising faster than aggregate
throughput — on a laptop CPU this comes at much lower concurrency than on a GPU. With prefix caching on, TTFT for
requests sharing the long prefix drops sharply after the first request, and `vllm:prefix_cache_hits_total` grows; with it
off, every request pays the full prefill. Report your hardware and measured numbers rather than expecting the lesson's
GPU numbers.
</details>
