# C02 — News feed / timeline (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C02-news-feed.md](../course/04-case-studies/C02-news-feed.md)

## Slide 1 — The requirement

- 200 M DAU; feed p99 < 300 ms
- Post visible to followers in < 5 s (p95)
- Follower counts from hundreds to tens of millions
- Ranked by a model; blocks effective immediately

**Visual:** A phone feed with a stopwatch (300 ms) and a "posted 5 s ago" label.
Icons: `domain-feed`, `ops-latency`, `domain-follow`.

**Speaker notes:** Work per post grows with followers, work per feed load grows with ranking. Both are skewed, and
both are the design.

## Slide 2 — The numbers

- ≈ 70,000 feed loads/s at peak
- Average post: 200 inserts; one mega-account post: 50 M
- Timelines: ≈ 4.8 TB RAM with overhead and replicas
- Ranking: ≈ 35 M candidate scores/s at peak

**Visual:** Two skewed bars (write amplification, ranking compute) next to a small storage bar.
Icons: `ops-throughput`, `pattern-fan-out`, `domain-ai`.

**Speaker notes:** All labelled assumptions. Storage is not the problem; skewed fan-out and ranking compute are.

## Slide 3 — Sketch

- Post service → event log → fan-out workers → timeline cache
- Feed service: timeline + big-author index + retrieval
- Ranker, visibility filter, hydration
- Async everywhere except the author's own post

**Visual:** The lesson's 14-node flowchart.
Icons: `arch-api-gateway`, `arch-event-stream`, `arch-worker`, `arch-cache`, `domain-ai`.

**Speaker notes:** The event log decouples "accepted" from "delivered" and lets other consumers (search,
notifications) replay posts.

## Slide 4 — Push, pull, hybrid

- Push: cost ∝ followers at write time
- Pull: cost ∝ follows at read time
- Feeding Frenzy (SIGMOD 2010): decide per producer/consumer pair from update rate vs view rate
- Practice: per-author follower threshold

**Visual:** Seesaw: write cost on one side, read cost on the other; threshold *T* as the pivot.
Icons: `pattern-fan-out`, `pattern-fan-in`, `pattern-push`, `pattern-polling`.

**Speaker notes:** If a consumer looks more often than the producer posts, push wins for that pair; otherwise pull.
Systems simplify to a threshold because per-pair state is expensive.

## Slide 5 — Fan-out done right

- Push IDs (16 B), not content
- Skip inactive followers (≈ 60 % fewer inserts in our assumptions)
- Partition the log by author; chunk big follower lists
- Idempotent inserts — the log redelivers

**Visual:** Sequence: post → 201 → log → worker → graph → batched inserts.
Icons: `arch-event-stream`, `pattern-idempotency`, `arch-worker`.

**Speaker notes:** Pushing IDs means edits and deletes need no fan-out; hydration reads the current post.

## Slide 6 — Timeline store

- Capped list of 500 entries ≈ 8 KB per active user
- Partition by user; one partition per feed load
- Miss = rebuild from follows + author index (normal path)
- Lost node → rate-limited rebuilds + cheaper feed meanwhile

**Visual:** A capped list with a trim marker; a rebuild arrow from the author index.
Icons: `arch-cache`, `pattern-sharding`, `pattern-backup`.

**Speaker notes:** Rebuild on miss is also how returning users and failed cache nodes are handled — design it as a
first-class path.

## Slide 7 — The ranking funnel

- Candidates: in-network + out-of-network (≈ 1,500)
- Light ranker → ≈ 500; heavy ranker predicts multiple actions
- Meta: 1,000+ posts per user per day, pass 0 keeps ≈ 500
- X Home Mixer: ≈ 6,000 features per candidate

**Visual:** Funnel diagram with counts at each stage.
Icons: `domain-ai`, `pattern-batching`, `arch-data-pipeline`.

**Speaker notes:** Every published feed uses this funnel. The light ranker exists to keep the expensive model's input
small.

## Slide 8 — A 300 ms budget

- Reads 15 ms ‖ retrieval 30 ms
- Hydration 40 ms, light ranker 20 ms, heavy ranker 80 ms
- Filters + mixing 40 ms, slack 75 ms
- Rank once per session, page from the stored snapshot

**Visual:** Horizontal stacked bar summing to 300 ms.
Icons: `ops-latency`, `ops-slo`.

**Speaker notes:** The exact numbers are assumptions; the habit of budgeting every stage is the senior signal.

## Slide 9 — Degrade, don't fail

- Heavy ranker down → light ranker → chronological
- Fallback rate is an SLI
- Server timeout returns a partial page, not an error
- Feed availability > ranker availability

**Visual:** Three-step fallback ladder.
Icons: `pattern-circuit-breaker`, `ops-slo`, `pattern-timeout`.

**Speaker notes:** Users tolerate a less clever feed far better than an error screen.

## Slide 10 — Pagination and visibility

- Opaque cursor = ranked snapshot + position + seen IDs
- "New posts" pill starts a new snapshot
- Author's own post injected at read time
- Blocks/deletes filtered at read time — never by deleting fan-out entries

**Visual:** Two scroll sessions, offset vs cursor, with duplicates highlighted in the offset version.
Icons: `pattern-pagination`, `security-authorization`.

**Speaker notes:** X's repository states it bluntly: ranking decides order, visibility decides whether a post can be
shown at all.

## Slide 11 — Scale ×10

- 700,000 loads/s; timeline RAM ≈ 48 TB
- Materialize only for the most active users
- Ranker becomes the dominant cost line
- Graph store partitioned with a cache (TAO-style)

**Visual:** Before/after cost pie: fan-out and RAM shrink, ranking grows.
Icons: `pattern-horizontal-scaling`, `ops-cost`.

**Speaker notes:** At ×10 the question changes from "how do we fan out" to "how much ranking can we afford".

## Slide 12 — Modern twist

- X's 2026 open feed: in-network from Thunder, an in-memory recent-posts index (pull)
- Two-tower retrieval for out-of-network
- Transformer ranker with candidate isolation → cacheable scores
- EU DSA Art. 38: a non-profiling feed option for very large platforms

**Visual:** Feed request fanning to an in-memory recent-post index and an embedding index, then a transformer box.
Icons: `company-x`, `domain-ai`, `arch-search-index`, `security-authorization`.

**Speaker notes:** The classic push design is still right for in-network-heavy feeds; recommendation-heavy feeds
shift the balance toward pull and ranking.

## Slide 13 — WRAP

- Junior: push vs pull, data model, celebrity problem
- Senior: hybrid with threshold, idempotent async fan-out, rebuild, cursors, ranking funnel
- Staff: cost of ranking and fan-out, when timelines stop paying, regulatory mode, freshness SLOs
- Red flags: full-content fan-out, offset pagination, blocks by deletion

**Visual:** Staircase junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** Close with numbers: freshness p95, degraded-feed rate, accelerator-seconds per 1,000 loads.
