# C16 — Exercises

Lesson: [course/04-case-studies/C16-deep-research-agents.md](../course/04-case-studies/C16-deep-research-agents.md).
Numbers are assumptions unless the lesson gives a source. Lab exercises use existing labs; they were not run for
this unit.

## 1. [Core] Bottom-up tokens

A "comparison" run uses a lead with 6 calls at 15 k input each and 3 researchers with 12 steps each, whose context
grows from 5 k by 3 k per step. Compute total input tokens. How does it compare with the deep run's 2.46 M?

<details><summary>Answer</summary>

Researcher input per agent = Σ (5 k + 3 k·i) for i = 0…11 = 12 × 5 k + 3 k × 66 = 60 k + 198 k = 258 k; three
researchers ≈ 774 k. Lead = 6 × 15 k = 90 k. Total ≈ 0.86 M, about 35 % of the deep run. Note the quadratic term
(198 k of 258 k per researcher comes from growth): capping steps per researcher, or truncating fetched pages harder,
cuts cost more than cutting researchers.
</details>

## 2. [Core] Do not turn a ratio into a number

A colleague says: "Anthropic says multi-agent uses 15× the tokens of chat; a chat turn is 2 k tokens, so a report is
30 k tokens and costs ten cents." What is wrong?

<details><summary>Answer</summary>

The post reports ratios to its own chat baseline and does not state the size of that baseline, so you cannot pick a
chat size and multiply. The ratio also averages over many interactions, not a single turn. The bottom-up estimate
(88 calls, ≈ 2.46 M input tokens) is two orders of magnitude larger than 30 k. Use the published ratio only to check
that "multi-agent is roughly an order of magnitude more than single-agent", and size the system from its own call
counts and context sizes.
</details>

## 3. [Deep] Researcher model choice

Using the lesson's cost table, what is the cost per deep report if researchers use a model at half the strong model's
prices (instead of a third)? At 50 k reports/day, how much does that choice change the daily bill compared with the
strong model?

<details><summary>Answer</summary>

Half prices: $1.50 input, $0.15 cached, $1.875 cache write, $7.50 output. Researcher input: 1.575 M × $0.15 +
0.675 M × $1.875 ≈ $0.236 + $1.266 ≈ $1.50. Output: 12 k × $15/M + 30 k × $7.50/M = $0.18 + $0.225 = $0.405. Total ≈
$0.28 + $1.50 + $0.405 + $0.30 + $0.15 + $0.05 ≈ $2.69. Versus $4.41: ≈ $1.72 saved per report, ≈ $86 k/day.
Check it against the budget too: a half-price researcher expects about $0.30 + $0.045 + $0.03 ≈ $0.375 of its $0.65
share (58 %), so the 80 % wrap-up still does not fire on a typical run. Whether
it is the right choice depends on quality per dollar measured on the evaluation suite for each effort class, not on
price alone.
</details>

## 4. [Deep] Effort routing errors

50 % of questions are simple. The effort classifier sends 10 % of simple questions to deep mode (waste) and 5 % of
deep questions to simple mode (poor reports). With strong-model prices ($4.41 deep, $0.24 simple), what is the
average cost per question, and what does each error cost you?

<details><summary>Answer</summary>

Deep runs = 0.5 × 0.95 + 0.5 × 0.10 = 0.525; simple runs = 0.475. Average ≈ 0.525 × $4.41 + 0.475 × $0.24 ≈ $2.32 +
$0.11 ≈ $2.43 per question (perfect routing: 0.5 × $4.41 + 0.5 × $0.24 ≈ $2.33). The 10 % error sends 5 % of all
questions to deep mode: 0.05 × ($4.41 − $0.24) ≈ $0.21 per question. The 5 % error sends 2.5 % of all questions the
other way and saves 0.025 × $4.17 ≈ $0.10, so the net is ≈ +$0.10 against perfect routing, but it produces poor
reports for 2.5 % of all questions; that cost appears in user ratings, not the bill. Measure
both errors: one with spend, the other with quality labels on a sample. Letting the user upgrade a simple answer to a
deep run cheaply ("go deeper") turns the second error into a recoverable one.
</details>

## 5. [Deep] Straggler deadline

Round 1 has three researchers. Each researcher's duration is 105 s with probability 0.9 and 400 s with probability
0.1 (it hit a slow site). Without a deadline, what is the probability round 1 takes 400 s? What does a 150 s deadline
change, and what must the report say?

<details><summary>Answer</summary>

P(at least one slow) = 1 − 0.9³ ≈ 0.27, so more than a quarter of runs wait 400 s in round 1 alone, and with two
rounds (3 then 2 researchers) 1 − 0.9⁵ ≈ 41 % of runs hit at least one straggler. A 150 s deadline caps each round:
the slow researcher is cancelled and returns partial findings, and the lead marks the sub-topic as partial coverage.
Wall time becomes predictable (≈ 8.5 min worst case), at the price of coverage gaps that the report must state
explicitly, so readers know what was not checked.
</details>

## 6. [Deep] Why the history needs references

A team passes full contexts in and out of every activity. Researcher calls average 30 k tokens, the lead 20 k, at
about 4 bytes per token. Estimate the history size for one run and for a "very deep" run with 10 researchers × 25
steps, and compare with Temporal's documented limits.

<details><summary>Answer</summary>

Normal run: 75 × 120 KB + 8 × 80 KB ≈ 9.0 MB + 0.64 MB ≈ 9.6 MB of inputs alone (outputs add a little), at the 10 MB
warning threshold. Very deep: 250 researcher calls, with contexts that grow longer over 25 steps (say 50 k average ≈
200 KB): ≈ 50 MB, at the 50 MB hard limit where the execution is terminated. Fix: store contexts, pages and findings
in the artefact store, pass references and hashes, and use a child workflow per researcher. Budgets on steps protect
the engine as well as the bill.
</details>

## 7. [Interview] Single agent or multi-agent?

The product owner asks you to justify the multi-agent design in two minutes. What evidence do you cite, what
counter-evidence, and what measurement would settle it for Lumen?

<details><summary>Answer</summary>

For: Anthropic reports a 90.2 % improvement over a single agent on its internal research eval, that token usage
explained 80 % of BrowseComp variance, and up to 90 % shorter research time with parallel sub-agents. Against:
Cognition argues that agents without shared context make conflicting implicit decisions, and its 2026 follow-up says
multi-agent works best when writes stay single-threaded; a controlled study found results from +80.8 % to −70.0 %
depending on task shape. Research is the favourable shape (breadth-first, read-only, one writer). Measurement: run
the same evaluation suite with a single-agent baseline and the multi-agent design per effort class, report quality
*and* cost, and route each class to whichever wins on quality per dollar.
</details>

## 8. [Deep] Find the leak

A new feature lets the lead "email the report to a colleague". Internal researchers can read the HR wiki. Using the
Rule of Two, explain the risk and two ways to ship the feature safely.

<details><summary>Answer</summary>

In its synthesis phase the lead already holds untrusted input (summaries derived from web pages) and private data
(internal findings). Adding email gives it the third property, external communication, so an injected page could steer it to email
internal content to an attacker-chosen address. Options: (1) the email action is not a lead tool; after the report
is finished, a separate step sends the stored report only to recipients from the organisation's directory, chosen by
the user in the UI, with the report's ACL checked against the recipient; (2) require explicit user confirmation of
recipient and content for every send, outside the model's control. Either way the model never chooses the recipient
from free text. Note the parallel with briefs: an email tool is an obvious outbound channel, but a web-search brief
written after the lead has read internal findings is the same leak in a less obvious form.
</details>

## 9. [Lab] Budgets and loop detection for a researcher

[labs/25-agentic-systems](../labs/25-agentic-systems/) implements step and token budgets, loop detection and a JSONL
trace. How would you use it to prototype one researcher with a $0.65 budget, a wrap-up instruction at 80 %, a partial
result at 100 % and a separate reserve that pays for the final findings call? What would you look for in the trace?

<details><summary>Answer</summary>

Convert the dollar budget to a token budget with the placeholder prices, set the step cap to 15, and add a check
that injects a "wrap up and return findings" message once 80 % of the token budget is used. At 100 % the runtime
should stop the loop, then make one final findings call charged to the separate reserve, so the partial result
still contains findings rather than only the runtime's "stopped: budget" status. In the trace, check that the reservation happens
before each model call (not after), that the wrap-up message appears exactly once, that repeated identical searches
trip the loop detector, and that the final output is a structured findings list rather than a crash. Designed
against the lab's README; not run for this unit.
</details>

## 10. [Lab] Admission control with token limits

[labs/26-llm-gateways-llmops](../labs/26-llm-gateways-llmops/) shows a per-key tokens-per-minute limit returning `429`
and overshoot by in-flight requests. What does that overshoot mean for a $5 per-report cap, and where should the
admission decision for deep runs live?

<details><summary>Answer</summary>

The lab shows that a gateway enforcing limits after the fact lets a key overshoot by the tokens of in-flight requests,
because output length is unknown at admission. A deep run has up to three researchers calling in parallel, so a
post-hoc cap can overshoot by several calls. The lesson's answer is reservation: before each call reserve its expected cost (the previously cached part of the
context at the read price, the rest at the write price, plus max output × output price) and refuse when the
reservation exceeds the remaining budget. A cache miss can then overrun by at most that one call, which is exactly
the "cap + one call" the SLO allows; reserving every call at the uncached price would be safer but would stop
researchers early. Admission
of whole runs belongs in front of the run queue (per-user and per-organisation quotas, a global concurrency ceiling),
not only at the gateway, so that a run is not started if it cannot finish. Not run for this unit.
</details>
