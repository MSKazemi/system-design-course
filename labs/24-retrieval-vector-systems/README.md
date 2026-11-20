# Lab L24 — Exact vs approximate search, filters and hybrid retrieval (SYSDESIGN-24)

## Goal

Measure, on your own laptop, the three trade-offs that dominate vector retrieval design:

1. **Recall vs latency** of approximate indexes (HNSW `ef_search`, IVFFlat `probes`) against exact search.
2. **Filtering**: why post-filtering an ANN index starves selective queries, and two fixes (iterative index scans and
   a pre-filter plan).
3. **Hybrid retrieval and ACLs**: dense vs keyword vs reciprocal rank fusion on a small fictional corpus, plus
   what an un-filtered retriever would leak.

Lesson: [SYSDESIGN-24](../../course/03-ai-systems/24-retrieval-vector-systems.md).

## What you will observe

- Table size close to the `n × (4·d + 8)` bytes estimate, and an HNSW index of similar size.
- Recall@10 rising with `ef_search` / `probes` while latency rises. Exact scan is slower but perfect.
- With a 1% selective filter, plain HNSW returns far fewer than 10 rows. `hnsw.iterative_scan` fixes it at a
  latency cost. With a B-tree on the filter column, the planner switches to an exact pre-filter plan.
- Dense retrieval missing exact error codes that keyword search finds, and RRF combining both.
- An `hr`-only document reaching the candidate list when the ACL predicate is dropped.

## Prerequisites

- Docker Engine 29.x and Docker Compose v5 (tested with 29.10.0 / v5.8.0).
- ~2 GB free RAM, ~1.5 GB disk for images. Internet access on first run (images; ~25 MB embedding model from
  Hugging Face; ~430 MB chat model only for the optional `--generate` step).
- Images (pinned): `pgvector/pgvector:0.8.7-pg18-trixie`, `ghcr.io/ggml-org/llama.cpp:server-b12464`,
  `python:3.12-slim` (client, with `psycopg[binary]==3.3.9`, `numpy==2.5.5`).
- Host ports: `127.0.0.1:12401` (Postgres), `12411` (embeddings), `12412` (optional chat).

## Run

```bash
cd labs/24-retrieval-vector-systems
docker compose -p sd-24 up -d db embed            # embed downloads all-MiniLM-L6-v2 (GGUF) on first start
docker compose -p sd-24 build app

# Part A — ANN recall/latency/filters on 50,000 synthetic 384-d vectors (~1 min)
docker compose -p sd-24 run --rm app python bench_recall.py

# Part B — hybrid retrieval + ACL demo on the fictional Lumen corpus
docker compose -p sd-24 run --rm app python rag_demo.py

# Optional — also generate one cited answer with a 0.5B model and check its citations
docker compose -p sd-24 --profile gen up -d chat
docker compose -p sd-24 run --rm app python rag_demo.py --generate
```

## Experiments

1. **Recall/latency curve.** Run Part A. Plot recall@10 vs p50 latency for each `ef_search` and `probes`. Where is
   the knee?
2. **Harder data.** `python bench_recall.py --spread 3.0` makes clusters overlap (closer to uniform random
   high-dimensional data). Compare the curves. What does this say about trusting someone else's benchmark?
3. **Scale.** `--n 200000` (needs ~1.5 GB of database RAM and a few minutes). How do build time, index size and
   exact-scan latency scale?
4. **Filter selectivity.** `--tenants 10` (10%) vs `--tenants 1000` (0.1%). How many rows does plain HNSW return,
   and how does the iterative-scan latency change?
5. **Dimensions and precision.** Change `vector(...)` to `halfvec(...)` in `bench_recall.py` (and the operator class
   to `halfvec_cosine_ops`). Compare index size and recall.
6. **Hybrid.** In `rag_demo.py` change the RRF constant `c` (60) to 1 and 1,000. Which queries change rank?
7. **ACL.** Add a document for group `finance` in tenant `northwind`, then ask about it as a user in `{"all"}`.

## Expected results

Look for shapes, not exact numbers. They depend on your CPU, Docker settings and the random seed.

- Part A: the table size within a few percent of the estimate. HNSW recall at `ef_search=10` well below 1.0,
  climbing towards 1.0 by `ef_search` ≈ 80–160. Every ANN setting much faster than the sequential scan. Plain HNSW
  with a 1% filter returning < 1 row of 10 on average. `relaxed_order` returning 10/10 at higher latency. A
  `Bitmap Index Scan on items_tenant` plan once the B-tree exists.
- Part B: hybrid-RRF ≥ the better of dense and lexical on these hand-labelled queries. Dense retrieval ranks the
  wrong document first for at least one error-code query. The un-filtered ACL query lists `hr` documents.
- `--generate`: the citation check reports whether cited ids are inside the retrieved set. A tiny model may cite a
  retrieved but *irrelevant* passage. The check is necessary but not sufficient.

## Clean up

```bash
docker compose -p sd-24 --profile gen --profile tools down -v
docker rmi sd-24-app        # optional: the locally built client image
```

## Cost

€0. Everything runs locally on CPU. No API keys.

## Test status

**runtime-tested** on 2026-11-19/20. Host: Ubuntu 24.04.5 LTS, kernel 7.0.0-43-generic, 12 vCPU, Docker 29.10.0,
Compose v5.8.0. Images as pinned above.

Observed output (one run each; your numbers will differ):

- Part A, defaults (`--n 50000 --dim 384 --spread 1.8`): load 22 s. Estimate 73.6 MiB vs table 79.6 MiB. Exact
  scan p50 44 ms. HNSW (`m=16, ef_construction=64`) built in 20 s, index 97.7 MiB. Recall@10 / p50 at
  `ef_search` 10 → 0.702 / 1.0 ms, 20 → 0.852 / 1.2 ms, 40 → 0.973 / 1.4 ms, 80 → 0.995 / 1.6 ms,
  160 → 1.000 / 2.2 ms, 320 → 1.000 / 4.7 ms. Filtered (1%): `iterative_scan=off` returned 0.3/10 rows on average
  (recall 0.034). `relaxed_order` returned 10/10 (recall 0.750, p50 19 ms). With a B-tree the plan was
  `Limit -> Sort -> Bitmap Heap Scan -> Bitmap Index Scan on items_tenant`. IVFFlat `lists=50`: built in 1.4 s,
  78.4 MiB. Recall@10 at `probes` 1 → 0.866, 4 → 0.915, 16 → 0.961 (p50 1.4 → 9.6 ms).
- Part A, `--spread 3.0`: HNSW recall@10 only 0.365 at `ef_search=10` and 0.836 at 320. IVFFlat 0.238 at
  `probes=1`. Overlapping clusters are much harder.
- Part B: 25 chunks, 384-d. recall@3 / MRR / nDCG@3 = dense 1.000 / 0.967 / 0.975, lexical 0.900 / 0.917 /
  0.883, hybrid-RRF 1.000 / 1.000 / 0.995 on 15 hand-labelled queries. For the query `LUM-5002`, dense ranked
  `nw-02` above the correct `nw-11`, lexical ranked `nw-11` first, and RRF put `nw-11` first. The ACL demo listed
  `fb-08 (hr)` and `fb-04 (hr)` without the filter.
- `--generate` (Qwen2.5-0.5B-Instruct Q4_0): the answer cited `[nw-04]`, which was inside the retrieved set but not
  relevant to the question. The citation check passed. This illustrates its limit.

The corpus and relevance labels are tiny and hand-made. These scores show the *mechanics*, not the quality of any
embedding model.

## Troubleshooting

- `could not resize shared memory segment … No space left on device` during `CREATE INDEX`: the db container needs
  `shm_size` (already set to 1 GB in `compose.yaml`). Parallel index builds use dynamic shared memory.
- `embed` not healthy: the first start downloads the GGUF from Hugging Face. Check `docker logs sd-24-embed-1`.
- Slow HNSW builds: raise `maintenance_work_mem` in `compose.yaml` so the graph fits in memory (pgvector README).
- Port already in use: change the left-hand side of the `ports:` mappings (keep them in 12400–12499).
- Using Ollama instead of llama.cpp: any OpenAI-compatible `/v1/embeddings` endpoint works. Set `EMBED_URL` (and
  `EMBED_MODEL`) in the `app` service.
