# C17 — Enterprise workflow-automation agent (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- Agent runs procure-to-pay and IT-service workflows across ERP, CRM, IT desk, email
- Approvals take days; segregation of duties; full audit
- 500 enterprises, 20,000 runs a day, ≈ 40,000 in flight
**Visual:** request card → plan → approver → ERP, CRM, email icons. Icons: `ai-agent`, `ops-human-approval`, `arch-data-warehouse`, `domain-email`.
**Speaker notes:** The run outlives every process, deploy and token it uses.

## Slide 2 — CLARIFY and rank
- Which APIs support idempotency or unique references? Which steps are reversible?
- Who approves, and what happens when they are away? Run length vs deploy frequency?
- Rank: correctness of effects > authorisation and SoD > audit > durability > latency > cost
**Visual:** ranked list. Icons: `ops-check`, `security-authorization`.
**Speaker notes:** A slow run is fine; a payment made twice is an audit finding.

## Slide 3 — QUANTIFY in-flight state
- Little's law on elapsed time: 0.23 runs/s × 2 days ≈ 40 k in flight
- Waiting costs storage, not compute: workers use nothing while a timer waits
- Model ≈ 72 k tokens and ≈ $0.22 per run (placeholder prices; ≈ $0.14 at unit 33's Sonnet 5.5 prices)
**Visual:** many small sleeping run icons on a timeline. Icons: `ops-clock`, `devops-temporal`, `ops-cost`.
**Speaker notes:** The model is the cheap part of this system.

## Slide 4 — QUANTIFY the real limits
- Target ERP at an assumed 5 req/s per tenant
- Monday burst: 2,000 runs × 32 calls = 64 k calls → ≈ 3.6 h to drain
- 3 risky steps at 1 % → ≈ 590 runs/day need compensation; ≈ 160/day ambiguous outcomes
**Visual:** queue draining through a narrow pipe. Icons: `arch-token-bucket`, `pattern-backpressure`.
**Speaker notes:** Partial failure is a designed state with a queue and an owner, not an exception.

## Slide 5 — SKETCH
- Intake → durable engine → planner (LLM activity) → policy → approvals
- Executor → connector gateway (rate limits, idempotency, delegated tokens) → SaaS
- Webhook ingress, reconciler, append-only audit log
**Visual:** the lesson flowchart. Icons: `devops-temporal`, `arch-policy-engine`, `arch-api-gateway`, `arch-audit-log`.
**Speaker notes:** The connector gateway is the only path to systems of record.

## Slide 6 — Plan, approve, execute
- The model emits a typed plan over a fixed operation vocabulary
- Policy validates; the approver signs the exact plan hash
- A deterministic executor runs it; edits create a new version and void approvals
**Visual:** three lanes: model, policy and human, executor. Icons: `ai-llm`, `arch-policy-engine`, `ops-human-approval`.
**Speaker notes:** Agentic where language is ambiguous, deterministic where money and permissions move.

## Slide 7 — Waiting for days, within limits
- Approvals are signals; reminders and escalation are durable timers
- Temporal Cloud: 2 MB payload, 51,200 events or 50 MB history, 10,000 signals per execution
- Attachments by reference; Continue-As-New for standing workflows
**Visual:** run state machine. Icons: `devops-temporal`, `ops-calendar`, `arch-object-storage`.
**Speaker notes:** Filter external events before they become signals.

## Slide 8 — Exactly-once effects across SaaS
- Idempotency key from (run, step), never random per attempt
- Stripe-style keys may be pruned after 24 h: look up before late retries
- No key? Unique business key, marker plus lookup, or at-most-once with an unknown state
**Visual:** capability matrix of connectors. Icons: `pattern-idempotency`, `pattern-deduplication`.
**Speaker notes:** The engine makes the workflow exactly once, not the ERP.

## Slide 9 — Unknown outcomes and sagas
- Intent → effect → record; recovery starts with a lookup
- Saga: compensating steps; put the irreversible step last
- Compensation is a new business action, sometimes with its own approval
**Visual:** saga timeline with a pivot step. Icons: `pattern-saga`, `pattern-retry`.
**Speaker notes:** Never ask the model whether the PO was created.

## Slide 10 — Webhooks
- At-least-once, unordered, retried for days (Stripe documents up to three days)
- Verify signature, dedupe on event id, signal "changed", read current state
**Visual:** duplicate and out-of-order events collapsing into one signal. Icons: `pattern-webhook`, `pattern-deduplication`.
**Speaker notes:** Reading current state makes ordering irrelevant.

## Slide 11 — Identity and segregation of duties
- Delegated, step-scoped tokens with RFC 8693 `act` claims; no admin service account
- Approval token bound to the plan hash, enforced by the gateway
- Requester ≠ approver ≠ agent, rechecked when the decision arrives
**Visual:** three distinct principals and the token chain. Icons: `security-token`, `security-authorization`, `security-key`.
**Speaker notes:** A bug in the executor still cannot skip the human.

## Slide 12 — Approval fatigue and audit
- 93 % of manual prompts accepted in one vendor's data: frequent approvals become rubber stamps
- Track approval rate and decision time per approver; batch low-risk work
- Audit log outlives the engine (Temporal Cloud retention 1–90 days): hash-chained, write-once, crypto-shredding
**Visual:** approver dashboard; chained audit blocks. Icons: `arch-audit-log`, `security-key-shred`, `ops-dashboard`.
**Speaker notes:** Auditors want years of evidence; workflow history is not it.

## Slide 13 — Runs outlive deploys
- Daily deploys, 14-day runs → up to 14 code versions alive
- Pinned for short runs; for long ones, Continue-As-New after approval *with* Upgrade on Continue-as-New (public preview)
- Plain Continue-As-New keeps a pinned run on its old version
- Agent version (prompt, model, tools) pinned on the run at plan time; replay tests in CI
**Visual:** deploy timeline with draining versions. Icons: `ops-deploy`, `ops-ci-cd`, `devops-temporal`.
**Speaker notes:** Temporal says that for the longest-running workflows neither Pinned nor Auto-Upgrade alone offered
a clean answer, and recommends Upgrade on Continue-as-New where the workflow already continues-as-new. It is an
opt-in, experimental SDK option as of 2026-11; without it, use Auto-Upgrade with patching and replay tests.

## Slide 14 — WRAP
- Junior: queue, workers, LLM, APIs, approval email, retries
- Senior: durable workflow, typed plan approved first, derived keys, webhook dedupe, compensation, delegated tokens, separate audit
- Staff: drain-time maths, connector capability matrix, irreversible last, approval tokens at the gateway, fatigue metrics, engine limits vs audit retention, versioning and revocation
- Red flags: re-planning after approval, admin service account, "the engine guarantees exactly once"
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** End with what happens to 40,000 in-flight runs during tomorrow's deploy.
