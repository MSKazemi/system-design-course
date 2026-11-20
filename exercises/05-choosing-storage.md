# 05 — Exercises

Lesson: [course/01-foundations/05-choosing-storage.md](../course/01-foundations/05-choosing-storage.md) · Bracketed
numbers such as [3] refer to the lesson's References.

## 1. [Core] Model by access pattern

For each Lumen feature, choose a data model and justify it in one sentence: (a) organisation → teams → members →
permissions, queried with joins; (b) a user's notification preferences, always read and written as one blob;
(c) "who are the colleagues of my colleagues who also use feature X?"; (d) per-GPU utilisation every 10 s, queried as
"average per hour, last 30 days"; (e) "documents semantically similar to this question".

<details><summary>Answer</summary>

(a) **Relational**: many-to-many relationships, constraints (a member belongs to an existing team), ad-hoc joins.
(b) **Document** (or a JSONB column in the relational DB): the unit of read and write is the whole blob; no joins.
(c) **Graph** (or recursive SQL if the graph is small): multi-hop traversal is the dominant operation.
(d) **Time-series**: append-only points, time-range aggregation, downsampling, retention.
(e) **Vector index** (pgvector or a vector database): approximate nearest-neighbour search over embeddings, usually
with metadata filters.
Acceptable alternative for (b), (d), (e): all in PostgreSQL (JSONB, time-partitioned tables, pgvector) if the scale
fits, which is the lesson's staged plan.
</details>

## 2. [Core] B-tree or LSM

A Lumen audit log receives 50,000 small inserts/s, is never updated, and is read rarely by `(tenant_id, time range)`.
A billing table receives 50 writes/s and serves 5,000 point reads/s with strict latency. Which engine family fits each,
and what do you pay?

<details><summary>Answer</summary>

**Audit log → LSM** (or an append-optimised/columnar store): writes are batched in the memtable and flushed
sequentially, so 50k inserts/s is comfortable; reads by `(tenant_id, time)` are range scans within a partition. You pay
compaction write amplification (leveled ≈ 10 per level [3]) and some read amplification; with no updates or deletes,
tombstones are not a concern, and tiered compaction or time-window compaction lowers WA further.

**Billing → B-tree** (PostgreSQL/InnoDB): low write volume, predictable point-read latency (root and inner pages cached,
~1 disk read worst case), mature transactions. You pay page-level write amplification and vacuum/bloat management,
neither of which matters at 50 writes/s.
</details>

## 3. [Deep] Amplification arithmetic

Using the RocksDB example (leveled compaction, WA ≈ 33 for a 500 GB database [3]), compute the device write rate for
12 MB/s of ingest and the yearly device writes. If an SSD is rated for 1 drive write per day on a 3.84 TB drive, is one
drive enough for endurance?

<details><summary>Answer</summary>

Device writes ≈ 12 × 33 = **396 MB/s** worst case. Per day: 396 MB/s × 86,400 s ≈ 34.2 TB/day; per year ≈ 12.5 PB.
A 3.84 TB drive at 1 DWPD tolerates 3.84 TB/day: about **9× too little**. You would need more drives (spreading writes),
higher-endurance drives, or lower WA (tiered/universal compaction, larger memtables, fewer levels, key-value
separation). The exercise shows why WA is an endurance and cost number, not only a throughput number. (The rating and
ingest figures here are assumptions for the exercise.)
</details>

## 4. [Core] Choose the index

Query: `SELECT * FROM messages WHERE conversation_id = $1 AND created_at < $2 ORDER BY created_at DESC LIMIT 50`.
Propose the index. Would an index on `(created_at, conversation_id)` work as well? What about adding an index on
`author_id` "just in case"?

<details><summary>Answer</summary>

`CREATE INDEX ON messages (conversation_id, created_at DESC)`: the equality column first, then the range/sort column,
so the database seeks to the conversation and reads 50 entries in order, no sort step. Optionally `INCLUDE (author_id,
body_preview)` to make it covering.

`(created_at, conversation_id)` is much worse: the leading column is the range, so the scan walks all recent messages of
every conversation and filters (leftmost-prefix rule).

An unused `author_id` index costs on every insert (another B-tree to update, more WAL, more cache pressure) and buys
nothing until a query uses it. Add it when a query needs it; check `pg_stat_user_indexes.idx_scan` for unused indexes.
</details>

## 5. [Lab] Reproduce write skew

In either lab stack (L04 or L06, both PostgreSQL 18), create `seats(org int, member text)` with 9 rows for org 7. Open
two `psql` sessions, run the seat-limit transaction from the lesson in both at `REPEATABLE READ`, interleaving as in the
sequence diagram. What happens? Repeat at `SERIALIZABLE`.

<details><summary>Answer</summary>

Commands (each session):

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM seats WHERE org = 7;   -- both see 9
INSERT INTO seats VALUES (7, 'alice');      -- session B inserts 'bob'
COMMIT;
```

At **REPEATABLE READ** (snapshot isolation) both commits succeed and `count(*)` becomes 11: write skew (A5B), because the
two transactions wrote different rows and SI only detects write-write conflicts on the same row.

At **SERIALIZABLE**, PostgreSQL's SSI detects the read-write antidependency cycle and one transaction fails with
`ERROR: could not serialize access due to read/write dependencies among transactions` (SQLSTATE 40001). The application
must retry it; on retry it sees 10 seats and refuses. (Expected behaviour per the PostgreSQL documentation [7] and
Ports and Grittner [8]; run it to confirm on your version.)
</details>

## 6. [Core] Name the anomaly

Name the anomaly and the weakest PostgreSQL level that prevents it: (a) two requests each read `credits = 100`, each
write `credits = 101`; (b) a monthly report sums invoices while a transfer moves money between two org accounts, and the
sum is off by the transfer amount; (c) a transaction sees a row that another transaction later rolls back.

<details><summary>Answer</summary>

(a) **Lost update (P4)**. In PostgreSQL, REPEATABLE READ prevents it (the second writer gets a serialization error for
the concurrent update); at READ COMMITTED it happens unless you write `UPDATE ... SET credits = credits + 1` or use
`SELECT ... FOR UPDATE`.
(b) **Read skew (A5A)**: the report saw the debit but not the credit. Prevented by REPEATABLE READ (one snapshot for the
whole transaction).
(c) **Dirty read (P1)**: impossible in PostgreSQL at any level (READ UNCOMMITTED behaves as READ COMMITTED [7]).
</details>

## 7. [Deep] MVCC and the 6-hour query

An analyst runs a 6-hour `REPEATABLE READ` query on the primary of Lumen's billing database. Explain two effects on the
OLTP workload and one design change.

<details><summary>Answer</summary>

1. The query's snapshot keeps every row version created after it started "possibly visible", so VACUUM cannot remove
   dead tuples older than its snapshot: tables and indexes **bloat**, scans slow down, cache efficiency drops.
2. It holds back the database's oldest-xmin horizon, which also delays freezing (transaction-id wraparound protection
   [10]) and, on replicas with `hot_standby_feedback`, propagates the same effect.
Design change: run analytics on a replica (accepting that long queries on a hot standby can conflict with replay) or,
better, on an analytical copy fed by CDC into a columnar store; set `idle_in_transaction_session_timeout` and statement
timeouts on the primary.
</details>

## 8. [Interview] Postgres for everything?

"We are a 10-person startup. Should we run Postgres, Redis, Kafka, Elasticsearch, MongoDB and a vector DB from day one?"
Give a 5-sentence answer.

<details><summary>Answer</summary>

No: start with the fewest stores that meet the requirements, typically PostgreSQL plus Redis, because every extra
product adds backups, upgrades, security patching, on-call knowledge and data-sync code. PostgreSQL covers relational
data, JSONB documents, full-text search, a job queue (`SKIP LOCKED`) and vector search (pgvector) well at startup
scale, and keeps them transactionally consistent. Write down the measurable trigger for each extraction (for example,
vector p99 or recall at N vectors, write rate beyond one primary, search relevance features you cannot build), and
separate workloads with different blast radius into different databases or clusters even on the same engine. Add
Kafka when you have a real stream-processing or fan-out need ([SYSDESIGN-08](../course/01-foundations/08-async-event-driven.md)),
not to decouple two services that could share a table. The staged plan with exit criteria is the answer; the product
list is not.
</details>

## 9. [Deep] Distributed SQL latency

A team wants to move billing (60 writes/s, one region) to a multi-region distributed SQL database "for scalability".
Write two questions you would ask and estimate the commit latency if the database requires a majority of replicas in
Frankfurt, Virginia and Singapore.

<details><summary>Answer</summary>

Questions: (1) What requirement does one PostgreSQL primary with a synchronous standby fail to meet: write volume
(no, 60/s), regional write latency, or region-loss RPO? (2) Do users in all regions need to *write* with strong
consistency, or would regional read replicas suffice?

Estimate: a majority of 3 needs the leader plus one more replica. If the leader is in Frankfurt, the closest other
region is Virginia; at ~5 µs/km over a ~7,000 km fibre path (assumption) the round trip is ≥ ~70 ms, so commits cost
**≥ ~70 ms** plus processing, versus ~1–3 ms for an intra-region synchronous standby. For 60 writes/s that is affordable
if the business needs region-loss RPO = 0; otherwise it is latency paid for nothing. "Scalability" is not the reason.
</details>

## 10. [Frontier] Object-storage-backed engine

Explain why LSM-trees fit object storage better than B-trees, and name one workload you would and would not put on an
engine like SlateDB.

<details><summary>Answer</summary>

LSM files (SSTables) are immutable and written once in large sequential chunks; object storage is good at durable,
large, immutable objects and bad at small in-place updates and low-latency random writes (per-request latency of tens
of ms, per-request pricing). A B-tree updates pages in place, which would mean rewriting objects for every page change.
Would: a metrics or event log store that batches writes every few hundred ms and tolerates read latency served mostly
from a local cache. Would not: interactive OLTP with single-row commits that must return in 5 ms (each commit would wait
for an object write).
</details>
