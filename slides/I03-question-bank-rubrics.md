# I03 — Question bank & rubrics (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The bank at a glance
- 90 original prompts in 7 categories
- Each: prompt, what it tests, key trade-offs, course units, four-outcome rubric
- Levels J (junior) → P (principal); by entry level: 15 J · 21 M · 48 S · 6 St
- Junior track: 15 questions (two agentic) with a narrowed junior scope and a junior-hire anchor
**Visual:** seven category tiles with counts (CL 16, DI 10, RT 10, IP 11, AI 13, AG 21, SC 9).
**Speaker notes:** Classic domains such as chat or short links are universal. The framings, twists and rubrics here are
written for this course.

## Slide 2 — The six-dimension rubric
- Framing · Quantitative · Architecture · Depth · Resilience & operations · Communication
- Each dimension maps to one framework step
- Score 1–4: No hire / Lean / Hire / Strong hire
**Visual:** 6 × 4 grid with one anchor phrase per cell.
**Speaker notes:** No company publishes its internal rubric. This is a practice tool synthesized from public guidance
and the I01 signals.

## Slide 3 — Level calibration
- Junior: ≥ 2 on all, 3 on architecture with help, coachable under hints (use the junior scope)
- Mid: ≥ 3 on framing, numbers and architecture
- Senior: ≥ 3 on all, at least one 4 (usually depth)
- Staff: 4 on framing or numbers and on resilience or depth
**Visual:** level ladder with the minimum profile per rung.
**Speaker notes:** The same prompt can be asked at every level. The anchors move, the prompt does not.

## Slide 4 — Classical and data-intensive
- CL: short links, rate limiter, timelines, chat, video, proximity, payments, KV store, crawler …
- DI: ad-click aggregation, metrics, logs, lakehouse, CDC, GDPR erasure, multi-tenant DB …
- What separates hire from strong hire: edge cases (unknown outcomes, late events, deletion)
**Visual:** two columns of prompt titles. Icons: `domain-link`, `domain-feed`, `domain-chat`, `domain-payment`, `arch-data-warehouse`.
**Speaker notes:** Notice how often strong-hire signals involve an outcome you cannot observe directly, such as an
unknown payment state or a late event.

## Slide 5 — Real-time and platform
- RT: collaborative editing, live scores, fraud scoring, matching engine, webhooks …
- IP: progressive delivery, gateway, active-active migration, flags, GPU observability, cost attribution, carbon-aware scheduling
- Platform prompts reward "platform as a product" thinking
**Visual:** two columns. Icons: `protocol-websocket`, `ops-deploy`, `pattern-autoscaling`, `ops-cost`.
**Speaker notes:** For platform prompts, adoption and safety of change are as important as throughput.

## Slide 6 — AI/LLM and agentic
- AI: chat service, RAG, gateway, multi-LoRA, GPU scheduler, semantic cache, vector search, evals, fine-tuning, recsys, moderation, voice, registry
- AG (21): coding agents, MCP tool gateway, durable execution, memory, support agent, browser fleet, multi-agent budgets, replay, plus runaway spend, unknown outcomes, injection containment, eval gates, approvals, sandboxes, cross-org delegation, single vs multi-agent, long contexts, multi-day workflows, data analyst; junior on-ramp: a two-tool help-chat agent, ticket triage as a workflow
- Common no-hire: model as a stateless service; agents with broad credentials
**Visual:** two columns. Icons: `domain-ai`, `domain-bot`, `arch-containers`.
**Speaker notes:** I04 goes deeper on eight of these, with four fully worked answers, including a support agent.
Agentic questions also carry Numbers to expect, Red flags and Follow-ups lines.

## Slide 7 — Security and compliance
- Auth, audit log, EU-resident AI platform, tenant isolation, provenance, PII redaction, prompt injection, bot defense, tenant keys
- Increasingly asked as twists on classical prompts
**Visual:** shield with nine labels. Icons: `security-auth`, `security-key`, `security-lock`, `security-encryption`.
**Speaker notes:** A good habit: for any prompt, ask how residency or tenant isolation would change it.

## Slide 8 — Anatomy of a question rubric (CL-12)
- No hire: synchronous send in the producer's request
- Lean: a queue but no priority isolation
- Hire: priority lanes, cached preferences, dedup, per-channel breakers
- Strong hire: unknown-outcome sends, quiet hours with jitter, SMS cost as a constraint
**Visual:** four stacked cards from No hire to Strong hire. Icons: `domain-notification`.
**Speaker notes:** Compare with the I01 mock, which demonstrates every strong-hire signal on this card.

## Slide 9 — Ten red flags
- Designing before clarifying; boxes without reasons; unused or wrong numbers
- "Exactly-once" without mechanism; unacknowledged single points of failure
- "Add replicas"; ignoring redirects; bluffing facts; LLM as a stateless microservice
**Visual:** checklist with crosses. Icons: `ops-warning`.
**Speaker notes:** Each red flag has a cheap fix described in I01.

## Slide 10 — Ten strong signals
- Ranked NFRs; the shaping constraint found early; numbers → decisions
- Every box justified; four-part trade-offs; depth two levels down
- Detection with every mitigation; true ×10 bottleneck; knows what not to build; clear summary
**Visual:** checklist with ticks. Icons: `ops-check`.
**Speaker notes:** The signals mirror the red flags. Most are habits you can practice deliberately.

## Slide 11 — 4-week plan
- W1 method and numbers · W2 classical depth · W3 AI-era systems · W4 your target mix
- 2–4 timed mocks per week, scored with the rubric
- Agent roles: week 4 skims 29 and 31, reads C15, and runs AG-05, AG-09, AG-12, AG-16
- ≈ 8–11 h per week, computed from unit reading times (skim = 1 h, mock = 1 h)
**Visual:** four-week timeline with unit codes. Icons: `ops-calendar`.
**Speaker notes:** For people already working on distributed systems. Each week's hours are the sum of unit reading
times, 1 h per skimmed unit and 1 h per mock with scoring. If time is short, drop skims, never mocks.

## Slide 12 — 8-week plan
- Foundations (W1–W5), modern requirements (W6), AI (W7), agents and governance (W8)
- Optional week 9 for agent-heavy roles: skim 29–33, read C15, C16 or C17, three AG mocks (≈ 10 h)
- Staff+ add-on: a five-minute "evolution" segment in every mock
- ≈ 15–25 questions, 5–8 repeated with twists
- ≈ 8.5–11 h per week; many chapters are skimmed, not read in full
**Visual:** eight-week timeline. Icons: `ops-calendar`.
**Speaker notes:** All 90 questions would take 67.5 hours of mocks, and the plan has 20 mock slots (23 with week 9). Choose by
category and level, and go deeper on fewer.

## Slide 13 — Agentic questions: numbers, red flags, follow-ups
- Every AG question adds three lines: Numbers to expect, Red flags, Follow-ups
- Numbers: doubling steps from 40 to 80 costs ≈ 3.9× the input (AG-09); refund exposure = volume × limit (AG-05)
- Gates: a 200-task suite is ±4.9 points; a 3-point drop needs ≈ 870 paired tasks if 10 % of tasks change outcome between versions (AG-12)
- Warm pools from the prompt's own numbers: 8,000 sandboxes ÷ 20 min ≈ 6.7 claims/s × 20 s refill ≈ 133 ready (AG-14)
- Recurring no-hire: the model, not deterministic code, holds the limit, the identity or the credential
**Visual:** one AG-09 question card with its three new lines highlighted; a quadratic token curve beside it. Icons: `ai-agent`, `ops-budget`, `ai-evaluation`.
**Speaker notes:** The numbers come from chapters 29–33 and cases C15–C17, which each question links. When you run
these as an interviewer, the Follow-ups line gives ready-made constraint changes, and the Red flags line tells you what
to write down.
