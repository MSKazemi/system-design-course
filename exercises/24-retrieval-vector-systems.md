# 24 — Exercises

Lesson: [SYSDESIGN-24 Retrieval & vector systems](../course/03-ai-systems/24-retrieval-vector-systems.md)

### 1. [Core] Index memory

Estimate the memory for 20M vectors of 768 dimensions in an in-RAM HNSW index with `M = 32`, float32. Then redo it
with int8 scalar quantization and with PQ at 96 bytes per vector.

<details><summary>Answer</summary>

Vectors: 20×10⁶ × 768 × 4 B = 61.4 GB. Graph: hnswlib's rule of thumb is about `M × 8–10` bytes per element, so
256–320 B × 20M = 5.1–6.4 GB. Total ≈ **67–68 GB** before allocator and OS overhead. Plan for ~80 GB nodes or
shard across two.

int8 SQ: 768 B per vector → 15.4 GB + the same graph ≈ **21–22 GB**. That fits on a single 32 GB node, and you can
rescore the top candidates with full vectors on SSD.

PQ at 96 B: 1.9 GB of codes. With an IVF-PQ index (no HNSW graph) total RAM is a few GB. Recall from codes alone is
lower, so oversample (for example fetch 100) and rescore with full vectors.

Key point: the vectors dominate. Compression changes the *tier*, from RAM to SSD, not just the size.
</details>

### 2. [Core] Exact vs approximate

Your corpus has 80,000 chunks and grows by 1,000 per month. A colleague proposes a dedicated vector database with
HNSW. What do you ask and what might you recommend?

<details><summary>Answer</summary>

Ask: latency SLO, QPS, filter patterns (tenant, ACL), and whether the data already lives in Postgres.

At 80k vectors, exact search is often fast enough. Lab L24 measured ~44 ms p50 for a sequential scan of 50k 384-d
vectors on a laptop, and a pre-filter by tenant shrinks the scan further. If the SLO is 50–100 ms and QPS is
modest, exact search (or pgvector HNSW in the existing database) avoids a new stateful system and gives perfect
recall. Recommend measuring first. Revisit when n is in the millions, QPS is high, or the filter mix makes exact
scans slow. Acceptable alternative: pgvector HNSW with iterative scans, which keeps one database.
</details>

### 3. [Deep] Post-filter starvation

A query filters on `tenant_id`, which matches 0.5% of rows. You use HNSW with `ef_search = 40` and post-filtering.
How many results do you expect for `LIMIT 10`? Give three fixes, with the trade-off of each.

<details><summary>Answer</summary>

Expected matches among 40 candidates ≈ 40 × 0.005 = **0.2 rows**. Most queries return nothing. (Lab L24 saw
0.3/10 at 1% selectivity.)

Fixes:
1. **Iterative index scans** (pgvector ≥ 0.8: `hnsw.iterative_scan`). Correct counts. Latency grows with
   selectivity (the lab measured p50 ≈ 19 ms vs 2 ms at 1%) and is capped by `hnsw.max_scan_tuples`.
2. **Pre-filter plan** (B-tree on `tenant_id`, exact scan of the tenant's rows). Perfect recall, cost ∝ tenant size.
   Great for small tenants, bad for huge ones.
3. **Physical partitioning** per tenant (partitions, collections, or Qdrant `is_tenant` sub-indexes). Filter-free
   ANN per tenant and no leakage by construction. Costs: many indexes and uneven sizes.

A strong answer combines them: partition by tenant (or tenant group), with exact search for tiny tenants and HNSW for
large ones.
</details>

### 4. [Core] Why RRF?

Explain why reciprocal rank fusion needs no score normalisation, and give a case where weighted score fusion could
be better.

<details><summary>Answer</summary>

RRF uses only *ranks*: `Σ 1/(c + rank)`. BM25 scores are unbounded and corpus-dependent, while cosine similarities
sit in [−1, 1] with model-specific distributions. Adding them directly is meaningless without calibration, and ranks
sidestep the problem (Cormack et al., 2009).

Weighted score fusion (after min-max or z-normalisation) can be better when score *gaps* carry information. For
example, when dense similarity is very high for one document and flat for the rest, RRF discards that confidence.
Weaviate's `relativeScoreFusion` keeps it. Tune either on a labelled set.
</details>

### 5. [Deep] Re-embedding migration

You must move 50M chunks from embedding model v1 (768-d) to v2 (1,024-d) without downtime. Design the migration and
estimate its cost using the lesson's assumptions.

<details><summary>Answer</summary>

Cost: 50M × 300 tokens = 15×10⁹ tokens. At the assumed 20k tokens/s per GPU, that is ≈ 208 GPU-hours (for example 26
GPUs for 8 hours). Storage roughly doubles during the overlap (v2 float32 alone is 205 GB).

Plan (blue/green):
1. Create index v2 with its own `model_version` and dimension. Never mix vectors in one index.
2. Backfill from the chunk store, in tenant batches with fair queuing.
3. Dual-write: ingestion embeds new and changed chunks with both models until cut-over.
4. Evaluate v2 offline (recall@k and nDCG on the golden set, faithfulness on sampled RAG answers), then
   shadow-query it with live traffic.
5. Flip the alias per tenant (canary first). Keep v1 for rollback. Then drop it.

Pitfalls: query embeddings must switch at the same moment as the index. Cached query embeddings are invalid.
Matryoshka v2 models could store 1,024-d but search a 256-d prefix first.
</details>

### 6. [Core] Evaluation diagnosis

Answer quality dropped after a release. Retrieval recall@10 on the golden set is unchanged, but faithfulness on
sampled traffic fell from 0.92 to 0.80. Where is the problem likely to be, and what do you check?

<details><summary>Answer</summary>

Retrieval is probably fine, since the right chunks still reach the top 10. The generation stage is now not using
them faithfully. Check in this order:
- The prompt template and model version (did the release change the model, temperature, or system prompt?).
- Context assembly: ordering (relevant chunks in the middle of a long context can be underused, see "Lost in the
  Middle"), reranker output, truncation of the token budget.
- Whether the judge itself changed. Faithfulness is LLM-judged, so pin the judge model and re-score old outputs to
  rule out judge drift.

Also check recall@k for the k you actually put in the prompt (for example 5). Recall@10 can stay flat while the top
5 changes.
</details>

### 7. [Interview] ACL-aware retrieval

"Users must only see answers based on documents they are allowed to read. Permissions change hourly." Design the
permission model for retrieval.

<details><summary>Answer</summary>

Principle: **enforce before the prompt.** Never rely on instructions to the model.

- *Early binding:* store `acl_principals` (user and group ids) per chunk, and filter `acl && user_principals` inside
  the vector and lexical queries. Keep it fresh with permission-change events (CDC from the identity source) that
  re-tag affected chunks. The hourly churn is fine if re-tagging is a metadata update, not a re-embed.
- *Late check* on the final top-k against the source system's authorisation API, for defence in depth and for
  sources whose permissions are too dynamic to copy.
- *Over-fetch* (for example 3× k) to survive late-check denials.
- Physical tenant isolation underneath.
- Bound the group explosion with access tags. Test with the worst-case user (hundreds of groups).
- Audit: log which chunk ids were retrieved for which principal.

Red flag: filtering after generation, or caching answers across users with different permissions.
</details>

### 8. [Deep] Long context or RAG?

A legal team asks for "summaries of each 200-page contract" and separately "which of our 30,000 contracts contain
an unlimited liability clause?". Which architecture fits each, and why?

<details><summary>Answer</summary>

Per-contract summary: the input is one document (~100–150k tokens), and the task needs the whole document. Use long
context (or map-reduce over sections). Retrieval adds little. Watch cost (prefill scales with tokens) and uneven
use of the middle of long inputs. Section-wise summarisation then a merge is more robust.

Corpus question: it is a *filtering and extraction* problem over 30,000 documents. Running long context over all of
them per question is prohibitive. Options: clause-level chunking + hybrid retrieval (keyword "unlimited liability"
plus dense paraphrases) + reranking + LLM verification per candidate. Better still, extract a structured
"liability cap" field at ingestion and answer with SQL. GraphRAG-style global summaries help with "what are the
common themes", not with exhaustive "which ones" questions. Exhaustive questions need recall close to 1, which
argues for offline extraction.
</details>

### 9. [Lab] Read your curve

From your L24 Part A output, pick the `ef_search` you would ship for a 0.95 recall@10 target. Then run with
`--spread 3.0` and say whether the choice still holds.

<details><summary>Answer</summary>

In the recorded run, `ef_search = 40` gave 0.973 at ~1.4 ms p50. That meets 0.95 with headroom, and 20 (0.852)
does not. With `--spread 3.0` even `ef_search = 320` reached only 0.836, so the choice does **not** transfer. Recall
depends on the data distribution and must be re-measured per corpus. Real embeddings usually sit between these two
synthetic cases, so tune on a sample of *your* vectors and queries, and re-check after each embedding-model change.
</details>

### 10. [Interview] Freshness SLO

"Edits must be visible to the assistant within 15 minutes." What do you measure, and how do you meet it under a
bulk import of 2M documents by one tenant?

<details><summary>Answer</summary>

Measure **ingestion lag**: `index_visible_at − source_updated_at` per chunk, p95/p99 per tenant. Also check the
age of cited chunks in answers.

Meet it with: change events (webhooks or CDC) instead of periodic crawls; a queue with **per-tenant fair
scheduling** so one tenant's 2M-document import cannot starve others' edits; a priority lane for small interactive
edits; idempotent, hash-diffed re-embedding (only changed chunks); and autoscaled embedding workers. For
read-your-writes, add a small exactly-searched "recent changes" overlay. Alert when p95 lag approaches 15 minutes,
and degrade by pausing bulk lanes.
</details>
