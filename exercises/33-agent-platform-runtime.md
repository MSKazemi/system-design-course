# 33 — Exercises

Lesson: [SYSDESIGN-33 Agent platform runtime: queues, tenancy, fairness, rollout](../course/03-ai-systems/33-agent-platform-runtime.md)

### 1. [Core] Concurrency from runs per day

A platform runs 90,000 agent runs a day. 60% arrive in an 8-hour window, and a run is active for 4 minutes on
average (human waits excluded). How many runs are active at once in that window? Why is this number not the number of
worker machines you need?

<details><summary>Answer</summary>

λ = 0.6 × 90,000 / (8 × 3,600 s) = 54,000 / 28,800 ≈ **1.875 runs/s**. Little's law: L = λW = 1.875 × 240 s ≈ **450
active runs** in the window, more during bursts.

This is not a machine count, because agent runs are I/O-bound: they wait on model tokens and tool responses. One
async worker process can hold dozens or hundreds of runs. With 100 per process (an assumption to measure), that is
about 5 processes plus spares. The real limits are elsewhere: provider tokens per minute, sandboxes and tool quotas.
Size those from the 450 concurrent runs (tokens per second per run × 450), not workers from CPU.
</details>

### 2. [Core] Which limit binds?

Each active run consumes, in the provider's counting, 60 uncached input tokens/s (cache writes included) and 10
output tokens/s. Your tier allows 6,000,000 ITPM and 900,000 OTPM. What is the maximum number of concurrent runs, and
what admission limit would you set? What happens if the cache-hit rate collapses and each run then consumes 500
counted input tokens/s?

<details><summary>Answer</summary>

ITPM: 6,000,000 / 60 = 100,000 tokens/s ÷ 60 ≈ **1,667 runs**. OTPM: 900,000 / 60 = 15,000 tokens/s ÷ 10 = **1,500
runs**. OTPM binds first at about 1,500 runs. Set admission around 90% of that, about **1,350**, so that bursts and
estimation error do not hit provider 429s, and queue the rest fairly.

With a cold cache, ITPM allows 100,000 / 500 = **200 runs**, so the ceiling drops 7.5×. Cache-hit rate is a capacity
parameter, not just a price. The lesson's rules follow: schedule in-flight steps before new runs so caches stay warm,
keep the prompt prefix and tool definitions stable, and alert on the cache-read share. The adaptive concurrency limit
should also react, because throttled time rises immediately.
</details>

### 3. [Core] FIFO versus fair

Admission allows 1,200 concurrent runs; runs last 8 minutes on average. At 09:00 tenant A submits 12,000 runs. Tenant
B submits one run at 09:00:10. Estimate B's wait under (a) one FIFO queue, (b) deficit round robin over 40
backlogged tenants with equal weights, (c) (b) plus a per-tenant cap of 10% of slots.

<details><summary>Answer</summary>

Slots free at 1,200 / 8 = 150 per minute.

(a) FIFO: B is behind 12,000 runs, so it waits about 12,000 / 150 = **80 minutes**.

(b) DRR over 40 tenants: B waits about one rotation, 40 slot releases ≈ 40 / 150 min ≈ **16 s**.

(c) The cap limits A to 120 running runs, so A cannot grab every free slot at 09:00:00 before others arrive. B's wait
is still about one rotation, about 16 s or less, and every other tenant keeps headroom.

Note that 16 s breaks a 2 s interactive target. Interactive runs need a reserved share of slots and tokens, or their
own priority class with a starvation guard for the classes below.
</details>

### 4. [Deep] Runs or tokens?

Tenant X's runs take 12 steps and about 165,000 input tokens. Tenant Y's runs take 300 steps and tens of millions of
tokens. Both have equal weight. Explain what happens under run-level fairness only, and design the fix.

<details><summary>Answer</summary>

Run-level fairness gives X and Y equal numbers of worker slots. Each of Y's runs consumes far more model capacity per
minute of occupancy as its context grows, so Y takes most of the provider's tokens per minute. X's steps then queue in
the gateway: its runs hold slots but are `Throttled`. Equal runs do not mean equal service, which is Sheng et al.'s
argument for counting tokens (OSDI 2024).

Fix: two-level scheduling. Keep run-level DRR (and caps) for worker slots and sandboxes. Add a step scheduler per
provider and model class that runs DRR with deficits in **weighted tokens**, counted the way the provider counts
(uncached input plus cache writes plus weighted output under Anthropic's rules). Reset an idle tenant's deficit so
credit cannot be banked overnight. Charge reconciled cost after completion. Acceptable alternative: fair-share in
dollars, which also weights by model price.
</details>

### 5. [Core] The 429 taxonomy

Your gateway receives three kinds of 429 from a provider: one with `retry-after: 7`, one with error code
`ramp_limit_exceeded`, and one with `enforced_spend_limit_reached` and no `retry-after`. What should the platform do in
each case?

<details><summary>Answer</summary>

- **Rate limit with `retry-after`:** wait at least 7 s with jitter, retry at one layer only (the gateway), shrink the
  local token bucket so subsequent calls queue locally, and mark affected runs `Throttled`.
- **Ramp limit:** usage grew too fast. Anthropic advises waiting at least `retry-after`, holding traffic at a level
  that succeeds, then increasing by at most one step per minute. Lower the run admission limit, ramp it back up
  slowly, and spread scheduled bulk jobs (jitter).
- **Spend cap:** not retryable until the next month (00:00 UTC on the first) or a higher limit. Every tenant behind
  that organization is down. Stop sending, fail over to another provider or model class if policy allows, page a
  human, and fix the root cause: projected monthly spend must fit the tier's cap (Scale: $200,000 as of 2026-11, so
  the lesson's ≈ $25,800/day platform needs a Custom-tier agreement), and the platform's own per-workspace limits
  should sit below the cap, with alerts well before it (for example at 70/85/95% of spend, a suggestion of this
  course, not a provider feature).

A related case without a 429: when a spend limit *you* set is reached, Anthropic returns HTTP 400
`invalid_request_error`. Treat it like the tier cap (non-retryable, page), not like a malformed request.
</details>

### 6. [Deep] The late retry

A run reaches step 9, records the intent to call `issue_refund(order=123, amount=40)` with key `r-77:9:0`, and sends
the call. The payment API's gateway times out, so the outcome is unknown. Then the payment API returns 503 for three
days, and the activity keeps retrying under a retry policy with unlimited attempts. The payment API may prune
idempotency keys once they are 24 hours old. (a) What happens when it recovers? (b) A colleague says "the same thing
happens to every run that waits 3 days for a manager's approval". Is that right? (c) How do you prevent the duplicate?

<details><summary>Answer</summary>

(a) If the first call did reach the payment system, the refund happened and the key was stored. Three days later the
retry carries the same key, but the key may have been pruned, so the API treats the call as new: **a second refund**.
(Stripe's v1 API, for example, may remove keys once they are at least 24 hours old and says a reused key after pruning
creates a new request.)

(b) No. A durable engine replays workflow code against history and does not call again a step whose result is
recorded. A step whose result was lost is retried after its activity timeout, minutes later, inside the key window.
A run that waits 3 days for approval has recorded every step before the wait, and the steps after it are new calls
with new keys. The risk is specific to a *retry of an unknown outcome* that happens later than the downstream key
retention: a long outage under an unbounded retry policy, or a step parked as `unknown` and resumed days later.

(c) The tool broker keeps its own intent/result journal for longer than the longest run, and any retry later than
the downstream retention goes through it and a **lookup** ("is there a refund with external reference r-77:9:0?")
instead of a blind resend. Bound automatic retries of side-effecting activities with a deadline below the retention
(in Temporal, a Schedule-To-Close timeout), then move the step to `unknown` for the reconciler or a human. The
downstream idempotency key is the second line of defence. Never include the attempt number in the key, or every retry
is a new operation.
</details>

### 7. [Core] History limits

An agent workflow passes the full context into each model activity. The context starts at 6,000 tokens and grows by
2,000 tokens per step. Assume 4 bytes per token. At which step does a single activity input exceed a 2 MB payload
limit, and roughly when does cumulative history pass 50 MB? What do you change?

<details><summary>Answer</summary>

Input at step k ≈ 6,000 + 2,000k tokens. The payload limit is 2 MB / 4 B = 500,000 tokens, reached when 2,000k ≈
494,000, so around **step 247**.

Cumulative tokens through step n ≈ 6,000n + 1,000n(n+1). The history limit is 50 MB / 4 B = 12.5 M tokens. At n = 108:
648,000 + 1,000 × 108 × 109 ≈ 12.4 M. At n = 109: about 12.6 M. So history passes 50 MB at about **step 109**, long
before any single payload is too big. (The warning at 10 MB comes much earlier, at about step 47.)

Change: pass references (claim check). Store transcripts and tool outputs in object storage and put keys and hashes in
history. Continue-As-New at step boundaries, or when the engine suggests it, carrying only task state. Enforce a step
budget, because runaways are what reach these limits.
</details>

### 8. [Interview] Deploy with 8,000 runs in flight

You must ship a new prompt and one changed tool schema at 14:00 while 8,000 runs are in flight, some of them waiting
on approvals for days. Walk through the rollout and the rollback.

<details><summary>Answer</summary>

1. **Pin:** every run already carries its version tuple (agent code, prompt, tool catalogue, model snapshot, policy).
   In-flight runs stay on v41, which keeps its workers until it is *drained* (rainbow deployment, or Temporal Pinned
   behaviour with a Draining version).
2. **Tool change:** make it additive (new optional field or a new tool version). Keep serving the old shape for v41
   runs. Expect a cost spike, because changing tool definitions invalidates the prompt cache.
3. **Canary:** ramp v42 to 1–5% of *new* runs (by run id), internal tenants first, then a percentage, then plans.
   Compare success rate, cost per successful run, steps, escalations and tool errors over enough runs. Shadow runs, if
   used, run tools in record or dry-run mode only.
4. **Promote or roll back:** rollback is setting the ramp to 0% or pointing "current" back to v41. New runs go to v41
   at once. Runs already pinned to v42 follow a pre-decided policy: finish, suspend or cancel and notify.
5. **Runs waiting for days** stay pinned. If v41 depends on a model with a retirement date, migrate them at a
   checkpoint before that date.
6. **Never delete v41 workers until it is Drained**, or pinned runs are stranded.

Red flags: replacing all workers and hoping the 30 s termination grace period is enough, or upgrading runs mid-flight
without replay compatibility.
</details>

### 9. [Deep] Schedule and event storms

All 2,000 tenants schedule a "weekly report" agent at Monday 07:00 local time, most in one time zone. Separately, a
ticketing integration fires 15 webhooks per ticket during a busy update, and the agent's own ticket updates emit
webhooks too. Identify the failure modes and the controls.

<details><summary>Answer</summary>

**Schedules:** about 2,000 runs start in the same minute, a burst into the provider's ramp limit, which advises
starting scheduled or bulk jobs at a low rate. Controls: jitter (Temporal Schedules support a random offset up to a
maximum jitter) or a tenant-hash offset over, say, 30 minutes; a background priority class with a reserved but bounded
share; an overlap policy (`Skip` by default in Temporal) so a slow previous run does not stack; and a deliberate
catch-up window, because the default is one year and a paused schedule could otherwise fire every missed run.

**Webhooks:** 15 events per ticket should not mean 15 runs. Debounce on `(tenant, trigger, ticket_id)` and have the
run read the current ticket state. Dedup on the delivery id. The agent's own updates create a **feedback loop**:
propagate a causation id through the tool broker and refuse to trigger on effects the same agent caused on the same
entity within a window, and cap hop counts. Per-trigger budgets (runs per hour, dollars per day) are the backstop.
</details>

### 10. [Core] Warm pool sizing

30% of 5 runs/s need a sandbox. Refilling one warm sandbox (create, boot, warm dependencies) takes 25 s, measured.
Bursts reach 2× for several minutes. How many warm sandboxes do you keep, and which rules govern their reuse?

<details><summary>Answer</summary>

Claim rate = 0.3 × 5 = 1.5/s. To absorb arrivals while refilling, pool ≥ 1.5 × 25 ≈ **38**, about **75** for 2×
bursts, plus margin for losing a host. Monitor claim-to-ready p95: if it jumps to cold-start time, the pool ran dry.

Rules: the pool holds only never-used sandboxes. After a run, a sandbox is destroyed, never returned (no cross-tenant
reuse). Waiting runs snapshot and release their sandbox. Each tenant has a sandbox cap, and a run that needs a sandbox
is admitted to `Running` only when it holds one. Firecracker's < 125 ms boot is the VMM's figure, so plan with
measured claim-to-ready time, not boot time.
</details>

### 11. [Interview] SLOs for the platform

Propose four SLIs for the agent platform, at least one of which measures fairness and one of which has a target of
zero. Explain why platform SLOs are separated from agent quality SLOs.

<details><summary>Answer</summary>

Examples: interactive time to first step (p95 ≤ 2 s); standard time to start measured **per tenant**, alerting on the
worst tenant within quota (fairness SLI; a global p95 hides one tenant waiting an hour); throttled share of running
time (capacity health); **lost runs = 0** (runs past deadline with no terminal state, found by a sweeper);
**duplicate effects = 0** (broker journal audit); budget overruns beyond one step's reservation = 0; trigger latency
p99.

Separation: a model or prompt regression lowers task success without any platform fault, and a lost run is a platform
bug no prompt can fix. Mixing them makes the platform team burn error budget on quality changes and hides runtime
defects behind model noise. Quality SLOs (task success, pass^k, escalations) belong to evaluation (SYSDESIGN-32).
Zero-target SLIs are invariants with detectors, not error budgets.
</details>

### 12. [Lab] Planned simulation

Lab L33 is planned, not built. Using its plan, predict qualitatively what the simulation should show for (a) FIFO vs
DRR during the 20,000-run burst, and (b) "new runs first" vs "in-flight first" with a 5-minute cache TTL under load.
State how you would decide whether the simulation confirms or refutes your prediction.

<details><summary>Answer</summary>

(a) Under FIFO, the worst-tenant p95 time-to-start should approach the burst's drain time (tens of minutes in the
lesson's arithmetic) while the burst tenant's own wait is unchanged. Under DRR, other tenants' waits should drop to
about one rotation of slot releases, and total throughput should be the same (work-conserving).

(b) Under load, "new runs first" should leave in-flight runs throttled past the TTL, so more steps pay full cache
writes. Cost per run and counted input tokens per run rise, which lowers the token-limited concurrency further, a
feedback loop. "In-flight first" should keep cache-read share high and cost per run lower.

Deciding: fix seeds, run several replications, and compare per-tenant percentiles and cost per run with confidence
intervals, not single runs. A prediction is refuted if the intervals overlap or point the other way. Record parameters
and results in the lab's Test status. Until the lab is built, these are predictions, not results.
</details>
