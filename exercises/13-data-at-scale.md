# 13 — Exercises

Lesson: [course/01-foundations/13-data-at-scale.md](../course/01-foundations/13-data-at-scale.md). Numbers marked
"assumption" are for practice; replace them with measured values in real designs.

## 1. [Core] What changed when S3 became strongly consistent and gained conditional writes?

Explain what a table-format commit needed on S3 before December 2020, between December 2020 and August 2024, and
after August 2024.

<details><summary>Answer</summary>

- **Before 2020-12:** LIST and overwrite reads could be stale, so a reader might not see the newest log entry, and
  there was no atomic put-if-absent. The Delta Lake paper describes both problems: its protocol tolerated eventual
  consistency (retry when a listed object is missing), and on S3 Databricks used a separate coordination service
  so that only one writer could create each log entry [lesson ref 9].
- **2020-12 → 2024-08:** strong read-after-write for PUTs, overwrites and LISTs [ref 1] removed the stale-read
  workarounds, but there was still no compare-and-swap, so you still needed a catalog database, DynamoDB-style lock
  or similar for the atomic commit.
- **After 2024-08:** `PutObject` with `If-None-Match: *` fails with `412 Precondition Failed` if the key exists, and
  concurrent conditional writers resolve as "first to finish wins" [refs 3, 4]. That is exactly put-if-absent:
  writing `_delta_log/00000000000000000042.json` conditionally is now an atomic commit by itself.

Acceptable nuance: many deployments still use a catalog (Iceberg REST, Glue, a database) for governance, naming
and multi-table operations, even though the storage primitive now exists.
</details>

## 2. [Core] Replication vs erasure coding for 1 PB

For 1 PB of logical data compare 3× replication, RS(6, 3) and RS(10, 4): raw capacity, overhead, failures
tolerated, and bytes read to rebuild one lost 16 TB drive.

<details><summary>Answer</summary>

| Scheme | Raw | Overhead | Losses tolerated | Rebuild one 16 TB drive reads |
|---|---|---|---|---|
| 3× | 3 PB | 200% | 2 | ~16 TB (copy from a survivor) |
| RS(6,3) | 1.5 PB | 50% | 3 | up to 6 × 16 = 96 TB |
| RS(10,4) | 1.4 PB | 40% | 4 | up to 10 × 16 = 160 TB |

RS(k, m) stores *k + m* fragments, any *k* reconstruct, so it survives *m* losses at overhead *m/k*. Repair reads
*k* fragments for every lost one, so erasure coding saves capacity but multiplies repair network traffic and slows
degraded reads. HDFS's documentation gives the 200% vs ≤50% comparison and warns about network bisection
bandwidth [ref 6]. Choose replication for hot or small data, coding for large and cold data — the f4 paper's
temperature-based split [ref 7].
</details>

## 3. [Core] Bytes scanned

A 50 TB Parquet table holds 365 daily partitions and 60 columns of similar size. A query filters on 2 days and
reads 3 columns. Estimate bytes scanned, then explain one reason the real number could be higher and one reason it
could be lower.

<details><summary>Answer</summary>

50 TB × (2/365) × (3/60) ≈ 50 TB × 0.00548 × 0.05 ≈ **13.7 GB**.

- **Higher:** columns are not equal-sized (a free-text column can dominate); partitions are skewed (a launch day may
  be 5× a normal day); small files add per-file footer reads and request overhead; deletion vectors or merge-on-read
  logs must also be read.
- **Lower:** row-group/page min/max statistics skip more data if the table is sorted by a filtered column; dictionary
  encoding makes low-cardinality columns tiny; the engine may answer `COUNT(*)` from metadata alone.
</details>

## 4. [Core] The small-files tax

A Flink job with 40 parallel writers commits to an Iceberg table every 30 seconds. Each commit writes one file per
writer. Daily ingest is 120 GB compressed. (a) How many files per day, and of what average size? (b) What breaks?
(c) Propose two fixes.

<details><summary>Answer</summary>

(a) 40 × (86,400 / 30) = 40 × 2,880 = **115,200 files/day**, averaging 120 GB / 115,200 ≈ **1 MB** — about 500×
smaller than Parquet's recommended 512 MB–1 GB row groups [ref 15].

(b) Query planning must read manifests listing hundreds of thousands of files; each file costs at least one GET with
~100–200 ms first-byte latency [ref 5]; compression and row-group statistics are poor on tiny files; there are
2,880 commits per day, so metadata (snapshots, manifests) bloats and concurrent writers contend on the pointer swap.

(c) Any two of: lengthen the commit interval (freshness permitting, e.g. 5 min → 10× fewer files); reduce writer
parallelism or add a shuffle by partition before the sink so each partition gets one writer; schedule compaction
("rewrite data files") to ~512 MB targets; expire old snapshots and rewrite manifests; consider merge-on-read with
periodic compaction for upsert workloads.
</details>

## 5. [Deep] Optimistic concurrency

Two jobs write to the same Iceberg table: an hourly append job and a nightly compaction job that rewrites
yesterday's small files. Walk through what happens if the append commits while compaction is running. When can
compaction re-apply its change, and when must it fail?

<details><summary>Answer</summary>

Both read snapshot *v*. The append writes new files and swaps *v → v+1*. Compaction then tries *v → v+2*; the swap
fails because current is *v+1*. Per the spec, the writer must retry on the new current version, and "a change that
rewrites files can be applied to a new table snapshot if all of the rewritten files are still in the table" [ref 10].
The append only *added* files, so the rewritten files are still present: compaction re-applies (new metadata on top
of *v+1*) and commits. It must fail (or redo work) if a concurrent writer **deleted or rewrote** any of the files it
compacted — e.g. a GDPR delete job that produced deletion vectors for those files, since rewriting them without the
deletes would resurrect erased rows. The validation a writer chooses sets the isolation level.
</details>

## 6. [Deep] Lambda vs Kappa for Lumen

Lumen's growth team wants a "messages per workspace" metric visible within one minute, and exact numbers for
monthly billing. A bug fix to the counting logic ships every few weeks. Propose an architecture and justify it.

<details><summary>Answer</summary>

A reasonable answer is **Kappa-style streaming into a lakehouse table**: events in Kafka (retention ≥ the
reprocessing window you need, or tiered storage to object storage), a Flink job that maintains per-minute counts and
commits to an Iceberg table every minute, dashboards reading that table. When counting logic changes, run v2 of
the job from the start of the retained log into a new table, compare, then switch readers — Kreps' reprocessing
recipe [ref 19]. Billing reads the same table after a cut-off (e.g. close the month after late data has arrived),
so there is one code path.

Lambda is acceptable if the billing logic is complex batch SQL that cannot run as a stream, but you must budget for
keeping two implementations in agreement and for a reconciliation check — the cost Kreps calls "not fixable" [ref 19].
Watch-outs: late and duplicate events (idempotent keys, event-time windows — see SYSDESIGN-08/20), and log
retention cost for long replays.
</details>

## 7. [Core] BM25 intuition

Query: "kv cache eviction". Document A (100 words) contains "eviction" 3 times; document B (2,000 words) contains it
6 times. "Cache" appears in 40% of the corpus, "eviction" in 0.1%. Without computing exact scores, which document
likely ranks higher for the "eviction" term and why? What happens if you set b = 0?

<details><summary>Answer</summary>

"Eviction" has much higher IDF than "cache" (rarer), so it dominates. For that term, B has twice the raw frequency
but is 20× longer than A. BM25's term-frequency saturation (k₁ = 1.2) means 6 vs 3 occurrences adds only modestly,
while length normalization with b = 0.75 discounts B heavily, so **A likely ranks higher**. With **b = 0**, length
normalization disappears, B's higher term frequency wins on that term, and long documents are favored generally —
usually worse for chunked RAG corpora with very uneven chunk lengths. (Defaults k₁ = 1.2, b = 0.75 in
Elasticsearch [ref 22].)
</details>

## 8. [Interview] Size the search tier

Design the shard layout for 500 M chunks, average 1 KB of text each, p99 < 200 ms, 2,000 queries/s peak, new
content searchable within 5 s. State assumptions.

<details><summary>Answer</summary>

Assumptions: index + stored fields ≈ source size ≈ 500 GB (measure!); a shard copy sustains ~200 queries/s at the
target latency (assumption; benchmark it).

- **Shards:** 25 GB primaries → 20 primaries, 25 M docs each — inside Elastic's 10–50 GB and <200 M docs guidance
  [ref 32].
- **Replicas for throughput:** each query hits 20 shard copies; 2,000 q/s × 20 = 40,000 shard-queries/s; at 200/s
  per copy that is 200 copies → 10 copies of each shard (1 primary + 9 replicas), plus headroom. This shows why
  high-QPS search often routes by tenant (query hits 1 shard, not 20) rather than scattering every query.
- **Tail:** with 20-way fan-out, if each shard misses its p99 independently 1% of the time, ~18% of queries see at
  least one slow shard (1 − 0.99²⁰), so target per-shard p99.9 or use hedged requests / adaptive replica selection.
- **Freshness:** a `refresh_interval` of 1–2 s meets "searchable within 5 s" [ref 23]; bulk index with batching;
  watch merge pressure.

Strong answers question the 20-way fan-out first: routing by tenant or using fewer, larger shards changes the math.
</details>

## 9. [Deep] When DuckDB instead of a cluster?

A team has 400 GB of Parquet on S3 and runs ~50 ad-hoc queries per day, one analyst at a time. Would you deploy a
Spark/Trino cluster or use DuckDB (2.0, as of 2026-11)? What would change your mind?

<details><summary>Answer</summary>

DuckDB (or a similar single-node engine) is a strong default: the data is small enough that a single large machine
scanning pruned, columnar data finishes most queries quickly, and there is no cluster to operate. DuckDB 2.0 adds
asynchronous I/O for reading Parquet from object storage [ref 30]. Change your mind when: concurrency grows (many
users at once); data grows past one machine's scan budget for interactive latency; you need fine-grained access
control and auditing across many teams; or writes from many concurrent jobs need a table format with a shared
catalog (DuckDB can read table formats, but the catalog and maintenance still have to live somewhere).
</details>

## 10. [Interview] Deleting one user everywhere

A Lumen user invokes GDPR erasure. Their data lives in: raw uploads in object storage (versioned bucket), an Iceberg
events table, a search index, and Kafka with 7-day retention. Outline a deletion design and its timeline.

<details><summary>Answer</summary>

- **Object storage:** delete the objects *and* their non-current versions (versioning keeps old copies); check
  replication targets and backups; record the request in an audit log.
- **Iceberg:** issue a row-level delete (deletion vectors / delete files) → logically gone immediately; then
  compaction rewrites affected files and **snapshot expiry** removes old snapshots and unreferenced files —
  otherwise time travel still exposes the data. The physical-deletion deadline sets the snapshot-retention policy.
- **Search:** delete by user ID; the document is marked deleted in a live-docs bitmap and physically removed only
  when segments merge [ref 21] — force-merge or reindex if your promise is strict.
- **Kafka:** with 7-day retention, data ages out within 7 days; for faster removal use per-user keys with compacted
  topics and tombstones, or crypto-shredding (per-user keys, delete the key).

Timeline: logical deletion everywhere within hours; physical deletion bounded by max(snapshot expiry, merge
schedule, log retention, backup rotation). Full treatment: SYSDESIGN-19.
</details>
