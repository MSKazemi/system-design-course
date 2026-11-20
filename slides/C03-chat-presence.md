# C03 — Chat & presence (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C03-chat-presence.md](../course/04-case-studies/C03-chat-presence.md)

## Slide 1 — The requirement

- 100 M DAU; 1:1 and groups up to 1,000
- Online delivery p99 < 500 ms to every device
- Ordered history, offline delivery, multi-device
- Presence, typing — and an E2EE mode

**Visual:** Three devices of one user lighting up with the same message; a lock icon for E2EE.
Icons: `domain-chat`, `arch-mobile-client`, `arch-desktop`, `security-encryption`.

**Speaker notes:** Chat is the mainstream workload with tens of millions of long-lived stateful connections, and
ordering mistakes are visible to humans.

## Slide 2 — The numbers

- ≈ 139,000 messages/s at peak
- ≈ 8 recipients per message → ≈ 670,000 device deliveries/s
- 60 M concurrent WebSocket connections → ≈ 300 gateways
- ≈ 1.2 TB/day stored, ≈ 1.3 PB/year with replicas

**Visual:** Four counters; the connection counter is the biggest.
Icons: `ops-throughput`, `protocol-websocket`, `arch-storage-disk`.

**Speaker notes:** Labelled assumptions. Connection count and delivery fan-out are the hard numbers, not message rate.

## Slide 3 — Sketch

- L4 LB → WebSocket gateways (connection state only)
- Session registry: device → gateway (soft state)
- Conversation owner = sequencer → message store
- Router → recipient gateways or offline queue → push

**Visual:** The lesson's flowchart.
Icons: `arch-load-balancer`, `protocol-websocket`, `arch-microservice`, `nosql-cassandra`, `domain-notification`.

**Speaker notes:** Slack publishes the same split: gateway servers, channel servers by consistent hashing, admin
servers, presence servers.

## Slide 4 — Wire protocol

- SEND carries `client_msg_id` (idempotency key)
- ACK returns `seq`; MSG carries `seq`
- RECV / READ are cursors, not per-message rows
- HELLO resumes with `last_seen` per conversation

**Visual:** Frame list with arrows device ↔ server.
Icons: `protocol-websocket`, `pattern-idempotency`.

**Speaker notes:** Cursors make receipts O(1) per update and make resume cheap.

## Slide 5 — One owner per conversation

- Consistent hashing on `conv_id` → owner assigns `last_seq + 1`
- Total order per conversation; no global order needed
- Failover stalls a conversation briefly (Slack: new channel server < 20 s)
- Leases + fencing tokens stop a stale owner

**Visual:** Ring of owners; one conversation's sends converge on one node.
Icons: `pattern-consistent-hashing`, `pattern-leader-election`, `security-lock`.

**Speaker notes:** Client timestamps and per-region clocks cannot give everyone the same order.

## Slide 6 — Exactly once is built, not given

- Transport: at least once (retries, resume)
- Sender dedupe: `(conv_id, client_msg_id) → seq`
- Receiver dedupe: render by `(conv_id, seq)`, buffer gaps, fetch missing ranges
- Same idempotency pattern as payments (C06)

**Visual:** Sequence diagram from the lesson.
Icons: `pattern-idempotency`, `pattern-retry`, `pattern-deduplication`.

**Speaker notes:** "Exactly-once delivery" claimed from the network alone is a red flag.

## Slide 7 — Storage that survives success

- Partition `(conv_id, bucket)`, cluster by time-sortable ID
- Discord 2017: ~10-day buckets to keep partitions < 100 MB
- Discord 2023: 177 Cassandra → 72 ScyllaDB nodes; p99 fetch 40–125 ms → ≈ 15 ms
- Data services coalesce identical reads, routed by channel hash

**Visual:** One long conversation history cut into bucket blocks; many identical reads merging into one DB call.
Icons: `nosql-cassandra`, `nosql-scylladb`, `company-discord`, `pattern-partitioning`.

**Speaker notes:** Bound partitions by time; put a coalescing data service in front of hot partitions.

## Slide 8 — Offline and multi-device

- Store first, deliver second; the store is the inbox
- Resume: missed messages or "sync required" per conversation
- Push only when no device is online; collapse and rate-limit
- Each device has its own delivery cursor; read cursor syncs

**Visual:** Phone offline → push; laptop online → live; both converge on the same read cursor.
Icons: `domain-notification`, `arch-mobile-client`, `arch-desktop`.

**Speaker notes:** Treat platform push services as an external API with budgets and backoff.

## Slide 9 — Presence without a storm

- Derive presence from the connection; TTL entries; write on change
- Subscribe lazily to users on screen
- Big groups: counts, not live dots
- Discord 2017: one event in a 30,000-user guild took 900 ms–2.1 s to publish → Manifold

**Visual:** Eager fan-out (2.8 M events/s, exercise 6) vs lazy (≈ 93,000 /s).
Icons: `pattern-fan-out`, `ops-clock`, `company-discord`.

**Speaker notes:** Presence is a hint with 30 s staleness tolerance — design it as cheap, approximate state.

## Slide 10 — Failures

- Gateway crash → reconnect storm: jitter, admission control, cheap resume
- Owner failover → short stall, retries with same `client_msg_id`
- Hot group → topic fan-out, coalescing, slow mode
- Never ACK before the durable write

**Visual:** Spike of reconnects flattened by jitter.
Icons: `ops-incident`, `pattern-retry`, `pattern-backpressure`.

**Speaker notes:** Measure delivery with synthetic conversations between probe devices; servers cannot see the last
hop.

## Slide 11 — E2EE with MLS (RFC 9420)

- Group key agreement with forward secrecy and post-compromise security
- Costs grow logarithmically with group size (ratchet tree)
- Server becomes the Delivery Service; stores KeyPackages
- RCS Universal Profile 3.0 adopts MLS (GSMA, March 2025)

**Visual:** Ratchet tree with a member update touching only one path.
Icons: `security-encryption`, `security-key`, `domain-chat`.

**Speaker notes:** RFC 9750 says groups must agree on one Commit per epoch, and most Delivery Services order
handshake messages — that is our sequencer.

## Slide 12 — AI assistants in chat

- On-device models: E2EE-compatible, device-limited
- Confidential computing: WhatsApp Private Processing (TEE + OHTTP, stateless, user-initiated)
- Oblivious HTTP = RFC 9458
- Either way: a new trust boundary and an LLM serving workload (C09)

**Visual:** Two paths from a chat: into the phone's chip, or through an OHTTP relay into an attested enclave.
Icons: `domain-ai`, `security-encryption`, `company-whatsapp`.

**Speaker notes:** Sending plaintext to a normal LLM API breaks the E2EE promise.

## Slide 13 — WRAP

- Junior: WebSockets, message table, offline delivery, push
- Senior: registry, sequencer, idempotent sends, cursors, buckets, reconnect storms, lazy presence
- Staff: connections as capacity driver, failover cost, multi-region homing, synthetic SLOs, E2EE role change
- Red flags: polling, client-timestamp order, unbounded partitions, server search in "E2EE"

**Visual:** Staircase junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** The strongest answers show where each guarantee comes from: order from the sequencer, no
duplicates from idempotency keys, durability from ACK-after-write.
