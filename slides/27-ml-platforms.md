# 27 — ML platforms & data for AI (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The model is the small box
- A model is a function learned from data: change the data and you change the program
- Sculley et al.: only a small fraction of a real ML system is ML code
- A mature system can be "at most 5% ML code and at least 95% glue code"
- This unit covers the other 95%

**Visual:** Small black box (model) inside a large frame of labelled boxes (data, features, serving, monitoring).
**Speaker notes:** Open with the 2015 Sculley figure idea, redrawn. The point is that platform work is most of
ML engineering, and each platform box exists because a specific failure kept recurring.

## Slide 2 — The lifecycle as a system of contracts
- Data → validate → features → offline/online stores → train → evaluate → registry → serve → log → monitor
- Every arrow is a contract: schema, point-in-time, lineage, signature, logging
- Break one and you fail silently, not loudly

**Visual:** Lifecycle flowchart from the lesson. Icons: arch-data-pipeline, arch-database, arch-server, ops-metrics.
**Speaker notes:** Walk the loop once. Stress that labels flow back into the offline store, which is how the
loop closes.

## Slide 3 — Training-serving skew
- Zinkevich: a difference between performance in training and in serving
- Three causes: pipeline discrepancy, data change, feedback loop
- Example: `days_since_last_login` in UTC vs local time
- Fixes: define once and materialize twice; log served features (Rule #29)

**Visual:** Two pipelines computing "the same" feature, producing two histograms that do not overlap.
**Speaker notes:** The first cause is a bug you can design out, the second is drift you monitor for, and the
third is a product property you mitigate with holdouts.

## Slide 4 — Feature store anatomy
- Registry: entities, feature views, owners, TTLs
- Offline store: history with timestamps, built for scans
- Online store: latest value per key, millisecond point reads
- Ingestion: batch materialization plus streaming push; eventual consistency

**Visual:** Registry on top, offline store (columnar) on the left, online store (KV) on the right. Icons: cache-redis, nosql-dynamodb, data-spark, data-flink.
**Speaker notes:** Feast pushes values into the online store because pulling at request time would make
latency at least as long as the slowest source. Feast's docs say strong consistency is not guaranteed out of
the box.

## Slide 5 — Point-in-time correctness
- For an event at time t, use only values known at or before t
- Join on "latest" and the future leaks into training, so offline metrics lie
- Feast scans backward from each row's timestamp, bounded by the TTL
- `filter_by_created_timestamp` keeps backfilled corrections out

**Visual:** Timeline with values at 07:10, 09:41 and 10:05. The row at 10:00 picks 09:41; 10:05 is greyed as future; 07:10 is outside the TTL.
**Speaker notes:** If your training-set builder calls max(timestamp) without a bound, you have a leak.

## Slide 6 — Fine-tuning is the new training
- Full fine-tune with mixed-precision Adam needs 16 bytes per parameter (ZeRO)
- 7B parameters × 16 B = 112 GB of model states, more than one 80 GB GPU
- LoRA: 10,000× fewer trainable params and 3× less memory (GPT-3 175B)
- QLoRA: a 65B model fine-tuned on one 48 GB GPU

**Visual:** Stacked bars: full fine-tune 112 GB vs LoRA ~14 GB base vs QLoRA ~3.5 GB base, with an 80 GB line.
**Speaker notes:** Adapters also shrink checkpoints from 350 GB to about 35 MB in the LoRA paper's GPT-3 example,
which is what makes multi-LoRA serving practical.

## Slide 7 — Parallelism in one table
- Data parallel: replicate the model, split the batch
- ZeRO/FSDP: shard optimizer states, gradients and parameters
- Tensor parallel (Megatron): split matrices; keep it inside a node
- Pipeline parallel (GPipe): split layers into stages; micro-batches; bubbles

**Visual:** Four mini-diagrams of GPUs with model slices. Icon: arch-servers-cluster.
**Speaker notes:** Big runs combine them all. Topology and scheduling live in unit 23.

## Slide 8 — Failure is the steady state
- Llama 3 405B: 419 unexpected interruptions in 54 days
- About 78% hardware-related; GPU issues were 58.7%
- Young: checkpoint interval T ≈ √(2·C·M)
- C = 2 min, M = 186 min gives T ≈ 27 min; async sharded saves pay off

**Visual:** Sawtooth progress line with failures and rollbacks to the last checkpoint.
**Speaker notes:** Meta still reached more than 90% effective training time, by cutting checkpoint and start-up
time and diagnosing quickly with the NCCL flight recorder.

## Slide 9 — Registry and lineage
- Registered model → versions → aliases (`@champion`, `@challenger`)
- Promotion and rollback are one metadata write
- Lineage chain: prediction → model version → run → commit, image, data snapshot
- That chain answers the auditor's question

**Visual:** Chain of four linked boxes from prediction log to dataset snapshot.
**Speaker notes:** MLflow links each version to the run that produced it. Log the model version on every
prediction, or the chain breaks at the first link.

## Slide 10 — Two-tower retrieval plus ranking
- Funnel: ANN retrieval (~1000) → filters → ranking (~500) → re-rank (~50)
- Towers embed the user and items separately; relevance is a dot product
- Ranking adds cross features from the online feature store
- Version the query tower and the item index together

**Visual:** Funnel diagram from the lesson. Icons: arch-search-index, arch-cache, arch-user.
**Speaker notes:** Covington et al. split candidate generation from ranking; Yi et al. trained towers with
in-batch negatives and sampling-bias correction. Candidate counts are illustrative.

## Slide 11 — Drift: three distributions to watch
- Data drift: P(x) changes
- Concept drift: P(y|x) changes
- Prediction drift: cheap, label-free, often the first signal
- Check data quality first: bugs are a frequent cause of sudden drops

**Visual:** Three small histogram pairs (before/after).
**Speaker notes:** Rabanser et al. found that two-sample tests on classifier-reduced representations worked
best among the detectors they studied. Labels can take seconds or months.

## Slide 12 — Data contracts
- Schema, units, timezones, quality rules, freshness and volume SLOs, owner
- ODCS (Bitol) is one open YAML standard
- Enforce in producer CI and as a gate before training
- Fail loudly before training, not silently after deploy

**Visual:** A contract document between a producer box and a consumer box. Icons: domain-document, ops-check.
**Speaker notes:** Sculley et al. note that data dependencies cost more than code dependencies because no
compiler finds them. A contract is the closest thing to that compiler.

## Slide 13 — Interview angle
- CLARIFY: decision, latency, label delay, error costs
- QUANTIFY: online-store size, feature reads/s, index size
- DEEPEN: point-in-time, skew, two-tower, drift, checkpoints
- Red flags: "join on latest", no rollback, no label-delay story

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Interviewers want the system around the model. Name the contracts and the rollback path.
