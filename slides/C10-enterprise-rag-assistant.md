# C10 — Enterprise RAG assistant (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- 1,000 companies; answers from their wiki, drive, tickets, chat — with citations
- Never show a document the asker cannot open
- Edits ≤ 15 min, revocations ≤ 5 min; EU data stays in the EU; < 1 cent per answer
**Visual:** question bubble → cited answer with three source cards. Icons: `domain-document`, `domain-chat`, `security-lock`.
**Speaker notes:** Weak answers stop at "embed, store, top-k". The interview is about permissions, freshness and trust.

## Slide 2 — CLARIFY
- Which sources; do they offer permission APIs and webhooks?
- Largest tenant size; tolerated revocation delay; tenant-provided LLM?
- Out of scope: training, acting in source systems, public web
**Visual:** question list. Icons: `ops-check`.
**Speaker notes:** The revocation question separates senior answers.

## Slide 3 — QUANTIFY the corpus
- 200 M docs × ≈ 8 chunks ≈ 1.6 B chunks
- 1,024-d float32 ≈ 6.5 TB; int8 ≈ 1.6 TB; HNSW links ≈ 0.2 TB
- Churn 2 %/day → 32 M chunks/day ≈ 4 embedding GPUs (assumption)
- Full re-embed ≈ 4,400 GPU-hours
**Visual:** stacked storage bars. Icons: `arch-database`, `arch-storage-disk`.
**Speaker notes:** Steady state is cheap; changing the embedding model is a project.

## Slide 4 — QUANTIFY queries and cost
- 10 M questions/day; peak ≈ 700 QPS
- ≈ 5,300 input + 300 output tokens per answer
- Assumed prices → ≈ $0.0045 per answer; context tokens dominate
**Visual:** cost breakdown donut (LLM input, output, rerank, retrieval). Icons: `ops-cost`.
**Speaker notes:** Sending 8 well-reranked chunks instead of 20 beats any infrastructure trick.

## Slide 5 — SKETCH: two planes plus permissions
- Ingestion: connectors → per-tenant queue → parse/chunk/embed → hybrid index
- Permission sync → ACL graph → index tokens
- Query: rewrite → ACL-filtered hybrid search → rerank + re-check → LLM with grounding
**Visual:** the lesson flowchart. Icons: `arch-data-pipeline`, `arch-queue`, `arch-search-index`, `arch-api-gateway`.
**Speaker notes:** Permission sync is small, but it is the security-critical pipeline with its own SLO.

## Slide 6 — Connectors and isolation
- Incremental sync + webhooks + periodic reconciliation
- Per-tenant queues: onboarding must not starve freshness
- Isolation: per-tenant index vs shared index with mandatory tenant key vs hybrid tiers
**Visual:** three isolation options as diagrams. Icons: `pattern-partitioning`, `security-lock`.
**Speaker notes:** Enforce the tenant filter in one query builder and test it with cross-tenant canaries.

## Slide 7 — Where to enforce permissions
- Index-time: ACL tokens on chunks, filter inside search — fast, as fresh as the sync
- Query-time: check each candidate at the source — current, slow, recall collapses
- Recommended: index-time filter + late re-check of final chunks, fail closed
**Visual:** two pipelines with a lock at different stages. Icons: `security-authorization`, `security-lock`.
**Speaker notes:** Never retrieve with a service account and ask the LLM to respect permissions.

## Slide 8 — The filter vs ANN trap
- pgvector: filtering happens after the index scan; ef_search 40 + 10 % filter ≈ 4 results
- Fixes: iterative scans (pgvector ≥ 0.8.0), filter-aware graphs (Qdrant)
- Test recall@k under each user's ACL
**Visual:** 40 candidates, 36 greyed out by a filter. Icons: `arch-search-index`, `ops-warning`.
**Speaker notes:** Users with narrow access get empty answers unless the engine handles restrictive filters.

## Slide 9 — Permission sync as an SLA
- Groups as tokens: removing a user from a group = one row, not 450,000 chunks
- Webhooks + change feeds + reconciliation
- Propagation lag p99 ≤ 5 min, alerted like availability
**Visual:** user → groups → token set; one edge removed. Icons: `security-key`, `ops-slo`.
**Speaker notes:** Unmapped identities get no access. "Anyone with the link" is a policy decision.

## Slide 10 — Hybrid retrieval and freshness
- BM25 + ANN → RRF → cross-encoder rerank top ≈ 50 → keep 8
- Query rewrite for follow-ups
- Freshness budget: webhook → queue → embed → refresh ≤ 15 min; priority lane for changes and deletes
**Visual:** retrieval funnel with counts. Icons: `arch-search-index`, `pattern-fan-in`.
**Speaker notes:** Deletions and revocations are urgent; tombstone first, purge later.

## Slide 11 — Trust: citations, groundedness, evaluation
- Numbered chunks; reject invalid citations; quote check
- Groundedness judge per sentence; fall back to "not found"
- Eval harness: ACL-aware recall@k, canary leak = 0, faithfulness (RAGAS-style), human ratings
**Visual:** answer with per-sentence support ticks. Icons: `ops-check`, `ops-dashboard`.
**Speaker notes:** Run the harness on every change to chunking, embeddings, prompts or model.

## Slide 12 — Prompt injection from documents
- Indirect injection: hostile instructions inside retrieved data (Greshake et al.)
- OWASP LLM01:2025: least privilege, segregate untrusted content, human approval
- Real control: the ACL filter; plus no side-effect tools, output link allowlist, detection
**Visual:** wiki page with a hidden instruction being fenced as "data". Icons: `security-bug`, `arch-firewall`.
**Speaker notes:** The model can only leak what the asker could already read — if retrieval is ACL-filtered.

## Slide 13 — STRESS, operate, modern twist
- Missed webhook, source outage, big onboarding, embedding change (blue/green), missing tenant filter
- SLOs: 0 leaks, revocation ≤ 5 min, freshness ≤ 15 min, TTFT < 2.5 s
- 2026: agentic retrieval, MCP connectors, embeddings as personal data, EU residency
**Visual:** failure table + KPI tiles. Icons: `ops-incident`, `arch-region`.
**Speaker notes:** Embeddings can be inverted to text; they follow the same residency and deletion rules.

## Slide 14 — WRAP
- Junior: chunk, embed, top-k, citations
- Senior: sync, ACL tokens, hybrid + rerank, groundedness, eval, cost
- Staff: permission SLA, filter-ANN trap, blue/green re-embed, isolation tiers, residency incl. vectors
- Red flags: service-account retrieval, post-filter top-10, no deletions
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** Close on the permission SLA and the cost per answer.
