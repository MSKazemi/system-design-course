# 13 — Data at scale (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement

- Lumen: 2 PB of documents, 200 M events/day, 500 M searchable chunks
- Analytics over 90 days in < 30 s; search p99 < 200 ms; fresh within seconds
- One OLTP database cannot serve any of the three
- Three shapes: object storage, lakehouse, search index

**Visual:** Three columns (object store, lakehouse table, search index) under a Lumen banner. Icons: `arch-object-storage`, `arch-data-warehouse`, `arch-search-index`.

**Speaker notes:** Open with the numbers, not the technologies. Each of the three requirements forces a different storage shape, and the rest of the talk is about why.

## Slide 2 — Object storage in one sentence

- Cheap per byte, expensive per request, slow per request, nearly infinitely parallel
- No append, no in-place update, rename = copy + delete
- S3: 11-nines durability design, ≥ 3 AZs, 99.99% availability design
- ≥ 3,500 writes / 5,500 reads per second per prefix; ~100–200 ms first byte

**Visual:** A key → blob map with a price tag on "bytes" (small) and on "requests" (large). Icons: `storage-aws-s3`, `storage-minio`, `storage-ceph`.

**Speaker notes:** Everything later — big files, columnar formats, batched commits — follows from this one sentence. The numbers come from the S3 user guide.

## Slide 3 — Consistency and compare-and-swap arrive

- Dec 2020: S3 strong read-after-write for PUT, overwrite and LIST
- Aug 2024: conditional writes — `If-None-Match: *` → 412 if key exists
- Nov 2024: `If-Match` on ETag; first concurrent writer to finish wins
- Delta Lake (2020) needed a separate coordination service on S3 — no longer required for the primitive

**Visual:** Timeline 2020 → Aug 2024 → Nov 2024 with the three milestones. Icons: `storage-aws-s3`, `pattern-consistency`, `pattern-transaction`.

**Speaker notes:** A put-if-absent primitive that table formats wished for is now an HTTP header. This is why commits on object storage got simpler.

## Slide 4 — Replication vs erasure coding

- 3×: 200% overhead, survives 2 losses, repair reads 1 fragment
- RS(6,3): 50%, survives 3; RS(10,4): 40%, survives 4
- Repair reads k fragments → network becomes the bottleneck
- Replicate hot/small, code large/cold (f4: 3.6 → 2.8 or 2.1)

**Visual:** Bar chart of raw PB for 2 PB logical: 6.0 vs 3.0 vs 2.8. Icons: `pattern-replication`, `arch-storage-disk`.

**Speaker notes:** Capacity savings are real but repair is the bill. HDFS docs and the f4 OSDI paper are the sources.

## Slide 5 — From lake to lakehouse

- Lake: open files, no transactions — half-visible writes, clobbering, painful deletes
- Two-tier lake + warehouse: reliability, staleness, limited ML support, cost (Armbrust et al., CIDR 2021)
- Lakehouse: open files + transactional metadata layer + performance features
- Formats: Iceberg, Delta Lake, Hudi

**Visual:** Layer stack: object storage → Parquet → manifests → metadata → catalog → engines. Icons: `arch-object-storage`, `data-spark`, `data-databricks`.

**Speaker notes:** The lakehouse is not a product, it is a pattern: immutable files plus a log that says which files are the table.

## Slide 6 — How a commit works

- Files are immutable; the table is a pointer to a file list
- Writer: read version v, write files + new metadata, swap pointer v → v+1
- Conflict → re-apply on the new version if still valid
- Contention scales with commit rate, not data size

**Visual:** Sequence: two writers, one swap succeeds, one retries. Icons: `pattern-transaction`, `pattern-consensus`.

**Speaker notes:** This is optimistic concurrency, straight from the Iceberg spec. The swap is the only coordination point.

## Slide 7 — Parquet and pruning

- Row groups → column chunks → pages; footer written last
- Dictionary + RLE + Zstd; recommended row groups 512 MB–1 GB, pages 8 KB
- Projection pushdown, predicate pushdown, file skipping via manifest stats
- Lumen: 3.6 TB table, query reads ~28 GB (4/40 columns × 7/90 days)

**Visual:** A grid of columns × row groups with only 4 columns and 7 rows highlighted. Icons: `pattern-compression`, `pattern-partitioning`.

**Speaker notes:** The 600× reduction is arithmetic on stated assumptions, not a benchmark. Sorting by the filtered column is what makes min/max skipping work.

## Slide 8 — The small-files tax

- 50 writers × commit/min = 72,000 files/day of ~0.5 MB
- Every file = requests + footer reads + planning work
- Compaction to ~512 MB → ~80 files/day
- Also: expire snapshots, remove orphans

**Visual:** Confetti of tiny files collapsing into a few large blocks. Icons: `pattern-batching`, `ops-cost`.

**Speaker notes:** Streaming into a lakehouse is easy; streaming into a lakehouse cheaply requires compaction and sensible commit intervals.

## Slide 9 — Batch: MapReduce → Spark

- MapReduce (2004): map, shuffle, reduce; re-run failed tasks; backup tasks for stragglers
- Spark RDDs (2012): in-memory, lineage-based recovery
- Shuffle skew and stragglers are still the main failure modes
- Mitigate with salting, broadcast joins, adaptive execution

**Visual:** Map tasks → all-to-all shuffle arrows → reduce tasks, one reducer glowing as "skewed". Icons: `data-hadoop`, `data-spark`.

**Speaker notes:** The vocabulary of batch has not changed in twenty years. Skew is the question interviewers like most.

## Slide 10 — Lambda vs Kappa

- Lambda (Marz 2011): batch layer + speed layer, merge at query time
- Kreps (2014): two code paths that must agree is the real cost
- Kappa: replay the log into a new table when logic changes
- 2026: stream jobs commit to lakehouse tables read by batch engines

**Visual:** Two pipelines side by side; Lambda with two boxes merging, Kappa with v1/v2 jobs reading one log. Icons: `messaging-kafka`, `data-flink`, `arch-event-stream`.

**Speaker notes:** The choice is about how many implementations of your logic you are willing to maintain.

## Slide 11 — Search: inverted index and BM25

- Term → postings list; segments are immutable, merged in the background
- BM25: IDF × saturating term frequency × length normalization (k₁ = 1.2, b = 0.75 defaults in Elasticsearch)
- Refresh (1 s default) gives near-real-time visibility
- Shards 10–50 GB; fan-out over 20 shards turns per-shard p99 into ~query p82

**Visual:** Word → document list; three small segments merging into one. Icons: `arch-search-index`, `search-elasticsearch`, `search-opensearch`.

**Speaker notes:** Search is an LSM tree in spirit. Licensing note: Elastic added AGPL in 2024; OpenSearch moved to a Linux Foundation project the same year.

## Slide 12 — Frontier (as of 2026-11)

- Iceberg v3 adopted (variant, deletion vectors, row lineage); v4 in development
- S3 Tables: managed Iceberg with automatic compaction
- Object-storage-native streaming: KIP-405 production-ready (Kafka 3.9), WarpStream, KIP-1150 accepted (not yet released)
- DuckDB 2.0 LTS: laptop-scale analytics directly on Parquet in S3

**Visual:** Four tiles with version badges. Icons: `messaging-kafka`, `storage-aws-s3`, `arch-object-storage`.

**Speaker notes:** Disks are becoming caches in front of object storage. Treat vendor latency claims as claims and measure.

## Slide 13 — Interview angle and red flags

- CLARIFY freshness, query shape, retention, deletes
- QUANTIFY bytes/day, bytes scanned, files/day, shard count
- STRESS small files, contention, hot tenants, fan-out tail, erasure
- Red flags: S3 as a filesystem, no compaction, hundreds of tiny shards, ignoring deletes

**Visual:** The six-step CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip with this unit's prompts. Icons: `ops-check`, `ops-warning`.

**Speaker notes:** A strong answer draws the catalog and the compaction job explicitly. Those two boxes are what separate a senior answer from a diagram of logos.
