# C03 — Exercises

Lesson: [course/04-case-studies/C03-chat-presence.md](../course/04-case-studies/C03-chat-presence.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Connections, not messages

30 M DAU, 50 % online at peak, 1.8 devices per online user, 200,000 connections per gateway at most, and you want to
survive losing 20 % of gateways. How many gateways? If each connection costs 20 KB of memory, how much per gateway?

<details><summary>Answer</summary>

Connections = 30 M × 0.5 × 1.8 = 27 M → 27 M / 200,000 = 135 gateways at full load. To absorb a 20 % loss the remaining
80 % must carry everything: 135 / 0.8 ≈ **169 gateways** (round to 170+). Memory ≈ 200,000 × 20 KB = 4 GB at full load.
The insight: connection count, plus failure headroom, sizes this tier — not message throughput.
</details>

## 2. [Core] Delivery fan-out

60 % of messages are 1:1, 40 % are in groups averaging 50 members. 30 % of recipients are online, each with 1.4
devices. At 80,000 messages/s, how many device deliveries per second?

<details><summary>Answer</summary>

Recipients per message = 0.6 × 1 + 0.4 × 49 = 20.2. Online = 20.2 × 0.3 = 6.06 users × 1.4 = 8.5 devices →
80,000 × 8.5 ≈ **680,000 deliveries/s**. Groups dominate: the 40 % of group messages produce ≈ 97 % of deliveries. This
is why large groups use topic-based fan-out to gateways (publish once per gateway) rather than one RPC per device.
</details>

## 3. [Deep] Why a per-conversation sequencer?

Two members send at the same moment from different continents. Compare ordering by (a) client timestamp, (b) server
receive timestamp in each region, (c) a per-conversation owner assigning `seq`. Which guarantees every member sees the
same order? What does (c) cost when the owner fails?

<details><summary>Answer</summary>

(a) Client clocks are wrong by seconds or more; members may see different orders and replies before their parents.
(b) Two regions' clocks and arrival times differ; without coordination there is no single order. (c) One owner assigns
`last_seq + 1` atomically, so all members render the same total order. Cost: when the owner fails, sends to its
conversations stall until a new owner takes the lease (Slack reports a replacement channel server ready in under
20 s). Use leases with fencing tokens so a partitioned old owner cannot keep issuing sequence numbers; clients retry
with the same `client_msg_id`, so nothing is duplicated.
</details>

## 4. [Core] Idempotent send

A phone sends a message, the server stores it as seq 501, and the ACK is lost. The phone retries twice. Trace what
happens with and without `client_msg_id`, and say how long the server must remember it.

<details><summary>Answer</summary>

Without it: seq 501, 502, 503 — the recipient sees the message three times. With it: the owner finds
`(conv_id, client_msg_id) → 501` and returns ACK 501 for both retries. Retention must exceed the client's maximum retry
window (minutes to hours, e.g. 24 h if the app retries after coming back online); a small TTL'd map per conversation
owner, or a unique index on `(conv_id, client_msg_id)` in the store, both work.
</details>

## 5. [Deep] Bucket sizing

The busiest group conversation receives 30 messages/s at peak and 3 /s on average; each stored message is 400 B. You
want partitions under 100 MB (the threshold Discord reported). The lesson's buckets count messages,
`bucket = floor(seq / N)`. What N do you choose, and what does a "latest 50 messages" query read? How would the answer
change if you bucketed by time instead?

<details><summary>Answer</summary>

Hard ceiling = 100 MB / 400 B = 250,000 messages per bucket. Leave headroom for indexes, tombstones and compaction
(say 5×): **N ≈ 50,000 messages ≈ 20 MB**. Because N counts messages, the partition size no longer depends on the
message rate: at the busiest conversation's 3 /s average a bucket fills in ≈ 4.6 h, at a sustained 30 /s peak in
≈ 28 min, and a quiet conversation keeps years in one bucket. "Latest 50" reads bucket `floor(last_seq / N)` (from
`conversations.last_seq`) and, if `last_seq mod N` < 49, the previous bucket too; `before_seq` pages compute their
bucket the same way. With time buckets you must size to the busy tail, not the mean: average volume is
3 × 86,400 × 400 B ≈ 104 MB/day, and a 12 h bucket would reach ≈ 518 MB (30 × 43,200 × 400 B) if the peak lasted, so
size to the 95th-percentile day, as Discord did with ~10 days for its (different) workload.
</details>

## 6. [Core] Presence traffic

A user has 300 contacts; 40 M users are online; each changes state 20 times a day. Estimate presence events/s with
eager fan-out to all contacts, then with lazy subscription where on average 10 contacts are on screen.

<details><summary>Answer</summary>

Changes = 40 M × 20 / 86,400 ≈ 9,260 /s. Eager: × 300 contacts ≈ **2.8 M events/s** — more than the message deliveries in
the lesson. Lazy: each change goes only to users currently viewing that person; if a typical user is visible to ~10
viewers at a time (assumption), ≈ 93,000 events/s, a 30× reduction. Typing indicators should be rate-limited and
dropped first under load because they are ephemeral.
</details>

## 7. [Interview] Gateway deploy

You must deploy a new gateway version across 300 gateways holding 60 M connections without a reconnect storm. Write
the rollout plan with numbers.

<details><summary>Answer</summary>

Roll in waves of, say, 5 % (15 gateways ≈ 3 M connections). In each wave, stop admitting new connections on draining
gateways, then send a "reconnect after random 0–300 s" control frame so 3 M reconnects spread over 5 minutes
(≈ 10,000 /s fleet-wide). Cap per-gateway admission rate; make resume cheap (client sends one `sync_token`; the server returns
only changed conversations). Watch handshake latency, reconnect success and delivery p99 before the next wave. Total: 20 waves; at
~10 minutes each, a few hours. A crash (no drain) is the same problem without the jitter control frame — so clients
must also apply jittered backoff on their own.
</details>

## 8. [Deep] MLS and the server

Your product adds MLS-based E2EE for groups. List what the server can no longer do, what new state it must store, and
which existing component becomes protocol-critical.

<details><summary>Answer</summary>

Can no longer: read message bodies, so server-side search, link previews and content-based spam filtering stop
(move to client-side indexes, user reporting, metadata signals). New state: per-device KeyPackages for adding offline
members, and handshake messages (Proposals, Commits, Welcome) to route. Protocol-critical: the per-conversation
sequencer — RFC 9750 says the group must agree on a single Commit per epoch and expects most Delivery Services to take the
strongly consistent approach of ordering handshake messages and breaking ties. Multi-device becomes group membership
churn, so device additions must be rate-limited and sequenced.
</details>

## 9. [Lab] Lease failover

In [labs/09-coordination-consensus](../labs/09-coordination-consensus/), kill the etcd leader and measure how long the
cluster takes to elect a new one. Treat that as the stall a conversation owner would see if ownership were stored in
etcd. Then explain how fencing tokens prevent a deposed owner from assigning duplicate sequence numbers.

<details><summary>Answer</summary>

Report the election time you measured (it depends on election timeout settings); that time, plus lease expiry, bounds
how long sends to affected conversations stall. Fencing: each ownership grant carries a monotonically increasing token
(e.g. the etcd revision); the message store rejects writes whose token is lower than the latest seen for that
conversation, so an old owner that wakes up after a pause cannot write `seq` values that collide with the new owner's.
</details>

## 10. [Interview] AI summaries in an E2EE app

Product wants "summarize unread messages" in an E2EE messenger. Give two architectures, the trade-offs, and the system
requirements each adds.

<details><summary>Answer</summary>

(1) **On-device model**: preserves E2EE trivially; limited by model size, memory, battery; requires shipping and
updating models to devices. (2) **Confidential-computing server** (e.g. WhatsApp's Private Processing): user-initiated
requests go over Oblivious HTTP to an attested confidential VM that processes statelessly and keeps no messages after
the session. Adds: attestation and binary transparency, an LLM serving fleet with its own capacity and cost
(see C09), strict statelessness, and abuse controls. A "just send plaintext to our normal LLM API" design breaks the
E2EE promise and is a red flag.
</details>
