# C15 — Customer-support agent platform (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- 3,000 businesses run support agents on chat and email, 12 languages
- Answers from help content; orders, address changes, refunds up to a per-business limit
- Handoff to the business's human team; cost per resolved conversation
- 400,000 conversations a day
**Visual:** customer chat bubble → agent → order, refund and human-agent cards. Icons: `domain-chat`, `ai-agent`, `domain-payment`, `arch-users`.
**Speaker notes:** The agent spends other people's money for a customer it must first identify, in a multi-tenant system.

## Slide 2 — CLARIFY and rank
- How is the end customer authenticated? Who sets refund limits? What counts as resolved?
- Rank: wrong-action rate > tenant isolation > handoff quality > containment > latency > token cost
- Out of scope: voice, training, the helpdesk itself
**Visual:** ranked list with the top two highlighted. Icons: `ops-check`, `security-authorization`.
**Speaker notes:** The authentication answer decides most of the authorisation design.

## Slide 3 — QUANTIFY load
- ≈ 13.9 conversations/s at peak; ≈ 3,500 concurrent chats (Little's law, 6 min)
- ≈ 240 k open email threads: state, not compute
- 15 model calls per conversation → ≈ 210 calls/s at peak
**Visual:** Little's law triangle; a database icon for email threads. Icons: `ops-throughput`, `arch-database`.
**Speaker notes:** None of this needs GPUs; the model is a dependency behind a gateway.

## Slide 4 — QUANTIFY cost
- 120 k input, 3.75 k output tokens per conversation
- Placeholder prices, 60 % cached, write premium → ≈ $0.08 model, ≈ $0.10 total
- ≈ $40 k/day; ≈ $0.17 per resolved conversation
**Visual:** small stacked bar: cached, uncached, output, guardrails. Icons: `ops-cost`, `ai-tokens`.
**Speaker notes:** Email turns hours apart miss the 5-minute cache and re-write the 5 k prefix: about $0.006 a turn, roughly $4 k/day or 10 % on top. Keep the tenant's prefix byte-identical so steady chat traffic keeps it warm.

## Slide 5 — The containment equation
- saving = H − [T + (1 − c)(1 − s)H + eL]
- e = writes per conversation × wrong rate per write = 0.15 × 0.2 % (assumptions)
- Baseline ≈ $2.61 per conversation
- Containment −10 points costs $0.32; the handoff summary is worth $0.32; doubling tokens costs $0.10
- Wrong actions × 10 cost only ≈ $0.08 on average: their danger is the tail, not the mean
**Visual:** tornado chart of the four sensitivities. Icons: `domain-analytics`, `ops-cost`.
**Speaker notes:** Keep the denominators straight: the NFR is per executed write, and most conversations have none. Containment and handoff dominate the average; wrong actions earn their top rank through exposure, repetition of a bad policy and liability, so they are bounded by construction.

## Slide 6 — Exposure sets the limits
- 5 % refund intents × $50 → $1 M/day worst case across tenants
- Per customer: 2 automatic refunds per 30 days → $100 max
- Per tenant: daily automatic budget plus a rate circuit breaker
- The breaker catches bursts; a paced attack under 3× baseline is bounded by the daily budget and the caps
**Visual:** funnel from worst case to capped exposure. Icons: `domain-payment`, `pattern-circuit-breaker`.
**Speaker notes:** The per-refund limit alone does not bound an injection campaign or a fraud ring, and the breaker alone does not bound a patient one.

## Slide 7 — SKETCH
- Channel gateway → identity → single-writer conversation service → stateless agent runtime
- Tool broker → policy engine → tenant connectors
- Handoff to the helpdesk; event log feeds evals and audit
**Visual:** the lesson flowchart. Icons: `arch-api-gateway`, `arch-policy-engine`, `ai-llm-gateway`, `arch-audit-log`.
**Speaker notes:** The durable unit is the turn plus pending actions, not a workflow per conversation.

## Slide 8 — Authorisation per end user
- Identity levels L0–L3; money needs a fresh step-up
- The broker binds the customer to every call; the model only proposes ids
- Delegated tokens name customer and agent (RFC 8693 `act`); MCP tokens audience-bound
- One fixed tool list in the cached prefix; the broker enforces the level (changing tools breaks the cache)
**Visual:** ladder of identity levels with allowed actions. Icons: `security-auth`, `security-token`, `ai-mcp`.
**Speaker notes:** If the model chooses the customer id, any customer can read any order.

## Slide 9 — Agent proposes, policy disposes
- Deterministic decide(): identity, eligibility, limits, cumulative caps, breaker
- Fail closed for writes; reads and help answers continue
- Commitment check: no promise in text without an executed or approved action
**Visual:** decision table with allow / approval / handoff / deny outcomes. Icons: `arch-policy-engine`, `ops-human-approval`.
**Speaker notes:** A tribunal held Air Canada responsible for its chatbot's promise; what the agent says, the business said.

## Slide 10 — Grounded answers
- One logical index per tenant; tenant id from the auth context, never the model
- Structured policy beats article prose; disagreements reported to the tenant
- Per-article kill switch; find affected conversations by citation
**Visual:** tenant-partitioned index with a red-flagged article. Icons: `ai-vector-db`, `domain-document`.
**Speaker notes:** Cross-tenant retrieval is a platform bug, not a prompt problem.

## Slide 11 — Escalation and handoff
- Rule triggers: asked for a person, policy said so, two failed tools, sensitive topics
- Handoff payload: identity level, intent, actions taken, pending actions, summary
- One writer per conversation (lease); honest wait times; 2.5× surge if all fail over
**Visual:** conversation passing from agent to human with a lease token. Icons: `arch-user`, `domain-ticket`, `arch-queue`.
**Speaker notes:** "Fail open to humans" during an outage is not a plan; the humans do not exist.

## Slide 12 — Evaluate and roll out
- Replay with simulated customers, grade the final state (τ-bench style), pass^k
- 0.95 per run → all 8 of 8 runs succeed only ≈ 0.66 of the time
- Autonomy ladder per intent: shadow (read-only or mocked tools) → assist → supervised → autonomous
- Approval fatigue: track approval rate and dwell per approver; ≈ 100 % in seconds is a failed control
- Audit samples: ≈ 10 k actions for ±0.09 points at 0.2 %
**Visual:** ladder with promotion metrics on each rung. Icons: `ai-evaluation`, `ops-deploy`, `ops-metrics`.
**Speaker notes:** Order tracking reaches autonomous first; refunds last, and some tenants stop at supervised.

## Slide 13 — STRESS and ×10
- Injection in order notes, social engineering, refund storm, wrong article, provider outage
- Tenant outage spike: per-tenant caps and fair queueing
- ×10: model capacity procurement, trace sampling, cells per tenant group
**Visual:** failure grid with mitigations. Icons: `security-prompt-injection`, `ops-incident`, `arch-cell`.
**Speaker notes:** At ten times the volume, containment improvements matter more than infrastructure.

## Slide 14 — WRAP
- Junior: chat + RAG + a few tools + transfer button
- Senior: verified identity, broker binding, limits in code, idempotent refunds, rule escalation, staged rollout
- Staff: containment and exposure maths, caps plus breaker, approval-fatigue metrics, commitment checks, fail-closed plan sized against humans, pass^k, autonomy ladder, cells, disclosure
- Red flags: model picks customer or amount; "escalate when not confident"; limits in the prompt
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** Close with the containment equation and the three controls that bound exposure.
