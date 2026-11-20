# 26 — Exercises

Lesson: [SYSDESIGN-26 LLM gateways & LLMOps](../course/03-ai-systems/26-llm-gateways-llmops.md)

### 1. [Core] Concurrent streams

1,000 requests/s, average stream duration 12 s. How many concurrent connections must the gateway hold? What design
consequence follows?

<details><summary>Answer</summary>

Little's law: L = λW = 1,000 × 12 = **12,000 concurrent streams** (more at the tail). Consequences: an event-driven
(non-thread-per-connection) proxy; raised file-descriptor and connection limits on gateway and LB; idle timeouts
longer than the longest silent gap before the first token; and graceful draining on deploys, since 12-second
streams must finish or be resumable when a replica is replaced.
</details>

### 2. [Core] Why tokens, not requests?

Why is RPM-only rate limiting inadequate for LLM APIs? Design a token-based limiter for a team quota of 2M TPM.

<details><summary>Answer</summary>

Request cost varies by >1,000× (50 vs 100,000 tokens), so RPM neither protects capacity nor allocates cost fairly.

Design: a token bucket per (team, model) with a 2M/min refill. At admission, count input tokens and **reserve
input + max_tokens**. Reject with 429 and `Retry-After` if insufficient. On completion, cancel or error, **refund
the unused reservation**. Counters live in Redis (atomic scripts) or use local leases to avoid a round trip per
request. Clamp `max_tokens` per route to avoid over-reservation. Separate buckets for batch vs interactive. Decide
fail-open vs fail-closed when Redis is down. Lab L26 shows the *post-hoc* variant: 304 tokens passed a 200-TPM
limit before the 429, because accounting happened after completion.
</details>

### 3. [Deep] Fallback pitfalls

Your fallback chain is `frontier-model → mid-model → self-hosted-8B`. List four ways the fallback can harm users
even when it "works".

<details><summary>Answer</summary>

1. **Tool-calling incompatibility:** the fallback cannot emit the tool-call format agents depend on, so agent
   tasks fail or misbehave.
2. **Context window:** a long request cannot fit the fallback's window. Route by required context, or fail clearly.
3. **Quality and safety drift:** different refusal behaviour or lower accuracy on that route. It needs its own eval
   gate.
4. **Policy:** a content-policy refusal "fixed" by a more permissive model may violate your own policy.
Also: hidden cost or latency changes, and logs that record only `model_requested`, which makes incidents
undiagnosable. Log `model_served`, and alert on fallback rate.
</details>

### 4. [Core] Semantic cache risk

A semantic cache has a 25% hit rate and 96% precision. What share of all responses is wrong-from-cache? For which
Lumen routes would you enable it?

<details><summary>Answer</summary>

0.25 × 0.04 = **1%** of all responses are confidently wrong cached answers. Enable it only for non-personalised,
low-stakes, templated routes (public FAQ: opening hours, supported file types), partitioned by tenant, keyed with
document versions, short TTL, and never for tool-calling turns, account-specific, medical, legal or financial
answers. Audit a sample of hits continuously. Prefer exact caching and prefix caching elsewhere.
</details>

### 5. [Core] LLM-as-judge

Name three documented biases of LLM judges and a control for each. How do you decide whether to trust a judge for
your task?

<details><summary>Answer</summary>

From Zheng et al. (2023):
- **Position bias:** evaluate both orders and keep only consistent verdicts, or average.
- **Verbosity bias:** control for length (compare similar lengths, or penalise padding) and check correlation of
  score with length.
- **Self-enhancement bias:** use a judge from a different model family than the candidates.
Also limited maths and reasoning ability: give reference answers.

Trust: build a human-labelled calibration set *for your task* and measure judge-human agreement (and human-human
agreement as the ceiling). Re-check after any judge-model change. The paper's >80% agreement on MT-bench does not
transfer automatically.
</details>

### 6. [Deep] Streaming through proxies

Users report that streamed answers appear all at once after ~15 s, but gateway metrics show TTFT ≈ 400 ms. Diagnose.

<details><summary>Answer</summary>

Something between the gateway and the client is **buffering** the SSE response: a CDN, an ingress controller or an
nginx with `proxy_buffering on`, or compression middleware that waits for a full buffer. Confirm with curl at each
hop (`curl -N` directly to the gateway, then via the LB, then via the CDN) and compare first-byte times. Fix: disable
buffering and compression for streaming routes (`proxy_buffering off` or `X-Accel-Buffering: no`), set appropriate
idle timeouts, and add a synthetic probe that measures client-side TTFT through the full path. Also check that
client disconnects propagate cancellation upstream.
</details>

### 7. [Interview] Silent model regression

A provider updated a model behind an alias. Thumbs-down rate doubled overnight. Walk through detection, mitigation
and prevention.

<details><summary>Answer</summary>

Detection: dashboards segmented by version tuple (model snapshot, prompt version, config). Canary prompts with known
answers every few minutes. Judge-score and refusal-rate drift on sampled traffic. Output-length shift.

Mitigation first: flip the alias to the previous pinned snapshot (or another provider that passed the evals) via
gateway weights. That is a config change with no deploys. Confirm recovery on the same metrics.

Root cause: re-run the offline suite against both versions on the failing slice and diff behaviours.

Prevention: pin dated model versions, and treat "latest" as an unpinned dependency. Every change, including
upstream ones, goes through offline eval → canary → ramp. Add the failing cases to the golden set. Keep canary
prompts permanent.
</details>

### 8. [Core] What belongs in the gateway?

Classify: provider API keys, RAG retrieval, per-team TPM quotas, JSON-schema validation of a product's output,
prompt template for the support bot, PII redaction before logging.

<details><summary>Answer</summary>

Gateway: provider keys, per-team quotas, PII redaction before logging (a cross-cutting policy), and optionally
generic schema validation as a hook.

Application: RAG retrieval and the support-bot prompt template (product logic, owned by the team). The product's
output-schema validation is owned by the app that defines the schema, though the gateway can host a generic
validator hook.

Reasoning: the gateway holds cross-cutting, per-request policy. Product logic in the gateway couples every team's
release to the platform team.
</details>

### 9. [Deep] Cost attribution with self-hosted models

Team A uses a hosted API, team B uses your vLLM pool (8 GPUs at an assumed $2.50/GPU-hour, 60% average utilisation,
measured 2,500 output tokens/s per GPU at that utilisation). Propose a per-token transfer price for B.

<details><summary>Answer</summary>

Pool cost/hour = 8 × $2.50 = $20. Tokens/hour = 8 × 2,500 × 3,600 = 72M output tokens (at the measured average
throughput, which already reflects 60% utilisation). Price ≈ $20 / 72M = **$0.28 per million output tokens**, plus
an input-token component if prefill load is significant (measure prefill throughput separately, or split cost by
GPU-time per phase). Include overheads (idle headroom, ops, networking) as an explicit uplift. Publish the formula,
record it in the gateway as `input_cost_per_token` / `output_cost_per_token` for that deployment, and recompute
monthly from measured utilisation. All numbers here are assumptions, so measure yours.
</details>

### 10. [Lab] Failure detection latency

In L26, the first request after stopping a replica took tens of seconds in one run. Explain why this matters at
2,000 req/s and how you would reduce it.

<details><summary>Answer</summary>

At 2,000 req/s, if every request that hits the dead deployment waits for retries and backoff (seconds) before the
deployment is cooled down, hundreds or thousands of in-flight requests see a latency spike, and client timeouts can
trigger their own retries (a retry storm). Reduce it with short **connect** timeouts (distinct from long read or
stream timeouts), active health checks that remove a replica before user traffic hits it, a cooldown after the first
connection error, outlier detection in the load balancer, and retry budgets. Then measure the result: L26
experiment 2 asks you to compare first-request latency with and without a per-deployment timeout.
</details>
