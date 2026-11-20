# C15 — Exercises

Lesson: [course/04-case-studies/C15-support-agent-platform.md](../course/04-case-studies/C15-support-agent-platform.md).
Numbers are assumptions unless the lesson gives a source. Lab exercises use existing labs; they were not run for
this unit.

## 1. [Core] Load and state

A tenant cohort produces 1 M conversations/day, 70 % chat and 30 % email, with a peak factor of 2.5. Chats stay open
8 minutes; email threads stay open 3 days on average. Each conversation makes 15 model calls. How many concurrent
chats, open email threads and model calls per second at peak?

<details><summary>Answer</summary>

Peak arrival = 1 M / 86,400 × 2.5 ≈ 28.9 conversations/s. Chat peak = 700 k / 86,400 × 2.5 ≈ 20.3/s; Little's law
× 480 s ≈ 9,700 concurrent chats. Email: 300 k/day × 3 days ≈ 900 k open threads, which are rows in a database, not
workers. Model calls ≈ 28.9 × 15 ≈ 430/s at peak. The design consequence: size the channel gateway for about 10 k
open streams and the conversation store for about a million open threads; the model fleet or provider quota is sized
by calls and tokens, not by open conversations.
</details>

## 2. [Core] The cache is a small lever here

A tenant's prompt change drops the prompt-cache hit rate from 60 % to 30 %. With the lesson's placeholder prices, what
happens to cost per conversation and to the containment saving? Then: which of these two changes could cause the
drop, and how would you tell them apart: (i) the customer's name at the top of the system prompt, (ii) the current
time, to the second, at the top of the system prompt?

<details><summary>Answer</summary>

Model cost at 60 %: 72 k × $0.10/M + 48 k × $1.25/M + 3.75 k × $4/M ≈ $0.082. At 30 %: 36 k × $0.10/M + 84 k ×
$1.25/M + $0.015 ≈ $0.0036 + $0.105 + $0.015 ≈ $0.124, about $0.04 more per conversation, ≈ $17 k/day at 400 k
conversations. Against the ≈ $2.61 saving per conversation it is under 2 %. Fix it, but do not mistake it for the
main economic lever: ten points of containment or the handoff summary move the saving about eight times more
($0.32 each).

Causes. (i) A per-customer string at the top makes every conversation's prefix unique, so only within-conversation
reuse remains: the first call of each conversation (and each email turn after the TTL) writes the whole prefix, but
calls 2 to 15 still read it. That loses the cross-conversation share, which may be modest for chat. (ii) A timestamp
that changes on every call makes every call a miss, so the hit rate falls towards zero, not to 30 %. Tell them apart
from the cached-token share per call position: with (i), call 1 misses and later calls hit; with (ii), all calls miss.
Either way the fix is the same: move per-conversation and per-call data after the stable prefix.
</details>

## 3. [Deep] Break-even and a suspicious result

Using `saving = H − [T + (1 − c)(1 − s)H + eL]` with H = $4, T = $0.10, L = $30, s = 0.2, and *e* = *w* · *r* where
*w* = 0.15 executed writes per conversation and *r* = 0.2 % wrong per executed write (so *e* = 0.0003): (a) what is
the saving at zero containment? (b) Why is that result suspicious, and what value of *s* makes c = 0 break even?
(c) At the baseline c = 0.6, what wrong-action rate per write wipes out the saving? (d) Why would it be wrong to plug
*r* = 0.002 in directly as *e*?

<details><summary>Answer</summary>

(a) c = 0: 4 − [0.10 + 0.8 × 4 + 0.009] = 4 − 3.309 ≈ $0.69 saved per conversation, even though no conversation was
resolved by the agent. (b) It assumes the handoff summary saves 20 % of handle time on *every* conversation. A failed
agent attempt can instead make the customer angrier and the human slower, so *s* may be zero or negative. Break-even
at c = 0: s × H = T + eL → s = 0.109 / 4 ≈ 0.03. Measure *s* in the assist rung (deep dive 4) before believing it.
(c) Baseline saving ≈ $2.61; it reaches zero when e × 30 = 2.61 + 0.009 → e ≈ 0.087 wrong actions per conversation,
i.e. r = e / w ≈ 58 % of executed writes. Long before that, trust and legal exposure would end the product, so the
real constraint on *r* is not the average arithmetic but the tail (exposure, a wrong policy repeated at scale,
liability). (d) The NFR's 0.2 % is per executed write; most conversations execute none. Using it per conversation
overstates the average wrong-action loss about sevenfold (0.002 vs 0.0003) and wrongly makes "wrong actions × 10"
look five times more costly than doubling tokens, when at these assumptions it is slightly less ($0.08 vs $0.10).
</details>

## 4. [Deep] Refund splitting and the breaker

Policy: automatic refunds ≤ $50, at most 2 per customer per 30 days, tenant daily automatic budget $25 k, circuit
breaker at 3× the trailing hourly baseline. The tenant normally makes about 300 automatic refunds a day, spread
evenly. A fraud ring controls 1,000 verified accounts and tries to take 2 × $50 from each over 24 hours. How far does
it get? Then: what if the ring paces itself to stay just under the breaker?

<details><summary>Answer</summary>

Per-customer caps allow the ring at most 1,000 × 2 × $50 = $100 k over 30 days, and the $25 k daily budget would cap
one day at $25 k. The breaker acts first. Baseline ≈ 300 / 24 ≈ 12.5 refunds/hour, so the breaker opens at about
37/hour. The ring adds 2,000 / 24 ≈ 83/hour, so the total (≈ 96/hour) trips it within the first hour. Loss before
the trip is at most about one hour of attack traffic, ≈ 83 × $50 ≈ $4.2 k, after which refunds go to human approval
and the tenant is paged. Without the breaker, the daily budget would let $25 k out on day one.

Paced attack: the ring can add up to about 37.5 − 12.5 = 25 refunds/hour without tripping, ≈ 600 a day, ≈ $30 k at
$50. The breaker never opens, so the daily budget (shared with the ≈ 300 legitimate refunds) is what binds: up to
$25 k a day, minus legitimate spend. At that pace the ring exhausts its 2,000 per-customer refunds in about 3 to 4
days, so the caps bound the whole attack at $100 k over 30 days. Lessons: the breaker bounds loss to the detection
window only for bursts; the daily budget and the cumulative caps bound a patient attacker, so size the budget against
baseline volume (here $25 k is well above a normal day's at most 300 × $50 = $15 k) and add detection the breaker cannot do (many new
accounts refunding at once, shared payment instruments or devices). And the baseline must be per hour of day, or a
normal Monday morning trips it.
</details>

## 5. [Interview] "I changed my email, send the refund to my new card"

A customer at identity level L1 (code sent to the email on file) says they lost access to that email, gives a new
address, and asks for a $40 refund to a new card. Walk through what the system does.

<details><summary>Answer</summary>

The refund needs L3 (fresh step-up), and the rule "never change the contact channel and move money in the same
conversation" applies. The agent cannot change the email on file by chat at all. It offers the tenant's account
recovery flow (which happens on the tenant's site, outside the agent) and a handoff to a human if the customer
cannot complete it. The refund, if eligible, goes to the original payment method recorded on the order, never to a
new card typed into the chat; the amount comes from the order line, not the customer's text. The policy decision
(`deny: identity_level` or `handoff: contact_change`) is logged with its rule id. A common wrong answer is "the model
will judge whether the customer sounds legitimate": that is exactly the judgement an attacker can talk the model into.
</details>

## 6. [Deep] Critique an escalation rule

A team proposes: "escalate when the model's self-reported confidence is below 0.7". Give two problems and a
replacement.

<details><summary>Answer</summary>

(1) Self-reported confidence is poorly calibrated and is produced by the same model that is being manipulated, so a
persuasive customer can raise it. (2) It ignores the reasons that matter: the customer asked for a person, policy
requires approval, a tool failed twice, a sensitive topic. A confident model handling a chargeback threat should
still escalate. Replacement: rule-based triggers on observable events (customer request, policy outcome, repeated
tool failure or restated intent, retrieval below threshold for a policy question, tenant-configured topics,
sentiment classifier over two turns), each logged with the trigger name so you can measure which ones fire and
whether the human agreed.
</details>

## 7. [Deep] pass^1 versus pass^k

Two agent versions on a 200-task replay suite. Version A succeeds on every task with probability 0.9, independently
per trial. Version B always succeeds on 85 % of the tasks and always fails on the other 15 %. Compute pass^1 and
pass^4 for each. Which would you ship for refunds, and what else do you need to know?

<details><summary>Answer</summary>

A: pass^1 = 0.90, pass^4 = 0.9^4 ≈ 0.66. B: pass^1 = 0.85, pass^4 = 0.85 (its failures are deterministic). A looks
better on a single run but is inconsistent: about a third of tasks fail at least once in four attempts, and each
customer sees one draw. B's failures are concentrated in identifiable tasks, which you can route to humans (keep
those intents on the supervised rung) while B runs the rest autonomously. Before deciding, look at *which* tasks fail
and how: a wrong refund is worse than a handoff, so grade the failure severity by final state, not just pass/fail
(τ-bench-style end-state grading, lesson reference 7).
</details>

## 8. [Deep] How many actions must you audit?

You want to know whether the wrong-action rate is at most 0.2 %, with a 95 % confidence half-width of 0.05
percentage points. How many executed actions must be audited per month? What do you do about the human cost?

<details><summary>Answer</summary>

n ≈ 1.96² × p(1 − p) / h² = 3.84 × 0.002 × 0.998 / 0.0005² ≈ 30,700 audited actions. That is far too many for human
review at most tenants. Combine: a judge model screens every executed write against the policy and the transcript;
humans review every judge-flagged case, every action above a value threshold, and a random sample to estimate the
judge's miss rate. Report the interval, not just the point estimate, and pool small tenants for the platform-level
estimate while still alerting per tenant on flagged cases.
</details>

## 9. [Interview] The model provider is down at peak

At 13.9 conversations/s the primary model provider returns errors for 40 minutes. What happens, step by step, and why
not route everything to the tenants' human agents?

<details><summary>Answer</summary>

(1) The gateway fails over to a pre-evaluated fallback model (evaluated on the same suite, per locale), possibly with
write tools disabled if the fallback is not approved for actions. (2) If no fallback is healthy, degrade: the agent
answers from help-centre search results (retrieval without generation), offers a ticket form or email follow-up, and
keeps pending actions pending. (3) Only conversations that meet normal escalation rules go to humans. Routing all
traffic to humans needs about 13.9 × 480 s ≈ 6,700 concurrent agents against about 2,700 staffed for the 40 %
escalation rate, so queues would explode and the human channel would fail for the customers who most need it. The
status of the degradation is shown to tenants, and conversations are tagged so their outcomes can be reviewed later.
</details>

## 10. [Lab] A refund tool behind a policy and an idempotency key

In [labs/25-agentic-systems](../labs/25-agentic-systems/), the runtime already has an approval gate for a
side-effecting tool and idempotent side effects across a simulated crash. Describe how you would add a
`refunds.create` tool that (a) takes `subject` from the runtime, not the model, (b) applies a `decide()` function with
a per-refund limit and a per-subject count, and (c) uses the key `task_id:seq`. What should you observe when you crash
the runtime after the tool ran but before the checkpoint?

<details><summary>Answer</summary>

(a) The runtime injects `subject` from task configuration and drops any `subject` field the model proposes, logging
the attempt. (b) `decide()` runs in the runtime before dispatch: amounts above the limit become an approval request
(the lab's existing gate), and the per-subject counter lives in the same store as the checkpoint. (c) On resume, the
call is re-sent with the same runtime-generated key and the tool returns the stored result instead of refunding
again, which is the same behaviour the lab demonstrates for its email tool. Expected observation: one refund recorded,
one `DUPLICATE`-style suppression in the tool log, and the per-subject count incremented once. This exercise was
designed against the lab's README; it was not run for this unit.
</details>

## 11. [Lab] Tenant isolation in retrieval

[labs/24-retrieval-vector-systems](../labs/24-retrieval-vector-systems/) shows a document reaching the candidate list
when an ACL predicate is dropped. Map that experiment to C15's per-tenant help index. Where must the tenant predicate
come from, and what does the lab's filtering experiment tell you about selective filters with HNSW?

<details><summary>Answer</summary>

The tenant predicate must be added by the retrieval service from the authenticated request context, never passed
through the prompt or chosen by the model; dropping it reproduces the lab's leak, but across businesses. The lab's
filtering experiment shows that post-filtering an approximate index starves selective queries (a small tenant is a 1 %
filter on a shared index), and that iterative scans or a pre-filter plan fix it at a latency cost. For C15 that
argues for a partition or namespace per tenant (or per tenant group for small ones) rather than one shared index
with a post-filter. Not run for this unit.
</details>
