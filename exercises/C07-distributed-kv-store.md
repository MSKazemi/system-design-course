# C07 — Exercises

Lesson: [course/04-case-studies/C07-distributed-kv-store.md](../course/04-case-studies/C07-distributed-kv-store.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Capacity

40 TB logical data, N = 3, nodes with 8 TB of disk kept ≤ 50 % full. Peak 400,000 reads/s at R = 2 and 100,000 writes/s.
How many nodes, and how many replica operations per node per second?

<details><summary>Answer</summary>

Stored = 120 TB; per node 4 TB → **30 nodes** (round up to a multiple of 3 zones: 30 works, 10 per zone). Replica ops =
400,000 × 2 + 100,000 × 3 = 1.1 M /s → ≈ 36,700 per node. That is higher than the lesson's ≈ 15,000 because nodes are
denser; check it against measured node capacity and remember that denser nodes also mean longer rebuilds (exercise 2).
</details>

## 2. [Core] Rebuild time and vnodes

A node holding 4 TB dies. Compare rebuild time (a) streaming from one neighbor at 250 MB/s and (b) streaming from 24
peers in parallel, each limited to 100 MB/s, with the new node's disk able to absorb 1.5 GB/s.

<details><summary>Answer</summary>

(a) 4 TB ÷ 250 MB/s = 16,000 s ≈ **4.4 h** — a long window with only two replicas for that data. (b) Aggregate source
bandwidth 2.4 GB/s, but the receiving disk caps at 1.5 GB/s → ≈ 2,700 s ≈ **45 min**. Many small ranges (vnodes) are what
make (b) possible. Also acceptable: not rebuilding onto one node at all, but letting the remaining nodes take over
ranges (with vnodes spread across many nodes), which parallelizes writes as well.
</details>

## 3. [Core] Quorum choices

For each workload pick N, R, W and justify: (a) session store where a lost update is tolerable but latency matters most;
(b) user preferences where users must see their own change; (c) write-heavy telemetry ingest read only by batch jobs.

<details><summary>Answer</summary>

(a) N = 3, R = 1, W = 1 — lowest latency, tolerates 2 replicas down; stale reads acceptable. (b) N = 3, R = 2, W = 2 —
strict quorum overlap so a read after an acknowledged write sees it (absent sloppy-quorum substitution); add sticky
routing for read-your-writes if needed. (c) N = 3, W = 1 (or 2 for safety), R = 3 or R = ALL in batch jobs — writes are
fast, reads are rare and can afford waiting for all replicas. The point: consistency is a per-workload knob, and each
choice has a stated failure tolerance.
</details>

## 4. [Deep] Quorum is not linearizable

With N = 3, R = W = 2, construct a sequence of events in which two clients reading concurrently with a write see
values in an order impossible under linearizability.

<details><summary>Answer</summary>

Initially all replicas hold v1. Client W writes v2; it reaches replica A only so far. Client X reads from A and B → sees
v2 (newest of v2, v1). Then client Y, starting *after* X finished, reads from B and C → sees v1. X saw the new value and
a later reader saw the old one — not linearizable, even though R + W > N. Fixes: read repair before returning (write
v2 back to a quorum during the read) gives stronger guarantees at extra latency; consensus-based replication gives
linearizability by construction.
</details>

## 5. [Deep] Sloppy quorum anomaly

Replicas for key k are A, B, C. A and B are partitioned away from the coordinator; it writes v2 to C and to stand-ins D
and E (with hints) and returns success with W = 2. A client then reads at R = 2 from A and B. What does it see, and
when is the anomaly repaired?

<details><summary>Answer</summary>

A and B still hold v1, so the read returns v1 — an acknowledged write is invisible despite R + W > N, because the W
nodes (C/D/E) and R nodes (A/B) do not overlap. It is repaired when the partition heals and D and E replay their hints
to A and B, or when anti-entropy repair runs, or when a read touching C triggers read repair. This is why the lesson
says sloppy quorums trade the overlap guarantee for availability.
</details>

## 6. [Core] Vector clocks

Node X writes a cart [book] with clock {X:1}. Two clients concurrently update from that version: one through node X
adding a pen ({X:2}), one through node Y adding a lamp ({X:1, Y:1}). What does a read return, and how should a cart
service reconcile it? What would last-write-wins do?

<details><summary>Answer</summary>

{X:2} and {X:1, Y:1} are concurrent (neither dominates), so the read returns **both siblings**: [book, pen] and
[book, lamp]. The cart service merges by union → [book, pen, lamp] and writes back through a coordinator; if X coordinates, it
increments its own entry, giving {X:3, Y:1}, which dominates both siblings (Dynamo §4.4 shows the same step). LWW would keep only whichever write carries the later timestamp and silently drop the other item —
acceptable for "last login time", not for carts. Union merges can resurrect deleted items, which Dynamo accepted for
carts; CRDT sets with tombstones avoid that.
</details>

## 7. [Deep] Zombie data

A Cassandra-style cluster uses the default 10-day tombstone grace period. Replica C is down for 12 days; meanwhile key
k is deleted (tombstones on A and B) and compaction later removes the tombstones. C returns and repair runs. What
happens, and what operational rules prevent it?

<details><summary>Answer</summary>

C still holds the old value of k; A and B no longer have tombstones (purged after the grace period), so repair sees "C
has data, A and B have nothing" and copies the old value back — the deleted data **resurrects** (a zombie). Rules: run
full repair on every range more often than the grace period; never let a node rejoin after being down longer than the
grace period — wipe and rebootstrap it instead; raise the grace period for tables where long outages are plausible
(at the cost of more tombstones kept).
</details>

## 8. [Core] Merkle trees

Two replicas hold 2^20 keys in a range; 8 keys differ. With a binary Merkle tree whose leaves cover 1,024 keys each,
roughly how many hashes must be exchanged to find the differing leaves, versus comparing all keys?

<details><summary>Answer</summary>

Leaves = 2^20 / 2^10 = 1,024 → tree depth 10. Each differing leaf is found by descending one path, comparing two child
hashes per level: ≈ 2 × 10 = 20 hashes per differing leaf; with at most 8 differing leaves and shared upper levels,
on the order of 100–160 hashes, then the keys in ≤ 8 leaves (≤ 8,192 keys) are compared or streamed. Versus 1,048,576
key comparisons naively. That is why Dynamo and Cassandra use Merkle trees per key range.
</details>

## 9. [Lab] Data movement on resize

Run [labs/07-partitioning-sharding](../labs/07-partitioning-sharding/) `shardsim.py` to compare modulo hashing with a
consistent-hash ring when growing from 10 to 11 nodes, and vary the number of virtual nodes. Report the fraction of
keys moved and the load imbalance you observe, and connect them to rebuild time and hot nodes in this case study.

<details><summary>Answer</summary>

Record your own output. Expect modulo hashing to move most keys (theory: about 1 − 1/11 ≈ 91 %) and the ring to move
roughly 1/11 ≈ 9 %; more virtual nodes should reduce load imbalance between nodes. Connect: fewer moved keys means
less streaming when adding capacity; better balance means no node is disproportionately hot or slow to rebuild.
</details>

## 10. [Interview] Dynamo-style or Raft-style?

A team needs a KV store for (a) shopping carts that must accept writes during partitions and (b) account balances
with conditional updates ("decrement if ≥ amount"). Which replication design fits each, and what does DynamoDB's own
design tell you?

<details><summary>Answer</summary>

(a) Dynamo-style leaderless quorums with sloppy quorums, hints and mergeable values (siblings or CRDTs): always
writable, convergent. (b) A leader-based design (Raft or Multi-Paxos per partition): conditional updates need a single
serialization point and linearizable reads; a range is briefly unavailable during leader failover, which the
application can retry. DynamoDB's 2022 paper shows that even Amazon's managed service uses Multi-Paxos replication
groups with a leader per partition — leaderless quorums are a choice for a specific requirement, not "how Amazon does
KV".
</details>
