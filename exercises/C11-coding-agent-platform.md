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
with its minimal configuration). For single-tenant, trusted workloads containers with seccomp may be acceptable.
</details>

## 4. [Deep] Secrets

An integration test needs a payment-sandbox API key. Design how the agent can run it without the key reaching the
model or persisting in the sandbox.

<details><summary>Answer</summary>

Prefer credential injection at the egress proxy (the test calls the API through the proxy, which adds the key based
on the sandbox's workload identity). If the key must be local, mount it as a file only for that command, gated by an
org approval policy; scrub the key from stdout/stderr before the output is added to the model context; scan diffs and
PR text for secret patterns; revoke or rotate short-lived keys after the task. Never place it in environment variables
visible to every process, and never in the prompt.
</details>

## 5. [Interview] Approvals

Which of these need human approval by default, and why: (a) run unit tests, (b) push to the task branch, (c) add a new
npm dependency, (d) run a database migration against staging, (e) open network access to a new domain?

<details><summary>Answer</summary>

(a) No — local and disposable. (b) No, but logged — reversible, scoped branch. (c) Yes — supply-chain risk.
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
