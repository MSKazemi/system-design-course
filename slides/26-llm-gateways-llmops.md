# 26 — LLM gateways & LLMOps (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- 40 teams, 4 providers + self-hosted vLLM, 2,000 req/s
- Per-team token quotas and cost attribution
- ≤ 10 ms added latency; automatic fallback
- Every model or prompt change gated by evals

**Visual:** many services → one gateway → many backends; icons `arch-api-gateway`, `domain-ai`, `ops-cost`.
**Speaker notes:** Ordinary API-gateway assumptions break: cost is unknown until the end, responses stream, and
correctness is statistical.

## Slide 2 — The gateway pattern
- One OpenAI-compatible API, model aliases
- Virtual keys per team; provider keys stay inside
- Quotas, routing, retries, fallbacks, caching, guardrails
- Telemetry: tokens, TTFT, cost, model served

**Visual:** gateway flowchart from the lesson.
**Speaker notes:** Keep product logic (RAG, agents, prompts) out of the gateway, or it becomes a distributed
monolith.

## Slide 3 — Routing
- Shuffle, least-busy, latency, usage-aware, cost-based
- Learned routing: RouteLLM; cascades: FrugalGPT
- Self-hosted pools: KV-cache and queue-aware endpoint picking
- Two-tier gateways (tier one global, tier two inference pool)

**Visual:** alias → deployments fan-out; icon `arch-load-balancer`.
**Speaker notes:** Gateway API Inference Extension's InferencePool is v1 and GA. The endpoint picker uses
model-server signals.

## Slide 4 — Retries, fallbacks, cooldowns
- Retry the same group (bounded, jittered)
- Then fall back to another group in order
- Cooldown = per-deployment circuit breaker
- Retry budgets prevent storms

**Visual:** state diagram: healthy → failing → cooled down → healthy; icons `pattern-retry`, `pattern-circuit-breaker`.
**Speaker notes:** In L26 a dead replica cost one request 64 s in one run before cooldown kicked in. Measure
failure-detection latency.

## Slide 5 — Fallbacks change behaviour
- Tool-calling formats differ
- Context windows differ
- Content policies differ
- Log model_requested and model_served

**Visual:** two model cards side by side with mismatched capabilities.
**Speaker notes:** A fallback that has not passed the route's evals is an untested deploy.

## Slide 6 — Token-based rate limits
- Requests vary 1,000× in cost, so limit TPM, not just RPM
- Reserve input + max_tokens, refund on completion
- Shared counters (Redis) or local leases
- Fail open or closed: decide per tier

**Visual:** token bucket with a reservation and a refund arrow; icon `pattern-rate-limiter`.
**Speaker notes:** L26: four requests of 76 tokens passed a 200-TPM limit before the 429. That is post-hoc
accounting overshoot.

## Slide 7 — Streaming through proxies
- Buffering turns streams into blobs
- Idle timeouts kill long generations
- Propagate client cancellation upstream
- Usage arrives at the end of the stream

**Visual:** proxy chain CDN → LB → gateway → model with a "buffer" trap; icon `proxy-nginx`.
**Speaker notes:** Test TTFT through every hop, not just against the gateway. L26 measured 187 ms TTFT vs 1.6 s
total.

## Slide 8 — Caching
- Exact cache: safe, low hit rate for chat
- Prefix caching: reuse KV, fresh answer, almost always safe
- Semantic cache: closest previous prompt's answer
- Error = hit rate × (1 − precision)

**Visual:** example: 20% hits × 5% wrong = 1% wrong answers; icon `arch-cache`.
**Speaker notes:** Partition by tenant, version the key, and never cache personalised or tool-calling turns.

## Slide 9 — Versioning and evals
- Version tuple: model snapshot + prompt + tools + params + retrieval
- Offline golden set → canary → A/B → ramp
- Rollback = flip the alias
- Sample traffic into new eval cases

**Visual:** LLMOps loop diagram from the lesson; icons `ops-ci-cd`, `ops-deploy`.
**Speaker notes:** "Harmless" prompt edits go through the same pipeline as model changes.

## Slide 10 — LLM-as-judge caveats
- >80% agreement with humans on MT-bench (Zheng et al.)
- Position, verbosity, self-enhancement biases
- Weak on maths and reasoning without references
- Calibrate on your own labelled sample

**Visual:** judge icon comparing A/B, then swapped order.
**Speaker notes:** Agreement on a public benchmark does not transfer automatically to your domain.

## Slide 11 — Monitoring
- TTFT, time per token, tokens/s, errors by class
- Fallback rate, cache hit rate, model_served ≠ requested
- Cost per team and per successful task
- OTel GenAI conventions: Development status, dedicated repo (2026)

**Visual:** dashboard mock with the signal table; icons `observability-opentelemetry`, `ops-dashboard`.
**Speaker notes:** Pin the semconv version you emit. Prompt and completion content is opt-in and is personal data.

## Slide 12 — Regression incident runbook
- Detect: canary prompts, judge drift, thumbs-down
- Triage: diff the version tuple
- Mitigate: flip alias / pin snapshot
- Learn: add failing cases to the golden set

**Visual:** five-step runbook strip; icon `ops-incident`.
**Speaker notes:** The gateway makes rollback a config change. That is its strongest operational argument.

## Slide 13 — Interview angle
- CLARIFY teams, providers, streaming share, compliance
- QUANTIFY Little's law streams, tokens/s, counter ops, log volume
- DEEPEN token limiter *or* streaming *or* eval loop
- Red flags: RPM-only, keys in apps, shared semantic cache

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Also mention supply chain: the gateway holds every key, and pinned digests matter (LiteLLM's
March 2026 advisory).
