# C12 — Exercises

Case: [course/04-case-studies/C12-realtime-fraud-recsys.md](../course/04-case-studies/C12-realtime-fraud-recsys.md)

## 1. [Core] Why not compute features at request time?

A colleague proposes computing `count of payments on this card in the last 10 minutes` with a SQL query on the
transactions database for each authorization. At 15,000 payments/s peak, what goes wrong, and what is the
alternative?

<details><summary>Answer</summary>

Each request becomes an index range scan on the OLTP database, on the hot path, 15,000 times per second, and
more than once if there are several windows and entities. Tail latency then depends on the busiest database
shard, and fraud scoring competes with payment writes for the same database. Card-testing bursts make exactly
the hottest keys slowest.

Alternative: precompute velocity aggregates in a stream processor (Flink keyed state with event-time windows)
and serve them from an online KV store with a single batched lookup. Request-time computation is acceptable
only for features that depend on the request itself (amount vs card average, distance from the last location),
and those are cheap arithmetic on already-fetched values.
</details>

## 2. [Core] Tail amplification

The decision service fetches 4 feature groups in parallel, each with an independent per-call p99 of 8 ms. What
fraction of requests sees at least one call slower than 8 ms? How would you reduce it?

<details><summary>Answer</summary>

P(all four under their p99) = 0.99⁴ ≈ 0.961, so about **3.9%** of requests have at least one slow call. The
"p99 feature fetch" behaves like a p96.

Reductions: fewer calls (co-locate groups by entity so most payments need one or two multi-gets); hedged
requests (send a duplicate to another replica after the p95 latency); hard timeouts with default values and a
missing indicator; and keeping hot, slowly changing groups (merchant, BIN) in an in-process cache.
</details>

## 3. [Deep] Late events and watermarks

Mobile payments made offline arrive up to 90 s late at p99, and up to 30 min late at p99.99. Your `cnt_10m(card)`
feature uses event-time windows. How do you configure watermarks and allowed lateness, and what happens to the
p99.99 events?

<details><summary>Answer</summary>

Set the watermark's out-of-orderness bound near the bulk of the lateness distribution (for example, a few
seconds), so windows fire promptly for the common case. Set **allowed lateness** to about 90–120 s, so late
events within that bound still update the window state and re-fire the result. Flink drops elements later than
the watermark plus allowed lateness by default, so route them to a **side output**.

The p99.99 stragglers go to the side output and into the batch backfill used for training. Online, they are
missing from the velocity count, which is acceptable because they are, by definition, old by the time they
arrive. Record the late-drop rate as a metric. Longer allowed lateness keeps more state in memory, which is the
trade-off.
</details>

## 4. [Core] Choose the metric

The fraud rate is 0.1%. Model A has 99.95% accuracy, Model B 99.90%. Analysts can review 12,000 payments per day.
Which metric should decide between them?

<details><summary>Answer</summary>

Not accuracy: approving everything already scores 99.9%. Use **precision at k**, where k is the daily review
capacity (the fraction of frauds among the top-12,000 scored payments, the "alert precision" of Dal Pozzolo et
al.). Pair it with **amount-weighted recall** for the auto-decline band and the **false-decline rate** for good
customers. Compare models on a time-ordered holdout whose labels have matured. A model with lower accuracy but
higher precision at k and higher euro recall is the better business choice.
</details>

## 5. [Deep] Label delay in training

You retrain nightly using all payments up to yesterday, labelling anything without a dispute as genuine. Why is
this wrong, and how do you fix it?

<details><summary>Answer</summary>

Most fraud labels arrive after days or weeks (Dal Pozzolo et al. give "e.g., one month" for delayed supervised
samples). Yesterday's frauds therefore look genuine, which teaches the model that recent fraud patterns are
benign: the worst possible bias against an adapting adversary.

Fixes: train the "delayed" model only on payments older than the label-maturity window (for example, 30+ days),
where default-genuine is reasonable. Use recent analyst feedbacks separately, as a feedback model or as features,
knowing they are biased toward alerted payments. Record `label_time` and train point-in-time. Evaluate only on
matured periods.
</details>

## 6. [Deep] Selection bias from declines

After two years, your model's training data contains almost no examples from a high-risk merchant category,
because the model declines most of those payments. What is happening, and how do you get unbiased signal back?

<details><summary>Answer</summary>

Declined payments never produce a dispute or a confirmed outcome, so the model's own decisions remove those
examples from future training sets. That is a direct feedback loop and a form of selection bias. The model's
knowledge of that segment freezes, and it cannot learn whether it is over-blocking.

Get signal back with a small, amount-capped **exploration slice**. A random fraction of borderline payments is
*challenged* (step-up authentication) instead of declined. The step-up outcome and subsequent disputes become
labels. Log the decision probability (propensity) so offline evaluation can reweight by inverse propensity.
Monitor the cost of the slice as a budget line.
</details>

## 7. [Core] Fallback design

Write the fallback policy for these failures, and say whether each is fail-open, fail-closed or degraded: (a)
model server down; (b) the device feature group times out; (c) the decision service is unreachable from the
gateway.

<details><summary>Answer</summary>

(a) **Degraded:** rules-only decisions with a conservative profile (lower challenge thresholds, decline only on
hard rules). Rules are in-process, so they still work.
(b) **Degraded:** use defaults plus a `missing_device` indicator the model was trained with; continue scoring.
(c) **Gateway static policy**, decided in advance: approve below a small amount, challenge above it (or decline
for high-risk channels). This is partly fail-open by design, because declining every payment is an outage for
merchants. Bound the risk by amount, and alert immediately.

All three set a fallback flag in the decision log, and the fallback rate is an SLI.
</details>

## 8. [Interview] Shadow-testing a new model safely

How do you shadow-test model v58 against champion v57 without affecting latency, and what do you compare before
the canary?

<details><summary>Answer</summary>

Compute v58's score **after** responding, from the same logged feature snapshot (an async consumer of the
decision log, or a post-response task in the decision service). This adds zero hot-path latency and guarantees
both models saw identical inputs.

Before the canary, compare: score distributions overall and per segment; the would-be decline, challenge and
review volumes under the current score policy (do they fit analyst capacity?); agreement with the champion on
high-risk decisions; inference latency and CPU on production hardware; and, as labels mature, precision at k
and euro recall on the shadowed period. Then canary 1–5% of traffic, bucketed by card so retries are consistent,
with automatic alias rollback on guardrail breaches.
</details>

## 9. [Deep] Hot merchant

A marketplace accounts for 20% of payments. Its merchant feature key receives 3,000 reads/s and continuous
updates at peak. What breaks, and how do you fix it?

<details><summary>Answer</summary>

A single KV shard holds that key. It becomes a hot spot for reads, with lock or contention issues on writes.
Its latency inflates the tail for 20% of all payments.

Fixes: cache the merchant record in-process in each decision-service instance with a ~1 s TTL (merchant-level
aggregates tolerate 1 s staleness); pre-aggregate writes in Flink so the key is updated once per flush; and if
needed, split the hot aggregate into N sub-keys (`merchant:m_big:{0..N-1}`) that Flink writes round-robin and
the reader sums. Read replicas for that shard also help. See SYSDESIGN-07 on hot keys.
</details>

## 10. [Interview] Fraud vs recommendations

You are asked to reuse the fraud platform for home-page recommendations. List three components you keep as-is
and three that change.

<details><summary>Answer</summary>

**Keep:** the event log (Kafka) and stream processor for session features; the online/offline feature store with
point-in-time training on logged features; the model registry with shadow → canary → alias promotion; and the
decision/impression log as the training set.

**Change:** add two-tower retrieval with an ANN index of item embeddings, a ranking stage that scores hundreds of
candidates (feature fetch becomes a large batched multi-get plus item caches), and re-ranking for diversity.
Labels arrive in seconds, so training can be more frequent. The feedback-loop mitigation becomes exploration
slots and propensity logging against popularity bias, instead of a challenge-instead-of-decline slice.
Explainability requirements are usually lighter.
</details>
