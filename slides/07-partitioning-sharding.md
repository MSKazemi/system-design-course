# 07 — Partitioning & sharding (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/07-partitioning-sharding.md](../course/01-foundations/07-partitioning-sharding.md)

## Slide 1 — The requirement

- 40 TB of chat, 20,000 writes/s, 8 → 64 nodes online
- No node above 1.25× average load
- "Latest messages of a conversation" = one partition

**Visual:** A single overflowing database splitting into eight shards. Icons: `pattern-sharding`, `arch-servers-cluster`.

**Speaker notes:** The busiest node sets the cluster's capacity, which is why balance is a requirement, not a nicety.

## Slide 2 — Partition key and scheme

- Hash: even load, no range scans over the key
- Range: scans and ordering, hot tail on monotonic keys
- Compound: hash the conversation, sort by time inside it
- Directory: arbitrary placement (tenants, residency)

**Visual:** Four mini-diagrams of key → partition. Icon: `pattern-partitioning`.

**Speaker notes:** Choose the key from the query that must be single-partition; everything else becomes scatter-gather.

## Slide 3 — Why hash % n fails

- A key stays only if h mod n = h mod (n+1): ~1/(n+1) of keys
- 10 → 11 nodes moves ~91 % of keys; only ~9 % had to move
- For a cache: a self-inflicted stampede

**Visual:** Bar chart from lab L07: modulo 90.9 % vs ring 9.1 %, rendezvous 9.1 %, jump 9.1 %.

**Speaker notes:** The lab measures this on 100,000 keys; the numbers are deterministic.

## Slide 4 — Consistent hashing

- Nodes and keys on one ring; key → next node clockwise
- Adding a node takes one arc; nothing else moves (monotonicity)
- Karger et al., 1997, for distributed web caches

**Visual:** Ring with three node tokens and a new token taking one arc. Icon: `pattern-consistent-hashing`.

**Speaker notes:** Monotonicity is the property the lab's unit test checks: moved keys only go to the new node.

## Slide 5 — Virtual nodes

- One token per node: busiest node 2.9× mean (lab)
- 8 tokens 1.44×, 64 tokens 1.15×, 256 tokens 1.12×
- Failed node's load spreads over many successors; bigger machines take more tokens

**Visual:** Ring with many small coloured-and-labelled arcs per node; balance bar chart.

**Speaker notes:** Dynamo adopted virtual nodes; Cassandra 4.0 defaults to 16 tokens with a balance-aware allocator.

## Slide 6 — Rendezvous and jump hash

- Rendezvous (HRW): highest hash(node, key) wins; O(n) lookup; top-r gives replicas
- Jump hash: few lines, no memory, minimal movement; only numbered buckets, remove only the last
- Pick by failure model: arbitrary node loss vs stable shard numbers

**Visual:** Score table for one key across five nodes; jump hash bucket line.

**Speaker notes:** Thaler and Ravishankar 1998; Lamping and Veach 2014.

## Slide 7 — Fixed partitions: decouple placement

- Key → one of P partitions (fixed); partition → node (table)
- Rebalance by moving whole partitions
- Dynamo strategy 3, Redis Cluster 16,384 slots, Kafka partitions

**Visual:** Two-level map: keys → 4,096 partitions → 8 nodes. Icons: `cache-redis`, `messaging-kafka`.

**Speaker notes:** Choose P large enough to spread over future nodes, small enough that per-partition overhead stays low.

## Slide 8 — Numbers: resize and fan-out

- 8 → 9 nodes moves 40 TB / 9 ≈ 4.4 TB: ~6 h at 200 MB/s; modulo would move ~35.6 TB
- Fan-out to 64 partitions at 99 % each under 10 ms: all 64 in time only 53 % of the time
- Partition-aligned queries are a tail-latency decision

**Visual:** Data-movement bar; fan-out probability curve.

**Speaker notes:** Throttle movement to protect foreground p99.

## Slide 9 — Secondary indexes

- Local: cheap writes, scatter-gather reads
- Global: one-partition reads, distributed writes, often asynchronous
- DynamoDB GSIs update asynchronously, eventually consistent

**Visual:** Two-column comparison with arrows for write and read paths. Icon: `nosql-dynamodb`.

**Speaker notes:** A global asynchronous index cannot enforce uniqueness; use a conditional write on a key table.

## Slide 10 — Hot keys and salting

- Frequency skew: one key → one partition, no hash helps
- Salt hot keys into S sub-keys; reads fan out to S and merge
- Lab: Zipf(1.1) busiest node 1.93× mean → 1.19× salting top 10 keys into 16

**Visual:** One overheated partition splitting into 16 cooler ones; read merge arrow. Icon: `pattern-fan-out`.

**Speaker notes:** Salting fixes frequency skew, virtual nodes fix placement skew. Salt only detected hot keys.

## Slide 11 — Online resharding

- Copy snapshot → stream changes → verify → switch reads → switch writes
- Brief write pause or buffering at cutover; reverse replication for rollback
- Vitess Reshard: VDiff, SwitchTraffic, ReverseTraffic, Complete

**Visual:** State diagram of the reshard workflow. Icon: `sql-vitess`.

**Speaker notes:** The write switch is where writes can be lost; the pause plus catch-up prevents it.

## Slide 12 — Distributed SQL

- Spanner: splits + Paxos + TrueTime (1–7 ms uncertainty, commit wait)
- CockroachDB: 512 MiB ranges, Raft, size- and load-based splits
- Vitess and Citus: shard MySQL / PostgreSQL; co-locate by tenant

**Visual:** Table of the four systems. Icons: `sql-cockroachdb`, `sql-vitess`, `sql-postgresql`, `company-google`.

**Speaker notes:** Cross-shard joins and transactions work; they are the expensive path, so the schema should make them
rare.

## Slide 13 — Interview wrap

- CLARIFY the single-partition query → QUANTIFY nodes and partitions → SKETCH key + fixed partitions + routing
- DEEPEN consistent hashing or salting → STRESS add a node, celebrity key, reshard
- Red flag: `hash % n` with no plan for growth

**Visual:** Six-step framework strip.

**Speaker notes:** End with what became scatter-gather and why that is acceptable.
