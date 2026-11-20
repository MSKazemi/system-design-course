# 08 — Asynchronous & event-driven systems (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/08-async-event-driven.md](../course/01-foundations/08-async-event-driven.md)

## Slide 1 — The requirement

- Lumen ingest: 2,000 events/s at peak, upload API < 150 ms p99
- Embedding takes seconds; the GPU fleet can be down for 30 minutes
- Never lose an upload, never bill a tenant twice
- Synchronous processing cannot meet the latency target

**Visual:** Upload arrow into a slow GPU box with a stopwatch showing 150 ms. Icons: `arch-user`, `arch-api-gateway`, `arch-worker`, `ops-latency`.

**Speaker notes:** The request path cannot wait for the GPU, so the work has to be handed off. Once work is handed
to another process over a network, loss, duplication and reordering become your problems. The rest of the
chapter is about handling them deliberately.

## Slide 2 — Why the buffer is there

- Decouples **time**: the consumer can be down
- Decouples **rate**: bursts are absorbed (Little's law still applies)
- Decouples **failure**: a worker crash becomes a delay, not an error page
- Price: the API can only answer "202 Accepted + job id"

**Visual:** Producer → buffer → consumer, with three labelled decoupling arrows. Icons: `arch-queue`, `pattern-backpressure`.

**Speaker notes:** Every box in an async design needs a reason. These three decouplings are the reason for the
broker. What you lose is the synchronous answer, so status has to be polled or pushed later.

## Slide 3 — Queue vs log

- Queue: per-message state, deleted on ack, competing consumers, native retry/DLQ
- Log: append-only, offset per consumer group, retained, replayable
- Kafka paper (NetDB 2011): stateless broker, offsets, time-based retention, rewind
- Commands → queue; facts → log

**Visual:** Side-by-side: queue handing m1/m2 to two workers; a partition with two groups at offsets 42 and 17. Icons: `messaging-rabbitmq`, `messaging-kafka`, `arch-event-stream`.

**Speaker notes:** These are two abstractions, not two vendors. RabbitMQ has streams and Kafka now has share
groups. Choose by semantics. Do you need to replay and fan out facts, or to hand out tasks with per-message retry?

## Slide 4 — Delivery semantics

- At-most-once: record, then work. A crash loses the message
- At-least-once: work, then record. A crash causes a duplicate (Kafka default)
- Exactly-once *delivery*: not on a lossy network between independent parties
- What you can build: exactly-once **effects**

**Visual:** Sequence: deliver m7 → commit → crash before ack → redeliver m7 → "applied twice?". Icons: `pattern-retry`, `ops-error`.

**Speaker notes:** The order of "do the work" and "record that it is done" decides the guarantee. Since losing
data is unacceptable, you pick at-least-once and then make duplicates harmless.

## Slide 5 — Idempotency keys

- Key generated **once** by the originator, reused on every retry
- Dedup record and effect commit **atomically**
- Keys have a retention horizon; size it to the maximum redelivery/replay window
- Example: Stripe saves the first response per key; keys prunable after 24 h

**Visual:** Same request sent twice with one key; second returns the stored response. Icons: `pattern-idempotency`, `pattern-deduplication`, `payments-stripe`.

**Speaker notes:** A key generated per attempt protects nothing. Keeping the dedup record and the effect in one
transaction is the part people most often get wrong.

## Slide 6 — The dual write and the outbox

- DB commit then publish: a crash in between loses the event
- Publish then commit: the event describes a row that does not exist
- Outbox: insert the event row in the **same** local transaction
- Relay (poll or CDC, e.g. Debezium) publishes; it is still at-least-once

**Visual:** API → one transaction (documents + outbox) → relay → broker. Icons: `sql-postgresql`, `pattern-transaction`, `arch-data-pipeline`, `messaging-kafka`.

**Speaker notes:** The outbox turns an impossible distributed atomic write into a local one. It does not remove
duplicates. It moves them downstream, where the inbox deals with them.

## Slide 7 — The inbox: idempotent consumer

- Unique `message_id` row and effect in one transaction
- Duplicate → constraint violation → ack without effect
- Outbox + inbox = exactly-once effects over at-least-once transport
- External side effects (payments, model APIs) need their own idempotency keys

**Visual:** Lab L08 result: balance with inbox vs naive (duplicates visible). Icons: `pattern-idempotency`, `arch-database`.

**Speaker notes:** This is what the lab demonstrates. Turn the inbox off and you can watch the balance go wrong
when a duplicate send and a crash before ack happen.

## Slide 8 — Kafka exactly-once, precisely

- Idempotent producer: producer ID + per-partition sequence numbers (KIP-98)
- Defaults since 3.0: `enable.idempotence=true`, `acks=all` (KIP-679)
- Transactions: atomic multi-partition writes; `sendOffsetsToTransaction`
- `read_committed` consumers; covers Kafka-to-Kafka only

**Visual:** consume → transform → produce loop wrapped in one transaction box. Icons: `messaging-kafka`, `pattern-transaction`.

**Speaker notes:** Kafka's exactly-once is real and scoped. As soon as the output is an external database, the
docs tell you to store the offset with the output. That is the inbox again.

## Slide 9 — Ordering and partition keys

- Order exists only within a partition / message group
- Key by the entity whose events must stay ordered (`document_id`)
- `tenant_id` keys create hot partitions
- Retries reorder; changing partition count remaps keys; use version numbers

**Visual:** Three partitions; one overloaded by a large tenant. Icons: `pattern-partitioning`, `pattern-sharding`.

**Speaker notes:** Global order needs a single sequencer and does not scale. Choose the smallest scope of order
the business actually needs, and make consumers tolerate the rest.

## Slide 10 — Backpressure, lag, poison, DLQ

- Prefetch bounds unacked deliveries; pull consumers slow only themselves
- Alert on **time-lag** (age of oldest unprocessed), not just depth
- Poison message + delivery limit → DLQ with reason (`x-death`)
- RabbitMQ 4.3+: `basic.reject` counts towards the limit, `basic.nack` requeue does not

**Visual:** Queue with a red message cycling, then exiting to a DLQ after N attempts. Icons: `pattern-backpressure`, `arch-queue`, `ops-alert`.

**Speaker notes:** A DLQ without an owner, an alert and a redrive tool is data loss with extra steps. The RabbitMQ
4.3 change is a good example of why you should read the release notes for your broker.

## Slide 11 — Sagas

- Garcia-Molina & Salem 1987: T1…Tn with compensations Cj…C1
- Choreography: services react to events; low coupling, implicit flow
- Orchestration: a coordinator owns the flow; explicit, must be durable
- No isolation: semantic locks (`PENDING`), idempotent compensations

**Visual:** State machine: reserve seat → charge → provision; failure arrows to refund → release. Icons: `pattern-saga`, `domain-payment`.

**Speaker notes:** Put the hardest-to-undo step as late as possible. Compensations are new business actions, such
as a refund entry, not rollbacks.

## Slide 12 — CQRS and event sourcing

- CQRS: separate write model and read projections (Greg Young, via Fowler)
- Event sourcing: events are the source of truth; replay rebuilds state
- Wins: audit, temporal queries, rebuildable projections
- Costs: schema evolution, replay side effects, snapshots, erasure; "risky complexity"

**Visual:** Event log feeding three projections (search, dashboard, vector index). Icons: `pattern-event-sourcing`, `arch-search-index`, `ops-dashboard`.

**Speaker notes:** Lumen's vector index is already a read model. Full event sourcing should be applied to the
bounded contexts that need audit and history, not to the whole system.

## Slide 13 — Frontier (as of 2026-11)

- Kafka 4.0 removed ZooKeeper (KRaft only); current release 4.4.0
- Kafka share groups (KIP-932) production-ready in 4.2
- RabbitMQ 4.4: quorum queues + streams; mirroring removed in 4.0
- Durable execution (Temporal): event history + replay; idempotent Activities
- LLM batch APIs: 50% price, 24 h window → design inference as queued jobs

**Visual:** Timeline 2011 Kafka paper → 2025 Kafka 4.0 → 2026 4.2 share groups → 4.4. Icons: `messaging-kafka`, `messaging-rabbitmq`, `domain-ai`.

**Speaker notes:** The building blocks are converging. Logs gain queue semantics, and orchestration moves into
durable-execution engines. Interviewers increasingly expect you to know both.

## Slide 14 — Interview wrap

- CLARIFY: result now or acceptance? ordering key? never lose / never twice?
- QUANTIFY: workers = rate × service time; drain time = backlog ÷ headroom
- SKETCH: API → DB + outbox → broker → idempotent consumers → DLQ
- STRESS: crash before ack, poison message, 30-min outage, hot tenant, replay
- WRAP: "at-least-once transport, exactly-once effects"

**Visual:** The six-step framework strip with the async sketch underneath. Icons: `arch-queue`, `pattern-idempotency`, `ops-slo`.

**Speaker notes:** The strongest signal in an interview is stating the guarantee precisely and showing which
mechanism provides each part of it. "We use Kafka so it is exactly-once" is the classic red flag.
