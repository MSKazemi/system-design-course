# 29 — Agent architectures & orchestration (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- Five Lumen features: contract Q&A, invoice reconciliation, vendor research, code migration, ticket triage
- Vendor brief: under 2 minutes, under $0.50 (assumed targets)
- Triage under 2 s; reconciliation auditable step by step
- Question per feature: workflow, one agent, or a team?

**Visual:** five feature cards, each with an empty "shape" slot; icons `ai-agent`, `ops-latency`, `ops-cost`.
**Speaker notes:** The architecture choice multiplies tokens, latency, failure points and lock-in at once. Anthropic
reports its multi-agent research system used about 15× the tokens of a chat interaction, so the choice is not free.

## Slide 2 — Workflow versus agent
- Workflow: you write the control flow, the model fills steps
- Agent: the model chooses the next step at run time
- Five questions: steps known? error cost? latency? budget? independent read-heavy parts?
- Only one of Lumen's five features needs a team

**Visual:** the decision-tree flowchart from the lesson (10 nodes).
**Speaker notes:** Anthropic's definitions: workflows orchestrate LLMs "through predefined code paths", agents
"dynamically direct their own processes". Most features sit on the workflow side.

## Slide 3 — Five workflow building blocks
- Prompt chaining: fixed sequence
- Routing: one decision, one path
- Parallelisation: sectioning or voting
- Orchestrator-workers and evaluator-optimiser

**Visual:** five mini-diagrams in a row; icons `arch-router`, `pattern-fan-out`, `pattern-fan-in`, `ops-check`.
**Speaker notes:** Orchestrator-workers is the boundary pattern. The decomposition is agentic, the fan-out is a
workflow run by code.

## Slide 4 — Multi-agent patterns
- Router, supervisor (agents as tools), handoff
- Hierarchical, graph/state machine, blackboard
- Two questions: who picks the next actor, who owns the context?
- Debate and voting multiply tokens by agents × rounds

**Visual:** the four-topology flowchart from the lesson (router, supervisor, handoff, blackboard).
**Speaker notes:** The blackboard idea dates from HEARSAY-II and Nii's 1986 survey. A shared board is shared mutable
state, so it needs concurrency control. Debate is not a safe default: one benchmark found debate protocols do not
reliably beat self-consistency or ensembling.

## Slide 5 — Handoff versus agents-as-tools
- Agents as tools: control returns, callee sees only the brief, a digest comes back
- Handoff: control transfers, by default the new agent sees the whole history
- Thin briefs cause misread tasks, full history carries confusion forward
- Briefs need objective, output format, tools and sources, boundaries

**Visual:** two-column comparison table; arrows for control flow.
**Speaker notes:** OpenAI's Agents SDK exposes handoffs as `transfer_to_<agent>` tools. Anthropic found vague briefs
made subagents duplicate each other's work.

## Slide 6 — Isolation beats the quadratic
- Single agent, 41 steps: ≈ 1.35 M input tokens, ≈ $1.41
- 8 isolated workers (same 40 research steps) + lead: ≈ 0.34 M input tokens, ≈ $0.43
- The single agent re-reads vendor 1 while researching vendor 8
- A team is more expensive only when it does more work

**Visual:** two stacked bars of tokens processed (1.37 M versus 0.36 M); icons `ai-tokens`, `ops-cost`.
**Speaker notes:** All numbers are from the lesson's labelled assumptions ($1 / $4 per million, illustrative). The
saving (about 3.3×) comes from removing cross-vendor history, not from magic. Compare equal work: each worker does 5
research steps plus a digest step.

## Slide 7 — Caching narrows the gap
- Write 1.25×, read 0.1×, 5-minute TTL (Anthropic-style, check your provider)
- Single agent ≈ $0.26, team ≈ $0.21–0.23
- Gap shrinks from ≈ 3.3× to ≈ 1.1–1.3×
- Parallel calls only hit the cache after the first response starts

**Visual:** before/after bar pairs, uncached versus cached; icon `arch-cache`.
**Speaker notes:** Choose a team for latency and context limits, not for dollars alone. Output tokens are not
discounted and become nearly 40% of the team's bill. The 3,000-token prefix must also meet the model's minimum
cacheable length.

## Slide 8 — Latency is the critical path
- Serial agent ≈ 381 s
- Plan 10.5 s + slowest worker 63 s + synthesis 40.5 s ≈ 114 s (6 s margin)
- Stragglers and a synchronous lead set the floor
- Parallel tool calls: LLMCompiler up to 3.7× on its benchmarks

**Visual:** the orchestrator-workers sequence diagram with a `par` block.
**Speaker notes:** Anthropic notes its lead agents run subagents synchronously and that this creates bottlenecks.
Give each worker a deadline and accept marked partial results.

## Slide 9 — What the published data says
- Anthropic: single agent ≈ 4× chat tokens, multi-agent ≈ 15×, +90.2% on internal eval
- Token usage explains 80% of BrowseComp variance
- Google study: +80.9% on parallelisable finance, −39% to −70% on sequential planning
- Error amplification 17.2× independent versus 4.4× centralised

**Visual:** table of sourced figures with source labels; icon `ai-evaluation`.
**Speaker notes:** "15×" is against chat, not against a single agent doing the same job. Cite the version of the
Google work: the blog says 180 configurations, the v3 abstract 260.

## Slide 10 — Writes stay single-threaded
- Many agents may read, search, review, plan
- One agent, or code, writes the artefact
- C compiler: 16 agents overwrote each other until work was re-partitioned
- Verify outside the generator's context

**Visual:** several reader agents feeding one writer; a reviewer with its own context; icons `ai-agent`, `ops-check`.
**Speaker notes:** Cognition's 2026 follow-up states the rule. Anthropic's harness found agents "reliably skew positive
when grading their own work", so a separate evaluator pays.

## Slide 11 — Failure modes
- Error compounding: one wrong digest, one confident wrong report
- Context loss at handoffs; coordination loops; over-spawning (50 subagents)
- Premature completion; lenient reviewer; stragglers; deploy mid-run
- MAST: 14 modes, 3 categories, 1,600+ traces

**Visual:** failure table; icons `ops-error`, `ops-tracing`.
**Speaker notes:** Many of these look like success in metrics. Trace the whole agent tree and read trajectories
(SYSDESIGN-32).

## Slide 12 — Who executes the call?
- Client tools: your runtime runs them, so your policy point applies
- Hosted tools: the provider runs them during the model request
- Managed harnesses run the whole loop provider-side
- Check approvals, logging, egress, residency before enabling

**Visual:** two lanes, "your runtime" and "provider runtime", with tool calls placed in each; icons `arch-policy-engine`, `arch-cloud`.
**Speaker notes:** The model itself only emits text. With hosted tools someone else's runtime executes, and it joins
your trust boundary (SYSDESIGN-31).

## Slide 13 — Frameworks and lock-in, as of 2026-11
- LangGraph 1.2.24, OpenAI Agents SDK 0.25.0, Google ADK 2.15.0, CrewAI 1.15.44, Claude Agent SDK 0.2.186
- AutoGen README: archived, successor Microsoft Agent Framework; AG2 continues as a community project
- ADK deprecated its Sequential/Parallel/Loop agents in Python and TypeScript for graph workflows
- Own: state schema, prompts, MCP tools, OTel traces, gateway, budgets

**Visual:** dated landscape table (no ranking); icons `ai-langgraph`, `ai-openai`, `ai-gemini`, `ai-anthropic`, `ai-mcp`.
**Speaker notes:** This is a record of what exists, not a bake-off. The portability boundary decides what a migration
costs.

## Slide 14 — Interview angle
- CLARIFY: steps known? writes? latency and budget?
- QUANTIFY: quadratic versus isolated, critical path, caching, reliability
- SKETCH: least agentic design first; DEEPEN: brief/digest contract or verification
- STRESS and WRAP: caps in code, single writer, cost per successful task

**Visual:** the six-step framework strip.
**Speaker notes:** Red flag: "multi-agent because it is modern". Strong answers compare architectures with numbers and
name the condition under which the team pays off.
