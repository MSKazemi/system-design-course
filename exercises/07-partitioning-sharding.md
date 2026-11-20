# 07 — Exercises

Lesson: [course/01-foundations/07-partitioning-sharding.md](../course/01-foundations/07-partitioning-sharding.md) ·
Lab: [labs/07-partitioning-sharding](../labs/07-partitioning-sharding/README.md) · Bracketed numbers refer to the
lesson's References.

## 1. [Core] Movement under modulo

A cache cluster uses `hash(key) % n`. Compute the fraction of keys that move when (a) 4 → 5 nodes; (b) 10 → 9 nodes
(one node removed). What does each mean for a cache's hit ratio right after the change?

<details><summary>Answer</summary>

A key stays only if `h mod n = h mod n'`. For n → n+1 that is ~1/(n+1) of keys, so the moved fraction is ~n/(n+1).
(a) 4 → 5: ~**80 %** move (lab L07 measures 80.2 % with 100,000 keys).
(b) 10 → 9: by the same argument ~1/10 stay, ~**90 %** move, even though only the removed node's 10 % *had* to move.
For a cache, moved keys are misses: right after (a) the hit ratio drops to about 20 % of its previous value and the
backend absorbs ~5× its usual miss load: a self-inflicted stampede. With consistent hashing only ~20 % (a) or ~10 % (b)
of keys miss.
</details>

## 2. [Core] Virtual nodes

Explain, with the lab's numbers, why a ring with one token per node is unacceptable for the requirement "no node above
1.25× average", and how many virtual nodes the lab suggests. Give one more benefit of virtual nodes during a node
failure.

<details><summary>Answer</summary>

With one token per node, arc lengths are very uneven: the lab's busiest of 10 nodes held **2.94×** the mean (and one
held only 0.06×). With 8 tokens: 1.44×; 64: 1.15×; 256: 1.12×. So at least ~64 virtual nodes per node meet the 1.25×
cap with margin in this simulation (more nodes or keys change the details; measure for your setup).
Failure benefit: a failed node's many small arcs are taken over by many *different* successors, so its load spreads
across the cluster instead of doubling one neighbour's load. Also, a bigger machine can take proportionally more
tokens.
</details>

## 3. [Core] Pick the hash scheme

Choose between ring + vnodes, rendezvous and jump hash, and justify: (a) a client-side cache library talking to 12
memcached servers that may fail at any time; (b) a storage system with 1,024 numbered shards mapped to nodes by a
separate table; (c) choosing 3 replica locations for each object among 30 storage nodes, without a metadata service.

<details><summary>Answer</summary>

(a) **Ring with vnodes** or **rendezvous**: arbitrary servers can disappear, which rules out jump hash (it can only
remove the last bucket). With 12 servers, rendezvous's O(n) lookup is trivial and needs no tuning; a ring is equally
fine.
(b) **Jump hash** (or plain modulo onto a *fixed* 1,024): shard ids are stable numbers, jump needs no memory and moves
the minimum when the shard count grows; nodes are mapped to shards by the table, so node failures never change the
key → shard function [4].
(c) **Rendezvous**: take the top 3 scores for the key; when a node fails, only objects that had it in their top 3 move,
each to its 4th choice [2]. O(30) hashes per lookup is acceptable.
</details>

## 4. [Deep] Size the rebalance

A cluster holds 60 TB over 12 nodes. You add 4 nodes at once. With fixed partitions and even placement, how much data
moves? At 300 MB/s aggregate throttled copy, how long does it take? What changes if you add the nodes one at a time?

<details><summary>Answer</summary>

After the change each of 16 nodes should hold 60/16 = 3.75 TB; the 4 new nodes must receive 4 × 3.75 = **15 TB**
(= 60 × 4/16). At 300 MB/s: 15 × 10^12 / 3 × 10^8 = 50,000 s ≈ **13.9 hours**.
One at a time: 12→13 moves 60/13 ≈ 4.62 TB, 13→14 60/14 ≈ 4.29, 14→15 4.0, 15→16 3.75: total ≈ 16.7 TB (more than 15 TB,
because some data moves to node 13 and then again to node 14). Adding all at once moves less total data; adding one
at a time limits risk and lets you watch p99 between steps. A common compromise: add all nodes, then move partitions in
throttled batches.
</details>

## 5. [Core] Partition key for chat

Lumen stores messages with `(message_id, conversation_id, author_id, created_at, body)`. Queries: (1) latest 50 of a
conversation (99 % of reads); (2) a user's own messages for GDPR export (rare); (3) daily counts across all
conversations (batch). Choose the partition key and sort key, and say how each query is served.

<details><summary>Answer</summary>

Partition key `conversation_id` (hashed), sort key `created_at` (with `message_id` as tiebreaker).
(1) Single-partition range read in sort order: the requirement.
(2) Scatter-gather over all partitions, or better a small global index / lookup table partitioned by `author_id` that
lists `(conversation_id, message_id)`; it can be asynchronous because exports are not latency critical.
(3) A batch job over a CDC-fed copy in the lakehouse ([SYSDESIGN-13](../course/01-foundations/13-data-at-scale.md)),
not the OLTP cluster.
Wrong answers: partitioning by `message_id` (every conversation read becomes scatter-gather) or by `created_at`
(range-partitioned hot tail).
</details>

## 6. [Deep] Salting a hot channel

The community channel writes 3,000 messages/s, and one partition sustains 1,000 writes/s. Design salting: number of
buckets, how the suffix is chosen, how "latest 50" is read, and the cost.

<details><summary>Answer</summary>

Need ≥ 3 buckets at 100 % utilisation; choose **S = 8** for headroom (~375 writes/s each). Partition key becomes
`(conversation_id, bucket)`. Suffix: random (`bucket = rand(0..7)`) spreads evenly; a calculated suffix
(`hash(message_id) % 8`) does too and lets you find a specific message's bucket. Reads of "latest 50": query all 8
buckets for their latest 50 (8 single-partition reads in parallel), merge by `created_at`, keep 50. Cost: 8× read fan-out
and a merge step for this channel only (store `S` per conversation in metadata so ordinary conversations keep S = 1), and
a slightly slower p99 because the read waits for the slowest of 8. Ordering across buckets relies on timestamps, so use
a time source with bounded skew or per-conversation sequence numbers issued by one service.
</details>

## 7. [Core] Local vs global index

DynamoDB-style table partitioned by `user_id`. You add an index on `email` for login. Compare a local and a global index
for this query and for the write path, and say what can go wrong right after signup with the global one.

<details><summary>Answer</summary>

Login looks up *by email without knowing user_id*. A **local** index lives in each partition, so the lookup must ask
every partition (scatter-gather): unacceptable for every login. A **global** index is partitioned by `email`, so the
lookup hits one partition. Write path: with the global index, each signup writes the user's partition *and* the index
partition, and in DynamoDB the GSI is updated "asynchronously, using an eventually consistent model" [15]. Right after
signup, a login lookup by email might not find the user yet; and two signups with the same email can both succeed,
because an asynchronous index cannot enforce uniqueness. Fix: make email the key of a separate table written with a
conditional put (`attribute_not_exists`) in the same transaction as the user, which gives uniqueness and a consistent
lookup.
</details>

## 8. [Deep] Online reshard

Describe the steps to split one MySQL shard into two with Vitess-style tooling, and identify the moment where writes
could be lost and how it is prevented.

<details><summary>Answer</summary>

Create target shards → copy a consistent snapshot → stream binlog changes to catch up → verify with a diff (VDiff) →
switch read traffic → switch write traffic → keep reverse replication for rollback → complete (delete source) [13].
The dangerous moment is the **write switch**: writes accepted by the source after the target's last applied position
but before clients route to the target would be lost. Prevention: briefly stop writes on the source, wait until the
target has applied everything up to the source's final position, then flip routing; Vitess's SwitchTraffic does this
and VTGate can buffer queries during the pause [13]. Reverse replication then keeps the old shard current, so rollback
does not lose writes made on the new shards.
</details>

## 9. [Interview] Shard the users table

"We have 500 million users in one Postgres. How would you shard it?" Give a structured 6-step answer.

<details><summary>Answer</summary>

1. **CLARIFY** why: data size, write rate, or connection/CPU limits? Is a bigger box, read replicas or archiving enough?
   (Shard last.)
2. **QUANTIFY**: e.g. 500 M × 2 KB = 1 TB of rows plus indexes; peak writes/s; target per-shard size (say 100–200 GB) →
   8–16 shards now, plan for 4× growth.
3. **Key**: `user_id` (most queries are by user); co-locate user-owned tables by `user_id` so joins stay local; global
   lookup tables for email/username uniqueness.
4. **Scheme**: hash `user_id` into a fixed 4,096 logical partitions mapped to physical shards (decouples growth from
   rehashing).
5. **Routing**: a routing tier (Vitess/Citus) or a smart client with a versioned partition map in a consensus store.
6. **Migrate online**: dual-write or CDC-based copy, verify, switch reads then writes, keep rollback; then
   **STRESS** the design with a celebrity user (not a problem for a users table, but it is for their followers table)
   and **WRAP** with what became cross-shard (admin analytics → warehouse).
</details>

## 10. [Lab] Extend the simulator

Add consistent hashing with bounded loads (c = 1.25) to `shardsim.py`. Predict, then measure: max/mean for 10 nodes, 64
vnodes, 100,000 keys, and the fraction of keys moved when growing 10 → 11.

<details><summary>Answer</summary>

Implementation sketch: compute capacity `cap = ceil(c × keys / nodes)`; assign keys in a fixed order (e.g. sorted by
hash) to the first node clockwise whose load < cap (linear probing on the ring) [8].
Prediction: max/mean ≤ 1.25 by construction (versus 1.147 for plain v = 64 in the lab, so the cap only binds on
unlucky placements or skewed weights); movement slightly above the 9.1 % minimum, because when the new node joins, some
keys that were forwarded due to the cap can now settle differently. The paper bounds the extra movement by a factor
O(1/ε²) for ε ≤ 1 [8]. Measure and compare: the interesting case is weighted keys (Zipf), where the cap forces hot keys'
neighbours to move.
</details>
