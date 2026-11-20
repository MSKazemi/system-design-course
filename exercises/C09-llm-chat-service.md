# C09 — Exercises

Lesson: [course/04-case-studies/C09-llm-chat-service.md](../course/04-case-studies/C09-llm-chat-service.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Users to tokens

A product has 2 M DAU, 4 requests per user per day, average input 2,500 tokens, output 300 tokens, peak-to-average 2.5×.
Compute peak requests/s, peak output tokens/s and peak raw input tokens/s.

<details><summary>Answer</summary>

Requests/day = 8 M → average 8 M / 86,400 ≈ 93 req/s → peak ≈ 230 req/s. Output ≈ 230 × 300 ≈ 69,000 tokens/s.
Raw input ≈ 230 × 2,500 ≈ 580,000 tokens/s. Input is ≈ 8× output, so prefill matters even before you consider
caching. Acceptable to round differently; what matters is that each step is shown and that input is not ignored.
</details>

## 2. [Core] KV bytes per token

A model has 32 layers, 8 KV heads, head dimension 128, and a BF16 KV cache. How much KV does a 2,000-token system prompt
use per sequence? How much with 64 concurrent sequences and no prefix sharing?

<details><summary>Answer</summary>

2 × 32 × 8 × 128 × 2 B = 131,072 B = 128 KiB/token. 2,000 tokens → 250 MiB per sequence. 64 sequences → ≈ 15.6 GiB of
identical KV. With prefix caching the shared prefix is stored once (≈ 250 MiB). The formula — 2 × layers × KV heads ×
head dim × bytes — is what the interviewer wants to see; grouped-query attention (fewer KV heads than query heads) is
why modern models need far less KV than the head count suggests.
</details>

## 3. [Deep] Decode roofline

Using the lesson's method, estimate per-replica decode throughput for an FP8 70B model on 2 × H100 (3.35 TB/s each),
with 48 sequences of 3,000 tokens and an FP8 KV cache (160 KiB/token), at 50 % achieved bandwidth. Does it meet a
50 ms TPOT SLO?

<details><summary>Answer</summary>

Weights ≈ 70 GB on 160 GB of HBM leaves ≈ 75 GB for KV after overheads (assumption). KV for the batch = 48 × 3,000 ×
160 KiB ≈ 23.6 GB — fits. Bytes per step ≈ 70 + 23.6 ≈ 93.6 GB; bandwidth 6.7 TB/s × 0.5 = 3.35 TB/s → ≈ 28 ms per step.
TPOT ≈ 28 ms meets 50 ms; replica output ≈ 48 / 0.028 ≈ 1,700 tokens/s (≈ 850 per GPU). Fewer GPUs per replica means
weights dominate each step, so per-GPU throughput is lower than the 4-GPU case; that is why tensor parallelism helps
decode even when the model fits. State that this is a roofline estimate, not a benchmark.
</details>

## 4. [Core] SSE through proxies

Users report that answers appear "all at once after 10 seconds" in production but stream fine locally. List three
likely causes and how to confirm each.

<details><summary>Answer</summary>

(1) A reverse proxy buffering the upstream response — NGINX's `proxy_buffering` is on by default; confirm by curling
each hop and timing events, fix with `proxy_buffering off` or `X-Accel-Buffering: no`. (2) Response compression at a
CDN or gateway holding bytes until a block fills — confirm by disabling compression for `text/event-stream`. (3) A
service-mesh sidecar or load balancer that does not stream HTTP/1.1 chunked/HTTP/2 data frames promptly — confirm with
a synthetic probe that measures inter-event gaps at the client. A strong answer adds a permanent synthetic streaming
probe as an SLI.
</details>

## 5. [Deep] Why cache-aware routing

Your fleet uses least-connections load balancing. Explain, with the lesson's numbers, what happens to the prefill load
and GPU count if you switch to prefix-score + load routing, and what new risk you introduce.

<details><summary>Answer</summary>

With least-connections, consecutive turns of a conversation land on random replicas, so almost nothing beyond the
system prompt is cached: prefill demand approaches the raw 12.6 M tokens/s (≈ 2,200 GPUs of prefill in the lesson's
model). With prefix-aware routing, the assumed 70 % hit rate cuts it to ≈ 3.8 M tokens/s (≈ 670 GPUs). The new risk
is **hot replicas**: affinity concentrates popular prefixes; mitigate by blending a load score, spilling to a
second-best replica, and alerting on per-replica queue depth. Also: the router's view of cache state is approximate and
can be wrong after evictions.
</details>

## 6. [Interview] Token quotas

Design the rate limits for a free tier (small model only) and an API tier (60,000 TPM per org). Include what happens
when output length is unknown at admission.

<details><summary>Answer</summary>

Free: 1 concurrent stream, a daily weighted-token allowance, small model only, shed first under load. API: concurrent
stream cap per org plus a token bucket refilled at 60,000 tokens/min. At admission debit input tokens (tokenizer count)
plus an estimate such as `min(max_output_tokens, p90 output)`; reconcile from the final usage event, refunding or
charging the difference. Reject with 429 and a `Retry-After`. Billing uses the durable usage log with idempotent event
IDs, not the fast counters. Alternative accepted: debit full `max_output_tokens` for strict tiers, at the cost of
rejecting more.
</details>

## 7. [Deep] Mid-stream failure

A GPU node fails while 120 streams are mid-answer. Walk through what the user sees and what the system does.

<details><summary>Answer</summary>

vLLM requests on that node die; the orchestrator's upstream connections error. For each, the orchestrator keeps the
partial text already sent (from the stream buffer), resubmits the request to another replica with the partial
assistant text appended as a prefix (or regenerates from scratch, policy decision), and continues emitting events with
increasing IDs; the client sees a pause. The other replica must recompute the prefill (no shared KV), so TTFT for those
120 requests is high; the inference gateway should spread them. If resubmission fails, mark the message `interrupted`
and offer regenerate. Count these in the stream-interruption SLI.
</details>

## 8. [Interview] Disaggregation: yes or no?

An interviewer asks whether you would use disaggregated prefill/decode from day one.

<details><summary>Answer</summary>

Default no. vLLM labels it experimental and states it does not improve throughput; its value is independent control
of TTFT and tail ITL. DistServe and Splitwise show large gains on their workloads, but it adds KV transfer (≈ 1.25 GiB
per 4,000-token 70B request in BF16) that needs a fast interconnect. Start with chunked prefill and tune
`max_num_batched_tokens`; adopt disaggregation when long prompts keep breaking the ITL SLO and measurements show the
gain. Saying "it depends, and here is the measurement that decides" is the senior answer.
</details>

## 9. [Core] Residency

An EU region is out of GPU capacity at peak. A colleague proposes spilling EU traffic to the US region. Respond.

<details><summary>Answer</summary>

Not if residency was promised for processing: GDPR Chapter V restricts transfers of personal data, and enterprise
contracts often require EU processing. Instead degrade inside the EU: route free traffic to the small model, shed free
traffic, use reserved headroom, or add capacity in a second EU region. Make the policy explicit in the router config
and test it. Non-resident users can spill freely.
</details>

## 10. [Lab] Prefix caching measured

Use [labs/22-serving-llms-at-scale](../labs/22-serving-llms-at-scale/). Send 50 requests sharing a 1,500-token system
prompt, first with prefix caching disabled (`--no-enable-prefix-caching`), then enabled. Record TTFT p50/p95 and the
prefix-cache hit rate from `vllm:prefix_cache_hits` / `vllm:prefix_cache_queries`. Then insert a timestamp at the start
of the system prompt and repeat.

<details><summary>Answer</summary>

Expect lower TTFT with caching on for every request after the first, and a high hit rate; decode speed (TPOT) should
not change, because prefix caching only shortens prefill. With a timestamp at the start of the prompt, every request
has a unique first block, so the hit rate collapses and TTFT returns to the uncached level. Report your own measured
numbers with the vLLM version and hardware; do not compare CPU and GPU results directly.
</details>

## 11. [Lab] Token rate limit at the gateway

Use [labs/26-llm-gateways-llmops](../labs/26-llm-gateways-llmops/). Configure a per-key TPM limit and send a burst of
requests with a large `max_tokens`. Observe whether the gateway debits estimated or actual tokens and when it returns
429.

<details><summary>Answer</summary>

Look for which number the gateway debits at admission (input only, input + `max_tokens`, or an estimate) and whether
it corrects after the response. If it debits only actual usage after completion, a burst of concurrent long requests
overshoots the limit — the pre-debit-and-reconcile design in the lesson exists to close that gap. Record the
gateway's version and configuration with the result.
</details>

## 12. [Interview] Cost sensitivity

Finance asks which single change would cut GPU cost most: FP8 KV cache, cache-aware routing, or routing 70 % of
traffic to the small model. Rank them with reasoning.

<details><summary>Answer</summary>

Using the lesson's model: (1) small-model routing — moves 70 % of tokens to a model roughly an order of magnitude
cheaper per token, cutting the fleet by more than half; (2) cache-aware routing — the difference between ≈ 3.8 M and
12.6 M prefill tokens/s, roughly halving an all-70B fleet; (3) FP8 KV — fits more sequences per replica and reduces
bytes per decode step, a meaningful but smaller gain. The ranking depends on quality constraints (can the small model
answer?) and on the measured hit rate; say so.
</details>
