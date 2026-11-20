# 27 — Exercises

Lesson: [course/03-ai-systems/27-ml-platforms.md](../course/03-ai-systems/27-ml-platforms.md)

## 1. [Core] Name the skew

A churn model scores 0.91 AUC offline and barely beats the old rules online. The training pipeline computes
`orders_last_30d` in Spark from a daily snapshot. The serving path computes it in the API from an orders cache
that excludes cancelled orders. Which cause of training-serving skew is this, and what are two design fixes?

<details><summary>Answer</summary>

It is the first cause in Zinkevich's definition: a discrepancy in how the training and serving pipelines
handle data. Cancelled orders are counted in one pipeline and not the other. Fixes:

1. **Define once, materialize twice.** Declare the feature once in a feature store and have the platform write
   it to both the offline and online stores, so there is one implementation.
2. **Log and train.** Log the feature values actually served (Rule #29) and build future training sets from
   those logs, so the training input *is* the serving input.

A third acceptable answer is a skew monitor. For a sample of keys, compare the logged online value with the
offline recomputation and alert on mismatch rate. That detects the bug but does not prevent it.
</details>

## 2. [Core] Point-in-time join by hand

Feature view `user_stats` has TTL = 2 h. For user 7 the history contains values written at 08:15, 09:50,
11:05 and 12:40. The entity dataframe has rows for user 7 at 10:00, 12:00 and 15:00. What value does each row
get?

<details><summary>Answer</summary>

For each row the join looks backward from the row's timestamp, no further than the TTL:

- **10:00** → window 08:00–10:00 → the latest value at or before 10:00 is **09:50**.
- **12:00** → window 10:00–12:00 → **11:05** (12:40 is in the future relative to the row).
- **15:00** → window 13:00–15:00 → no value in the window → **null**. The 12:40 value is older than the TTL.

The TTL is measured from each row's timestamp, not from query time. A "latest value" join would wrongly give
12:40 to all three rows and leak the future into two of them.
</details>

## 3. [Core] Size the online store

Lumen has 50 M documents and 30 M users. Each document has 40 features and each user 120 features, at an
average of 8 bytes per value. Assume 50% storage overhead. Estimate the online-store memory. Would you also
store user × document cross features?

<details><summary>Answer</summary>

- Documents: 50 M × 40 × 8 B = 16 GB → 24 GB with overhead.
- Users: 30 M × 120 × 8 B = 28.8 GB → ~43 GB with overhead.
- Total ≈ 67 GB, which is a modest Redis/KV cluster (shard and replicate for throughput and availability).

Cross features: 30 M × 50 M = 1.5×10¹⁵ pairs, which is impossible to store. Compute cross features at request
time for the few hundred candidates (on-demand features) or let the ranking model learn the interaction from
the two entities' features.
</details>

## 4. [Deep] GPU memory for fine-tuning

You must adapt a 13B-parameter model. You have nodes with 8 × 80 GB GPUs. Estimate (a) the model-state memory
for full fine-tuning with mixed-precision Adam, (b) the minimum number of GPUs with ZeRO-3/FSDP ignoring
activations, and (c) the base-model memory for LoRA in bf16 and for QLoRA at 4 bits.

<details><summary>Answer</summary>

(a) ZeRO's accounting gives 16 bytes per parameter (2 fp16 weights + 2 fp16 gradients + 12 fp32 optimizer
states): 13×10⁹ × 16 B = **208 GB**.

(b) With full sharding, states are split evenly: 208 / 80 = 2.6, so at least **3 GPUs** in theory. In practice
use a full 8-GPU node (26 GB of states per GPU), because activations, communication buffers and fragmentation
need the headroom.

(c) LoRA with a frozen bf16 base: 13×10⁹ × 2 B = **26 GB** plus small adapters, so one GPU. QLoRA at 4 bits:
~**6.5 GB** for the base weights. Note that QLoRA trades memory for extra dequantization compute, and quality
must be checked on your evaluation suite.
</details>

## 5. [Deep] Checkpoint interval

A training job on 2,048 GPUs has an observed MTBF of 6 hours. A synchronous checkpoint takes 12 minutes. An
asynchronous, sharded checkpoint blocks training for 1 minute. Using Young's approximation, compute the optimal
interval for each and the expected work lost per failure (assume half an interval on average, plus 10 minutes
of restart).

<details><summary>Answer</summary>

Young: T ≈ √(2·C·M), with M = 360 min.

- Synchronous, C = 12: T ≈ √(2 × 12 × 360) = √8640 ≈ **93 min**. Loss per failure ≈ 46 + 10 = 56 min.
- Asynchronous, C = 1 (the blocking part): T ≈ √720 ≈ **27 min**. Loss per failure ≈ 13 + 10 = 23 min.

Over a day, the synchronous job also spends about 12 × (1440/93) ≈ 186 min checkpointing. The asynchronous one
spends about 1 × (1440/27) ≈ 53 min blocked. Faster checkpoints let you checkpoint more often *and* lose less,
so the effective training time rises on both counts. Using the blocking time as C is a simplification: the
background write must finish before the next checkpoint starts.
</details>

## 6. [Core] Batch, online or hybrid?

For each, choose batch, online, streaming or hybrid inference and justify: (a) weekly "you might have missed"
digest emails; (b) card-transaction fraud scoring; (c) home-feed recommendations; (d) alerting when a GPU node's
temperature trend predicts failure.

<details><summary>Answer</summary>

(a) **Batch.** The entity set is enumerable, latency is irrelevant, and the output is consumed once.
(b) **Online.** The input (the transaction) exists only at request time and the decision must be inline,
usually with streaming features for velocity (see C12).
(c) **Hybrid.** Item embeddings and candidates are precomputed in batch; ranking runs online with session
features.
(d) **Streaming.** Score as telemetry arrives and push alerts. There is no user request to attach to (see C13).
</details>

## 7. [Deep] The embedding upgrade

A team retrains only the item tower of a two-tower recommender, rebuilds the ANN index, and deploys the new
index. Recall collapses. Explain why, and design a safe rollout.

<details><summary>Answer</summary>

The query tower is still the old one. Two-tower relevance is a dot product between the query and item
embeddings, which is only meaningful when both towers were trained together, in the same embedding space.
New item vectors and old query vectors are in different spaces.

Safe rollout: treat (query tower vN, item tower vN, index vN) as one versioned unit. Build index v2 alongside
v1. Deploy query tower v2. Route a canary slice so that each request uses only matching versions. Compare
recall@k on a canary query set and online engagement. Keep v1 until promotion so rollback is instant. Never
mix versions in one ANN search.
</details>

## 8. [Core] Drift or bug?

On Monday the fraud model's mean score drops by 40% and the approval rate jumps. What do you check first, and
why?

<details><summary>Answer</summary>

Check **data quality first**: per-feature null rates, defaults and ranges, freshness lag, volume, and schema
changes in the upstream sources since Friday. A sudden, large shift on a calendar boundary is far more likely
to be a pipeline or contract break (a renamed field defaulting to 0, a stale stream feature) than real-world
concept drift, which is usually gradual or tied to an identifiable event.

Then slice the shift by client version, region and merchant to localize it. Only after ruling out bugs, treat
it as drift: compare feature distributions against the training reference and wait for delayed labels. While
investigating, consider a fallback (the previous model, or tighter rules), because a jump in approvals in a
fraud system is a direct loss.
</details>

## 9. [Interview] Lineage for an audit

An auditor asks which data and code produced the model that answered a specific customer on 3 March. List the
records your platform must keep, and where the chain most often breaks.

<details><summary>Answer</summary>

1. The prediction log row for the request, with the **model version** (and adapter version for LLMs) and the
   served feature values.
2. Registry: model version → training run ID.
3. Experiment tracker: run → code commit, container image digest, hyperparameters, seed, metrics, evaluation
   report.
4. Run → dataset snapshot ID (a lakehouse table version or file manifest with hashes) → feature definitions and
   source table versions.

The chain most often breaks at link 1 (predictions are not logged with the model version) and link 4 (training
read "the table as of now", not a snapshot). Retention is a related point: the logs must be kept long enough
for the audit window, which for regulated, high-risk AI systems is a legal question (see unit 28).
</details>

## 10. [Interview] Feedback loop in recommendations

Your recommender's click-through rate keeps rising offline with every retrain, but catalog coverage shrinks
and new items never get traction. Diagnose the problem and propose two mitigations.

<details><summary>Answer</summary>

This is a **direct feedback loop**: the model chooses what is shown, so it only collects labels for items it
already favors, and each retrain reinforces that. Offline metrics rise because the evaluation data was produced
by the same biased policy.

Mitigations (any two): a small exploration slice (random or uncertainty-driven candidates); propensity logging
plus inverse-propensity-weighted offline evaluation; a freshness or new-item boost in re-ranking; position as a
training feature, neutralized at serving time; and measuring coverage and diversity as guardrail metrics in the
evaluation gate. Each one costs some short-term CTR, which is a business trade-off to make explicitly.
</details>
