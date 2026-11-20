---
id: SYSDESIGN-25
title: "Agentic systems"
part: "III — AI-native systems"
level: [core, deep, frontier]
status: SOURCES_CHECKED
prerequisites: [SYSDESIGN-08, SYSDESIGN-11, SYSDESIGN-18, SYSDESIGN-21, SYSDESIGN-24]
estimated_time: "3h reading + 2h lab"
requirement: "Run multi-step research-and-analysis tasks for 10,000 daily users: tasks up to 30 minutes, every tool call least-privileged and audited, risky actions approved by a human, a hard cost cap per task, and no duplicated side effects after a worker crash"
learning_objectives:
  - "Explain the agent loop (ReAct-style reason/act/observe) and why its cost grows super-linearly with the number of steps"
  - "Design tool interfaces that stay small in context, keep the prompt cache stable, validate arguments and are safe to retry"
  - "Describe MCP and A2A as of 2026-11: what each standardises, transports, and governance"
  - "Design intent records, idempotency keys and checkpoints so a crashed agent resumes without repeating side effects"
  - "Design a sandbox and permission model for tool execution, including human approval gates and budgets"
  - "Estimate tokens, cost, latency, sandbox concurrency and checkpoint volume for an agent workload"
last_reviewed: 2026-11-20
---

# 25 — Agentic systems

> **The requirement.** Lumen now offers "tasks": *"compare our three vendor contracts and chart the renewal costs"*.
> The assistant must search documents, run analysis code, call internal APIs, and write a report. Up to 10,000 users
> run tasks every day. One task may take 30 minutes and 20+ model calls. Every tool call must run with the minimum
> privileges it needs and leave an audit record. Sending an email or changing a record needs a human's approval.
> Each task has a hard cost cap. A worker crash must not cause a second email or a second database write.
> This is hard because an agent is a **non-deterministic program that writes its own control flow at runtime**, and
> every guarantee you normally get from code review has to be enforced by the runtime around it.

## In one minute

An *agent* is a loop. An LLM looks at the goal and the history so far, picks an action (usually a tool call such as
"search", "run this Python", "call the CRM API"), the runtime executes it, the result is appended to the history,
and the loop repeats until the model says it is done or a limit is hit. That is all. Everything difficult is in the
*runtime*. Tools need a standard interface (that is what MCP standardises). Agents may delegate to other agents
(A2A). Long tasks need saved state so a crash does not restart from zero. Code the model writes must run in a
sandbox. Dangerous actions need a human "yes". Budgets on tokens, time and money must stop runaway loops. And you
need traces to understand why the agent did what it did. Design the runtime as you would a workflow engine plus a
security boundary, and treat the model as an untrusted, creative planner inside it.

## Why this matters now

- **Tool calling became a native model feature.** ReAct (Yao et al., 2022) showed that interleaving reasoning traces
  with actions beats either alone on several tasks [1]. Toolformer (Schick et al., 2023) showed that a model can
  learn by itself when and how to call external APIs [2]. Model APIs and open inference servers now expose structured
  tool calls in the OpenAI-compatible format. Lab L25 uses llama.cpp's server for this.
- **Tool integration was standardised.** The Model Context Protocol (MCP) gives agents one way to discover and call
  tools, resources and prompts. Its current revision is **2026-07-28**, which made the core protocol **stateless**:
  the `initialize` handshake and `Mcp-Session-Id` were removed, so any server instance can handle any request [4][5].
  MCP was contributed to the Linux Foundation's **Agentic AI Foundation (AAIF)** at its formation on 9 Dec 2025
  [6]. *As of 2026-11.*
- **Agent-to-agent interoperability arrived.** The Agent2Agent protocol (A2A) reached **v1.0.0 on 2026-03-12**
  (v1.0.1 on 2026-05-28). It is Apache-2.0 and under Linux Foundation governance [7][8], and AAIF's project list
  includes it [41]. *As of 2026-11.*
- **Agents run for minutes to hours.** Coding agents are evaluated on real repositories (SWE-bench: 2,294 issues from
  12 Python repos; SWE-bench Verified: a 500-task human-validated subset) [13][14]. Verified is now a cautionary
  tale: Epoch AI rated it "Flawed" in September 2026 [29] ([SYSDESIGN-32](32-observing-evaluating-agents.md)). Long
  tasks made durable execution, checkpointing and sandboxes into mainstream infrastructure concerns.
- **Prompt injection through tools is the defining security problem.** Indirect prompt injection (Greshake et al.,
  2023) showed that content an agent *reads* can steer what it *does* [17]. Design-level defences such as CaMeL
  (2025) [18] and benchmarks such as AgentDojo [19] followed. SYSDESIGN-28 and
  [SYSDESIGN-31](31-securing-agentic-systems.md) treat this in depth. This chapter makes sure the runtime contains
  the blast radius.

The companion course **[AI Agent Systems](https://github.com/MSKazemi/ai-agent-systems-course)** goes deeper into
building agents in Python (MCP, A2A, LangGraph, a ReAct code-executor). This chapter is the *system design* view:
capacity, failure, isolation and cost.

**Where this chapter sits.** This is the *runtime* chapter: the loop, tool calling, MCP and A2A, budgets, sandboxes,
permissions and exactly-once effects. Five chapters build on it.
[SYSDESIGN-29](29-agent-architectures-orchestration.md) chooses the shape: a fixed workflow, one agent or a team of
agents. [SYSDESIGN-30](30-context-engineering-memory.md) manages the context window and long-term memory.
[SYSDESIGN-31](31-securing-agentic-systems.md) threat-models the platform and contains a hijacked agent.
[SYSDESIGN-32](32-observing-evaluating-agents.md) traces and evaluates agent runs.
[SYSDESIGN-33](33-agent-platform-runtime.md) runs agents as a multi-tenant platform: queues, fairness, durable
engines and rollout.

## Core ideas [Core]

### 1. The agent loop

```mermaid
sequenceDiagram
  participant U as User
  participant R as Agent runtime
  participant M as LLM
  participant T as Tool (via MCP)
  U->>R: goal
  loop until done or budget exhausted
    R->>M: system + tools + history
    M-->>R: tool_call(name, args) or final answer
    R->>R: policy check (allow / deny / needs approval)
    R->>T: call(args) with timeout, scoped credentials
    T-->>R: result (untrusted data)
    R->>R: append observation, update budgets, checkpoint
  end
  R-->>U: answer + trace link
```

*Diagram: the runtime repeatedly sends the history to the model, receives a tool call or final answer, checks policy,
calls the tool with a timeout and scoped credentials, appends the result, updates budgets and checkpoints, and finally
returns the answer.*

Three properties follow directly:

1. **The model never executes anything.** It *proposes* a call. The runtime decides. That decision point is where
   policy, approvals, budgets and audit live. Provider-hosted *server tools* (for example web search or code
   execution) are the exception: they run on the provider's infrastructure, not in your application [40]. For
   those, the policy decision is made when you enable the tool, not per call.
2. **Tool results are untrusted input.** A web page, an email or a PDF returned by a tool may contain instructions.
   The runtime must treat them as data (§Deep dive, and SYSDESIGN-28).
3. **Context grows every step.** Each iteration re-sends the growing history, so tokens *processed* per task grow
   roughly quadratically with steps. Dollars grow more slowly while the prefix stays cached (see Numbers).

### 2. Tool calling

A tool is a name, a description and a JSON Schema for arguments. The model emits a structured call. The runtime
validates the arguments against the schema (never trust the model to obey it), executes, and returns a result.
Design rules that matter at scale:

- **Few, well-described tools beat many.** Every tool's schema goes into every prompt (token cost), and long tool
  lists make the model's choice harder (measure it on your own evals). Group by task. Loading tools dynamically
  saves tokens but fights the prompt cache. Tool definitions are the first part of the cached prefix (tools, then
  system, then messages), so changing them invalidates the whole cache on Anthropic's API and breaks the prefix
  match on OpenAI's [30][31]. Patterns that keep both: choose one fixed tool list per task type at task start; keep
  every definition and restrict which tools may be called (OpenAI recommends `allowed_tools` or `tool_choice`
  instead of removing definitions [31]); or use provider tool search, which appends discovered definitions to the
  conversation instead of the prefix (Anthropic's `defer_loading` [30]). Providers also let you add a tool
  mid-conversation without editing the tools prefix (Anthropic's beta header `inline-tools-2026-09-15`, OpenAI's
  `additional_tools` input item, as of 2026-11; check support per model) [30][31]. Measure the cached-token share
  before and after any change.
- **Idempotency keys on side effects.** `send_email(..., idempotency_key=task_id+step_no)` makes retries safe
  (SYSDESIGN-08 for the pattern).
- **Typed, bounded outputs.** Truncate and summarise large results before they enter the context. Return structured
  data where possible.
- **Errors are observations.** Return `{"error": "timeout after 10s"}` to the model so it can adapt. Do not crash the
  loop.

### 3. Model Context Protocol (MCP) — *as of 2026-11, spec revision 2026-07-28*

MCP standardises the connection between an AI application (the *host/client*) and a capability provider (the
*server*). Before MCP, every agent framework had its own plugin format, so N agents × M tools needed N×M adapters.

- **Server primitives:** *tools* (model-invoked functions), *resources* (readable context identified by URI), and
  *prompts* (reusable templates) [4].
- **Transports:** stdio (local subprocess) and Streamable HTTP (remote). The older HTTP+SSE transport has been
  deprecated since 2025-03-26, so plan on Streamable HTTP now [5][27].
- **Statelessness (2026-07-28):** every request carries its own protocol version (in `_meta` and the
  `MCP-Protocol-Version` header) and client details. Servers can be load-balanced like ordinary HTTP services.
  On Streamable HTTP every request also carries `Mcp-Method`. Requests that name a target (`tools/call`,
  `resources/read`, `prompts/get`) add `Mcp-Name`, so a gateway can route and authorise per tool without parsing
  the body. A server that processes the body rejects a header that disagrees with it (400, `HeaderMismatch`) [33].
  Clients can call `server/discover` to learn versions and capabilities up front [3].
- **Extensions:** long-running *Tasks* moved into the `io.modelcontextprotocol/tasks` extension. Roots, Sampling
  and Logging are deprecated and will keep working for at least twelve months [5]. The deprecation registry lists
  their earliest removal as the first revision released on or after 2027-07-28 [27].
- **Multi round-trip requests (MRTR):** instead of the server opening its own requests to the client
  (elicitation, sampling, roots), a tool call can return `resultType: "input_required"` with the questions it
  needs answered, and the client retries the call with `inputResponses`. This is how a stateless tool asks the user
  to confirm an action. List and read results now also carry cache hints (`ttlMs`, `cacheScope`) [5].
- **Authorization:** OAuth 2.1-based and optional. HTTP servers that use it must publish Protected Resource
  Metadata (RFC 9728), and stdio servers should take credentials from the environment. Authorization servers
  *should* return the issuer (`iss`, RFC 9207), and clients *must* compare a returned `iss` with the issuer they
  recorded. A later revision is expected to make `iss` mandatory [32]. Client credentials are bound to the issuer
  that minted them, and Dynamic Client Registration is deprecated in favour of Client ID Metadata Documents [5][32].
  Token audience, passthrough and confused-deputy risks are in
  [SYSDESIGN-31](31-securing-agentic-systems.md#4-confused-deputies-and-token-passthrough-in-mcp).
- **Governance:** MCP is hosted by the Agentic AI Foundation, a Linux Foundation initiative launched with MCP,
  goose and AGENTS.md as founding projects [6]. The spec site carries the "LF Projects, LLC" copyright [5].

System-design consequences: an MCP server is a **microservice with a tool-shaped API**. It needs authN/Z, rate
limits, versioning, observability and SLOs like any other service. Because the protocol is now stateless, put MCP
servers behind ordinary L7 load balancers and gateways (SYSDESIGN-26). Any state a tool needs across calls is
returned as an explicit handle that the model passes back [5].

### 4. Agent2Agent (A2A) — *as of 2026-11, v1.0.x*

Where MCP connects an agent to *tools*, A2A connects an agent to *another agent* that it treats as opaque. You do not
see its prompts, tools or memory. Core concepts [8]:

- **Agent Card:** a JSON metadata document describing identity, capabilities, endpoint, skills and authentication
  requirements, used for discovery. Clients find it at `/.well-known/agent-card.json`, in curated registries or by
  direct configuration (§8.2). A card MAY be JWS-signed (RFC 7515, canonicalised with RFC 8785, §8.4), and an
  extended card is served only to authenticated clients (§3.1.11) [8]. A valid signature shows who published the
  card, not that the agent is safe to trust.
- **Task:** a stateful unit of work with an id and a lifecycle, which supports long-running and multi-turn
  collaboration.
- **Message / Part / Artifact:** turns of communication made of parts (text, file, structured data). Artifacts are
  the outputs, and they can be streamed.
- **Interaction:** operations are defined once and mapped to three protocol bindings: JSON-RPC 2.0 over HTTP(S),
  gRPC, and HTTP+JSON/REST, with guidance for custom bindings. Polling, streaming (SSE) and push notifications
  (webhooks) are supported for long tasks [8].
- **Versioning:** v1.0 clients must send an `A2A-Version` header (spec §3.6.1). Requests without it are treated as
  0.3, so this is a breaking change from 0.3 [8]. A `v1.1.0-rc` tag exists (commit dated 2026-10-29), but the
  latest published release is still v1.0.1 (as of 2026-11) [7].

Rule of thumb: **MCP for capabilities you control, A2A for delegating to agents you don't.** A2A is a federation
protocol across team or vendor boundaries.

### 5. Orchestration patterns

The loop in §1 is one agent. Larger designs combine loops: a *router* sends each request to one specialist, a
*supervisor* delegates to workers that report back, and a *graph* (state machine) fixes the process shape and leaves
only some steps to the model. A fixed workflow with LLM steps, and no agent loop at all, is often the right answer.
Start with the *least* agentic design that meets the requirement. Anthropic's engineering guidance makes the same
argument: workflows for predictable tasks, agents only where flexibility pays [20] (vendor blog, perspective). Every
extra agent adds latency, cost and a failure point. [SYSDESIGN-29](29-agent-architectures-orchestration.md) owns this
decision: the workflow-or-agent test, the patterns, and when multi-agent designs pay for themselves.

### 6. State and memory

**Task state** belongs to the runtime: plan, step number, budgets used, pending approvals, tool results and intent
records. Persist it after every step, keyed by task id, so a crash resumes from the last completed step and a human
can inspect or edit it. LangGraph's checkpointers, for example, persist a thread's graph state for continuity,
human-in-the-loop, time travel and fault tolerance [10]. **Memory**, meaning what enters the context window and what
is kept across sessions, is a context-engineering and data-governance problem (who reads it, how it is erased, can
injected content plant a "memory"). [SYSDESIGN-30](30-context-engineering-memory.md) owns it.

### 7. Durable execution for long-running agents

A 30-minute task on a worker that is redeployed every 10 minutes *will* be interrupted. Either checkpoint after each
step and resume, paired with idempotency keys because an effect between "tool executed" and "checkpoint written" can
repeat, or run the loop on a durable execution engine such as Temporal, which records each activity result in the
workflow's event history and replays from it after a failure [11]. The mapping: the **agent loop is the workflow**,
each **LLM call and tool call is an activity**, and **approvals are signals** the workflow waits on for hours without
holding a thread. Workflow code must be deterministic, so the model's output must come from a recorded activity.
Engines also bound one execution (Temporal: 2 MB per payload, 51,200 events or 50 MB of history [34]), so keep
transcripts in object storage, record only references in the history, and use Continue-As-New every N steps [35].
[SYSDESIGN-33](33-agent-platform-runtime.md#4-durable-execution-engines-and-their-limits) turns these limits into a
platform design.

### 8. Sandboxed code execution

When the agent writes code, run it as if it came from an anonymous internet user. Isolation options, from weakest to
strongest:

| Isolation | Mechanism | Wins when | Costs |
|---|---|---|---|
| Process + seccomp/rlimits | Same kernel, syscall filter | Trusted code, speed | One kernel bug from escape |
| **Container** (namespaces + cgroups) | Shared host kernel | Low latency, density; internal code | Kernel attack surface is shared |
| **gVisor** (`runsc`) | User-space "application kernel" (the Sentry) intercepts syscalls [15] | Untrusted code with container ergonomics | Higher per-syscall overhead; some syscalls and `/proc` files unsupported [15] |
| **microVM** (Firecracker) | KVM-based minimal VMM; each sandbox has its own guest kernel | Multi-tenant untrusted code at scale (Firecracker runs AWS Lambda and Fargate [16]) | Needs KVM; image and boot management. Its specification states ≤ 125 ms boot (minimal kernel and root filesystem) and ≤ 5 MiB VMM overhead (1 vCPU, 128 MiB guest) [22] |
| Wasm runtimes | Capability-based, no syscalls by default | Small pure functions | Limited language and library support |

Whatever the isolation layer, apply the same **container hygiene**: no network by default (or an egress proxy
with an allow-list), read-only root filesystem, a small writable tmpfs, CPU, memory and PID limits, a wall-clock
timeout, a non-root user, no host mounts, no cloud metadata endpoint, and a fresh sandbox per task (or per call) with
no credentials inside. Lab L25 implements this with `docker run --network none --read-only --memory --pids-limit`.

**What each layer does not do.** No runtime removes the need for host hardening. Containers isolate with namespaces
and cgroups over one shared kernel. Docker's own security page warns that default capabilities and mounts "may
provide incomplete isolation", alone or "in combination with kernel vulnerabilities" [39]. gVisor shrinks the host
kernel's system-call attack surface, but its security model says "a sandbox is not a substitute for a secure
architecture", that it does not in general protect against hardware side channels, and that it relies on host
cgroups against resource exhaustion [37]. Firecracker "is not able to mitigate host's hardware vulnerabilities". Its
production host guide recommends disabling SMT "in production scenarios that require tenant separation", running
each VMM under the jailer with its own uid and gid, keeping the default seccomp filters, and dropping guest packets
addressed to the host's metadata service [38]. Quote boot and overhead figures only with their configuration: a
minimal 128 MiB guest is not the 2 vCPU, 4 GiB build sandbox of case C11. [SYSDESIGN-31](31-securing-agentic-systems.md#5-containment-architecture)
assembles these layers into a containment architecture, and
[SYSDESIGN-33](33-agent-platform-runtime.md#9-sandboxes-as-a-pooled-resource) runs them as a pooled resource.

### 9. Permissions, least privilege and human-in-the-loop

OWASP lists **Excessive Agency** as a top risk (LLM03 in the 2026 edition, LLM06 in 2025) [21][28]. Its root causes are excessive functionality, excessive
permissions and excessive autonomy [21][28]. Controls:

- **Per-tool, per-task scopes.** The agent acting for Alice gets Alice's permissions, *narrowed* to the task (read
  the contracts folder, not the whole drive). Use short-lived, audience-restricted tokens (SYSDESIGN-18 workload
  identity), never a shared service account with admin rights. How the agent's own identity and the user's
  authority are combined in one token per hop, and what the audit record links (human, agent chain, action), is in
  [SYSDESIGN-18](../02-modern-requirements/18-security-by-design.md#agent-identity-and-delegation-chains).
- **Risk tiers.** Tier by reversibility *and* by who can read the result. Read-only tools: auto-allow. Writes
  that only the requester can see (a draft, a private scratch branch): allow with audit. Writes that other people can
  read, such as a comment, a pull request or a webhook, are a disclosure channel even when you can delete them,
  because a leak cannot be undone. Require approval for them once the task has read untrusted content, or confine
  them to a private destination. In the 2025 GitHub MCP attack, an injected public issue made an agent copy
  private-repository data into a pull request on the public repo [36]. Classify by what leaves the system, not by
  the tool's name: a web fetch or search whose URL or query text the model writes can carry data out, because any
  HTTP request "can be used to pass stolen information back to an attacker" [23]. Once the task has read untrusted
  content, treat such "reads" like writes others can read. Irreversible actions (send email, pay, delete, deploy):
  **require approval**.
- **Approval as a first-class state.** The runtime pauses the task, persists it, notifies a human with the *exact*
  call (tool, arguments, diff), and resumes on approve or reject. LangGraph `interrupt` [10] and Temporal signals
  [11] are two implementations. Approvals must show what will happen, not the model's summary of it.
- **The "lethal trifecta".** An agent that has (1) access to private data, (2) exposure to untrusted content and
  (3) a way to communicate externally can be made to exfiltrate data by injected instructions. Simon Willison named
  this combination [23] (blog, perspective). Break at least one leg per task.

Approval design at volume (approval budgets, approving plans rather than steps, rendering from structure) and Meta's Rule of Two, which generalises the
trifecta, are in [SYSDESIGN-31](31-securing-agentic-systems.md#approval-design-without-approval-fatigue).

### 10. Budgets and loop control

Every task carries budgets, enforced by the runtime and not by the prompt:

- **Steps** (max iterations), **tokens** (input + output, counted from API usage fields), **money** (tokens × price
  per model), **wall-clock** (deadline) and **per-tool timeouts**.
- **Loop detection:** the same tool with the same arguments N times, no new information for N steps, or oscillating
  between two states. On detection, inject a hint once, then stop with a partial result.
- **Graceful exhaustion:** when a budget runs out, return what was found plus "stopped: budget". Never crash
  silently and never keep going.

Per-tenant caps and defence against deliberate denial of wallet belong to the platform
([SYSDESIGN-33](33-agent-platform-runtime.md#7-budgets-and-cost-caps-defending-against-denial-of-wallet)).

## Numbers that matter

*Assumptions, labelled: base prompt (system + tool schemas) 3,000 tokens; each step adds 1,500 tokens (model
reasoning + tool result, truncated); 300 output tokens per step; 15 steps per task.*

**1. Tokens grow quadratically.** Input tokens at step `i` ≈ `base + (i−1)·Δ`. Summed over `N` steps:
`N·base + Δ·N(N−1)/2` = 15×3,000 + 1,500×105 = **202,500 input tokens** per task, plus 15×300 = 4,500 output tokens.
Doubling the steps to 30 gives 90,000 + 1,500×435 = 742,500 input tokens: **3.7× the tokens for 2× the steps**.
Mitigations: prompt/prefix caching (the stable prefix is cheap to re-send on servers with prefix caching,
SYSDESIGN-22), summarising old steps, and sub-agents with fresh contexts.

**2. Cost per task.** *Assume* a hosted model at $1.00 per million input tokens and $4.00 per million output tokens
(illustrative prices, not a quote). That gives 0.2025 × $1 + 0.0045 × $4 = **≈ $0.22** per 15-step task. 10,000
users × 3 tasks/day = 30,000 tasks/day ≈ **$6,600/day**. A runaway 100-step loop costs 100×3,000 + 1,500×4,950 ≈
7.7M input tokens plus 30,000 output tokens, about **$7.8** for one task. That is why budgets are a requirement, not a nicety.

*With provider prompt caching* (*assume* the Anthropic-style multipliers in Cost and energy: write 1.25×, read
0.1×, 5-minute TTL). Each step re-reads the previous prefix and writes only the new tokens. Writes are 3,000 +
14 × 1,500 = 24,000 tokens at $1.25/M = $0.030. Reads are the other 178,500 tokens at $0.10/M = $0.018. With output
($0.018), the task costs **≈ $0.066 instead of $0.22**. Tokens processed still grow quadratically. Dollars grow more
slowly, but only while the prefix stays cached. If a 20-minute approval pauses the task after step 10, the cache
has expired and step 11 re-writes its whole 18,000-token prefix: $0.0225 instead of about $0.0035. That one pause
adds about $0.02, nearly a third of the cached task's cost.

**3. Latency.** *Assume* 0.5 s time-to-first-token, 50 output tokens/s, 2 s average tool time. A step takes
0.5 + 300/50 + 2 = 8.5 s, so 15 steps take **≈ 2 minutes**. Users need progress streaming and a task model
(submit → poll/stream → result), not a blocking HTTP request. This is the serial worst case. If independent tool
calls are issued in parallel, wall-clock time falls (LLMCompiler reports up to 3.7× latency speedup over ReAct on its
benchmarks, see [SYSDESIGN-29](29-agent-architectures-orchestration.md#2-the-single-agent-loop-recapped)).

**4. Reliability compounds.** If each step independently succeeds with probability 0.98, a 15-step task succeeds with
0.98¹⁵ ≈ **0.74**, and a 30-step task with 0.98³⁰ ≈ **0.55**. Independence is a simplification, but the direction
is robust: long chains need checkpoints, retries per step and verification steps. τ-bench's **pass^k** metric (the
probability that *all* k trials succeed) measures this consistency directly [12].

**5. Sandbox load.** 30,000 tasks/day × 5 code runs = 150,000 sandbox starts/day ≈ **1.7/s average**. Assume a 5×
peak: ≈ 9/s. With each run at ≤ 512 MiB and ≤ 30 s, peak concurrency ≈ 9 × 30 = 270 sandboxes ≈ **135 GiB** of
sandbox memory at the limit. Plan pools and per-tenant concurrency caps.

**6. Checkpoint volume.** 30,000 tasks × 15 checkpoints × ~50 KB = **22.5 GB/day** of state. Set a retention
policy. Checkpoints contain user data (SYSDESIGN-19).

## Design choices and trade-offs

### Where does the loop run?

| Option | Wins when | Costs |
|---|---|---|
| In the request handler (synchronous) | Tasks < 30 s, few steps | Timeouts, lost work on deploys, no approvals |
| Background worker + queue + checkpoint store | Minutes-long tasks; simple ops | You build resume, idempotency and timers |
| Durable execution engine (Temporal etc.) | Hours-long tasks, approvals, strict exactly-once *effects* | Another platform; determinism constraints on workflow code |
| Managed agent platforms | Speed to market | Lock-in; less control over isolation and data residency |

At platform scale (thousands of runs, many tenants, schedules and events) the choice becomes a queueing and
fairness problem: see [SYSDESIGN-33](33-agent-platform-runtime.md).

### Tool integration

| Option | Wins when | Costs |
|---|---|---|
| In-process functions | Single app, few tools | No reuse; tools share the agent's privileges |
| MCP servers (stdio) | Local, per-user tools (IDE, desktop) | Process per server; local trust model |
| MCP servers (Streamable HTTP) behind a gateway | Shared, multi-tenant tools; central auth, quotas and audit | Network hop; another service to operate |
| A2A delegation | The capability is another team's or vendor's agent | Opaque behaviour; contractual trust; latency |

## Deep dive [Deep]

### Exactly-once *effects* in a non-deterministic loop

You cannot get exactly-once *execution* of a tool call across crashes. You can get exactly-once *effects*:

1. Before executing a side-effecting call, write `intent(step=7, tool=send_email, args_hash, idem_key)` to the
   checkpoint.
2. Call the tool with `idem_key`. The tool (or a proxy in front of it) deduplicates on the key (SYSDESIGN-08's
   idempotent consumer).
3. Write `result(step=7)`. On resume, a step with an intent but no result is *retried with the same key*. It is
   never re-planned by the model, which might choose different arguments the second time.

The subtle part is step 3's last clause. If you let the model "redo" the step after a crash, you get a *different*
non-deterministic decision. Recorded results are what make replay safe. That is the core idea behind durable
execution [11].

### Containing prompt injection with architecture

Filters on tool output are probabilistic, so containment has to be architectural. *Privilege separation*
(CaMeL-style) gives a planner only the trusted user request, lets a quarantined model read untrusted data without
calling tools, and tracks capabilities so untrusted values cannot reach sensitive sinks [18]. A plain agent loop
cannot track which value came from where, so taint the *session* instead: once a task has read untrusted content,
external-communication tools need approval. An allow-listing egress proxy in front of every sandbox and tool means
exfiltration needs an allowed destination. Measure all of it with injection suites such as AgentDojo [19] in CI.
SYSDESIGN-28 explains these patterns, and [SYSDESIGN-31](31-securing-agentic-systems.md) turns them into a threat
model, a containment architecture and a kill switch.

### Observability and evaluation

Give each task a trace: a root span, then child spans for each LLM call (model, tokens, latency, finish reason),
each tool call (name, arguments hash, duration, result size, error), approvals and checkpoints. OpenTelemetry's GenAI
semantic conventions define agent and tool spans (`invoke_agent`, `execute_tool`) and are still in **Development**
status (as of 2026-11) [9]. Many agent failures show only as strange trajectories (ten searches with the same query),
not as errors. Evaluate over many trials, with deterministic graders where possible, and report task success,
pass^k [12], and steps, tokens and cost per *successful* task. Public benchmarks only shortlist models: SWE-bench
Verified is now rated "Flawed" [29]. [SYSDESIGN-32](32-observing-evaluating-agents.md) owns trace design, sampling,
graders and regression gates.

## Frontier [Frontier]

*As of 2026-11; verify before relying on version specifics.*

- **Stateless MCP (2026-07-28)** makes tool servers horizontally scalable and gateway-friendly. Per-request
  method/name headers enable per-tool authorisation at the gateway [5]. Expect "MCP gateways" as a standard
  platform component. Kong's AI Gateway and Agent Router (formerly Envoy AI Gateway, now an AAIF project) both
  advertise MCP traffic management [24][25][41].
- **A2A v1.x** is in production integrations. The Linux Foundation reported 150+ adopting organisations in April
  2026 [26] (press release, a self-reported figure).
- **AAIF consolidation.** MCP, AGENTS.md and goose were founding projects [6]. AAIF's project list now also
  includes A2A and Agent Router, among others [41], which reduces the risk of single-vendor protocol capture.
- **Design-level injection defences** (CaMeL [18]) are moving from papers into runtimes. Watch for capability and
  taint tracking in agent frameworks.

## Failure modes and operations

| Failure | Detection | Mitigation |
|---|---|---|
| Infinite / repetitive loop | repeated (tool, args) hashes; steps without new tokens of information | loop detector; step and token budgets; partial result |
| Cost blow-up | spend per task vs cap; spend per tenant per hour | hard caps checked *before* each LLM call; alerts on p99 cost/task |
| Duplicate side effect after crash | idempotency-key collisions logged by tools | intent/result checkpointing; idempotent tools |
| Prompt injection via tool output | canary instructions in test docs; approval-required rate spikes | session taint; approvals; egress allow-list; privilege separation (SYSDESIGN-31) |
| Sandbox escape attempt / resource abuse | syscall denials, OOM kills, egress denials | gVisor or microVMs for untrusted code; per-tenant limits |
| Tool outage | tool error rate SLI per MCP server | timeouts, circuit breakers (SYSDESIGN-11); errors returned to the model as observations |
| Stuck approvals | age of pending approvals | reminders, expiry, auto-reject with notification |
| Model regression after an upgrade | task-suite success and pass^k in CI | pin model versions; canary rollout (SYSDESIGN-26, SYSDESIGN-32) |
| Context overflow | tokens per step near the window | summarisation; sub-agents; result truncation (SYSDESIGN-30) |

## Cost and energy

- Tokens processed per task scale ~N² with steps (dollars more slowly while the prefix stays cached). **Cutting
  steps is the biggest lever**: better tools (one call that does
  the right thing), better plans, smaller tool outputs.
- **Prefix caching** on self-hosted servers (SYSDESIGN-22), or provider prompt caching, makes the stable system and
  tool prefix cheap to resend. Keep it byte-stable (no timestamps at the top of the prompt, no per-step tool-list
  changes, see §2).
- **Provider caches have a write premium and a TTL** (as of 2026-11, varying by model). Anthropic bills a write at
  1.25× base input with the default 5-minute TTL (refreshed on each hit) or 2× for 1 hour, and a read at 0.1× on most
  models (0.05× on Opus 5.5 and Sonnet 5.5, 0.025× on Fable and Mythos 5.1 and 5.2) [30].
  OpenAI bills writes on GPT-5.6 and later at 1.25× (30 minutes) or 2.5× (12 hours) [31]. A prefix not reused before
  its TTL costs *more* than no caching, and a human wait longer than the TTL re-pays the write (Numbers #2).
  [SYSDESIGN-30](30-context-engineering-memory.md#1-the-context-window-is-a-budget-not-a-bucket) works through the
  mechanics.
- **Model routing:** use a small model for routine steps (extract, classify) and a large one for planning
  (SYSDESIGN-26).
- **Sandboxes cost memory-seconds.** Pool and reuse warm sandboxes *per tenant*, never across tenants.
- Report **cost per successful task**, not cost per call. A cheaper model that needs twice the steps, or fails more
  often, can be more expensive.

## Interview angle

**How it is asked:** "Design an AI agent that can operate our internal tools", "Design a coding-agent platform"
(case C11), "How do you stop an agent from running up a $10k bill?", "How would you make an agent safe to send
emails?"

**Model answer outline (CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP):**
1. **CLARIFY:** task types and length, tools and their risk tiers, who approves, tenancy, latency expectations
   (interactive vs background), audit requirements.
2. **QUANTIFY:** steps per task → tokens (quadratic) → cost/task and cost/day; sandbox concurrency; checkpoint
   volume.
3. **SKETCH:** API (submit task → stream progress → result), queue, agent workers on a durable runtime, LLM gateway,
   MCP tool servers behind a tool gateway, sandbox pool, checkpoint store, approval service, trace store.
4. **DEEPEN:** exactly-once effects with intents and idempotency keys, *or* sandbox isolation choice, *or*
   permission model and approvals.
5. **STRESS:** worker crash mid-email, injected instructions in a fetched page, a 100-step loop, a tool outage, a
   model upgrade.
6. **WRAP:** budgets enforced by the runtime, least privilege per task, human approval for irreversible actions
   and for writes other people can read, evaluation suite in CI.

**Red flags:** "the prompt tells it not to do X" as a control; one admin service account for all tools; no budgets;
running generated code on the app server; retrying a step by re-asking the model; no trace of tool calls.

**Follow-ups:** How do you test an agent (SYSDESIGN-32)? MCP vs A2A? Where do you put the approval UI's source of truth? How do
you resume after a deploy? How would you cap cost per tenant?

## Common mistakes

- Building a multi-agent hierarchy when a single agent (or a fixed workflow) meets the requirement (SYSDESIGN-29).
- Letting the model see secrets (API keys in the prompt or in the sandbox environment).
- Counting budgets in the prompt instead of in the runtime.
- Returning megabytes of tool output into the context.
- Treating MCP servers as "just plugins" without auth, quotas and SLOs.
- Approvals that show the model's paraphrase instead of the exact action.
- Evaluating with a single run per task. Agents are stochastic, so measure pass^k or success rates over trials
  (SYSDESIGN-32).

## Check yourself

1. Why do input tokens grow quadratically with steps, and name two mitigations.
2. A worker crashes after `send_email` returned but before the checkpoint was written. What happens on resume in
   your design?
3. What changed in MCP 2026-07-28 that matters for load balancing?
4. When would you choose a microVM over a container for code execution?
5. Give a concrete instance of the "lethal trifecta" in Lumen and break one leg.

Full set with answers: [exercises/25-agentic-systems.md](../../exercises/25-agentic-systems.md).

## Lab

[labs/25-agentic-systems](../../labs/25-agentic-systems/README.md). A minimal agent loop in plain Python talks to a
small local model (Qwen2.5-0.5B-Instruct served by llama.cpp's OpenAI-compatible server in docker compose, project
`sd-25`). It discovers tools from an **MCP server** (official Python SDK, stdio transport) and runs model-written
Python in a **locked-down container sandbox** (`--network none`, read-only root, memory, CPU, PID limits, timeout).
It enforces **step, token, wall-clock and per-tool budgets**, detects repeated calls, and requires **human approval**
for a side-effecting tool. A deterministic scripted-model mode lets you test the runtime without a model. No paid
API keys are needed.

**What one recorded run showed** (2026-11-20, details in the lab's Test status). Sandboxed code could not open a
network connection or write to `/`, ran as uid 65534, and an infinite loop was killed at the 10 s wall-clock limit.
A crash after `send_email` but before the checkpoint, followed by a resume, produced exactly one email ("duplicate
suppressed"). The 0.5B model sometimes emitted truncated tool-call JSON. Until the runtime dropped such calls from
the history, the model server rejected every later turn. Robustness to malformed model output is a runtime
requirement.

## Further reading

- Yao et al., ReAct [1]: the loop everything else builds on.
- MCP specification 2026-07-28 and its release post [3][5]: read the changelog, especially statelessness and auth.
- A2A specification v1.0 [8]: Agent Cards, Tasks and Artifacts.
- Temporal docs on workflow execution [11]: the mental model for durable agents.
- Greshake et al. [17] and Debenedetti et al., CaMeL [18]: why injection is an architecture problem.
- OWASP Excessive Agency (LLM03:2026, formerly LLM06:2025) [28][21]: a checklist for tool permissions.
- Yao et al., τ-bench [12]: pass^k and why single-run evaluation misleads.

## References

1. Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023. arXiv:2210.03629. https://arxiv.org/abs/2210.03629 (accessed 2026-11)
2. Schick, T. et al. "Toolformer: Language Models Can Teach Themselves to Use Tools." NeurIPS 2023. arXiv:2302.04761. https://arxiv.org/abs/2302.04761 (accessed 2026-11)
3. Model Context Protocol. "Versioning" (current revision 2026-07-28). https://modelcontextprotocol.io/docs/2026-07-28/learn/versioning (accessed 2026-11)
4. Model Context Protocol. Specification, revision 2026-07-28 (server features: tools, resources, prompts). https://modelcontextprotocol.io/specification/2026-07-28 ; https://modelcontextprotocol.io/specification/2026-07-28/server/tools (accessed 2026-11)
5. MCP maintainers. "MCP 2026-07-28" release post (stateless core, Tasks extension, deprecations, authorization changes). https://blog.modelcontextprotocol.io/posts/2026-07-28/ (accessed 2026-11)
6. Linux Foundation. "Linux Foundation Announces the Formation of the Agentic AI Foundation" (press release, 9 Dec 2025). https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation (accessed 2026-11)
7. A2A project. Releases v1.0.0 (2026-03-12), v1.0.1 (2026-05-28, latest); tag `v1.1.0-rc` (commit 2026-10-29, no published release). https://github.com/a2aproject/A2A/releases ; https://github.com/a2aproject/A2A/tags (accessed 2026-11)
8. A2A project. Documentation and "Key concepts". https://a2a-protocol.org/latest/ ; https://a2a-protocol.org/latest/topics/key-concepts/ ; specification v1.0.0 (§3.6.1 version header; §§9–12 JSON-RPC, gRPC, HTTP+JSON/REST and custom bindings) https://a2a-protocol.org/latest/specification/ (accessed 2026-11)
9. OpenTelemetry. GenAI semantic conventions (agent spans, execute_tool, MCP, A2A), status Development. https://github.com/open-telemetry/semantic-conventions-genai (accessed 2026-11)
10. LangChain. LangGraph "Persistence" and "Interrupts" docs (LangGraph 1.2.x). https://docs.langchain.com/oss/python/langgraph/persistence ; https://docs.langchain.com/oss/python/langgraph/interrupts (accessed 2026-11)
11. Temporal. "Workflow Execution" and "Understanding Temporal". https://docs.temporal.io/workflow-execution ; https://docs.temporal.io/evaluate/understanding-temporal (accessed 2026-11)
12. Yao, S., Shinn, N., Razavi, P., Narasimhan, K. "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains." arXiv:2406.12045 (2024). https://arxiv.org/abs/2406.12045 (accessed 2026-11)
13. Jimenez, C. E. et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" ICLR 2024. arXiv:2310.06770. https://arxiv.org/abs/2310.06770 (accessed 2026-11)
14. Princeton NLP / SWE-bench team. "SWE-bench Verified" dataset card (500 human-validated tasks). https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified ; leaderboard https://www.swebench.com/ (accessed 2026-11)
15. gVisor documentation. https://gvisor.dev/docs/ (accessed 2026-11)
16. Agache, A. et al. "Firecracker: Lightweight Virtualization for Serverless Applications." NSDI 2020. https://www.usenix.org/conference/nsdi20/presentation/agache (accessed 2026-11)
17. Greshake, K. et al. "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." AISec 2023. arXiv:2302.12173. https://arxiv.org/abs/2302.12173 (accessed 2026-11)
18. Debenedetti, E. et al. "Defeating Prompt Injections by Design" (CaMeL). arXiv:2503.18813 (2025). https://arxiv.org/abs/2503.18813 (accessed 2026-11)
19. Debenedetti, E. et al. "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents." NeurIPS 2024 Datasets & Benchmarks. arXiv:2406.13352 (accessed 2026-11)
20. Anthropic. "Building effective agents" (engineering blog, 19 Dec 2024; the page notes that much of the tooling landscape it describes has changed since December 2024; perspective). https://www.anthropic.com/engineering/building-effective-agents (accessed 2026-11-20)
21. OWASP GenAI Security Project. "LLM06:2025 Excessive Agency." https://genai.owasp.org/llmrisk/llm062025-excessive-agency/ (accessed 2026-11)
22. Firecracker project. `SPECIFICATION.md` (≤ 125 ms to guest user space with a minimal kernel and root filesystem; VMM overhead ≤ 5 MiB for 1 vCPU and 128 MiB, workload-dependent). https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md (accessed 2026-11-20)
23. Willison, S. "The lethal trifecta for AI agents" (blog, 16 Jun 2025; perspective). https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ (accessed 2026-11)
24. Kong. "AI Gateway" documentation (LLM, MCP and A2A traffic). https://developer.konghq.com/ai-gateway/ (accessed 2026-11)
25. Agent Router (formerly Envoy AI Gateway), README, v1.3.0. https://github.com/theagentrouter/agent-router (accessed 2026-11)
26. Linux Foundation. "A2A protocol surpasses 150 organizations…" (press release, Apr 2026). https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year (accessed 2026-11)
27. Model Context Protocol. "Deprecated Features" registry, revision 2026-07-28 (HTTP+SSE deprecated in 2025-03-26). https://modelcontextprotocol.io/specification/2026-07-28/deprecated (accessed 2026-11)
28. OWASP GenAI Security Project. "OWASP Top 10 for LLM Applications 2026" (LLM03:2026 Excessive Agency), 2026-08-04. https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/ (accessed 2026-11)
29. Epoch AI. "SWE-bench Verified" benchmark review (verdict "Flawed"; summarises OpenAI's 2026-02-23 audit "Why we no longer evaluate SWE-bench Verified"), 2026-09-03. https://epoch.ai/benchmarks/swe-bench-verified/review (accessed 2026-11)
30. Anthropic. "Prompt caching" (TTL, write and read multipliers by model, invalidation, `inline-tools-2026-09-15` beta) and "Tool use with prompt caching" (`defer_loading`). https://platform.claude.com/docs/en/build-with-claude/prompt-caching ; https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching (accessed 2026-11)
31. OpenAI. "Prompt caching" guide (retention, write multipliers for GPT-5.6+, tools in the cached prefix, `allowed_tools`, `additional_tools`). https://developers.openai.com/api/docs/guides/prompt-caching (accessed 2026-11)
32. Model Context Protocol. Specification 2026-07-28, "Authorization" (optional, RFC 9728, RFC 9207 `iss` rules, CIMD, DCR deprecated). https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization (accessed 2026-11)
33. Model Context Protocol. Specification 2026-07-28, "Streamable HTTP", Request Metadata (`Mcp-Method`, `Mcp-Name`, `HeaderMismatch`). https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http (accessed 2026-11)
34. Temporal documentation, Temporal Cloud limits page (2 MB payload, 4 MB gRPC message, event history 51,200 events / 50 MB, external storage for large payloads) and Workflow Execution limits page. https://docs.temporal.io/cloud/limits ; https://docs.temporal.io/workflow-execution/limits (accessed 2026-11)
35. Temporal documentation, Workflow Execution events page (execution terminated past 51,200 events; Continue-As-New). https://docs.temporal.io/workflow-execution/event (accessed 2026-11)
36. Invariant Labs. "GitHub MCP Exploited: Accessing private repositories via MCP" (blog, 2025-05-26). https://invariantlabs.ai/blog/mcp-github-vulnerability (accessed 2026-11)
37. gVisor documentation. "Security Model" (architecture guide). https://gvisor.dev/docs/architecture_guide/security/ (accessed 2026-11-20)
38. Firecracker project. "Production Host Setup Recommendations" (`docs/prod-host-setup.md`: hardware vulnerabilities, SMT, jailer, seccomp, metadata-service rule). https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md (accessed 2026-11-20)
39. Docker documentation. "Docker Engine security" (namespaces, cgroups, capabilities). https://docs.docker.com/engine/security/ (accessed 2026-11-20)
40. Anthropic. "Tool use with Claude" (client tools run in your application, server tools on Anthropic's infrastructure). https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview (accessed 2026-11-20)
41. Agentic AI Foundation. "Projects" (lists Agent2Agent, Agent Router "built on Envoy", AGENTS.md, goose, MCP and others). https://aaif.io/projects (accessed 2026-11-20)
