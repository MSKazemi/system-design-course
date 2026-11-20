# 24 — Retrieval & vector systems (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- 50M chunks, 2,000 tenants, p95 retrieval < 150 ms
- Zero cross-tenant or cross-ACL leakage
- Edits visible within 15 minutes
- Approximate indexes, filters and freshness fight each other

**Visual:** Lumen logo-free title card; icons `domain-ai`, `arch-search-index`, `security-lock`.
**Speaker notes:** Retrieval decides what goes into the prompt. This chapter makes that decision fast, correct and
safe at multi-tenant scale.

## Slide 2 — Embeddings are a versioned dependency
- Dimension drives memory, CPU and network linearly
- Max input length means silent truncation
- New model version means re-embedding everything
- Matryoshka models: truncate the prefix, re-normalise

**Visual:** a vector as a bar of d cells; a prefix highlighted (Matryoshka).
**Speaker notes:** Store the model name and version next to every vector. Mixing two models in one index is a
silent correctness bug.

## Slide 3 — Exact vs approximate
- Exact k-NN: O(n·d), about 5×10¹⁰ multiply-adds per query at 50M × 1,024
- ANN returns most of the true top-k: recall@k
- Every index has a recall/latency dial
- Measure on your data (ANN-Benchmarks methodology)

**Visual:** recall vs latency curve with a "knee"; icons `ops-latency`, `arch-search-index`.
**Speaker notes:** The design decision is a point on a curve, and the curve depends on your data. L24 shows the
same index giving 0.97 recall on one dataset and 0.64 on a harder one at the same setting.

## Slide 4 — HNSW in one picture
- Multi-layer proximity graph, greedy descent
- `M` (degree), `ef_construction` (build), `ef_search` (query)
- pgvector defaults: m=16, ef_construction=64, ef_search=40
- Needs RAM; deletes are awkward

**Visual:** three stacked layers, sparse at top, dense at bottom, a search path descending.
**Speaker notes:** Latency is dominated by random memory access, so "does the graph fit in RAM?" is the first
question.

## Slide 5 — IVF, PQ, DiskANN
- IVF: k-means lists, scan `nprobe` of them
- PQ: m sub-vectors × 8-bit codes, 4,096 B → 64 B
- DiskANN: PQ in RAM, graph and full vectors on SSD
- Search compressed, rescore exact

**Visual:** a vector split into 8 segments, each replaced by a codebook id; SSD icon `arch-storage-disk`.
**Speaker notes:** The DiskANN paper reports a billion points on one 64 GB-RAM machine. That is the paper's own
benchmark, so measure yours.

## Slide 6 — Storage math
- 50M × 1,024 × 4 B = 204.8 GB float32
- HNSW graph ≈ M × 8–10 B/vector → 6.4–8 GB
- int8 51 GB · PQ-64 3.2 GB · binary 6.4 GB
- "200 GB RAM" → "≈10 GB RAM + SSD"

**Visual:** bar chart of the compression menu (values from the lesson table).
**Speaker notes:** The vectors dominate, not the graph. Compression moves data between tiers.

## Slide 7 — Filtering breaks naive ANN
- Pre-filter: exact scan of matches (great when selective)
- Post-filter: ANN then drop (starves selective filters)
- In-filter: filter-aware traversal (ACORN, Filtered-DiskANN, Qdrant)
- pgvector ≥ 0.8: iterative index scans

**Visual:** 40 candidates, only 0.4 survive a 1% filter; lab result 0.3/10 rows.
**Speaker notes:** L24 reproduces the shortfall and both fixes. For tenants, physical partitioning is often the
safest answer.

## Slide 8 — Hybrid search + reranking
- Dense for paraphrase, BM25 for codes and names
- RRF: Σ 1/(60 + rank), no score calibration needed
- Cross-encoder reranks the top 50–200
- Funnel: ANN + BM25 → RRF → rerank → prompt

**Visual:** funnel diagram from the lesson; icons `search-elasticsearch`, `pattern-fan-in`.
**Speaker notes:** In L24, dense retrieval misranked an error-code query, and RRF fixed it.

## Slide 9 — RAG is two systems
- Ingestion: connectors → parse → chunk → enrich → embed → index
- Query: auth → ACL → hybrid → rerank → generate → citation check
- Metadata: tenant, ACL, version, offsets, model version
- Citations are a data-model feature

**Visual:** two-lane flowchart (write path, read path); icons `arch-queue`, `arch-database`, `arch-worker`.
**Speaker notes:** Most "it can't find it" bugs live in parsing and chunking, not in the index.

## Slide 10 — Freshness and ACLs
- Hash-diffed incremental upserts; hard deletes
- Blue/green index for model upgrades (~208 GPU-hours in the example)
- Filter before the model sees anything
- Early binding + late check; bound group explosion

**Visual:** blue/green index swap with an alias arrow.
**Speaker notes:** Prompt instructions are not a security boundary. ACLs must be enforced in the query.

## Slide 11 — Evaluate stages separately
- Retriever: recall@k, MRR, nDCG
- Generator: faithfulness, answer relevance, context precision/recall (RAGAS)
- LLM-judged metrics need calibration
- Diagnosis table: which stage failed?

**Visual:** 2×2 grid: recall high/low × faithfulness high/low → likely fix.
**Speaker notes:** If you only measure end-to-end, every retrieval regression looks like a model problem.

## Slide 12 — Long context, RAG or GraphRAG?
- Long context: small per-question corpus, whole-document reasoning
- RAG: big corpus, point questions, ACLs, freshness
- GraphRAG: global questions ("main themes?")
- Retrieval keeps per-request tokens bounded

**Visual:** three-column decision card.
**Speaker notes:** Lost in the Middle and RULER show that long windows are used unevenly. Xu et al. found
retrieval with 4K context comparable to a 16K fine-tuned model on their tasks.

## Slide 13 — Interview angle
- CLARIFY corpus, tenants, ACLs, freshness, SLO
- QUANTIFY n·d·bytes, graph, ingestion GPU-hours
- DEEPEN filtering *or* memory *or* evaluation
- Red flags: ACL by prompt, no BM25, no eval, mixed embeddings

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Put numbers on the board in the first five minutes. That is the main thing that separates
senior answers.
