# 05 — Choosing storage (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/05-choosing-storage.md](../course/01-foundations/05-choosing-storage.md)

## Slide 1 — Five workloads, three engineers

- Billing, chat history, sessions, usage metrics, embeddings
- Each pulls toward a different engine; operations pulls toward one
- Goal: zero lost invoices, 20,000 chat writes/s, fewest products

**Visual:** Five workload cards around one ops team. Icons: `domain-payment`, `domain-chat`, `security-token`, `ops-metrics`, `domain-ai`.

**Speaker notes:** The tension of this chapter: specialised engines versus the operational cost of each additional
product.

## Slide 2 — Access patterns before products

- Queries, read/write ratio, size and growth, latency, consistency, retention
- Write one row per workload before naming a database
- "Postgres" is a product; "Postgres at SERIALIZABLE because seats are a write-skew hazard" is a design

**Visual:** Table with the six columns, filled for Lumen.

**Speaker notes:** Interviewers listen for the access pattern first; the product name is the last word, not the first.

## Slide 3 — Data models

- Relational, key-value, document, wide-column, graph, time-series, vector, search
- Document vs relational = locality vs normalisation
- Choose by dominant access pattern

**Visual:** Grid of eight models with one strength and one weakness each. Icons: `sql-postgresql`, `cache-redis`, `nosql-mongodb`, `nosql-cassandra`, `nosql-neo4j`, `nosql-timescaledb`, `search-elasticsearch`.

**Speaker notes:** Modern engines blur the lines: JSON in relational databases, transactions in document stores.

## Slide 4 — B-tree

- Fixed pages, in-place updates, WAL first
- 3–4 levels for a billion rows; ~1 disk read per lookup in practice
- Pays write amplification on random writes, plus vacuum/bloat in MVCC engines

**Visual:** Three-level tree, a highlighted root-to-leaf path. Icon: `arch-storage-disk`.

**Speaker notes:** Bayer and McCreight, 1972. Predictable reads are why B-trees still run most OLTP.

## Slide 5 — LSM-tree

- Memtable + WAL → immutable SSTables → background compaction
- Bloom filters skip files: ~1 % false positives at 10 bits/key
- O'Neil et al. 1996: "defers and batches index changes"

**Visual:** Memtable flushing into L0, compaction arrows into L1, L2. Icons: `arch-memory`, `arch-storage-disk`, `pattern-compression`.

**Speaker notes:** Sequential batched writes are cheap; the bill arrives as compaction and multi-file reads.

## Slide 6 — Three amplifications

- Write, read, space amplification (RocksDB definitions)
- RUM conjecture: optimise two, pay in the third
- RocksDB example: leveled compaction WA ≈ 33 → 10 MB/s becomes ~330 MB/s of device writes

**Visual:** Triangle with R, U, M corners; B-tree and LSM placed on it.

**Speaker notes:** Write amplification is an SSD endurance number as much as a throughput number.

## Slide 7 — Indexes cost writes

- Leftmost-prefix rule for composite indexes
- Covering and partial indexes; GIN, BRIN, GiST, HNSW
- Every index is another structure to update on every insert

**Visual:** The chat query with `(conversation_id, created_at)` index vs the wrong order.

**Speaker notes:** Index for the queries you have; drop indexes nobody scans.

## Slide 8 — Isolation anomalies

- Dirty write/read, lost update, fuzzy read, read skew, write skew, phantom
- Berenson et al. 1995 named them and defined snapshot isolation
- Write skew: two admins each see 9 seats and each add one → 11

**Visual:** The seat-limit sequence diagram. Icon: `pattern-transaction`.

**Speaker notes:** Write skew is the anomaly snapshot isolation allows and serializable prevents.

## Slide 9 — What vendors mean by their levels

- PostgreSQL: default READ COMMITTED; REPEATABLE READ = snapshot isolation; SERIALIZABLE = SSI
- MySQL 8.0.34 REPEATABLE READ permits lost updates (Jepsen 2023)
- Test the anomaly you care about, on your version

**Visual:** Level × anomaly matrix with check and cross symbols (not colour alone).

**Speaker notes:** Names lie across vendors; tests do not.

## Slide 10 — MVCC and its bill

- Readers never block writers; old versions kept for snapshots
- Long transactions → bloat, held-back vacuum, wraparound risk
- Timeouts and analytics off the primary

**Visual:** Row version chain with xmin/xmax labels; a long-running query pinning old versions.

**Speaker notes:** Operational consequence of MVCC: watch the oldest transaction.

## Slide 11 — Distributed SQL

- Ranges/splits replicated with Raft/Paxos, distributed transactions across them
- Spanner, CockroachDB, TiDB, YugabyteDB, Aurora DSQL
- Removes manual sharding, not physics: cross-region commits cost tens of ms

**Visual:** Table split into ranges, each a three-replica group across regions. Icons: `sql-cockroachdb`, `sql-tidb`, `sql-yugabytedb`, `arch-region`.

**Speaker notes:** Use it for horizontal write scale with transactions, or multi-region strong consistency; not to fix
one slow query.

## Slide 12 — Frontier: Postgres-as-everything, serverless, object storage

- One PostgreSQL 18 cluster: relational, JSONB, full text, queue, pgvector 0.8.7
- Neon: stateless compute, Paxos safekeepers, pageservers on object storage
- Aurora DSQL: snapshot isolation + optimistic concurrency, retry on 40001
- LSM on object storage (SlateDB) for logs and cold data

**Visual:** One Postgres elephant with extension badges; a compute/storage split diagram. Icons: `sql-postgresql`, `arch-serverless`, `arch-object-storage`.

**Speaker notes:** The disciplined version of Postgres-for-everything: separate clusters for different blast radius,
and written exit criteria.

## Slide 13 — Interview wrap

- Per workload: model → engine → isolation → why → trigger to revisit
- Billing in Postgres SERIALIZABLE; chat partitioned by conversation; sessions in Redis
- Red flags: "NoSQL scales", not knowing the default isolation level

**Visual:** The decision table for Lumen.

**Speaker notes:** Finish with the staged plan: two products now, measurable triggers for a third.
