# 08 — Exercises

Lesson: [course/01-foundations/08-async-event-driven.md](../course/01-foundations/08-async-event-driven.md) ·
Lab: [labs/08-async-event-driven/](../labs/08-async-event-driven/README.md)

## 1. Crash before ack [Core]

A worker receives message `m7` ("credit account A with 10"), runs `UPDATE accounts SET balance = balance + 10`,
commits, and the process is killed before it acknowledges `m7`. The broker uses at-least-once delivery. What
happens next, and what is the smallest change that makes the outcome correct?

<details><summary>Answer</summary>

The broker never received an ack, so it redelivers `m7` when the consumer's channel or connection closes
(RabbitMQ) or when the visibility timeout expires (SQS). The new worker credits A a second time, and the balance
is now 10 too high.

The smallest fix is an **inbox / dedup table**. In the *same* transaction as the update, insert `m7`'s message ID
into a table with a primary-key constraint. On redelivery the insert conflicts, so the worker rolls back, acks,
and applies nothing. Two transactions (insert ID, then update) are not enough, because a crash between them
reopens the window.

Acceptable alternative: if the effect can be expressed as an overwrite with a version ("set balance to 110 as of
version 8"), a conditional update `WHERE version < 8` is idempotent without a separate table.
</details>

## 2. Queue or log? [Core]

For each Lumen flow, choose a work queue or a partitioned log and justify the choice in one sentence:
(a) "embed document 812" jobs; (b) "document uploaded" facts consumed by indexing, metering and analytics;
(c) password-reset emails; (d) the audit trail of ACL changes, which compliance wants to replay for any past date.

<details><summary>Answer</summary>

- (a) **Queue** (or Kafka share groups). These are commands with per-message retry and DLQ. Parallelism must scale
  with GPU workers, not with partition count.
- (b) **Log.** It is a fact with several independent consumer groups. New consumers can be added later and replay
  history.
- (c) **Queue.** One task per email, per-message retry with backoff, DLQ for bad addresses. Nobody needs a replay
  (and replaying would re-send emails).
- (d) **Log** (or an event-sourced store). Retention and replay are the requirement. Retention must be set to the
  compliance horizon, or the log must be archived to object storage.

The underlying rule: commands go to queues, facts go to logs. Mention that RabbitMQ streams and Kafka share
groups blur the product boundary, so the choice is about semantics.
</details>

## 3. Partitions from numbers [Interview]

Peak 3,000 events/s. Each event takes 200 ms of single-threaded work. You use Kafka with a classic consumer
group and one processing thread per partition. How many partitions do you need at minimum, and what would you
actually provision? What changes with a share group?

<details><summary>Answer</summary>

One thread processes 1 / 0.2 s = 5 events/s, so peak needs 3,000 / 5 = **600 concurrent processors**. In a
classic group a partition is consumed by at most one consumer in the group, so you need **≥ 600 partitions**.

Provision headroom for backlog drain and growth, for example 50% so the system can drain a backlog while peak
load continues: about 900. Then round to a count that divides evenly across expected consumer instances. Also
remember that adding partitions later remaps hash keys and breaks per-key ordering across the change, which is
another reason to over-provision up front.

With a **share group** (KIP-932) consumers are not bound one-to-one to partitions, so you can run 600+ consumers
on far fewer partitions. You lose strict per-partition ordering, because records in a partition are processed
concurrently. An alternative is fewer partitions with a per-key worker pool inside each consumer, which keeps
per-key order but takes more code.
</details>

## 4. Backlog drain time [Core]

The embedding fleet is down for 20 minutes while 1,500 events/s keep arriving. The fleet's capacity is
2,000 events/s. Load stays at 1,500/s after recovery. How long until the backlog is gone, and what is the worst
event age at that point?

<details><summary>Answer</summary>

Backlog = 1,500 × 1,200 s = **1.8 M events**. Net drain rate = 2,000 − 1,500 = 500 events/s, so drain time =
1.8 M / 500 = **3,600 s = 60 min**.

The event that arrived just as the outage started waits about 20 minutes plus its turn. Events arriving during
the drain wait behind the backlog. At FIFO, an event arriving at recovery waits roughly backlog / capacity =
1.8 M / 2,000 = 900 s = 15 min. So for about an hour, freshness is measured in minutes, not seconds.

Levers: more headroom (autoscale on time-lag), prioritising fresh events (serve live traffic first and drain the
backlog with spare capacity), or shedding non-critical work. If capacity equalled arrival rate, the backlog would
**never** drain.
</details>

## 5. The outbox still duplicates [Deep]

Explain precisely how a transactional outbox can publish the same event twice, and why the design is still
considered correct.

<details><summary>Answer</summary>

The relay reads outbox row `e-91`, publishes it, and the broker acks. Before the relay records "e-91 sent" (or
advances its CDC position), it crashes. On restart it reads from its last recorded position and publishes `e-91`
again. Richardson's pattern description lists exactly this issue.

It is still correct because the outbox's job is the **atomicity of state change and event**: the event exists if
and only if the transaction committed. Duplicates are then handled downstream by idempotent consumers (inbox or
versioned updates) keyed on the outbox row's stable `id`. Two cheap mechanisms (outbox plus inbox) give
exactly-once *effects* without 2PC.
</details>

## 6. Kafka transactions: what is covered? [Deep]

A stream processor reads `uploads`, computes per-tenant counters, writes them to topic `usage`, and also writes
an invoice row to Postgres. You enable Kafka transactions with `sendOffsetsToTransaction`. Which writes are
exactly-once, and how do you fix the rest?

<details><summary>Answer</summary>

The read of `uploads` (the offset commit) and the writes to `usage` commit atomically in one Kafka transaction,
so with `read_committed` downstream consumers the Kafka-to-Kafka path is exactly-once in effect (KIP-98).

The Postgres write is **outside** the transaction. If the processor writes Postgres and then the Kafka
transaction aborts, or the reverse, they diverge, and a retry after abort can write the invoice twice. Fixes:

- Write the invoice idempotently, using a primary key derived from the input (tenant + period), so retries are
  upserts.
- Or, as the Kafka docs advise for external sinks, store the consumed offset **in Postgres in the same
  transaction** as the invoice, and on restart resume from the offset stored in Postgres (the inbox pattern).
- Or move the Postgres write into a separate consumer of `usage` that is itself idempotent.
</details>

## 7. Poison message on RabbitMQ 4.4 [Lab]

A consumer handles any exception with `basic_nack(requeue=True)`. One message has a field that triggers a bug.
The quorum queue has a dead-letter exchange and the default delivery limit. What happens on RabbitMQ 4.4, and
what should the consumer do instead?

<details><summary>Answer</summary>

Since 4.3, the delivery limit is evaluated against `delivery-count`, and AMQP 0-9-1 `basic.nack` with requeue
does **not** increment it (before 4.3 it did). The message is redelivered in a loop, never reaches the limit and
never dead-letters. It burns CPU and log volume, and with low prefetch it delays other messages.

Better:
- Classify errors. For non-retryable ones (validation, parse, known-bad input), `basic_reject(requeue=False)`
  sends the message straight to the DLX.
- For retryable errors, use `basic_reject(requeue=True)`, which counts towards the limit, or better a
  delayed-retry queue with backoff.
- Keep the delivery limit and the DLX on every quorum queue, alert on DLQ depth, and give the DLQ an owner and a
  redrive tool.

Lab L08 uses `basic_reject` for both paths and shows `reason=delivery_limit` and `reason=rejected` in `x-death`.
</details>

## 8. Saga design [Interview]

Design the "upgrade to Pro" flow for Lumen: (1) charge the card via an external payment provider, (2) raise the
tenant's GPU quota, (3) migrate the tenant's index to a dedicated shard (can take 20 minutes), (4) send a
confirmation email. Choose orchestration or choreography, order the steps, and define the compensations.

<details><summary>Answer</summary>

**Orchestration**, ideally on a durable-execution engine. There are four steps, one is long-running with timeouts,
and support staff need to see where a given upgrade is stuck.

Order the steps by "hard to undo, and least likely to fail last":
1. Raise the quota with a `PENDING_UPGRADE` marker (semantic lock). Compensation: restore the old quota.
2. Migrate the index. Compensation: switch back to the shared shard and delete the copy. This is a long Activity
   with a heartbeat and a deadline.
3. **Charge the card (pivot).** Use an idempotency key derived from the saga ID so that retries cannot double-
   charge. Compensation if a later step must be undone: a refund, which is a new ledger entry.
4. Send the email. Retry until it succeeds, with no compensation, because steps after the pivot should be
   retriable rather than reversible.

Make every compensation idempotent, treat timeouts as failures, and accept that other readers may see
`PENDING_UPGRADE`. Acceptable alternative: charge first with an authorisation/hold and capture at the end, if the
provider supports holds, which makes the payment easier to compensate (void instead of refund).
</details>

## 9. Choosing the partition key [Core]

Lumen emits `ChunkEmbedded` events and needs, per document, that a `DocumentDeleted` event is never processed
before earlier `ChunkEmbedded` events for that document. The largest tenant produces 30% of all events. Which
partition key do you pick, and what residual risk remains?

<details><summary>Answer</summary>

Key by **`document_id`**. All events of one document land in one partition and are ordered. Documents spread
evenly, so the 30% tenant is spread across all partitions.

Keying by `tenant_id` would put 30% of the traffic on one partition: a hot partition whose lag dominates the
SLO.

Residual risks: (a) a single huge document is still serial, which is usually fine; (b) retries that requeue can
reorder, so the consumer should check a per-document version or tombstone ("ignore `ChunkEmbedded` for a
document already marked deleted"); (c) changing the partition count later remaps keys.
</details>

## 10. LLM batch import [Interview]

Lumen submits nightly summarisation jobs to a hosted model's batch API (50% price, 24 h window). Describe the
pipeline and the failure handling, including partial failures and expiry.

<details><summary>Answer</summary>

Pipeline: a scheduler selects documents → writes `batch_jobs` rows (one per request, `custom_id = doc_id +
prompt_version`) → a submitter packs them into batches within provider limits (for example 50,000 requests per
OpenAI batch, or 100,000 / 256 MB per Anthropic batch) → a poller checks batch status → an importer reads
results.

Failure handling:
- **Idempotent import.** Upsert summaries keyed by `custom_id`, so re-running the importer after a crash is
  harmless.
- **Partial failures.** Per-request errors are recorded and re-queued into the next batch with an attempt
  counter. Above N attempts they go to a DLQ table for inspection.
- **Expiry.** Requests not processed within 24 h come back as `expired` (Anthropic does not bill them). Re-submit
  them, or fall back to synchronous calls if the freshness SLO requires it.
- **Backpressure.** Respect the provider's queued-token limits and stop submitting when you approach them.
- **Versioning.** Including `prompt_version` in the key means a prompt change creates new work instead of being
  silently deduplicated.
</details>

## 11. Event sourcing: should we? [Deep]

A colleague proposes event-sourcing all of Lumen. Give two strong reasons to event-source the **ACL / sharing**
context and two reasons not to event-source the **chat message** context.

<details><summary>Answer</summary>

Event-source ACL/sharing:
1. Auditors and incident responders ask "who could see document X on date D?", which is a temporal query that
   event sourcing answers by replay.
2. Several read models (search filters, retrieval-time ACL checks, admin UI) can be rebuilt from the same history
   after a bug fix.

Do not event-source chat messages:
1. The domain is mostly append-and-read already. A plain table (or a log for fan-out) gives most of the value
   without upcasters and snapshots.
2. Chat content is personal data at high volume, and erasure requests conflict with an immutable event store
   (you would need crypto-shredding everywhere). Fowler's warning about "risky complexity" applies.
</details>
