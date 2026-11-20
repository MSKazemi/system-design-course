# C09 — ChatGPT-style LLM chat service (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- "Design ChatGPT" for 10 M daily users
- Streamed answers, first token p95 < 1 s, ≥ 20 tokens/s
- Two models (8B-class, 70B-class), paid tiers with token quotas
- History kept; EU data stays in the EU; cost per conversation
**Visual:** title card with a chat bubble streaming tokens. Icons: `domain-chat`, `arch-users`, `domain-ai`.
**Speaker notes:** The money and the latency are in the GPUs, not the web tier. Everything in this case follows from
counting tokens instead of requests.

## Slide 2 — CLARIFY
- Functional: create/resume conversations, stream, cancel, regenerate, model choice, safety
- Non-functional: TTFT and TPOT as separate SLOs, 99.9 % availability, RPO ≈ 0 for history
- Out of scope: training, RAG (C10), agents (C11)
- Key question: own GPUs or a hosted provider?
**Visual:** two-column list functional / non-functional. Icons: `ops-slo`, `ops-latency`.
**Speaker notes:** Owning GPUs makes capacity planning the centre of the interview; a hosted provider makes it a quota
and budget problem.

## Slide 3 — Users → requests/s
- 10 M DAU × 3 conversations × 3.3 turns ≈ 100 M requests/day
- Average ≈ 1,160 req/s; assumed peak 3× ≈ 3,500 req/s
- All labelled assumptions — the method is the point
**Visual:** funnel: DAU → conversations → requests → req/s.
**Speaker notes:** Say every assumption out loud and write it down; interviewers grade the chain, not the digits.

## Slide 4 — Requests → tokens/s
- Input per request ≈ 3,600 tokens (system prompt 1,500 + history 2,000 + message 100)
- Output ≈ 400 tokens → peak 1.4 M output tokens/s
- Raw input 12.6 M tokens/s; with 70 % prefix-cache hits ≈ 3.8 M tokens/s to prefill
- Chat is prefill-heavy (input ≈ 9× output)
**Visual:** stacked bar of one request's tokens (system / history / new / output).
**Speaker notes:** The 70 % hit rate is a design decision you have to earn with cache-aware routing.

## Slide 5 — KV cache: the senior insight
- KV bytes/token = 2 × layers × KV heads × head dim × bytes
- Llama 3.3 70B: 2 × 80 × 8 × 128 × 2 B ≈ 320 KiB/token (BF16)
- 1,500-token system prompt ≈ 470 MiB per sequence; × 128 sequences ≈ 59 GiB duplicated
- Prefix caching stores it once
**Visual:** 128 identical blocks collapsing into one shared block. Icons: `arch-memory`, `pattern-deduplication`.
**Speaker notes:** This one calculation shows you understand why prefix caching and cache-aware routing matter.

## Slide 6 — Tokens/s → GPUs
- Decode is bandwidth bound: 4 × H100, FP8 70B, 128 sequences → ≈ 1,400 output tokens/s/GPU (assumption)
- Prefill is compute bound: ≈ 140 GFLOP/token → ≈ 5,700 tokens/s/GPU at 40 % utilisation (assumption)
- All-70B: ≈ 1,000–1,700 GPUs with cache-aware routing; ≈ 2× without
- Route 70 % to an 8B model → planning figure ≈ 600–800 GPUs at peak
**Visual:** lever ranking bar: small-model routing > cache-aware routing > quantisation > web tier.
**Speaker notes:** Roofline estimates, not benchmarks — measure your own in labs/22. The ranking of levers is the
takeaway.

## Slide 7 — SKETCH
- Edge → API gateway (auth, quotas, SSE) → chat orchestrator
- Orchestrator ↔ conversation store, context assembler, safety
- Model router (which model) ≠ inference gateway (which replica)
- vLLM pools per model and region; metering stream → quota/billing
**Visual:** the lesson's flowchart. Icons: `arch-api-gateway`, `arch-load-balancer`, `arch-servers-cluster`,
`arch-database`, `arch-event-stream`.
**Speaker notes:** Separate the business decision of choosing a model from the cache and load decision of choosing a
replica.

## Slide 8 — Streaming path
- SSE: `text/event-stream`, event `id`, `Last-Event-ID` on reconnect
- No buffering at any hop (NGINX `proxy_buffering` is on by default; `X-Accel-Buffering: no`)
- Keep-alive comment about every 15 s; idle timeouts between reads
- Cancellation must abort the vLLM request; idempotency key on send
**Visual:** sequence diagram client → gateway → orchestrator → vLLM with resumable event IDs. Icons: `pattern-push`,
`proxy-nginx`, `pattern-idempotency`.
**Speaker notes:** Most streaming bugs are a proxy that buffers. Test the whole path with a synthetic streaming probe.

## Slide 9 — Inside the vLLM fleet
- Continuous (iteration-level) batching — Orca; PagedAttention — 2–4× throughput (paper claim)
- Chunked prefill on by default in V1; `max_num_batched_tokens` trades ITL vs TTFT
- Automatic prefix caching on by default since V1; full blocks, hash chain, LRU
- Keep the system prompt byte-stable; append-only context
**Visual:** GPU timeline with decode steps and prefill chunks interleaved. Icons: `pattern-batching`, `arch-cache`.
**Speaker notes:** Putting today's date at the top of the system prompt destroys the shared prefix for every user.

## Slide 10 — KV-aware routing and disaggregation
- Round-robin throws the cache away; hash affinity creates hot replicas
- Endpoint picker scores prefix hit + load (Gateway API Inference Extension, llm-d)
- Disaggregated prefill/decode: DistServe, Splitwise; in vLLM experimental, controls latency, not throughput
**Visual:** three routing policies side by side. Icons: `arch-load-balancer`, `pattern-consistent-hashing`.
**Speaker notes:** Disaggregation is a tail-latency tool. Mention it, but do not lead with it.

## Slide 11 — Quotas in tokens
- Three limits: concurrent streams, tokens per minute, daily allowance
- Pre-debit estimate at admission, reconcile from final usage
- Under saturation shed free tier at the gateway, not by vLLM preemption
**Visual:** token bucket with a pre-debit and a refund arrow. Icons: `pattern-rate-limiter`, `security-token`.
**Speaker notes:** Requests are the wrong unit; one request can be 100 or 100,000 tokens.

## Slide 12 — STRESS
- KV exhaustion → preemption → latency spikes (watch `vllm:kv_cache_usage_perc`, waiting requests)
- Node loss mid-stream → resume via event ID, resubmit elsewhere
- Cold start: GPU node + image + 70–140 GB weights → warm pools, NVMe cache, sleep mode
- Residency: EU traffic never spills to other regions
**Visual:** failure table with SLI column. Icons: `ops-incident`, `pattern-autoscaling`, `arch-region`.
**Speaker notes:** Autoscale on queue depth and KV usage, never CPU. Drain before scaling in.

## Slide 13 — Operate: SLOs, cost, energy
- SLOs: TTFT p95 < 1 s, ITL p95 < 50 ms, interruption < 0.1 %, prefix hit ≥ 60 %
- Cost (assumptions): ≈ $0.0008 per conversation, ≈ $0.63 per M output tokens
- Energy (assumptions): ≈ 12 MWh/day, ≈ 0.4 Wh per conversation
**Visual:** three KPI tiles. Icons: `ops-cost`, `ops-slo`, `ops-dashboard`.
**Speaker notes:** Cache hit rate is a capacity SLO: when it slips, cost rises before users notice.

## Slide 14 — WRAP
- Junior: flow, SSE, data model, rate limiter
- Senior: token math, batching, prefix caching, KV-aware routing, token quotas, autoscaling signals
- Staff: unit economics, GPU supply, routing policy, residency, model rollout with evals
- Red flags: autoscale on CPU, count requests, ignore KV cache, buffer for safety
**Visual:** three-level ladder. Icons: `ops-check`.
**Speaker notes:** Close with the cost per conversation and the top three levers that move it.
