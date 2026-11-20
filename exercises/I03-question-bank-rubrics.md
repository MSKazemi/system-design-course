# I03 — Exercises

Lesson: [course/05-interview/I03-question-bank-rubrics.md](../course/05-interview/I03-question-bank-rubrics.md).

## 1. [Interview] Score an excerpt

Excerpt from a CL-02 (distributed rate limiter) answer: "I'd use a token bucket. Each gateway node keeps buckets in
Redis and does a GET then a SET per request. If Redis is down we block all traffic to be safe. That handles
100 requests per second per key." Score Depth and Resilience (1–4) and explain.

<details><summary>Answer</summary>

Depth ≈ 2: the algorithm is named, but GET-then-SET is a race (two nodes can both read the same token count). An
atomic operation (an increment or a server-side script) is needed, and the over-admission bound is not discussed.
Resilience ≈ 1–2: failing closed on every endpoint turns a cache outage into a full API outage. A hire-level answer
fails open for low-risk endpoints with local fallback buckets, fails closed only where abuse is costly (login, paid
LLM calls), and alerts on the fallback mode.
</details>

## 2. [Core] Write a rubric

Write a four-outcome rubric for a new prompt: "Design a URL preview service that fetches page titles and images for
links pasted into Lumen chat."

<details><summary>Answer</summary>

*No hire:* fetches synchronously from the chat server on every message, with no cache or security. *Lean:* async
fetch and a cache, but no SSRF protection or size limits. *Hire:* async fetcher pool, cache keyed by normalized URL
with TTL, SSRF defenses (block internal address ranges, re-check after redirects, size and time limits), image
proxying through a sanitizing service, and per-domain rate limits. *Strong hire:* adds privacy (fetching reveals that
a user shared the link; avoid fetching private-workspace URLs or fetch from an anonymized egress), cache poisoning
and abuse cases, and cost per preview. Good rubrics name concrete, observable signals at each level.
</details>

## 3. [Core] Pick a practice set

You interview for a staff platform-engineering role in four weeks. Choose six questions from the bank and justify the
mix.

<details><summary>Answer</summary>

One reasonable set: IP-01 (progressive delivery), IP-03 (active-active migration), IP-07 (autoscaling mixed
workloads), AI-05 (GPU scheduler), SC-05 (build provenance), CL-08 (KV store) as a classical depth check. The set
covers platform-as-product, multi-region evolution, GPU-era capacity, supply-chain security and one fundamentals-heavy
prompt. Staff interviews often include a migration ("from today's system") angle, so IP-03 is the most important
to repeat with changed constraints. Other sets are fine if they cover platform, reliability, security and one
classical prompt.
</details>

## 4. [Interview] Spot the red flags

"For the chat app, I'll use microservices, Kafka, Cassandra and Redis. Messages are delivered exactly once. We'll
autoscale, so load isn't a concern." Which red flags appear?

<details><summary>Answer</summary>

Boxes without reasons (four technologies, no requirement linked to any); "exactly-once" asserted without mechanism
(it needs idempotent consumers and client-side dedup by message ID); no numbers (autoscaling is not capacity
planning); no failure discussion. Fix each by tying a component to a requirement and a number, and by explaining
at-least-once delivery with per-channel sequence numbers and dedup.
</details>

## 5. [Core] Map questions to units

Which course units would you study for (a) DI-01 ad-click aggregation, (b) AG-03 durable execution, (c) SC-03 EU-resident AI platform?

<details><summary>Answer</summary>

(a) [20](../course/02-modern-requirements/20-real-time-streaming.md) for event time, windows and watermarks;
[08](../course/01-foundations/08-async-event-driven.md) for delivery semantics and idempotent sinks.
(b) [33](../course/03-ai-systems/33-agent-platform-runtime.md) for durable-execution engines and their history and
payload limits, run leases and idempotent tool effects; [C17](../course/04-case-studies/C17-workflow-automation-agent.md)
for runs that wait days and outlive deploys; [08](../course/01-foundations/08-async-event-driven.md) for sagas, outbox
and idempotency. ([25](../course/03-ai-systems/25-agentic-systems.md) now covers only the single-agent runtime.)
(c) [19](../course/02-modern-requirements/19-privacy-compliance-sovereignty.md) for residency and the AI Act;
[28](../course/03-ai-systems/28-ai-trust-safety-governance.md) for AI governance as system requirements;
[15](../course/02-modern-requirements/15-multi-region-edge.md) for cell-based regional architecture.
</details>

## 6. [Deep] From lean to hire

A candidate's CL-03 (timelines) answer uses fan-out on write for everyone. The interviewer asks about a creator with
5 M followers. What should the candidate say to move from Lean to Hire?

<details><summary>Answer</summary>

Quantify the problem: one post × 5 M followers = 5 M timeline writes. At an assumed 50 k writes/s of fan-out
capacity that takes ≈ 100 s and starves other posts. Propose a hybrid: fan-out on write below a follower threshold
(say ≈ 100 k, to be tuned from measured costs), fan-out on read for large accounts, merged at read time with cached
recent posts from those accounts. State the trade-off: read-time merge latency vs write amplification, with the
threshold as the switching trigger. A strong-hire answer adds backfill when a user follows someone new, and deletion
propagation.
</details>

## 7. [Core] A two-week crash plan

You have only two weeks and target a senior AI-infrastructure role. Outline a plan using the course units.

<details><summary>Answer</summary>

Week 1: [I01](../course/05-interview/I01-interview-playbook.md), [I02](../course/05-interview/I02-numbers-cheat-sheets.md),
[21](../course/03-ai-systems/21-llm-inference-anatomy.md), [22](../course/03-ai-systems/22-serving-llms-at-scale.md),
[C09](../course/04-case-studies/C09-llm-chat-service.md); mocks AI-01 and CL-02 (to keep fundamentals warm).
Week 2: [23](../course/03-ai-systems/23-gpu-infrastructure.md), [26](../course/03-ai-systems/26-llm-gateways-llmops.md),
[I04](../course/05-interview/I04-ml-llm-interviews.md); mocks AI-03, AI-05, AI-04, plus a repeat of AI-01 with a changed
constraint (EU-only, or 4× longer contexts). Score every mock; spend the remaining time on your two weakest rubric
dimensions. Load check with the I03 rules (unit reading time, 1 h per mock): week 1 ≈ 13.5 h of reading + 2 h of
mocks ≈ 15.5 h, week 2 ≈ 9 h + 4 h ≈ 13 h. That is above the bank's 8–11 h/week plans, which is acceptable for a
two-week crash plan; to cut it, skim 22 and C09 instead of reading them (≈ 4.5 h saved).
</details>

## 8. [Interview] Score an AG-05 answer

A candidate answering AG-05 says: "The agent has a refund tool. The system prompt tells it never to refund more than
$50 and to escalate when it is unsure. We log every refund and review the logs weekly." Score it and say what moves
it to Hire.

<details><summary>Answer</summary>

**No hire.** A limit written only in the prompt is not enforced, so the tool is effectively unrestricted, which is the
AG-05 no-hire anchor. Two red flags from the question appear: the limit is in the prompt, and "unsure" (model
confidence) is the only escalation rule. Weekly log review detects losses days after they happen.

To reach **Hire**, the candidate must move control out of the model: verify the customer's identity (with step-up
before money moves); have the tool broker fill in the customer and read the amount from the order, not from the chat;
enforce per-refund, per-customer and per-window caps in a deterministic policy engine that fails closed; escalate on
rules (intents, limits, repeated failure) with a handoff summary; and evaluate offline on past tickets. **Strong
hire** adds the exposure line (5 % of 400 k conversations × $50 ≈ $1 M a day in C15's numbers) and a spend-rate circuit
breaker sized from it.
</details>

## 9. [Core] Numbers to expect for AG-09

An agent's base prompt is 2,000 tokens and each step adds 1,000. A bug makes tasks run 60 steps instead of 30. By how
much does input-token spend per task grow, and what does that imply for the controls?

<details><summary>Answer</summary>

30 steps: 30 × 2,000 + 1,000 × 435 = 495,000 tokens. 60 steps: 60 × 2,000 + 1,000 × 1,770 = 1,890,000 tokens. Twice
the steps cost ≈ **3.8×** the input, because each call re-sends the growing history. Implications: a step cap alone
lets cost grow quadratically up to the cap, so also cap tokens and money per task, enforced before each call
(reserve, then reconcile); alert on the spend *rate*, which here jumps within minutes, rather than on a daily total;
and set the caps from the context-growth curve, not from a guessed number of steps.
</details>

## 10. [Interview] Probe a release gate

You are interviewing on AG-12. The candidate says: "We have 50 test tasks, run each once, and ship if success does not
drop." Which follow-up do you ask, and what does a hire-level reply contain?

<details><summary>Answer</summary>

Ask: "Your success rate is 85 %. Would 50 tasks catch a 3-point drop?" At 85 % on 50 tasks the standard error is
√(0.85 × 0.15 / 50) ≈ 5.0 points, so the 95 % interval is about ±10 points: a 3-point regression is invisible. A
hire-level reply moves to a paired comparison on the same tasks, sized for the regression that matters (chapter 32
derives ≈ 870 paired tasks for 3 points, assuming 10 % of tasks change outcome between versions; at 900 tasks it
blocks when the paired difference is below about −2.1 points, catching ≈ 81 % of true 3-point drops), runs several trials per task and reports pass^k for a
customer-facing agent, grades the final state, and keeps the 50-task set as a cheap smoke suite per change. Strong
hire adds a canary with guardrail metrics and says how late outcomes (for example a 7-day re-contact) are handled.
</details>

## 11. [Interview] A junior agentic answer (AG-21)

A junior candidate answers AG-21 (ticket triage): "I'd build an agent that reads the ticket, decides which tools it
needs, and replies to the customer when it is confident." Score it against the AG-21 junior anchor, and give the two
numbers that make the case for a different design.

<details><summary>Answer</summary>

**No hire** on the full rubric and below the junior hire anchor: it is an autonomous agent that replies without a
human review step, the AG-21 no-hire anchor, and "use an agent" comes with no reason. Chapter 29's decision test
points the other way: the steps (classify, prioritise, draft) can be written down in advance, so a workflow with one
model step is enough.

The numbers, on AG-21's assumptions (20,000 tickets a day, one call of ≈ 3,000 input and 300 output tokens at
chapter 25's illustrative $1/$4 per million): one call is 0.003 + 0.0012 ≈ **$0.004 per ticket**, ≈ $84 a day. The
same job as chapter 25's 15-step agent at ≈ $0.22 per task is ≈ $4,400 a day, about **50×** more, for no gain in a task
with known steps. That 50× is the case of a 15-step loop; a 3-step agent would be ≈ $0.017 per ticket, ≈ $340 a day,
about 4×. A junior hire draws queue → model call → schema check → human review, keys the write by ticket id so
a retry does not create a second draft, and names one quality metric, such as the share of drafts sent with few edits.
An acceptable alternative is a workflow with one optional lookup step, as long as the candidate states when that
step would justify an agent.
</details>
