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
- `Mcp-Method` on every request, `Mcp-Name` on tools/call, resources/read, prompts/get
- Hosted by the Agentic AI Foundation (Linux Foundation)

**Visual:** N agents × M tools → N + M adapters through MCP; icons `ai-mcp`, `ai-tool`.
**Speaker notes:** Statelessness means MCP servers sit behind ordinary load balancers. Treat them as microservices
with SLOs.

## Slide 5 — A2A, as of 2026-11
- Agent ↔ opaque agent delegation
- Agent Card, Task, Message/Part, Artifact
- Three bindings: JSON-RPC 2.0 over HTTP(S), gRPC, HTTP+JSON/REST; polling, SSE, push
- v1.0.0 (Mar 2026), v1.0.1 (May 2026); `A2A-Version` header required

**Visual:** two agent boxes exchanging a Task and Artifacts; MCP tools under each.
**Speaker notes:** Use MCP for capabilities you control and A2A for agents you don't.

## Slide 6 — Where the runtime ends
- Shape (workflow, one agent, a team of agents): SYSDESIGN-29
- Context window and long-term memory: SYSDESIGN-30
- Threat model, containment, kill switch: SYSDESIGN-31
- Traces and evaluation: SYSDESIGN-32. Multi-tenant platform: SYSDESIGN-33

**Visual:** the runtime box from slide 2 in the centre, five labelled arrows out to units 29–33.
**Speaker notes:** This unit is the runtime: the loop, tools, protocols, budgets, sandbox, permissions and
exactly-once effects. Start with the least agentic design that meets the requirement. Each extra agent is latency,
cost and a failure point.

## Slide 7 — Tokens grow quadratically
- Σ = N·base + Δ·N(N−1)/2
- 15 steps ≈ 202,500 input tokens (lesson assumptions)
- 30 steps ≈ 742,500: 3.7× for 2× steps
- Tokens *processed* grow quadratically; with prompt caching the dollars grow more slowly (≈ $0.066 vs $0.22)
- Reliability: 0.98¹⁵ ≈ 0.74

**Visual:** line chart of cumulative tokens vs steps (quadratic).
**Speaker notes:** Cutting steps is the biggest cost lever, and long chains need checkpoints and verification.

## Slide 8 — Task state and durable execution
- Task state (plan, step, budgets, approvals, intents) is the runtime's; memory is unit 30's
- Checkpoint after every step
- Durable execution: the loop as a workflow, LLM and tool calls as activities
- Approvals as signals that wait for hours; engine limits (Temporal: 2 MB payload, 51,200 events)

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
- Firecracker microVM: own kernel; ≤ 125 ms boot only for a minimal kernel and root filesystem
- None covers host hardware flaws: gVisor and Firecracker docs say so; disable SMT, use the jailer
- Always: no network, read-only, limits, non-root, fresh per task

**Visual:** isolation ladder from process to microVM, each rung tagged with what it does not cover; icons
`arch-containers`, `security-lock`.
**Speaker notes:** In L25, sandboxed code could not reach the network, could not write to /, ran as uid 65534 and
was killed at 10 s. Quote boot figures with their configuration, and remember gVisor's own warning that a sandbox
is not a substitute for a secure architecture.

## Slide 11 — Permissions and approvals
- OWASP Excessive Agency (LLM03:2026, LLM06 in 2025)
- Per-task, short-lived, narrowed credentials
- Risk tiers: allow / audit / approve, by reversibility *and* by who can read the result
- Classify by what leaves: a fetch or search with a model-written URL or query is outbound
- Lethal trifecta: private data + untrusted content + external comms

**Visual:** triangle with the three legs; one leg cut.
**Speaker notes:** Approvals must show the exact action, not the model's summary of it. Break at least one leg of
the trifecta. How the agent's identity and the user's authority combine in one token per hop is in unit 18.

## Slide 12 — Budgets and loop control
- Steps, tokens, money, deadline, per-tool timeout, enforced by the runtime
- Caps checked *before* each model call; a runaway 100-step loop ≈ $7.8 (lesson assumptions)
- Loop detection on repeated (tool, args); hint once, then stop with a partial result
- Trace every call (OTel GenAI, Development); traces and evals in depth: unit 32

**Visual:** spend meter per task with a hard cap line; icons `ops-cost`, `ops-tracing`.
**Speaker notes:** Budgets in the prompt are wishes; budgets in the runtime are controls. Many agent failures are
visible only as strange trajectories, so record them, and evaluate over many trials (unit 32).

## Slide 13 — Interview angle
- CLARIFY task length, tools, risk tiers, approvers
- QUANTIFY tokens (quadratic), cost/day, sandbox concurrency
- DEEPEN exactly-once effects *or* sandbox *or* permissions
- Red flags: "the prompt forbids it", admin service account, no budgets

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Interviewers listen for the runtime, not the prompt. Put budgets, approvals and idempotency in
the design.
