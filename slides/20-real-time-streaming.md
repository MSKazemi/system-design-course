# 20 — Real-time & streaming systems (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/02-modern-requirements/20-real-time-streaming.md](../course/02-modern-requirements/20-real-time-streaming.md)

## Slide 1 — The requirement

- A fixed price in a document must stop being quoted within 5 s (p99)
- Tenant usage dashboards at most 10 s stale, at 50,000 events/s peak
- Billable tokens: never lost, never counted twice — even through crashes
- Nightly batch fails the first two; a naive stream fails the third

**Visual:** Three requirement cards (freshness, freshness, exactness) over a Lumen logo placeholder. Icons: `domain-document`, `ops-dashboard`, `domain-payment`.

**Speaker notes:** This unit starts from three concrete promises. Two are about time and one is about correctness, and they pull the design in different directions. By the end we will choose a different delivery guarantee for each sink.

## Slide 2 — Four boxes and why each exists

- PostgreSQL: system of record
- CDC (Debezium): every committed change, in order, no trust in app code
- Kafka: durable, replayable, partitioned log; consumers go at their own pace
- Flink: stateful work — diffs, windows, deduplication
- Sinks differ because requirements differ

**Visual:** Pipeline flowchart PostgreSQL → Debezium → Kafka → Flink → {vector index, OLAP, billing topic, feature store}. Icons: `sql-postgresql`, `messaging-kafka`, `data-flink`, `arch-search-index`, `nosql-clickhouse`.

**Speaker notes:** For every box, say why it is there. The database is the truth, CDC derives a stream from it, the log decouples consumers, and the processor holds state. The sinks are where the requirements finally diverge.

## Slide 3 — CDC beats dual writes

- Dual write: DB commit + publish → crash in between = permanent disagreement
- CDC reads the WAL via logical decoding (`pgoutput` built in since PostgreSQL 10)
- Events carry `before`, `after`, `op`, `source`, timestamps
- Outbox pattern: domain events written in the same transaction, shipped by CDC

**Visual:** Split screen: left, app writing to DB and Kafka with a crash bolt between; right, app writing only to DB, CDC tapping the log. Icons: `arch-database`, `pattern-transaction`, `messaging-kafka`.

**Speaker notes:** The stream is derived from the committed log, so it cannot disagree with it. When you need domain events instead of row changes, the outbox table keeps the same guarantee.

## Slide 4 — Two clocks

- Event time: when it happened on the producing device
- Processing time: the clock of the machine processing it
- Processing-time buckets turn an outage into a hole plus a fake spike
- Event time is right — but when is a window "complete"?

**Visual:** Two timelines; events drawn at their event time on top, at their arrival time below, with crossing arrows showing reordering. Icons: `ops-clock`.

**Speaker notes:** Lumen's dashboard must show what actually happened, not when we happened to see it. That choice creates the completeness question the rest of the unit answers.

## Slide 5 — The Dataflow model's four questions

- What is computed? (aggregation)
- Where in event time? (windows)
- When in processing time? (watermarks, triggers)
- How do refinements relate? (accumulation: overwrite, accumulate, retract)
- Trade-off: correctness vs latency vs cost

**Visual:** 2×2 grid of the four questions with Lumen answers. Icons: `arch-data-pipeline`.

**Speaker notes:** Akidau et al. argue you never know you have seen all the data, so you choose a trade-off deliberately. These four questions are a checklist for any streaming design.

## Slide 6 — Watermarks

- `Watermark(t)`: no more events with timestamp ≤ t expected
- Bounded out-of-orderness: max timestamp − bound; pick the bound from measured delay
- Operator watermark = minimum of its inputs → one idle partition stalls everything
- Fixes: idleness timeout; alignment for sources that race ahead

**Visual:** Several partition lanes with watermark flags; the slowest lane's flag pins the operator's watermark. Icons: `ops-clock`, `ops-latency`.

**Speaker notes:** The min-of-inputs rule explains most "my windows never fire" incidents. Idleness detection and watermark alignment are the two knobs for the two opposite failure modes.

## Slide 7 — Windows, triggers, lateness

- Tumbling, sliding, session windows
- Default trigger: fire when the watermark passes window end
- Allowed lateness / grace period: late events update the result
- After that: drop or send to a side output
- Consequence: sinks must accept updates (upsert by window key)

**Visual:** State diagram Open → Fired → (late updates) → Purged → side output. Icons: `ops-clock`, `pattern-deduplication`.

**Speaker notes:** A window can emit more than once. If the sink appends instead of overwriting, late events double-count.

## Slide 8 — State and barrier checkpoints

- Keyed state lives in a state backend (heap or on-disk LSM)
- Barriers flow with data; operator snapshots once barrier n arrives on all inputs
- No global pause: Asynchronous Barrier Snapshotting, a Chandy–Lamport variant
- Restore = last checkpoint + rewind sources to recorded offsets
- Checkpoints for crashes, savepoints for upgrades

**Visual:** Flowchart of two sources sending barriers into a join, then window, then sink, acking to the job manager. Icons: `data-flink`, `pattern-backup`, `arch-storage-disk`.

**Speaker notes:** The barrier is the consistent cut. Under backpressure, aligned barriers crawl, which is why unaligned checkpoints and buffer debloating exist.

## Slide 9 — Exactly-once, honestly

- Layer 1: state exactly once (checkpoints)
- Layer 2: output log exactly once (Kafka transactions, read_committed)
- Layer 3: external side effects — needs idempotency keys
- Kafka Streams `exactly_once_v2`; Flink sink commits on checkpoint completion
- Price: visibility delay of up to one checkpoint interval plus the checkpoint duration; stuck transactions block readers

**Visual:** Sequence diagram: write in txn → barrier → pre-commit → checkpoint complete → commit → visible. Icons: `pattern-idempotency`, `messaging-kafka`, `data-flink`.

**Speaker notes:** KIP-98 gives Kafka idempotent producers and transactions. Exactly-once is real for read-process-write pipelines in Kafka, but not for emails or HTTP calls made inside the job.

## Slide 10 — One guarantee per sink

- Vector index: at-least-once + upsert by (doc_id, chunk_no) with version check
- Billing totals: transactional exactly-once, checkpoint every 60 s
- Invoice creation: external idempotency key
- Why: a 10 s checkpoint alone would exceed the 5 s freshness budget

**Visual:** Table of sinks vs guarantee with a stopwatch on the vector-index row. Icons: `arch-search-index`, `domain-payment`, `ops-slo`.

**Speaker notes:** This is the key design decision of the unit. Exactness where totals matter, idempotent overwrite where latency matters.

## Slide 11 — Stream–table duality and analytics stores

- Stream = changelog; table = latest value per key
- Flink dynamic tables: append-only, retract, upsert encodings
- Druid: time-partitioned segments, data queryable on ingest
- Pinot: upserts, stream must be partitioned by primary key
- ClickHouse: ReplacingMergeTree dedups eventually; use `FINAL` or design idempotently

**Visual:** A table morphing into a stream of change events and back. Icons: `arch-event-stream`, `arch-database`, `nosql-clickhouse`, `domain-analytics`.

**Speaker notes:** Whether a sink accepts upserts decides whether a grouped aggregation is a valid streaming query for it. Each analytics store takes a different stance on updates.

## Slide 12 — How it breaks

- Consumer lag — measure in seconds, not records
- Stuck watermark from an idle partition
- Hot key on one subtask
- Unbounded state; checkpoint timeouts
- Replication slot pins WAL → primary disk fills

**Visual:** Dashboard mock with five red tiles and their SLIs. Icons: `ops-alert`, `ops-metrics`, `sql-postgresql`.

**Speaker notes:** The replication-slot failure is the classic surprise: an analytics consumer stops and the OLTP primary goes down. Set a WAL limit and alert on retained WAL.

## Slide 13 — Numbers and freshness for AI

- 50 MB/s peak ingress; ≈ 27 TB for 7 days at RF 3 (assumptions)
- 10-minute outage at peak → 600 s drain with 2× headroom
- Real-time RAG: diff chunks → embed changed chunks → upsert; deletes too
- Streaming features: push into the online store; keep online/offline consistent

**Visual:** Freshness budget bar: 0.5 + 0.2 + 0.3 + 1.5 + 1.5 + 1.0 = 5.0 s. Icons: `domain-ai`, `arch-search-index`, `ops-latency`.

**Speaker notes:** All numbers are labelled assumptions from the lesson. Headroom is a freshness decision, and the freshness SLI for RAG is commit-to-retrievable, measured with canary documents.

## Slide 14 — Interview angle

- CLARIFY freshness, exactness, event-time semantics, lateness
- QUANTIFY events/s, size, retention, key cardinality, state
- SKETCH CDC/outbox → log → stateful processor → per-requirement sinks
- DEEPEN watermarks and guarantees; STRESS hot keys, outages, replays
- Red flags: dual writes, processing-time business metrics, "Kafka is exactly-once so we're done"

**Visual:** The six-step framework strip with streaming keywords under each step. Icons: `ops-check`.

**Speaker notes:** A strong answer names a freshness SLO and a completeness check, and explains the latency cost of exactly-once. Close with reconciliation against the source of truth.
