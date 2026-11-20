# 33 — Agent platform runtime: queues, tenancy, fairness, rollout (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- 2,000 tenants, 240,000 agent runs a day, from chat, API, schedules and events
- Interactive first step ≤ 2 s at p95, even while one tenant submits 20,000 runs at 09:00
- No lost runs, no duplicated side effects across crashes and deploys
- Hard cost caps per run and per tenant; daily releases with canary and rollback

**Visual:** many tenant icons feeding one platform box; icons `arch-users`, `ai-agent`, `arch-queue`, `ops-budget`.
**Speaker notes:** The scarce resource is not CPU but shared model capacity, metered in tokens per minute. Runs
differ in cost by 25 times and last minutes to days, and the code being run decides its own control flow.

## Slide 2 — A run is a job
- Record before worker: tenant, trigger, version tuple, priority, budget, deadline, lease
- Triggers differ: chat (person watching), API (run id now), schedule (once per period), event (ack in seconds)
- Default async: `202 Accepted` + run id, then stream, poll or webhook
- Webhooks: ack within GitHub's 10 s, dedup on the delivery id, process later

**Visual:** the run record as a card with fields highlighted by the requirement each serves; icons `pattern-webhook`,
`arch-cron`, `arch-event-stream`.
**Speaker notes:** Each field exists because a requirement needs it. GitHub does not auto-redeliver failed
deliveries, and a manual redelivery keeps the same `X-GitHub-Delivery` id, so that id is the natural dedup key.

## Slide 3 — The run state machine
- Submitted → Queued → Running → Succeeded, Failed or Cancelled
- Throttled: waiting for model tokens, visible on its own
- Waiting: approval, timer or callback, holding nothing
- Suspended on budget, TimedOut on wait deadline, every state has a timeout

**Visual:** the lesson's state diagram (11 states).
**Speaker notes:** Separate platform state from agent memory. Failed-platform, failed-agent and suspended-budget
count against different SLOs, so terminal states carry a reason.

## Slide 4 — The architecture
- Run API (admission, dedup) → run store and event log → fair run queue → stateless workers
- Step scheduler → LLM gateway with token limiter → providers or self-hosted pools
- Tool broker (idempotency, per-tool quotas), sandbox pool, run stream to clients
- Workers are I/O-bound: worker slots are not capacity

**Visual:** the lesson's architecture flowchart; icons `arch-api-gateway`, `arch-queue`, `arch-worker`,
`ai-llm-gateway`, `arch-sandbox`.
**Speaker notes:** The commonest sizing error is autoscaling workers on CPU while the real queue forms in the
gateway. Capacity is tokens per minute, sandboxes and tool quotas.

## Slide 5 — Durable execution limits
- Temporal: 2 MB payload, history 51,200 events or 50 MB (warn at 10,240 or 10 MB)
- 2,000 pending activities, children, signals by default; 500 APS default on Cloud
- Pass references, not transcripts (claim check); Continue-As-New at step boundaries
- History grows roughly with the square of steps if contexts are inlined

**Visual:** bar growing quadratically: 12-step run ≈ 0.66 MB vs 300-step runaway ≈ 276 MB against a 50 MB line; icons
`devops-temporal`, `arch-object-storage`.
**Speaker notes:** These are the documented limits as of 2026-11. The 276 MB figure is arithmetic from the lesson's
labelled assumptions (4 bytes per token, 1,500 new tokens per step).

## Slide 6 — Backpressure from provider to submitter
- Provider limits: RPM, ITPM, OTPM, ramp limits, monthly spend cap
- Gateway buckets below provider limits, reserve and refund
- Throttled steps → lower run concurrency → 429 + `Retry-After` + queue position to submitters
- Spend-cap 429 has no `retry-after`: an outage, not a rate limit (Scale tier cap: $200,000/month)

**Visual:** chain of four boxes with arrows labelled "no" turning into "not yet"; icons `pattern-backpressure`,
`arch-token-bucket`, `pattern-rate-limiter`.
**Speaker notes:** Anthropic counts cache reads outside ITPM and ignores `max_tokens` for OTPM, while OpenAI counts
the maximum of `max_tokens` and the estimate. Retry only where `retry-after` says when, at one layer.

## Slide 7 — The noisy neighbour
- 2,250 slots, 6-minute runs: 375 slots free per minute
- FIFO: a 20,000-run burst delays everyone ≈ 53 minutes
- Fair rotation among 60 tenants: next run waits ≈ 10 s
- Plus a 10% per-tenant cap and a reserved interactive share

**Visual:** two timelines, FIFO with one colour block of 20,000 then others, fair queue interleaving; label each
lane by tenant name as well as colour; icons `arch-queue`, `arch-users`.
**Speaker notes:** Nothing is refused, only reordered. Ten seconds is fine for standard runs but breaks the 2 s
interactive target, which therefore needs reserved capacity.

## Slide 8 — Fairness mechanisms and units
- Concurrency caps, token buckets, WFQ / deficit round robin, priority classes, shuffle sharding
- Fair-share runs at admission, weighted tokens at the step scheduler
- VTC (OSDI 2024): fairness counted in tokens, proven 2× tight bound
- Borrow from Kubernetes API Priority and Fairness and Temporal fairness keys

**Visual:** two-layer diagram: run-level DRR feeding a token-level DRR; icons `pattern-sharding`, `pattern-bulkhead`,
`ai-tokens`.
**Speaker notes:** A tenant with 300-step runs gets 25 times the tokens of a 12-step tenant at equal run share.
Temporal's fairness has documented limits: per partition, not guaranteed across version transitions.

## Slide 9 — Budgets against denial of wallet
- OWASP LLM10:2025 Unbounded Consumption names denial of wallet
- Budgets per call, run, tenant, trigger and platform, enforced by the runtime
- Reserve before each call, reconcile after; suspend at 100%
- Own limits below the provider's spend cap, per workspace

**Visual:** nested budget rings; icons `ops-budget`, `ops-cost`, `security-ddos`.
**Speaker notes:** The attacker may be an injected loop, a schedule, an event storm or an honest runaway fan-out.
Step budgets also protect the durable engine's history limit.

## Slide 10 — Exactly-once effects over long runs
- Key `{run_id}:{step_seq}:{call_index}`, never the attempt number
- Stripe v1: saved first response, parameters compared, keys may be pruned once ≥ 24 h old
- IETF draft-08: 409 in flight, 422 key reused with new payload, 400 missing key
- Replay never re-runs a recorded step; an unrecorded one retries within minutes
- The risk is a *late* retry of an unknown outcome (multi-day outage, parked step): journal + lookup, never a blind resend

**Visual:** timeline: refund sent, timeout, outcome unknown, 3-day outage with a 24 h key-expiry marker, late retry
intercepted by the broker journal and a lookup instead of reaching the payment API; icons `pattern-idempotency`,
`pattern-retry`.
**Speaker notes:** A 3-day approval wait alone is harmless: steps before it are recorded and steps after it get new
keys. Bound automatic retries of side effects below the downstream key retention, then move the step to unknown. The
downstream key is the second line of defence.

## Slide 11 — Sandboxes as a pool
- Warm pools of never-used sandboxes; `agent-sandbox` SandboxWarmPool / SandboxClaim
- Pool ≥ claim rate × refill time (1.4/s × 20 s ≈ 28, ≈ 56 for bursts)
- Firecracker boots in < 125 ms, but boot is not ready: measure claim-to-ready
- Release during waits; never recycle across tenants

**Visual:** pool tank with a refill pipe and claim tap; icons `arch-sandbox`, `arch-containers`, `devops-kubernetes`.
**Speaker notes:** The 20 s refill is an assumption. Firecracker's numbers are the project's own. AgentCore
terminates and sanitises the microVM after each session.

## Slide 12 — Rollout with runs in flight
- Pin the whole version tuple at run start
- Pin and drain (rainbow), auto-upgrade for urgent fixes, upgrade at Continue-As-New
- Canary by run then tenant cohort; shadow runs with tools in dry-run
- Rollback is a pointer move; pins expire (≥ 60 days' notice before model retirement)

**Visual:** the lesson's rollout flowchart: v40 draining, v41 current, v42 ramping 5%; icons `ops-deploy`,
`ai-model-registry`, `ai-prompt`.
**Speaker notes:** Kubernetes gives 30 s of grace before SIGKILL, far less than a 6-minute run, so durability is the
guarantee. Editing a tool definition invalidates the whole prompt cache: expect a cost spike on the canary.

## Slide 13 — Capacity in five lines
- 240,000/day → 4.67 runs/s → 1,680 concurrent (Little's law)
- 165,000 input tokens per run, 89% cache reads → ≈ $0.108 per run on Claude Sonnet 5.5
- Per run: 50 ITPM tokens/s, 13.3 OTPM tokens/s → OTPM caps ≈ 2,500 concurrent runs (Scale-tier limits)
- ≈ $25,800/day hits the Scale tier's $200,000 monthly spend cap in ≈ 7.8 days: this volume needs a Custom tier
- Cold cache cuts the ITPM ceiling to ≈ 364 runs: cache hit rate is capacity

**Visual:** funnel from runs/day to tokens/s to dollars; icons `ops-throughput`, `ai-tokens`, `ops-cost`.
**Speaker notes:** All assumptions are labelled in the lesson and are yours to replace. Prices and limits are as of
2026-11 and change often.

## Slide 14 — SLOs and the interview
- Platform SLOs separate from quality SLOs
- Worst-tenant p95 time-to-start is the fairness SLI
- Zero-target invariants: lost runs, duplicate effects, budget overruns
- CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP; red flag: sizing workers by CPU

**Visual:** SLO table excerpt and the six-step framework strip; icons `ops-slo`, `ops-dashboard`.
**Speaker notes:** A global p95 can look healthy while one tenant waits an hour. Wrap: a run is a job with a pin and
a budget, capacity is tokens, rollout is pin and drain.
