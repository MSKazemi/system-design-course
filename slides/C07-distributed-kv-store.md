# C07 — Distributed key-value store (Dynamo-style) (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C07-distributed-kv-store.md](../course/04-case-studies/C07-distributed-kv-store.md)

## Slide 1 — The requirement

- Always writable (carts during partitions)
- 1 M ops/s, p99.9 < 10 ms in-region
- 100 TB across three zones; survive node or zone loss
- Consistency tunable per request

**Visual:** A ring of nodes across three zone bands; a cart icon writing during a cut link.
Icons: `nosql-dynamodb`, `nosql-cassandra`, `domain-cart`, `arch-region`.

**Speaker notes:** "Always writable" and "every read sees the latest write" pull in opposite directions; at 100+ nodes
something is always failing.

## Slide 2 — The numbers

- 150 nodes, 2 TB data each (50 % fill)
- ≈ 15,000 replica ops/s per node
- Rebuild 2 TB: ≈ 2.8 h from one peer, ≈ 8 min from 20
- 1 h outage ≈ 14 GB of hints

**Visual:** Rebuild bar shrinking from hours to minutes as streams multiply.
Icons: `arch-servers-cluster`, `arch-storage-disk`, `ops-clock`.

**Speaker notes:** Labelled assumptions. Throughput is easy; tail latency, failure handling and data movement drive
the design.

## Slide 3 — Sketch

- Ring-aware driver → any node coordinates
- N = 3 replicas, one per zone
- LSM engine per node; hint store
- Gossip + phi accrual; Merkle-tree repair; cluster metadata

**Visual:** The lesson's 10-node flowchart.
Icons: `pattern-consistent-hashing`, `pattern-replication`, `pattern-health-check`.

**Speaker notes:** No leader on the write path — so no leader failover, and also no single serialization point.

## Slide 4 — Partitioning and placement

- Consistent hashing: adding a node moves only its ranges
- Virtual nodes: balance and parallel rebuilds (Dynamo "Strategy 3")
- Preference list = first N distinct physical nodes
- Zone-aware placement makes "survive a zone" true

**Visual:** Ring with colored vnodes; a preference list skipping a duplicate physical node.
Icons: `pattern-consistent-hashing`, `pattern-partitioning`, `arch-region`.

**Speaker notes:** Lab L07 measures key movement and balance with and without vnodes.

## Slide 5 — Quorums

- R + W > N → read and write quorums overlap
- Dynamo's common (N, R, W) = (3, 2, 2)
- Cassandra: ONE / QUORUM / LOCAL_QUORUM; writes always sent to all replicas
- Overlap ≠ linearizable

**Visual:** The N/R/W table from the lesson.
Icons: `pattern-consistency`, `pattern-cap-theorem`.

**Speaker notes:** Exercise 4 builds a non-linearizable history with R = W = 2.

## Slide 6 — Sloppy quorum and hints

- Write to the first N *healthy* nodes; stand-ins keep a hint
- Hints replay when the owner returns
- Availability up, overlap guarantee gone
- Bound the hint window; repair beyond it

**Visual:** The lesson's write sequence with a stand-in node holding a hint.
Icons: `pattern-failover`, `arch-queue`.

**Speaker notes:** Cassandra calls hints and read repair best-effort convergence — not guarantees.

## Slide 7 — Versions

- Vector clocks: detect concurrent siblings; truncate at a threshold ("say 10")
- Dynamo cart, 24 h: 99.94 % of requests saw one version
- LWW (Cassandra): timestamp per mutation; drops a concurrent write
- CRDTs when data can merge

**Visual:** Two concurrent cart versions merging by union.
Icons: `pattern-consistency`, `domain-cart`.

**Speaker notes:** LWW is right for "last seen", wrong for carts.

## Slide 8 — The LSM engine

- Commit log → memtable → immutable SSTables
- Bloom filters skip SSTables; compaction merges (write amplification)
- Default periodic commit-log sync can lose the unsynced tail on crash
- Durability comes from replication + W

**Visual:** Write path pipeline with Bloom filter gates on reads.
Icons: `arch-storage-disk`, `arch-memory`, `pattern-compression`.

**Speaker notes:** The 50 % disk-fill assumption exists because compaction needs room.

## Slide 9 — Tombstones and zombies

- Deletes write tombstones; purged after gc_grace (default 864,000 s = 10 days)
- Node down > grace → repair resurrects deleted data
- Repair every range more often than the grace period
- Never rejoin a long-dead node — rebootstrap it

**Visual:** A deleted key rising from a returning node, labelled "zombie".
Icons: `ops-warning`, `pattern-backup`.

**Speaker notes:** Repair frequency is a correctness parameter, not a tuning knob.

## Slide 10 — Membership and repair

- Gossip spreads membership; phi accrual decides "down" per node
- Permanent changes need an operator (Dynamo, Cassandra)
- Merkle trees per range: compare roots, descend only differences
- Read repair for hot keys; full repair for everything

**Visual:** Two Merkle trees with one differing branch highlighted.
Icons: `pattern-health-check`, `pattern-consensus`.

**Speaker notes:** Automatic permanent removal on timeout causes flapping and expensive data movement.

## Slide 11 — Failures and ×10

- Slow node → speculative retry; route around it
- Hot key → client cache, bucketing
- ×10: 1,500 nodes; metadata and operations break first
- Gossip-propagated metadata → consensus-backed metadata

**Visual:** A larger ring with a metadata box turning into a replicated log.
Icons: `pattern-horizontal-scaling`, `ops-incident`.

**Speaker notes:** At scale, schema and topology changes are the risky operations, not reads and writes.

## Slide 12 — Modern twist

- DynamoDB (ATC 2022): Multi-Paxos per partition, leader + lease; 89.2 M req/s peak
- Raft per range: TiKV, CockroachDB; ScyllaDB tablets; Cassandra CEP-21 TCM (6.0 pre-release; GA 5.0.9)
- Object storage tier: SlateDB, turbopuffer, WarpStream (writes ~100s of ms, vendor-reported)
- S3 conditional writes (2024) and Express One Zone (single-digit ms)

**Visual:** Design-space map: leaderless ↔ leader-based on one axis, local disk ↔ object storage on the other.
Icons: `nosql-dynamodb`, `nosql-scylladb`, `sql-cockroachdb`, `storage-aws-s3`.

**Speaker notes:** Leaderless quorums are one point in the space, chosen for always-writable semantics.

## Slide 13 — WRAP

- Junior: consistent hashing, RF 3, R + W > N, replica failover
- Senior: vnodes + zones, tunable consistency, hints, vector clocks vs LWW, LSM, Merkle repair, tail tactics
- Staff: what each mechanism does *not* guarantee, repair vs grace, rebuild math, DynamoDB's Paxos, object tiers
- Red flags: R + W > N = "strong consistency", sloppy quorum = quorum, no tombstone story

**Visual:** Staircase junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** The staff signal is precision about guarantees and their limits.
