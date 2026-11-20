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

Stage 2 load doubles: ≈ 140 items/s at peak → ≈ 21 k uncached prefill tokens/s, still about one H100, plus
redundancy. Human review grows from 60 k to 100 k items/day → ≈ 250 reviewers at 400 items/day, an increase of about
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
