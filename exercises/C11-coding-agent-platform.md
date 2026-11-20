# C11 — Exercises

Lesson: [course/04-case-studies/C11-coding-agent-platform.md](../course/04-case-studies/C11-coding-agent-platform.md).
Numbers are assumptions unless the lesson gives a source.

## 1. [Core] Concurrency

50,000 tasks/day, peak factor 4, mean duration 30 min. How many concurrent sandboxes at peak? With 2 vCPU each and
64-vCPU hosts, how many hosts?

<details><summary>Answer</summary>

Peak arrival = 50,000 / 86,400 × 4 ≈ 2.3 tasks/s. Little's law: 2.3 × 1,800 s ≈ 4,200 concurrent sandboxes →
8,400 vCPU → ≈ 130 hosts without overcommit, plus headroom for failures and a warm pool. Paused tasks should not hold
sandboxes (snapshot and release), which lowers the real number.
</details>

## 2. [Core] Quadratic context

Context starts at 8 k tokens and grows by 2 k per step. Compare total input tokens for 30 and 60 steps.

<details><summary>Answer</summary>

Total = Σ (8 k + 2 k·i) for i = 0…n−1 = 8 k·n + 2 k·n(n−1)/2. n = 30: 240 k + 870 k ≈ 1.11 M. n = 60: 480 k + 3.54 M ≈
4.02 M — 3.6× for 2× the steps. Compaction (summarising old tool output) changes the growth from quadratic toward
linear; prompt caching lowers the price of the repeated prefix but not its size.
</details>

## 3. [Deep] Isolation choice

A customer asks why you don't simply run agents in Docker containers. Answer with trade-offs.

<details><summary>Answer</summary>

Containers share the host kernel; agent code is untrusted (prompt-injected, malicious install scripts), and a kernel
vulnerability would expose other tenants. gVisor puts a user-space kernel between the sandbox and the host, at the
cost of syscall overhead and compatibility limits — notable for builds and tests. Firecracker microVMs give each
sandbox its own guest kernel with small overhead (the NSDI 2020 paper reports < 5 MB memory overhead and < 125 ms boot
with its minimal configuration, so it does not transfer to a 4 GiB build sandbox). No layer removes host hardening:
Firecracker cannot mitigate host hardware vulnerabilities and recommends the jailer, seccomp and SMT off for tenant
separation, and gVisor does not in general protect against hardware side channels. For single-tenant, trusted
workloads containers with seccomp may be acceptable.
</details>

## 4. [Deep] Secrets

An integration test needs a payment-sandbox API key. Design how the agent can run it without the key reaching the
model or persisting in the sandbox.

<details><summary>Answer</summary>

Prefer credential injection at the egress proxy (the test calls the API through the proxy, which adds the key based
on the sandbox's workload identity). If the key must be local, mount it as a file only for that command, gated by an
org approval policy; scrub the key from stdout/stderr before the output is added to the model context; scan diffs and
PR text for secret patterns; revoke or rotate short-lived keys after the task. Never place it in environment variables
visible to every process, and never in the prompt. Remember that proxy injection hides the key, not its authority: a
hijacked agent can still make the proxy call the payment sandbox, so scope the injected key to that one API and
operation, bind it to the sandbox identity and task lifetime, and log every use.
</details>

## 5. [Interview] Approvals

Which of these need human approval by default, and why: (a) run unit tests, (b) push to the task branch, (c) add a new
npm dependency, (d) run a database migration against staging, (e) open network access to a new domain?

<details><summary>Answer</summary>

(a) No — local and disposable. (b) No, but logged, if the branch is in a private repository that only the requester
(or their org) can read. On a public
repository a push is a publication that anyone can read, so it needs approval once the task has read untrusted
content: you can delete the branch, but not un-disclose it. (c) Yes — supply-chain risk.
(d) Yes, by an authorised role — external, possibly irreversible. (e) Yes — the main exfiltration channel. Approvals are
bound to the exact command/diff hash so the agent cannot swap the action after approval.
</details>

## 6. [Deep] Replay safety

The workflow worker crashes after the agent posted an issue comment but before the result was recorded. What happens
on replay, and how do you avoid a duplicate comment?

<details><summary>Answer</summary>

On replay the workflow reaches the same step and re-issues the tool call. With an idempotency key (`task_id:seq`)
recorded as intent before execution, the tool broker sees the key, finds the earlier call's outcome (or checks the
tracker for a comment tagged with the key) and returns it instead of posting again. LLM outputs are recorded and never
regenerated during replay, so the agent's decisions stay the same.
</details>

## 7. [Interview] Loop detection

Describe three cheap loop detectors and what the platform does when one fires.

<details><summary>Answer</summary>

(1) The same tool with the same argument hash n times in a window; (2) the repository tree hash returning to an earlier
state (edit/revert cycles); (3) unchanged test results over k edit-test cycles. Response: inject a reflection prompt,
then ask the user, then stop with a summary and partial branch. Tune thresholds on evaluation runs so detectors do not
kill legitimate retries.
</details>

## 8. [Deep] Fairness

One org submits 3,000 background tasks at 09:00. Design the scheduler so other orgs' interactive tasks keep their
step-latency SLO.

<details><summary>Answer</summary>

Per-org concurrent-task caps (excess tasks queue with visible position, no sandbox started); per-org token-rate quotas
at the gateway; weighted fair queueing across orgs for LLM calls; two priority classes with interactive ahead of
background; background work backfills off-peak capacity. Measure queue age per org and per class.
</details>

## 9. [Lab] Sandbox timeouts, budgets and an MCP tool

Use [labs/25-agentic-systems](../labs/25-agentic-systems/). Give the agent a tool that sleeps forever and a task that
loops on a failing command. Configure a per-tool timeout, a token budget and a repeated-call detector, and connect one
tool through the lab's MCP server.

<details><summary>Answer</summary>

Expect the hung tool to be killed at the timeout and reported to the model as an error, the loop to trigger the
repeated-call detector before the budget is exhausted, and the budget to stop the run within one step of the cap if
the detector is disabled. Check that the MCP tool call appears in the trace with its arguments redacted. Record your
own observations and lab versions.
</details>

## 10. [Lab] Per-tenant token limits

Use [labs/26-llm-gateways-llmops](../labs/26-llm-gateways-llmops/). Create two virtual keys (two "orgs") with different
tokens-per-minute limits and drive both with concurrent agent-like loops.

<details><summary>Answer</summary>

The org with the lower limit should receive 429s (or queueing, depending on the gateway) while the other continues
unaffected. If the gateway only counts tokens after a response, concurrent long requests can overshoot the limit —
observe this and relate it to the reserve-then-reconcile design in the lesson. Report measured values with versions.
</details>

## 11. [Deep] Price a task, a cache expiry and a paused sandbox

Use the lesson's assumptions: 1.6 M input tokens per task with an 85 % cache hit, 20 k output tokens, $3 / $0.30 /
$15 per million (input / cached input / output), a 2 vCPU sandbox for 20 min at $0.05 per vCPU-hour, and $0.02 for
storage and orchestration. (a) Re-derive the cost per task. (b) Add a 1.25× cache-write premium on the uncached
tokens. (c) A 20-minute approval late in the task expires the 5-minute cache, and the next call re-writes an 80 k-token
prefix. What does that cost? (d) A colleague says "snapshotting a paused sandbox saves $0.48 per 2-hour pause: $0.20
of compute plus the $0.28 cache re-write". Is that right?

<details><summary>Answer</summary>

(a) Uncached 240 k × $3/M = $0.72; cached 1.36 M × $0.30/M = $0.41; output 20 k × $15/M = $0.30; sandbox
2 × 1/3 h × $0.05 = $0.03; other $0.02. Total ≈ **$1.48**, which the lesson rounds to $1.50. Tokens are over 95 %.
(b) The 240 k uncached tokens now cost 240 k × $3.75/M = $0.90, so the task is ≈ **$1.66** (+$0.18, about +12 %).
(c) 80 k × $3.75/M = $0.30 instead of a cached read of 80 k × $0.30/M = $0.024: **≈ $0.28 extra**, about a fifth
(19 %) of a mean task. (d) No. Holding costs 2 vCPU × $0.05 = $0.10 per hour, so $0.20 for 2 hours, and that part
is saved. The cache re-write is paid in both options, because the prompt cache expires whether or not the sandbox is
kept, so the saving is $0.20 per pause, ≈ $8,000/day at 40 k pauses, or about 70 hosts' worth of vCPU. Against that,
snapshots add ≈ 2.3 GiB/s of writes (and as much in restores) and a restore delay on the first step after approval.
A 2-minute hold costs only 2 vCPU × 2/60 h × $0.05 ≈ $0.003, which is why quick approvals should skip the snapshot.
Acceptable alternative for (c): if long waits are routine, pay the longer TTL (Anthropic: 2× write for 1 hour) and
compare the extra write premium on every task with the re-writes you avoid.
</details>

## 12. [Interview] Engine limits and the release gate

(a) The team stores the full context in every LLM activity's input (assume 4 bytes per token). Using Temporal's limits
(2 MB per payload, 50 MB or 51,200 events per history), will a normal 40-step task fit? The 400-step runaway? What
do you change? (b) A model upgrade raises the public SWE-bench Verified resolve rate by 4 points. Ship it?

<details><summary>Answer</summary>

(a) An average 40 k-token context is ≈ 160 KB per activity. 40 steps ≈ 6.4 MB: fits. The 50 MB history limit is
crossed after about 50 MB / 160 KB ≈ 310 steps, so the 400-step runaway (≈ 64 MB) is past the 50 MB history limit
(Temporal's docs state termination explicitly only for the 51,200-event, 2,000-update and 10,000-signal limits; for
size they give only the limit, so treat it as a hard stop too), and ≈ 64 MB is a lower bound, because late contexts
are larger (a 200 k-token context is ≈ 800 KB). One late 80 k-token payload (≈ 320 KB) fits the 2 MB payload limit,
but a large test log may not. Fix: keep transcripts and tool outputs in object storage and put only keys and hashes in
the history, use Continue-As-New every N steps, and let the step budget stop runaways before the engine does. (b) No,
not on that evidence. OpenAI found flawed tests in at least 59.4 % of the 138 problems it audited (problems o3 did not
consistently solve, not a random sample) and evidence of training contamination, and stopped reporting Verified. Epoch
AI rates the benchmark "Flawed" and puts the floor of broken tasks at 16.4 %. Gate on the internal suite of consented
tenant tasks. Size it for the decision, with the method of
[SYSDESIGN-32](../course/03-ai-systems/32-observing-evaluating-agents.md) (Numbers 4): at a 60 % resolve rate, a
500-task suite has a 95 % interval of about ±4.3 points (1.96 × √(0.6 × 0.4 / 500)), too wide to see a 2-point change.
Detecting a 2-point drop (60 % → 58 %) with 80 % power at two-sided α = 0.05 needs (1.96 + 0.84)² × (0.6 × 0.4 + 0.58
× 0.42) / 0.02² ≈ 9,500 tasks per model if the two runs are independent samples, or (1.96 + 0.84)² × 0.10 / 0.02² ≈
2,000 tasks in a paired comparison on the same tasks, assuming the two models disagree (one resolves, the other does
not) on 10 % of them. The paired figure scales with that discordance rate, so measure your own with an A/A run before
trusting it. (0.24 × (1.96 / 0.02)² ≈ 2,300 is only the size for a ±2-point interval on one model's rate, not for
detecting a difference.) Also compare cost per resolved task and approval requests per task, not only resolve rate.
</details>
