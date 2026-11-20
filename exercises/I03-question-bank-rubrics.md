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
(b) [25](../course/03-ai-systems/25-agentic-systems.md) for agent orchestration and durable execution;
[08](../course/01-foundations/08-async-event-driven.md) for sagas, outbox and idempotency.
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
dimensions.
</details>
