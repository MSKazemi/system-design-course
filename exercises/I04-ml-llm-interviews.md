# I04 — Exercises

Lesson: [course/05-interview/I04-ml-llm-interviews.md](../course/05-interview/I04-ml-llm-interviews.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Build a metric ladder

Write the five rungs of the metric ladder for a real-time fraud model on Lumen payments.

<details><summary>Answer</summary>

Business: fraud losses plus the cost of friction (lost legitimate payments). Online product metric: chargeback rate
and false-decline rate in an A/B or holdout. Offline model metric: precision and recall at the chosen threshold, or
precision at a fixed false-positive rate, on a time-split test set. System SLI: p99 scoring latency (< 100 ms) and
availability of the scoring path. Guardrails: approval rate for good customers, manual-review queue size, latency.
Note the label delay: chargebacks arrive weeks later, so the online metric lags and needs proxies.
</details>

## 2. [Core] RAG cost per day

A RAG assistant peaks at 200 QPS and averages 60 QPS. Each answer uses 4,000 input and 300 output tokens. With
placeholder prices of $0.50/M input and $1.50/M output, what is the cost per answer and per day?

<details><summary>Answer</summary>

Per answer: 4,000 × 0.5 × 10⁻⁶ + 300 × 1.5 × 10⁻⁶ = $0.0020 + $0.00045 ≈ **$0.0025**. Per day: 60 × 86,400 ≈ 5.2 M
answers → ≈ **$12,700/day** (≈ $380k/month). Input tokens are 80 % of the cost, so the levers are fewer and better
chunks, shorter history and prefix caching, not shorter answers.
</details>

## 3. [Deep] Calibrate an LLM judge

Design the calibration process for an LLM judge that scores RAG answers for correctness on a 1–5 rubric.

<details><summary>Answer</summary>

Have experts label a stratified sample (for example 10 % of the golden set, across languages and intents) with the
same rubric. Run the judge and measure agreement (exact and within-one agreement, or a correlation) per segment.
Control known biases: randomize order in pairwise comparisons (position bias), normalize or penalize length
(verbosity bias), and avoid using the same model family as judge and candidate where possible (self-enhancement), all
biases examined by Zheng et al. Re-calibrate when the judge model, rubric or domain changes. Track judge–human
agreement as a dashboard metric, and use humans for segments where agreement is low.
</details>

## 4. [Deep] Why prefill dominates

In worked answer A, why is the prefill GPU need (≈ 7) larger than the decode need (≈ 4–5)?

<details><summary>Answer</summary>

Each answer has ≈ 3,400 input tokens and only ≈ 250 output tokens, a 13:1 ratio. Prefill costs ≈ 2 × parameters FLOPs
per input token and is compute-bound, ≈ 30 k tokens/s per H100 at the assumed 50 % efficiency, so 238 k tokens/s
needs ≈ 8 GPUs (≈ 7 after prefix caching the system prompt). Decode is memory-bound but the output volume is small,
and concurrency (≈ 490 streams) fits in KV memory on 4–5 GPUs. RAG is input-heavy, so the levers are retrieving
fewer tokens and caching shared prefixes. Disaggregated prefill/decode can help when the two needs differ this much.
</details>

## 5. [Interview] Moving a moderation threshold

Product asks to widen the stage-1 "uncertain" band in worked answer C from 10 % to 20 % of items, and the human
review share from 0.3 % to 0.5 %. What changes?

<details><summary>Answer</summary>

Stage 2 load doubles: ≈ 140 items/s at peak → ≈ 21 k prefill tokens/s with the policy prompt prefix-cached (140 × 150;
≈ 91 k without caching, 140 × 650), so about one H100 with caching and three without, plus redundancy. Twice as many
items are also held before publish while the label-only stage-2 call runs (≈ 0.5 s p95 each), so check that the
judge pool keeps that latency at the higher load. Human review grows from 60 k to 100 k items/day → ≈ 250 reviewers at 400 items/day, an increase of about
100 people. GPU cost barely moves; human cost rises by two-thirds. Ask what quality gain justifies it (measured recall
improvement on the expert-sampled set), and consider widening the band only for high-severity policies.
</details>

## 6. [Core] Fine-tuning memory

Estimate GPU memory to (a) fully fine-tune an 8B model with mixed-precision Adam, and (b) LoRA fine-tune it with a
frozen BF16 base. Which fits on one 80 GB GPU?

<details><summary>Answer</summary>

(a) ZeRO's accounting gives ≈ 16 bytes per parameter of model state: 8 × 10⁹ × 16 ≈ 128 GB, plus activations. It
does not fit on one 80 GB GPU without sharding (ZeRO/FSDP across GPUs) or offloading. (b) The frozen base is
≈ 16 GB in BF16. Adapters and their optimizer state are small (LoRA trains a tiny fraction of parameters), so the
total is ≈ 16 GB + activations + a few GB, which fits on one 80 GB GPU. That difference is why a fine-tuning platform
defaults to adapters.
</details>

## 7. [Deep] Choosing the label

In worked answer B, why is long dwell a better training label than clicks, and what can still go wrong with it?

<details><summary>Answer</summary>

Clicks reward curiosity-gap titles. Long dwell (> 30 s) better reflects reading value and correlates more plausibly
with retention, which is the business outcome. Risks: dwell favors long articles regardless of quality, it is
affected by page load and device, and it still creates a feedback loop (the model only learns from what it showed).
Mitigations: normalize dwell by article length, add saves and follows as auxiliary labels, keep exploration slots and
log propensities, and validate against retention in a long-running holdout.
</details>

## 8. [Interview] "What would you build without ML?"

For the moderation system, the interviewer asks what you would build first without any ML. Answer.

<details><summary>Answer</summary>

Hash matching against known violating content, keyword and pattern rules per policy and language, rate limits and
account-age signals for spam, user reporting with a review queue prioritized by reach, and an appeals flow. That
baseline ships quickly, produces labelled data from reviewer decisions, and gives a benchmark the ML cascade must
beat on per-policy precision and recall. This follows Zinkevich's first rule: don't be afraid to launch without ML.
Saying it shows you treat ML as a means, not the goal.
</details>

## 9. [Core] Containment versus tokens in worked answer D

Using answer D's assumptions (saving = H − [T + (1 − c)(1 − s)H + e·L], with H = $4, c = 0.6, s = 0.2, T = $0.10,
w = 0.15 executed writes per conversation, r = 0.002 per write so e = w · r = 0.0003, L = $30, 150 k conversations a day), compare two projects: halving the token cost, or raising containment
from 0.6 to 0.7.

<details><summary>Answer</summary>

Baseline: 4 − [0.10 + 0.4 × 0.8 × 4 + 0.0003 × 30] = 4 − [0.10 + 1.28 + 0.009] = **$2.61** per conversation.

- Halve tokens (T = $0.05): 4 − [0.05 + 1.28 + 0.009] = $2.661, **+$0.05**, ≈ $7.5 k/day.
- Containment 0.7: 4 − [0.10 + 0.3 × 0.8 × 4 + 0.009] = 4 − [0.10 + 0.96 + 0.009] = $2.931, **+$0.32**, ≈ $48 k/day.

Ten points of *real* containment are worth over six times the token saving. Two cautions. Containment must be
measured with the strict definition (no handoff and no re-contact within 7 days), or customers who give up count as
wins. And containment gained by letting the agent act more often raises *e*: but at r = 2 % the term is only $0.09; the real risk is
the tail (a wrong policy repeated on every matching conversation, up to the $750 k/day exposure). So the levers are better tools, better articles and better escalation, under the same
policy caps.
</details>

## 10. [Deep] pass^k and audit sample size

In answer D's offline eval, a refund task succeeds with probability 0.9 per trial. (a) What are pass^4 and pass^8?
(b) Online, the true wrong-action rate is 0.2 % and you audit 1,000 actions a month. What can you conclude?

<details><summary>Answer</summary>

(a) pass^k = 0.9^k for a task with independent trials: pass^4 ≈ **0.66**, pass^8 ≈ **0.43**. A task that "works 90 %
of the time" fails for a large share of customers who repeat it, which is why customer-facing agents are judged on
pass^k, not on one run.

(b) Expected errors ≈ 2. The standard error is √(0.002 × 0.998 / 1,000) ≈ 0.14 points, so the 95 % interval is about
±0.28 points: roughly 0 % to 0.5 %. You cannot tell whether you meet a 0.2 % target. C15 computes that about 10,000
audited actions are needed for ±0.09 points. Since full human audit at that volume is expensive, pre-screen with a
calibrated judge, send disagreements and every high-value action to humans, and pool audits across a quarter for
low-volume intents.
</details>

## 11. [Deep] Where does the refund breaker trip?

Answer D has 15,000 refund intents a day (10 % of 150 k conversations), a $50 limit and a 3× peak factor. A candidate
proposes: "trip the breaker when refunds per hour exceed 3× the average hour". Is the threshold right? Propose a better
one and bound what a sudden refund storm can pay out before it trips.

<details><summary>Answer</summary>

The average hour is 15,000 / 24 = **625** refund intents, so the proposed threshold is ≈ 1,875 an hour. But a normal
peak hour is also 3 × 625 ≈ **1,875**: the breaker would trip at every busy hour and push honest refunds to approvers.

Compare with the baseline for the **same time of week** instead, as C15 does (3× the trailing four-week baseline for
that hour), and use a short rolling window so a storm is caught within minutes. With 15-minute windows: at peak the
baseline is 1,875 / 4 ≈ **470**, so the breaker trips near 1,400 refund intents in the window; in an average hour the
baseline is ≈ 156 and it trips near 470 in the window. Add a minimum count in the window (an assumed 50, for example)
so quiet hours, whose baseline is a handful of refunds, do not trip on noise. Before it trips, a sudden storm can add at most about two baselines of excess in the window: ≈ 940 × $50 ≈
**$47 k** at peak, ≈ $16 k in an average hour, against the $750 k/day worst case. A slow leak paced just under the
threshold is not caught by the breaker; the per-customer caps and the daily automatic budget bound it. Acceptable
alternatives: a rate-of-change trigger (refunds per window rising faster than conversations), or a per-tenant or
per-intent breaker; in every case the multiplier and window are assumptions to tune on replayed history, trading
false trips (approver time) against exposure.
</details>
