# I01 — Exercises

Lesson: [course/05-interview/I01-interview-playbook.md](../course/05-interview/I01-interview-playbook.md).
Numbers are assumptions unless the lesson gives a source.

## 1. [Interview] You are late

In a 45-minute interview you finish SKETCH at minute 25. You had planned two deep dives (cache invalidation and
sharding) and a STRESS section. What do you do, and what do you say?

<details><summary>Answer</summary>

Cut DEEPEN to one deep dive and fold the most important failures into it, so that you still produce resilience
signals. Say it out loud: "We're at 25 minutes. I'll go deep on sharding, because that's where our write numbers say
it breaks, and I'll cover its failure modes as part of that. Then two minutes on the rest of STRESS." Choose the deep
dive that the QUANTIFY numbers stressed, or ask the interviewer to choose. Do not rush through both deep dives at
level 1. Two shallow deep dives give less evidence than one at trade-off level plus a short failure table. Missing
STRESS entirely is the worst outcome, because it removes a whole rubric dimension.
</details>

## 2. [Core] Four-part trade-off sentences

Rewrite each statement as "I'll choose X because R; it costs C; I'd switch to Y if T":
(a) "Postgres is better here." (b) "We'll cache it." (c) "Use Kafka."

<details><summary>Answer</summary>

(a) "I'll use a relational database for orders because we need multi-row transactions and the write rate is about
2,000/s, well within one primary. It costs us horizontal write scaling. I'd move to a distributed SQL store or shard
by customer if sustained writes approached the primary's measured limit."
(b) "I'll cache product pages for 60 seconds because reads outnumber writes 200:1 and p99 must be under 100 ms. It
costs up to a minute of staleness after a price change. I'd add event-driven invalidation if a minute of stale price
caused order disputes."
(c) "I'll put a durable log between checkout and fulfilment because fulfilment is slower and spikier than checkout,
and we need replay after consumer bugs. It costs operational complexity and at-least-once semantics, which means
idempotent consumers. I'd use a simple queue instead if we never needed replay or multiple consumers."
Any version is acceptable if it has a concrete requirement, a real cost, and a trigger that could actually happen.
</details>

## 3. [Interview] Clarifying questions that change the design

Prompt: "Design photo sharing for Lumen workspaces." List five clarifying questions and, for each, say how the answer
would change the design.

<details><summary>Answer</summary>

Examples:
1. *Who can see a photo: the workspace, specific people, or public links?* Changes the authorization model and
   whether CDN URLs must be signed.
2. *Original resolution kept, and how large are uploads?* Drives storage estimates, upload protocol (multipart,
   resumable) and transcoding.
3. *How fast must a photo appear for others after upload?* Seconds means synchronous thumbnailing on the critical
   path; a minute allows an async pipeline.
4. *Is there EU residency for some workspaces?* Forces regional buckets and processing.
5. *Read/write ratio and peak events (e.g. company off-sites)?* Sets cache and CDN sizing and the burst plan.
Weak questions are those whose answers would not change anything ("Should it be scalable?"). The test for each
question is whether you can say the "because" out loud.
</details>

## 4. [Core] Bound, reason, commit

The interviewer asks: "What is the p99 latency of a cross-region synchronous write between Frankfurt and Virginia?"
You don't know the exact number. Answer using bound, reason, commit.

<details><summary>Answer</summary>

*Bound:* "I don't know a measured number for that path." *Reason:* "The distance is roughly 6,500 km. Light in fiber
is about 5 µs per km one way, so the round trip floor is about 65 ms. Real paths are longer, and a synchronous write
needs at least one round trip, often two with consensus, so p99 is likely 100–200 ms." *Commit:* "That's far too slow
for every user write in a 50 ms budget. I'd keep writes in the user's home region and replicate asynchronously, and
I'd measure the actual RTT before deciding." (The distance is an approximation; what matters is the physics floor
from [I02](../course/05-interview/I02-numbers-cheat-sheets.md).)
</details>

## 5. [Deep] Senior versus staff

Two candidates give the same notification-service design as in the lesson's mock. What extra evidence would make one
of them a staff-level hire rather than a senior-level hire?

<details><summary>Answer</summary>

Staff evidence goes beyond correct mechanisms:
- Framing that changes the problem, such as questioning whether SMS should exist for some types, or proposing that
  producers own a notification budget.
- Cost reasoning as a design driver: cost per 1,000 notifications per channel, reported back to producer teams to make
  quotas self-enforcing.
- Organizational and evolution view: how teams onboard, how policies for critical types are governed and audited, how to
  migrate today's ad-hoc senders onto the platform gradually.
- Knowing what not to build: no custom delivery infrastructure, and no stream processor until volume justifies one.
- Correlated failures and blast radius: a router bug that sends to wrong users is a privacy incident; kill switches
  per type; staged rollout.
The senior candidate shows correct, deep mechanisms. The staff candidate shows judgment about scope, cost and
organization, still backed by numbers.
</details>

## 6. [Interview] Handling a redirect

You are explaining your consistent-hashing ring when the interviewer says: "Let's talk about what happens when a client
retries a payment." What do you do in the next 20 seconds?

<details><summary>Answer</summary>

Finish your sentence, write "ring: vnode count, rebalancing" in the parking lot, and switch: "Sure. Retries are the
key correctness risk. Let me start with idempotency keys at the API." Do not argue for finishing the ring, and do not
return to it unless the interviewer asks. The redirect tells you where the rubric still needs evidence. If the redirect
conflicts with an agreed requirement, mention it briefly ("this changes our latency budget") and still follow.
</details>

## 7. [Interview] Critique a weak answer

A candidate's STRESS section for the notification service: "If something fails, we have replicas and retries. We use
Kubernetes, so pods restart. We'd add monitoring." Score it and rewrite one row properly.

<details><summary>Answer</summary>

Score on Resilience and operations: 1–2 (No hire to Lean). It is generic, names no specific failure, has no detection
signal and no overload behavior, and "retries" without backoff and budgets can make outages worse. A proper row:
"SMS provider outage → SMS backlog and possible cost spike if we fail over to a pricier provider → detected by
per-provider send success rate and queue age → circuit breaker per provider; fail over only high-priority SMS; bulk
SMS waits; retries with jittered exponential backoff and a retry budget." Each row should name the failure, its
impact, the SLI that detects it and the mitigation.
</details>

## 8. [Core] "So what" lines

For each estimate, write the design conclusion: (a) 40 k writes/s at peak; (b) 30 TB of new data per year;
(c) 250 k concurrent WebSocket connections; (d) p99 budget 80 ms and one cross-region call of ≈ 90 ms RTT.

<details><summary>Answer</summary>

(a) Too many for one relational primary on typical hardware (an assumption you should state), so partition the write
path or put a log in front of it. (b) Storage cost and backup time matter, so plan tiering to cheaper storage and
partition by time. Data size alone doesn't force exotic storage. (c) Size a dedicated connection-gateway tier with
Little's law, plan memory per connection, and design for reconnect storms during deploys. (d) The cross-region call
cannot be on the hot path, so serve from local replicas and replicate asynchronously.
</details>

## 9. [Interview] Remote tool failure

Ten minutes into a remote interview, the shared whiteboard stops syncing. What do you do?

<details><summary>Answer</summary>

Tell the interviewer at once and propose a fallback: "The board isn't syncing for me. Can I continue in the shared
doc or chat with a text outline?" Re-create the essential state as text: requirements, numbers, and the request path
as numbered steps (`1 client → API (HTTPS)`, `2 API → queue (async)`, …), or a Mermaid-style text diagram. Keep
narrating. Having practiced a text fallback beforehand turns this into a non-event, and handling it calmly is itself a
communication signal.
</details>
