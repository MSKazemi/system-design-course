# C08 — Web crawler & search engine (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- Polite crawler for a 5 B-page index; most pages ≤ 10 days old, fast tier ≤ 1 h
- Search API: 10,000 QPS, p95 < 300 ms
- Same corpus feeds a RAG product
**Visual:** globe of hosts feeding a funnel into an index. Icons: `arch-internet`, `arch-search-index`.
**Speaker notes:** One pipeline, two workloads: a politeness-bound crawl and a latency-bound query path.

## Slide 2 — CLARIFY
- Crawl, respect robots.txt, dedup, recrawl, index, search, export to RAG
- Out of scope: JS rendering at scale, images, ads, personalisation
- New question: is the output for humans, for an LLM, or both?
**Visual:** checklist. Icons: `ops-check`, `domain-document`.
**Speaker notes:** The "for an LLM" question changes consent, provenance and the export format.

## Slide 3 — QUANTIFY the crawl
- 5 B pages / 10 days + 60 % extra → ≈ 800 M fetches/day ≈ 9,300 pages/s
- ≈ 185 KB/page (derived from Common Crawl June 2026: 2.10 B pages, 354.59 TiB) → ≈ 14 Gbit/s
- Raw ≈ 925 TB per cycle; compressed ≈ 185 TB (assumption 5 : 1)
**Visual:** arithmetic ladder. Icons: `ops-throughput`, `arch-object-storage`.
**Speaker notes:** Every number except the Common Crawl ratio is an assumption; say so.

## Slide 4 — Politeness turns throughput into "ready hosts"
- ≤ 1 request/s per host → ≥ 9,300 hosts fetched concurrently
- Async fetchers: connections are cheap; ready hosts are scarce
- Group by IP too: shared hosting is one server
- A host with > 864,000 pages cannot be refreshed in 10 days at 1 req/s
**Visual:** many small per-host lanes each with a speed limit. Icons: `pattern-rate-limiter`, `arch-worker`.
**Speaker notes:** The bottleneck is not CPU; it is how many distinct hosts have work ready.

## Slide 5 — SKETCH
- Frontier → fetchers → raw store → parser → URL dedup (back to frontier)
- Content dedup → index builder → sharded index → query fan-out
- Link graph → ranking signals; export to RAG
**Visual:** the lesson flowchart. Icons: `arch-queue`, `arch-worker`, `arch-object-storage`, `arch-search-index`.
**Speaker notes:** The raw store means a parser bug costs a re-parse, not a re-crawl of the web.

## Slide 6 — robots.txt by RFC 9309
- Case-insensitive product-token match; longest match wins; equivalent allow beats disallow
- 4xx → may crawl; 5xx/unreachable → assume full disallow
- Cache ≤ 24 h; parse limit ≥ 500 KiB; follow ≥ 5 redirects
- Crawl-delay is not in the RFC
**Visual:** decision tree on the robots.txt HTTP status. Icons: `security-authorization`, `domain-document`.
**Speaker notes:** Treating a 5xx robots.txt as "allow all" is a classic red flag.

## Slide 7 — The Mercator-style frontier
- Front queues = priority; back queues = one host each
- Min-heap on next_allowed_fetch releases hosts
- Adaptive delay from response time; exponential back-off on 429/503
- Sharded by host hash; DNS cache in the host record
**Visual:** front queues → selector → back queues → heap → fetchers. Icons: `arch-queue`, `pattern-partitioning`, `arch-dns`.
**Speaker notes:** Partitioning by host keeps all politeness state on one shard, with no coordination needed.

## Slide 8 — Dedup at three levels
- URL normalisation + seen-set (Bloom filter in front)
- Exact content hash for mirrors
- SimHash: 64-bit fingerprints, Hamming distance k = 3 at ≈ 8 B pages (Manku et al. 2007)
**Visual:** two near-identical pages → fingerprints differing in 2 bits. Icons: `pattern-deduplication`.
**Speaker notes:** The hard part is the lookup within k bits; permuted sorted tables make it a few probes.

## Slide 9 — Index build and sharding
- Sort-based or SPIMI segments; delta-encoded postings
- Shard by document: fan-out to all shards, cheap updates
- Base index + real-time tier, merged at query time
**Visual:** doc-partitioned vs term-partitioned comparison. Icons: `pattern-sharding`, `data-spark`.
**Speaker notes:** Document partitioning wins almost always for web search; know why.

## Slide 10 — Ranking basics
- Stage 1 per shard: BM25 + static signals (PageRank, spam, freshness)
- Early termination; Stage 2: re-rank top few hundred
- PageRank by power iteration, offline
**Visual:** two-stage funnel. Icons: `domain-leaderboard`, `arch-search-index`.
**Speaker notes:** No per-query PageRank; it is a static signal computed in batch.

## Slide 11 — Freshness
- Budget: ≈ 800 M fetches/day for 5 B pages
- Estimate change rate per page (Cho & Garcia-Molina); conditional GETs → 304s
- Sitemaps' lastmod and feeds reduce blind polling
**Visual:** per-page recrawl intervals stretching or shrinking. Icons: `ops-clock`, `pattern-polling`.
**Speaker notes:** Visiting the fastest-changing pages more is not always optimal; the objective decides.

## Slide 12 — STRESS and scale ×10
- Spider traps → per-host budgets, depth limits, SimHash feedback
- Hot shard → replicas, hedged requests, partial results
- ×10: ≈ 93,000 pages/s; 1,000-way fan-out → ≈ 100,000 naive query nodes, so tiered indexes, early termination and two-level aggregation
**Visual:** failure table. Icons: `ops-warning`, `pattern-fan-out`.
**Speaker notes:** At ×10 the priority function decides coverage more than hardware does.

## Slide 13 — Modern twist
- AI-crawler tokens: GPTBot, OAI-SearchBot, Google-Extended (token only), ClaudeBot, CCBot
- Store consent per purpose with provenance; IETF AIPREF still drafts (as of 2026-11)
- Hybrid search: BM25 + vectors fused with RRF (k = 60)
**Visual:** robots.txt with separate groups for search vs training. Icons: `domain-bot`, `domain-ai`, `arch-search-index`.
**Speaker notes:** Never crawl for AI training under your search user agent.

## Slide 14 — WRAP
- Junior: queue + seen-set + robots + inverted index
- Senior: frontier, SimHash, doc-sharded index, recrawl policy, traps
- Staff: freshness/coverage as budget, consent and provenance, tiers, SLOs for politeness
- Red flags: global FIFO, robots read once, URL-only dedup
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** End with the politeness SLO: being blocked is a coverage outage.
