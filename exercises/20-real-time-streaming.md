# 20 — Exercises

Lesson: [course/02-modern-requirements/20-real-time-streaming.md](../course/02-modern-requirements/20-real-time-streaming.md).
All numbers are labelled assumptions unless a source is cited in the lesson.

## 1. [Core] Dual writes versus CDC

A Lumen service saves a document in PostgreSQL and then publishes `DocumentUpdated` to Kafka from application code.
List two concrete failure sequences that leave the database and the stream inconsistent, then describe two designs that
avoid them.

<details><summary>Answer</summary>

Failure 1: the transaction commits, then the process crashes (or Kafka is unreachable and retries give up) before
publishing. The database has the change and the stream never will, so the vector index serves the old document
indefinitely. Failure 2: the service publishes first, then the transaction fails or rolls back. The stream contains a
change that never happened, and the index now holds content the source of truth does not.

Design A, **CDC on the table**: Debezium reads committed changes from the WAL through logical decoding, so the stream is
derived from what was committed, in commit order. Design B, the **outbox pattern**: write a `DocumentUpdated` row into an
`outbox` table in the *same* transaction as the document change, and ship outbox rows with CDC (Debezium's Outbox Event
Router routes by `aggregatetype` and keys by `aggregateid`). Use B when consumers need stable domain events rather than
raw table rows, since it decouples the event contract from the table schema. A transactional "publish then commit" with
2PC across PostgreSQL and Kafka is possible in theory but rarely worth the operational cost.
</details>

## 2. [Core] Event time windows during an outage

Lumen's usage consumer is down from 10:00 to 10:20, then catches up by 10:30. Sketch what a per-minute "tokens used"
chart looks like if windows use processing time, and if they use event time with a 30 s out-of-orderness bound.

<details><summary>Answer</summary>

**Processing time:** minutes 10:00–10:19 show zero (nothing was processed), then 10:20–10:30 show a large spike as twenty
minutes of backlog is processed and counted in the minutes in which it was *processed*. The chart says "outage, then a
burst of usage". That is false, and if it fed rate alerts it would page someone twice.

**Event time:** each event lands in the minute in which it *happened*. During catch-up the watermark advances quickly
through 10:00…10:20 as backlog is processed, so the windows fire in order, late in wall-clock terms but with correct
values. The chart shows the true usage curve. The only visible effect is that those points appeared late; the freshness
SLI ("age of the newest complete window") burns during the outage, which is the correct signal.
</details>

## 3. [Core] The stuck watermark

A Flink job reads a 12-partition topic. Eleven partitions receive traffic; partition 7 has received nothing for an hour
because its producer was decommissioned. Event-time windows have stopped firing, although CPU is busy. Explain, and give
two fixes.

<details><summary>Answer</summary>

An operator's watermark is the **minimum** of its input watermarks. Partition 7's watermark has not advanced for an hour,
so the source's combined watermark stays an hour behind and no window whose end is after it can fire. The job keeps
processing events and accumulating state (CPU busy, state growing) but emits nothing.

Fix 1: configure **idleness** on the watermark strategy (`withIdleness(Duration.ofMinutes(1))` in Flink) so an input with
no events for that long is marked idle and excluded from the minimum. Fix 2: remove the dead partition from the pipeline,
for example by repartitioning into a topic sized for the actual producers, or have producers emit periodic heartbeat
events. Also add an alert on watermark lag (wall-clock time minus current watermark) per operator, so this is detected
in minutes and not discovered from a stale dashboard.
</details>

## 4. [Deep] Visibility delay of exactly-once sinks

A Flink job aggregates usage and writes to Kafka with `DeliveryGuarantee.EXACTLY_ONCE`. The checkpoint interval is 30 s
and checkpoints take 4 s on average. (a) What end-to-end delay do `read_committed` consumers see, roughly? (b) What setting
must be larger than what, and what happens if it is not? (c) Why would you *not* use this sink for the RAG index?

<details><summary>Answer</summary>

(a) Records are written into a Kafka transaction that commits only when the checkpoint completes. A record produced just
after a checkpoint started waits for the next one: up to ~30 s (interval) + ~4 s (checkpoint duration) before it becomes
visible, about 17 s on average for uniformly arriving records, plus normal processing latency. Readers with
`read_uncommitted` see records earlier but also see aborted ones, which defeats the purpose.

(b) The producer's `transaction.timeout.ms` must exceed the maximum checkpoint duration plus the maximum restart time.
Otherwise the broker aborts an open transaction while the job is recovering, and the records in it are lost even though
the checkpoint believed they would be committed. Note that brokers also cap the transaction timeout with their own
maximum setting, so both sides need checking.

(c) The RAG freshness budget is 5 s p99. The visibility delay alone exceeds it. The vector index has a natural key
(`doc_id`, `chunk_no`) and a version, so at-least-once delivery with idempotent, version-checked upserts gives
effectively-once results with only processing latency. Duplicates are harmless overwrites.
</details>

## 5. [Deep] Three layers of exactly-once

Classify each as guaranteed or not guaranteed by Kafka Streams with `processing.guarantee=exactly_once_v2`, and justify:
(a) a per-tenant count stored in a state store; (b) the output topic `tenant-usage`; (c) an HTTP POST to the billing
provider inside a `foreach`; (d) a row written to PostgreSQL by a separate consumer of `tenant-usage` using
`read_committed`.

<details><summary>Answer</summary>

(a) **Guaranteed.** State-store updates are backed by changelog topics written inside the same transaction as the input
offset commit, so after a crash the store reflects each input exactly once.

(b) **Guaranteed** for `read_committed` readers: output writes, changelog writes and offset commits commit atomically
(this requires brokers 2.5 or newer for v2).

(c) **Not guaranteed.** The HTTP call is an external side effect outside the Kafka transaction. On a crash after the call
but before commit, the record is reprocessed and the POST is repeated. Use an idempotency key derived from the input
(for example tenant + window + version) that the billing provider de-duplicates, or move the call to a separate consumer
that records "sent" keys transactionally in its own store.

(d) **Not guaranteed by Kafka Streams.** It is a separate system. The consumer must make writes idempotent (upsert by
`(tenant, window)` key) or store consumed offsets in the same PostgreSQL transaction as the row, then read them back on
restart.
</details>

## 6. [Core] Choose the window

For each Lumen metric pick a window type and justify: (a) invoiced tokens per tenant per hour; (b) "error rate over the
last 5 minutes, updated every 30 s" for alerting; (c) number of distinct chat sessions per user per day, where a session
ends after 30 minutes of inactivity.

<details><summary>Answer</summary>

(a) **Tumbling 1-hour event-time windows**, keyed by tenant: non-overlapping periods that sum exactly to the invoice
total. Allow lateness long enough for realistic client delays and reconcile daily against the source of truth.

(b) **Sliding (hopping) window**, 5 minutes size, 30 s slide. Each event belongs to 10 windows, so state is ~10× a tumbling
window; acceptable for a low-cardinality key such as service name. For alerting, a short out-of-orderness bound matters
more than completeness.

(c) **Session windows** with a 30-minute gap per user, then a tumbling daily count of closed sessions. Sessions can merge
when a late event bridges two of them, so the downstream count must accept updates.
</details>

## 7. [Core] Capacity and drain time

Assume a peak of 40,000 events/s, each subtask handles 8,000 events/s, and the topic has 6 partitions. (a) How many
subtasks are needed at peak with no headroom, and can 6 partitions support the headroom you want? (b) The consumer is down
for 15 minutes at peak. How long does catch-up take with 10 subtasks (assume enough partitions)?

<details><summary>Answer</summary>

(a) 40,000 / 8,000 = **5 subtasks** with zero headroom. With 6 partitions, a Kafka source can use at most 6 parallel
readers, giving 48,000 events/s capacity, only 20% headroom. For 2× headroom you need 10 subtasks and at least 10
partitions. Because adding partitions to a keyed topic changes key placement, create, say, 12–24 up front.

(b) Backlog = 40,000 × 900 s = 36 M events. Capacity with 10 subtasks = 80,000 events/s; net drain = 80,000 − 40,000
= 40,000 events/s; catch-up = 36 M / 40,000 = **900 s (15 minutes)**. With 6 subtasks the net drain is only 8,000 events/s
and catch-up takes 4,500 s (75 minutes), while freshness SLOs burn the whole time. Headroom is a recovery-time decision.
</details>

## 8. [Deep] The replication slot incident

The analytics team pauses a Debezium connector for a migration "for a few days". Two days later the OLTP primary runs
out of disk. Explain the causal chain, the metric that would have warned you, and three preventions.

<details><summary>Answer</summary>

The connector's logical replication slot remains while the connector is paused. PostgreSQL keeps all WAL from the slot's
restart position onwards so the consumer can resume without gaps. With `max_slot_wal_keep_size = -1` (the default),
retention is unlimited, so WAL accumulates at the database's write rate until the volume is full and the primary stops
accepting writes. The analytics pipeline has taken down the system of record.

Warning metric: retained WAL per slot (from `pg_replication_slots`, for example the distance between the current WAL
position and the slot's restart position) and free disk on the WAL volume, with alerts well before the limit.

Preventions: (1) set `max_slot_wal_keep_size` so a stalled slot is invalidated instead of filling the disk, accepting that
the connector must re-snapshot (`snapshot.mode=when_needed` handles a missing position); (2) on PostgreSQL versions that
support it, set `idle_replication_slot_timeout`; (3) treat slots as part of the connector lifecycle: pausing for more than
a few hours means dropping the slot and planning an incremental snapshot on resume; and keep WAL on a volume sized and
alerted for this case.
</details>

## 9. [Interview] Design: fresh RAG answers

"Lumen's enterprise customers complain that the assistant quotes outdated policy documents. Design the pipeline that
keeps retrieval fresh." Give a 5-step answer using the course framework, including the freshness SLI and how deletions are
handled.

<details><summary>Answer</summary>

**CLARIFY:** freshness target (here: 5 s p99 from commit to retrievable), document sizes and edit rate, whether ACL changes
must also propagate (yes — a revoked share is a security issue), multi-tenancy, embedding model and its latency.

**QUANTIFY:** for example 2,000 document edits/s at peak, about 20 chunks per document of which ~2 change per edit, so
~4,000 chunk embeddings/s at peak; the embedding service capacity and its cost per 1k chunks; vector-index upsert rate.

**SKETCH:** PostgreSQL → Debezium (documents, ACL tables) → Kafka keyed by `doc_id` → Flink job that keeps the previous
chunk hashes per document in keyed state, diffs, embeds only changed chunks (batched), upserts by `(doc_id, chunk_no)` with
a version check, and deletes removed chunks. ACL changes update chunk metadata used for filtering at query time.

**DEEPEN:** at-least-once with idempotent upserts (not transactional sinks, whose checkpoint-bound visibility would break
the 5 s budget); deletes from CDC `d` events and tombstones delete every chunk of the document; replay after an
embedding-model upgrade runs a new job version writing into a new index, then switches (Kappa).

**STRESS/WRAP:** a bulk import of 1 M documents must not starve interactive edits (separate priority topic or rate-limited
backfill); the embedding service is down (buffer in Kafka, alert on freshness); SLI measured with canary documents
edited every minute and queried until retrievable. Close with the freshness SLO and a daily reconciliation of index
contents against the database.
</details>

## 10. [Lab] Build a minimal CDC pipeline yourself (self-directed)

This unit has no maintained lab. Sketch an experiment you could run with Docker Compose to observe (a) the CDC event
format, (b) WAL retention when the connector is stopped, and (c) at-least-once duplicates after a crash. List components,
the steps and what to measure. (Pin image tags to current stable versions when you build it, and record what you
observe, not what you expect.)

<details><summary>Answer</summary>

Components: PostgreSQL with `wal_level=logical`; a Kafka broker in KRaft mode; Kafka Connect with the Debezium
PostgreSQL connector; a small consumer script that prints events and counts duplicates by event key + log position.

Steps: (a) create a table, register the connector with `plugin.name=pgoutput`, insert/update/delete rows, and inspect
`before`/`after`/`op`/`source`; change `REPLICA IDENTITY` to `FULL` and compare `before` on updates. (b) Stop Connect, run a
write loop for a few minutes, and watch retained WAL for the slot grow in `pg_replication_slots`; restart and confirm the
connector resumes; then set a small `max_slot_wal_keep_size` and repeat until the slot is invalidated, and observe the
connector's behaviour. (c) Kill the Connect container with `kill -9` during a write burst, restart, and count duplicates
seen by the consumer.

Measure: event latency (commit time vs consumer receive time), retained WAL size over time, duplicate count after crash.
Expected qualitative result: duplicates are possible after a crash (at-least-once), which is why downstream sinks must be
idempotent. Any numbers you report must be your own observations with versions and date.
</details>

## 11. [Interview] Hot tenant

One tenant generates 40% of all usage events. Your per-tenant aggregation job has one subtask at 100% CPU while the
others idle, and lag grows only on that subtask's partitions. Propose a fix and explain its cost.

<details><summary>Answer</summary>

Keyed processing sends every event of a key to one subtask, so one key can exceed one subtask's capacity regardless of
total parallelism. Fix: **salting with two-phase aggregation**. Key the first stage by `(tenant, hash(event_id) mod N)` to
spread the hot tenant over N subtasks, pre-aggregate per window, then key the second stage by `tenant` to combine the N
partial results. Costs: an extra shuffle and operator, more state (N partial windows), and the final result appears one
stage later. Apply salting only to known hot keys (configured or detected) to avoid the overhead for everyone. Also check
the Kafka side: if the producer keys by tenant, the hot tenant's partition is itself a bottleneck, so producers may need
to key by event or document instead, with the processor doing the per-tenant grouping.
</details>

## 12. [Deep] Pick an analytics store

Lumen's dashboard must (a) show per-tenant usage at ≤ 10 s freshness, (b) correct the latest status of each conversation
("open", "resolved") as it changes, and (c) serve a few hundred concurrent tenant admins. Compare Druid, Pinot and
ClickHouse for this, naming one risk per option.

<details><summary>Answer</summary>

**Druid**: time-partitioned columnar segments, streaming data is queryable on ingest, and Kafka ingestion is exactly-once
by offsets. Strong for (a) and (c). Risk for (b): updating a conversation's status is not its natural mode; you would model
status changes as events and compute "latest" at query time, or re-ingest.

**Pinot**: real-time upsert tables fit (b) directly (full or partial upsert by conversation ID, newest by comparison
column) and it targets user-facing concurrency. Risks: the stream must be partitioned by primary key, memory grows with
distinct keys, and the partition count cannot grow later for upsert tables, so capacity planning must be done up front.

**ClickHouse**: very fast aggregations with SQL; ingest via Kafka engine + materialized view. For (b) a `ReplacingMergeTree`
keyed by conversation ID works, but deduplication happens at merge time with no guarantee, so queries need `FINAL` (or
`argMax`-style queries) or they over-count. Risk: forgetting that and showing inflated numbers.

Any of the three is defensible; the reasoned answer names the update semantics and the operational risk, and proposes a
benchmark on Lumen-shaped data before deciding.
</details>
