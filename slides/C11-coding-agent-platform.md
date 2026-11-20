# C11 — AI coding-agent platform (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- Assign an issue to an agent; it works in a cloud sandbox up to an hour and opens a PR
- 5,000 orgs, 200,000 tasks/day
- Untrusted code + long-running workflow + growing token bills
**Visual:** issue card → robot in a sandbox box → PR card. Icons: `domain-bot`, `arch-containers`, `devops-git`.
**Speaker notes:** Three hard systems in one: multi-tenant code execution, durable workflows and an LLM client.

## Slide 2 — CLARIFY
- Tools (local + MCP), live progress, guidance mid-task, approvals for risky actions
- Budgets per task/user/org; full audit trail
- Key question: does the agent need internet access?
**Visual:** requirement list. Icons: `ops-check`, `security-authorization`.
**Speaker notes:** The internet-access answer decides most of the security design.

## Slide 3 — QUANTIFY sessions
- ≈ 7 tasks/s at peak × 20 min → ≈ 8,400 concurrent sessions (Little's law)
- 2 vCPU / 4 GiB each → ≈ 17,000 vCPU ≈ 175 hosts of 96 vCPU / 192 GiB (assumptions)
**Visual:** Little's law triangle with the three numbers. Icons: `arch-servers-cluster`, `ops-throughput`.
**Speaker notes:** Sandboxes are a fleet, but a modest one.

## Slide 4 — QUANTIFY tokens and cost
- 40 steps × ≈ 40 k input tokens → ≈ 1.6 M input tokens per task
- Context grows each step → input grows roughly quadratically
- Assumed prices → ≈ $1.50 per task; tokens over 95 %, sandbox ≈ 2 %
**Visual:** stacked area chart of context per step. Icons: `ops-cost`.
**Speaker notes:** A loop of 400 steps instead of 40 costs about 80× more input if context grows without bound, about 40× with a 200 k-token window cap (assumption).

## Slide 5 — SKETCH
- Control plane → fair scheduler → durable workflow → agent runtime
- Runtime ↔ LLM gateway, sandbox (via egress proxy), tool broker (MCP), approvals
- Repo cache, event log and checkpoints, traces
**Visual:** the lesson flowchart. Icons: `arch-api-gateway`, `arch-queue`, `arch-worker`, `arch-firewall`.
**Speaker notes:** The runtime holds no long-lived secrets; the proxy and the broker do.

## Slide 6 — Isolation choice
- Containers: shared kernel — not for hostile multi-tenant code
- gVisor: user-space kernel; syscall overhead and compatibility limits
- Firecracker: < 5 MB overhead, < 125 ms boot, 150 microVMs/s/host (NSDI 2020)
**Visual:** three stacks showing where the kernel boundary sits. Icons: `arch-containers`, `security-lock`, `arch-server`.
**Speaker notes:** Default to microVMs; keep defence in depth inside the guest.

## Slide 7 — Fast start
- Boot is fast; environment is slow (clone, install, build)
- Snapshots, regional Git mirror, partial + sparse clone, golden repo disks
- Dependency mirror keyed by lockfile
**Visual:** timeline: cold start vs snapshot start. Icons: `pattern-backup`, `arch-cache`, `devops-git`.
**Speaker notes:** Turn a five-minute setup into a copy-on-write clone plus a small fetch.

## Slide 8 — Tools via MCP
- JSON-RPC; tools/resources/prompts; spec 2026-07-28 (as of 2026-11)
- Hosts must get explicit consent before invoking tools; annotations untrusted
- OAuth 2.1 profile: resource indicators; servers accept only their own tokens
**Visual:** agent runtime → tool broker → several MCP servers. Icons: `pattern-api`, `security-oauth`.
**Speaker notes:** Treat third-party MCP servers and their results as untrusted.

## Slide 9 — Secrets never in the sandbox
- Egress proxy injects short-lived, scoped credentials
- Workload identity per sandbox
- Scrub outputs; scan diffs before LLM and PR
**Visual:** sandbox with no keys; proxy adds a key on the outbound arrow. Icons: `security-key`, `arch-firewall`, `devops-vault`.
**Speaker notes:** A token in the sandbox environment is one prompt injection away from leaking.

## Slide 10 — Approvals
- Risk classes: read, local write, reversible external, risky, irreversible
- Approval bound to the exact command/diff hash
- Workflow sleeps durably; sandbox snapshotted and released
**Visual:** risk ladder with gates on the top two. Icons: `security-authorization`, `ops-check`.
**Speaker notes:** The model asking politely is not a control; the gate is.

## Slide 11 — Durable sessions
- Each LLM/tool call is a recorded activity; replay from event history
- Idempotency keys per tool call; record intent then result
- Checkpoints: git commit + periodic microVM snapshot
**Visual:** the task state machine. Icons: `pattern-event-sourcing`, `pattern-idempotency`, `pattern-retry`.
**Speaker notes:** Never regenerate an LLM output on replay; record it.

## Slide 12 — Budgets and loops
- Reserve before each call, reconcile after; wrap-up at 80 %, stop at 100 %
- Detect repeated tool+args, edit/revert cycles, flat test results
- Reflect → escalate → stop
**Visual:** spend meter with thresholds. Icons: `ops-cost`, `ops-warning`, `pattern-circuit-breaker`.
**Speaker notes:** Budget checks after the task ends are not budgets.

## Slide 13 — Observe, evaluate, share fairly
- One trace per task; spans per LLM/tool call; OTel GenAI conventions still Development
- SWE-bench: 2,294 instances, 12 repos; Verified: 500 human-screened
- Per-org quotas, weighted fair queueing, interactive ahead of background
**Visual:** trace waterfall + fairness queues. Icons: `ops-tracing`, `observability-opentelemetry`, `pattern-rate-limiter`.
**Speaker notes:** Internal consented task suites gate releases; public benchmarks may be contaminated.

## Slide 14 — WRAP
- Junior: queue, workers, loop, PR, timeouts
- Senior: microVMs, egress control, durable replay, budgets, approvals, quotas
- Staff: injection-driven threat model, quadratic cost, fairness classes, eval gates, snapshot economics
- Red flags: shared-kernel containers, token in env, open internet, no budget
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** Close with cost per task and the three controls that bound it.
