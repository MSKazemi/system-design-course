# 22 — Serving LLMs at scale (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/03-ai-systems/22-serving-llms-at-scale.md](../course/03-ai-systems/22-serving-llms-at-scale.md).
Version facts are as of 2026-11 (vLLM v0.34.0); numbers carry the lesson's citations and labelled assumptions.

## Slide 1 — The requirement

- Qwen3-32B for 10,000 concurrently active users
- TTFT p95 < 2 s, TPOT p95 < 50 ms, and a price per million tokens
- New problems at fleet scale: full batches within SLO, no repeated prefill, stateful replicas that take minutes to start
- vLLM at the centre; SGLang, TensorRT-LLM, llama.cpp around it

**Visual:** many users → one gateway → a row of GPU servers. Icons: `arch-users`, `arch-api-gateway`, `arch-servers-cluster`.

**Speaker notes:** Chapter 21 explained one GPU. This chapter is about keeping a fleet of them full, fast and cheap.

## Slide 2 — PagedAttention

- Old servers reserved contiguous KV for the maximum length: only 20.4–38.2 % held real tokens (Kwon et al.)
- KV in fixed blocks (vLLM default now 64 tokens) + per-sequence block tables
- On-demand allocation; sharing with copy-on-write
- Result reported: near-zero waste, 2–4× throughput at the same latency

**Visual:** the lesson's block-table diagram: two sequences sharing one physical block. Icons: `ai-kv-cache`, `arch-memory`, `pattern-partitioning`.

**Speaker notes:** It's virtual memory for the KV cache. No kernel got faster; more sequences fit, so batches got bigger.

## Slide 3 — Continuous batching

- Orca (OSDI 2022): iteration-level scheduling + selective batching
- Finished sequences leave and waiting ones join every step
- vLLM V1: scheduler emits `{request_id: num_tokens}` under a token budget
- Out of KV → preempt by recompute (V1 default)

**Visual:** lanes timeline: static batch with idle gaps vs continuous batch with lanes refilled. Icons: `pattern-batching`, `arch-queue`.

**Speaker notes:** Walk through the 10/50/50/400-token example from the exercises: request 5 finishes at step 50 instead
of 430.

## Slide 4 — Prefix caching

- Block hash = parent hash + tokens + extras (LoRA ID, multimodal hash, cache salt)
- Only full blocks; LRU free queue keeps freed blocks reusable
- SHA-256 by default since v0.11; per-tenant `cache_salt` for isolation
- On by default in V1; SGLang's RadixAttention generalises it to a radix tree

**Visual:** a chain of hashed blocks; a second prompt reusing the first N blocks. Icons: `arch-cache`, `ai-kv-cache`, `security-key`.

**Speaker notes:** Stable content first, variable content last — a timestamp at the top of the system prompt takes the
hit rate to zero.

## Slide 5 — vLLM V1 architecture

- API server: HTTP, tokenisation, detokenisation, streaming
- Engine core: busy loop with scheduler and KV cache manager (one per DP rank)
- One worker process per GPU; ZMQ between processes
- V1 default since v0.8.0; V0 removed in v0.11.0; v0.34.0 = Model Runner V2 only

**Visual:** the lesson's process diagram. Icons: `ai-vllm`, `arch-server`, `language-python`.

**Speaker notes:** The architecture is CPU-sensitive: starve the API server or engine core and the GPU idles between
steps.

## Slide 6 — Chunked prefill and structured outputs

- Decodes first, then prefill chunks fill `max_num_batched_tokens`
- Big budget → better TTFT/throughput; small budget → flatter ITL
- Structured outputs: xgrammar or guidance mask logits per step
- Cost: CPU per step, grammar compilation on first use

**Visual:** one step's token budget as a bar: 100 decode tokens + a 1,948-token prefill chunk. Icons: `ops-throughput`, `protocol-json`.

**Speaker notes:** Sarathi-Serve introduced "stall-free" schedules; in vLLM V1 chunked prefill is on by default.

## Slide 7 — Routing: not round-robin

- Signals: queue depth, KV usage, prefix affinity, adapter affinity, P/D role
- Affinity vs load: always mix a hit score with a load penalty
- Gateway API Inference Extension: InferencePool (v1) + Endpoint Picker via Envoy ext-proc
- EPP now lives in llm-d/llm-d-router (as of 2026-11)

**Visual:** gateway with an "endpoint picker" choosing among pods annotated with cache and queue gauges. Icons: `proxy-envoy`, `devops-kubernetes`, `arch-load-balancer`.

**Speaker notes:** llm-d reports 3× throughput and 2× faster TTFT with prefix-aware routing in one Red Hat/Tesla
deployment (Llama 3.1 70B on 4 × AMD MI300X), a before/after on that running deployment rather than a controlled
benchmark — vendor-reported, so treat it as a direction, not a law.

## Slide 8 — Autoscaling on the right signals

- Not CPU, not "GPU utilisation"
- Queue depth (leading), KV usage + preemptions (capacity), TTFT/ITL percentiles (guard-rail)
- Cold start = node + image + weights + graphs + warm-up: minutes
- Weight streaming (Run:ai streamer), sleep mode, warm pools, headroom

**Visual:** HPA loop reading `num_requests_waiting` from Prometheus. Icons: `pattern-autoscaling`, `observability-prometheus`.

**Speaker notes:** Because scale-up lag is minutes, scale early and shed load gracefully while capacity arrives.

## Slide 9 — Disaggregated prefill and decode

- DistServe: 7.4× more requests or 12.6× tighter SLO (paper-reported)
- Splitwise: decode does not need the newest compute; Mooncake: KV-centric, tiered KV pool
- vLLM: KV connectors (NIXL, LMCache) — experimental; "DOES NOT improve throughput"
- Worth it for long prompts, strict ITL, big fleets on fast fabrics

**Visual:** prefill pool → KV transfer arrow → decode pool → SSE to user; tiered KV store underneath. Icons: `arch-servers-cluster`, `arch-network`, `arch-storage-disk`.

**Speaker notes:** The value is goodput — meeting TTFT and ITL together — not raw throughput.

## Slide 10 — Speculative decoding, quantisation, parallelism

- Speculation: expected tokens/step = (1 − α^(γ+1)) ÷ (1 − α); γ = 4, α = 0.7 → ≈ 2.8
- Best at low/medium load; lossless up to numerics
- FP8 W8A8, AWQ, GPTQ, FP8 KV: evaluate every one
- TP inside a node, PP across nodes, EP for MoE, DP for replicas

**Visual:** draft model proposing tokens, target verifying in one pass; table of parallelism types. Icons: `pattern-compression`, `arch-servers-cluster`.

**Speaker notes:** Quote published speed-ups with their conditions: Leviathan 2–3× on T5-XXL; EAGLE 2.7–3.5× on
LLaMA2-Chat 70B; expect less under heavy batching.

## Slide 11 — Capacity plan in seven lines

- 10,000 users ÷ 60 s think time ≈ 167 req/s
- 250k prompt tokens/s (100k uncached at 60 % hit rate); 50k output tokens/s
- Prefill ≈ 8.3 H100s (FP8, 40 % MFU assumed)
- Decode: FP8 KV 128 KiB/token, batch 128 → ≈ 4,960 tokens/s per GPU → ≈ 10.1 GPUs
- × 1.5 peak + failure headroom → 32 GPUs (four 8-GPU nodes)

**Visual:** funnel from users to GPUs with each conversion labelled. Icons: `arch-users`, `ops-throughput`, `arch-servers-cluster`.

**Speaker notes:** Every line is a fact or a labelled assumption. Change the assumptions, keep the method, then benchmark.

## Slide 12 — Cost per million tokens

- $96/hour fleet at an assumed $3.00 per GPU-hour
- ≈ $0.53 per 1M output tokens (all cost on output)
- Split by GPU time: ≈ $0.048 per 1M prompt tokens, ≈ $0.29 per 1M output tokens
- Utilisation is the hidden multiplier: half the load → double the price

**Visual:** price tag split into prefill and decode slices. Icons: `ops-cost`.

**Speaker notes:** These are GPU-only costs from a roofline model. Real unit economics (chapter 16) add CPUs, network,
storage, people and idle capacity.

## Slide 13 — The engine landscape (as of 2026-11)

- vLLM v0.34.0 — broad default; SGLang v0.5.23 — prefix-heavy and structured; TensorRT-LLM 1.2.1 stable (1.4 RCs out) — NVIDIA-max
- TGI — maintenance mode, archived; README recommends vLLM/SGLang
- llama.cpp / Ollama — laptops and edge
- Above engines: llm-d v1.0.0, NVIDIA Dynamo v1.6.2, KServe v0.21.0, vLLM production-stack

**Visual:** layered stack: engines at the bottom, orchestration in the middle, gateway on top. Icons: `devops-kubernetes`, `arch-api-gateway`.

**Speaker notes:** Versions move monthly; re-verify before any production decision.

## Slide 14 — Interview angle

- CLARIFY prefix reuse, lengths, SLO percentiles, tenants/adapters, peak vs average
- QUANTIFY users → req/s → tokens/s → prefill and decode GPUs → $/1M tokens
- DEEPEN two of: batching + paging, prefix caching + routing, P/D, quantisation/speculation
- Red flags: round-robin LB, CPU autoscaling, cross-node TP without reason, vendor speed-ups as laws

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip. Icons: `ops-check`.

**Speaker notes:** Close with the full case study C09 (ChatGPT-style service), which applies this chapter end to end.
