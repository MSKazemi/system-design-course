# 06 — Replication & consistency (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/06-replication-consistency.md](../course/01-foundations/06-replication-consistency.md)

## Slide 1 — The requirement

- Lose any one AZ: RPO 0, write unavailability < 30 s
- Every user always sees their own messages
- Durability, availability and a consistency promise

**Visual:** Region with three AZ boxes, one crossed out. Icons: `arch-region`, `arch-datacenter`, `pattern-replication`.

**Speaker notes:** The third promise sounds trivial; it is the one async replicas break first.

## Slide 2 — What replication buys, and what it cannot

- Durability, availability, read scale, latency near users
- Not a backup: a bad DELETE replicates in milliseconds
- Backups and point-in-time recovery are a separate requirement

**Visual:** A delete arrow propagating to all replicas. Icons: `arch-database-replica`, `pattern-backup`.

**Speaker notes:** Ask "what protects us from ourselves?" separately from "what protects us from hardware?".

## Slide 3 — Single-leader and when "committed" happens

- Leader streams WAL to followers
- synchronous_commit: off → local → remote_write → on → remote_apply
- Sync standby: RPO 0, plus a round trip per commit

**Visual:** Leader with two followers in other AZs; a ladder of commit points. Icons: `sql-postgresql`, `arch-database-replica`.

**Speaker notes:** Quorum commit `ANY 1 (b, c)` avoids a single synchronous standby becoming a single point of failure.

## Slide 4 — Synchronous means "possibly unavailable"

- Standby gone → commits wait
- Lab L06: commit did not return within 5 s; committed once the requirement was lifted
- A timed-out write is not necessarily a failed write

**Visual:** Clock icon over a blocked commit arrow. Icons: `ops-clock`, `pattern-timeout`.

**Speaker notes:** Synchronous replication converts possible data loss into possible unavailability. Make writes
idempotent so clients can retry safely.

## Slide 5 — Replication-lag anomalies

- Missing own write → read-your-writes
- Time going backwards → monotonic reads
- Reply before question → consistent prefix
- Fix with position (LSN) tokens, not timers

**Visual:** User refresh timeline hitting an up-to-date and a lagging replica.

**Speaker notes:** Lab L06 injected a 2 s apply delay: the replica returned the new row after about 2.2 s.

## Slide 6 — Multi-leader and conflicts

- Local writes per region; offline clients
- Last-writer-wins silently drops concurrent writes
- Siblings + version vectors, CRDTs, or a home leader per key

**Visual:** Two regions accepting different edits to the same record, then a merge box. Icon: `pattern-geo-distribution`.

**Speaker notes:** The cheapest conflict is the one you avoid by routing each key's writes to one home.

## Slide 7 — Leaderless quorums

- N replicas, write waits for W, read waits for R; R + W > N overlaps
- Dynamo (3,2,2); sloppy quorums, hinted handoff, Merkle anti-entropy, vector clocks
- 99.94 % of Dynamo shopping-cart requests (24 h profile) saw exactly one version

**Visual:** Write reaching A and B, read from B and C, read repair to C. Icons: `nosql-cassandra`, `nosql-dynamodb`.

**Speaker notes:** Quorums are not linearizable: Abadi notes Dynamo-style systems cannot achieve Gilbert–Lynch
consistency even with R + W > N.

## Slide 8 — CAP, precisely

- Gilbert & Lynch 2002: no linearizable + always-available object in an asynchronous network with lost messages
- C = linearizability; A = every non-failing node answers every request
- Not "pick two"; says nothing without a partition

**Visual:** Partition line through a cluster; minority side shows "refuse" vs "answer stale".

**Speaker notes:** A Raft cluster is not CAP-available, and it is still highly available for majority-side clients.

## Slide 9 — PACELC

- If Partition: Availability vs Consistency; Else: Latency vs Consistency
- Abadi: Dynamo/Cassandra/Riak PA/EL; VoltDB, Megastore, BigTable PC/EC; PNUTS PC/EL
- The ELC half is the everyday trade-off

**Visual:** 2×2 grid with the paper's classifications. Icon: `pattern-cap-theorem`.

**Speaker notes:** Cross-region physics: ~5 µs per km of fibre, so a Frankfurt–Virginia round trip is at least ~70 ms.

## Slide 10 — Consistency models

- Linearizable → sequential → causal → session guarantees → eventual
- Strict serializable unifies linearizable and serializable
- Jepsen map: sequential and stronger cannot be totally available; causal and RYW at most sticky available

**Visual:** Hierarchy diagram of models. Icon: `pattern-consistency`.

**Speaker notes:** Read-your-writes does not need a linearizable database, only stickiness or tokens.

## Slide 11 — CRDTs

- Merge is commutative, associative, idempotent → strong eventual consistency
- G-Counter, PN-Counter, LWW-Register, OR-Set, sequence CRDTs
- Cannot enforce "at most 10 seats" or "balance ≥ 0" without coordination

**Visual:** Three regional G-Counter vectors merging by element-wise max into 10 reactions.

**Speaker notes:** Shapiro et al. 2011. Escrow or a single owner per invariant fills the gap.

## Slide 12 — Failover and split brain

- Detect → choose → reconfigure → fence
- Async failover loses writes; unfenced old leader = split brain
- Lab L06: both nodes accepted writes after the old primary restarted
- GitHub 2018: 43 s partition, 24 h 11 min of degraded service

**Visual:** Two crowns on two database icons; a fence token counter. Icons: `pattern-failover`, `pattern-leader-election`, `security-lock`.

**Speaker notes:** Make "who is leader" a consensus decision (Patroni + etcd) and fence before promoting.

## Slide 13 — Interview wrap

- CLARIFY RPO/RTO and which reads must be fresh
- SKETCH leader + quorum-sync standbys + async read replicas
- STRESS: AZ partition, standby down, old leader returns
- WRAP: name the consistency model per data type

**Visual:** Six-step framework strip.

**Speaker notes:** Red flags: quorums called linearizable, LWW for money, failover without fencing.
