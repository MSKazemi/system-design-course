# 25 — Agentic systems (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- Multi-step tasks for 10,000 daily users, up to 30 minutes
- Least privilege and audit for every tool call
- Human approval for risky actions; hard cost cap
- No duplicate side effects after a crash

**Visual:** title card; icons `domain-bot`, `security-authorization`, `ops-cost`.
**Speaker notes:** An agent is a program that writes its own control flow at runtime. The runtime must enforce what
code review normally would.

## Slide 2 — The loop
- Model proposes a tool call, runtime decides
- Tool results are untrusted data
- Context grows every step
- Stop on done, budget or loop

**Visual:** sequence diagram User → Runtime → LLM → Tool from the lesson.
**Speaker notes:** ReAct (Yao et al.) interleaves reasoning and acting. Everything hard sits in the runtime around
that loop.

## Slide 3 — Tools that scale
- Few, well-described tools; schemas cost tokens
- Validate arguments; never trust the model's JSON
- Idempotency keys on side effects
- Errors are observations, not crashes

**Visual:** a tool card (name, description, JSON Schema) with a validator gate.
**Speaker notes:** In L25, a 0.5B model emitted truncated tool-call JSON. The runtime must survive that.

## Slide 4 — MCP, as of 2026-11
- Tools, resources, prompts over stdio or Streamable HTTP
- Spec 2026-07-28: stateless, no handshake, no session id
- `Mcp-Method` / `Mcp-Name` headers for gateways
- Hosted by the Agentic AI Foundation (Linux Foundation)

**Visual:** N agents × M tools → N + M adapters through MCP; icons `ai-mcp`, `ai-tool`.
**Speaker notes:** Statelessness means MCP servers sit behind ordinary load balancers. Treat them as microservices
with SLOs.

## Slide 5 — A2A, as of 2026-11
- Agent ↔ opaque agent delegation
- Agent Card, Task, Message/Part, Artifact
- JSON-RPC over HTTP(S); polling, SSE, push
- v1.0.0 (Mar 2026), v1.0.1 (May 2026)

**Visual:** two agent boxes exchanging a Task and Artifacts; MCP tools under each.
**Speaker notes:** Use MCP for capabilities you control and A2A for agents you don't.

## Slide 6 — Orchestration patterns
- Single agent: open-ended, few tools
- Router: clear categories
- Supervisor: parallel specialised workers
- Graph / workflow: known shape, checkpoints, approvals

**Visual:** four mini-diagrams from the lesson.
**Speaker notes:** Start with the least agentic design that meets the requirement. Each extra agent is latency,
cost and a failure point.

## Slide 7 — Tokens grow quadratically
- Σ = N·base + Δ·N(N−1)/2
- 15 steps ≈ 202,500 input tokens (lesson assumptions)
- 30 steps ≈ 742,500: 3.7× for 2× steps
- Reliability: 0.98¹⁵ ≈ 0.74

**Visual:** line chart of cumulative tokens vs steps (quadratic).
**Speaker notes:** Cutting steps is the biggest cost lever, and long chains need checkpoints and verification.

## Slide 8 — State, memory, durable execution
- Working, task state, semantic, episodic, procedural memory
- Checkpoint after every step
- Durable execution: the loop as a workflow, LLM and tool calls as activities
- Approvals as signals that wait for hours

**Visual:** timeline with checkpoints and a crash/resume arrow; icons `pattern-saga`, `arch-database`.
**Speaker notes:** Recorded results make replay safe. Never re-ask the model to redo a step that had side effects.

## Slide 9 — Exactly-once effects
- Write intent → call with idempotency key → write result
- On resume, retry the recorded intent, do not re-plan
- Tool deduplicates on the key
- L25: crash after send → resume → "duplicate suppressed"

**Visual:** three-step intent/result journal; icon `pattern-idempotency`.
**Speaker notes:** You can't get exactly-once execution, but you can get exactly-once effects.

## Slide 10 — Sandboxes
- Container: shared kernel, fast
- gVisor: user-space kernel, syscall overhead
- Firecracker microVM: own kernel, <125 ms boot (project claim)
- Always: no network, read-only, limits, non-root, fresh per task

**Visual:** isolation ladder from process to microVM; icons `arch-containers`, `security-lock`.
**Speaker notes:** In L25, sandboxed code could not reach the network, could not write to /, ran as uid 65534 and
was killed at 10 s.

## Slide 11 — Permissions and approvals
- OWASP LLM06 Excessive Agency
- Per-task, short-lived, narrowed credentials
- Risk tiers: allow / audit / approve
- Lethal trifecta: private data + untrusted content + external comms

**Visual:** triangle with the three legs; one leg cut.
**Speaker notes:** Approvals must show the exact action, not the model's summary of it. Break at least one leg of
the trifecta.

## Slide 12 — Budgets, loops, observability, evals
- Steps, tokens, money, deadline, per-tool timeout, enforced by the runtime
- Loop detection on repeated (tool, args)
- Traces: task → LLM spans → tool spans (OTel GenAI, Development)
- Evals: SWE-bench, τ-bench pass^k, AgentDojo for injection

**Visual:** trace waterfall; icons `ops-tracing`, `observability-opentelemetry`.
**Speaker notes:** Many agent failures are visible only as strange trajectories. Evaluate over many trials, not one.

## Slide 13 — Interview angle
- CLARIFY task length, tools, risk tiers, approvers
- QUANTIFY tokens (quadratic), cost/day, sandbox concurrency
- DEEPEN exactly-once effects *or* sandbox *or* permissions
- Red flags: "the prompt forbids it", admin service account, no budgets

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Interviewers listen for the runtime, not the prompt. Put budgets, approvals and idempotency in
the design.
