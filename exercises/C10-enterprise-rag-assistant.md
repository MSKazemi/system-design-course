# C10 — Exercises

Lesson: [course/04-case-studies/C10-enterprise-rag-assistant.md](../course/04-case-studies/C10-enterprise-rag-assistant.md).
Numbers are assumptions unless the lesson gives a source.

## 1. [Core] Index sizing

A tenant has 5 M documents of 3,000 tokens each. Chunks are 500 tokens with 10 % overlap; embeddings are 768-d. Estimate
the number of chunks and the vector storage in float32 and int8.

<details><summary>Answer</summary>

Effective stride ≈ 450 tokens → ≈ 7 chunks/doc → ≈ 35 M chunks. float32: 35 M × 768 × 4 B ≈ 108 GB; int8: ≈ 27 GB,
plus HNSW links (≈ 128 B per vector at M = 16 → ≈ 4.5 GB). Text and metadata add ≈ 35 M × 2.5 KB ≈ 88 GB. One large
tenant can be larger than many shared small tenants combined, which is why isolation tiers exist.
</details>

## 2. [Core] Cost per answer

With 6 chunks of 400 tokens, a 600-token system prompt, 300 tokens of history and 250 output tokens, and assumed prices
of $0.50/M input and $1.50/M output, compute the LLM cost per answer. What does doubling to 12 chunks do?

<details><summary>Answer</summary>

Input = 600 + 300 + 2,400 = 3,300 → $0.00165; output 250 → $0.000375; total ≈ $0.0020. With 12 chunks input = 5,700 →
$0.00285, total ≈ $0.0032 (+60 %). Chunk count is the main cost lever; a reranker that lets you send fewer, better
chunks usually pays for itself.
</details>

## 3. [Deep] Index-time vs query-time permissions

Compare the two for a tenant where the median user can read 2 % of documents. Which do you choose?

<details><summary>Answer</summary>

Query-time post-filtering of a top-50 would leave about one permitted result, and per-candidate source API calls add
latency and hit rate limits. Index-time ACL tokens filter inside the search so only permitted chunks compete, but
correctness depends on sync freshness. Choose index-time filtering with an engine that handles restrictive filters,
plus a late re-check of the final few chunks against a local ACL mirror (and the source for sensitive labels), failing
closed. Mention the propagation-lag SLO.
</details>

## 4. [Deep] Groups as tokens

Alice is removed from group `finance`, which grants access to 40,000 documents (320,000 chunks at the lesson's 8 per document). Describe the update
under (a) per-user ACL lists on chunks and (b) group tokens.

<details><summary>Answer</summary>

(a) Every chunk listing Alice must be rewritten: 320,000 updates (and every future membership change repeats this),
likely missing the 5-minute SLO. (b) Chunks carry `g:finance`; only Alice's principal → token set changes (one row),
effective on her next query. Document-level ACL changes still rewrite that document's chunks, which is bounded. Note
the cache: if token sets are cached in the API tier, the cache TTL is part of the propagation budget.
</details>

## 5. [Core] Freshness budget

Break a 15-minute freshness SLO into stages and say what breaks it during a big tenant's onboarding.

<details><summary>Answer</summary>

Webhook or poll ≤ 5 min; queue wait ≤ 5 min; parse + embed ≤ 2 min; index refresh ≤ 1 min; margin 2 min. During
onboarding, millions of backfill documents fill the queue and incremental changes wait behind them. Fix with a priority
lane for incremental changes, deletions and ACL updates, per-tenant concurrency caps, and a separate backfill worker
pool.
</details>

## 6. [Interview] Prompt injection

A user reports that the assistant answered with a link to an unknown site after reading a wiki page. Explain the
attack and your layered defence.

<details><summary>Answer</summary>

Indirect prompt injection: the wiki page contained instructions the model followed, possibly encoding data into the
link (an exfiltration channel when rendered). Defence: ACL-filtered retrieval so only the asker's readable data is in
context; no side-effect tools in the answer path; delimit sources as data; block rendering of links/images to
non-allowlisted domains; scan outputs; classify ingested chunks for instruction-like text and report to the tenant;
log the answer with retrieved chunk IDs to trace the source. Prompt instructions alone are not sufficient.
</details>

## 7. [Deep] Embedding-model migration

You want to switch to a better embedding model. Plan the migration.

<details><summary>Answer</summary>

Build a new index side by side (blue/green); re-embed in a rate-limited backfill (≈ 4,400 GPU-hours at the lesson's
scale), dual-writing new changes to both indexes; evaluate recall@k per tenant and language under ACL filters on the
eval set; shift traffic gradually per tenant; keep the old index until rollback is no longer needed. Never mix vectors
from two models in one index — distances are not comparable.
</details>

## 8. [Interview] Long context instead of RAG?

A stakeholder argues that million-token context models make RAG obsolete. Respond for this product.

<details><summary>Answer</summary>

A 200 k-document tenant does not fit in any context window; even small corpora would cost hundreds of thousands of
input tokens per answer versus ≈ 5,000; and pasting everything bypasses per-document permissions unless you filter
first — which is retrieval. Long context is useful for reading the retrieved documents in full rather than in small
chunks. Accept a counter-example: for a tiny, uniformly permitted corpus, long context can be simpler.
</details>

## 9. [Lab] Recall under an ACL filter

Use [labs/24-retrieval-vector-systems](../labs/24-retrieval-vector-systems/). Add an `acl` column/payload with random
group tokens so that a test user can read 50 %, 10 % and 1 % of chunks. Measure recall@10 against exact (filtered
brute-force) search for each fraction, with default settings and then with iterative scans (pgvector
`hnsw.iterative_scan`) or the engine's filter-aware index.

<details><summary>Answer</summary>

Expect recall to fall as the permitted fraction shrinks with default post-filtering (pgvector documents that a 10 %
filter with `ef_search` = 40 leaves about 4 results on average), and to recover with iterative scans or filter-aware
indexing at some latency cost. Record measured recall and latency with the engine version; do not reuse numbers from
the lesson as results.
</details>

## 10. [Lab] Cost and fallback at the gateway

Use [labs/26-llm-gateways-llmops](../labs/26-llm-gateways-llmops/). Route RAG answers through the gateway, log input and
output tokens per request, compute cost per answer with assumed prices, then stop the primary model and observe the
fallback.

<details><summary>Answer</summary>

Verify that the token counts per answer match your prompt assembly (system + history + chunks) and that the fallback
model answers within the latency budget. Discuss whether the fallback model must also be EU-hosted for EU tenants —
residency applies to fallbacks too. Report your observed values and versions.
</details>
