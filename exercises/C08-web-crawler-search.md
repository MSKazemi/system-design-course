# C08 — Exercises

Lesson: [course/04-case-studies/C08-web-crawler-search.md](../course/04-case-studies/C08-web-crawler-search.md).
Numbers are assumptions unless the lesson gives a source.

## 1. [Core] Crawl estimate

You must keep 1 B pages at most 7 days old, plus 30 % extra fetches for new URLs. Average page 185 KB. Compute
fetches/s and bandwidth.

<details><summary>Answer</summary>

1 B / 7 days ≈ 143 M/day; × 1.3 ≈ 186 M/day ≈ 2,150 pages/s. Bandwidth ≈ 2,150 × 185 KB ≈ 400 MB/s ≈ 3.2 Gbit/s. With
≤ 1 request/s per host you need ≥ 2,150 hosts concurrently ready. Mention that conditional GETs reduce bytes (304s)
but not request count.
</details>

## 2. [Core] robots.txt edge cases

For each case say what the crawler does under RFC 9309: (a) robots.txt returns 404; (b) returns 503 for 2 hours;
(c) returns 503 for 45 days; (d) `Disallow: /shop` and `Allow: /shop/public` for URL `/shop/public/item`.

<details><summary>Answer</summary>

(a) 4xx = unavailable → may crawl everything. (b) 5xx = unreachable → assume complete disallow (or keep a cached copy
within the cache window). (c) After a long period (the RFC's example is 30 days) the crawler may treat it as
unavailable or continue with a cached copy; pick one and document it — conservative crawlers keep the last good copy.
(d) Both match; the longest match (`/shop/public`, more octets) wins → allowed.
</details>

## 3. [Deep] Frontier design

Explain why a single global priority queue violates politeness, and how front and back queues fix it.

<details><summary>Answer</summary>

A global queue ordered by priority clusters URLs from the same important host at the top, so many fetchers hit one
host at once. Front queues encode priority; back queues hold one host each and are released through a heap keyed by
`next_allowed_fetch`, so each host is fetched at most at its allowed rate while a selector biased toward higher-priority
front queues keeps importance. Sharding the frontier by host hash keeps all state for a host on one node.
</details>

## 4. [Deep] SimHash sizing

For 5 B pages with 64-bit SimHash and k = 3, how big is the fingerprint table, and why does the lookup need permuted
copies?

<details><summary>Answer</summary>

5 B × 8 B = 40 GB per copy. Searching for any fingerprint within Hamming distance 3 by enumerating all flips takes tens
of thousands of probes (Manku et al. report 41,664 for 64-bit, k = 3). Splitting the 64 bits into blocks guarantees that
two fingerprints within distance 3 agree exactly on at least some blocks; keeping copies sorted with those blocks as
the leading bits turns the search into a few range lookups. Trade-off: more copies = more memory, fewer candidates per
probe.
</details>

## 5. [Core] Document vs term partitioning

Your index has 100 shards. Compare the per-query work and the update path for document- vs term-partitioning.

<details><summary>Answer</summary>

Document: every query fans out to 100 shards, each scanning short local lists; a new doc updates one shard. Term: a
2-term query touches ≈ 2 shards but must move long posting lists over the network to intersect them, hot terms create
hot shards, and a new doc touches one shard per distinct term. Document partitioning is the standard choice; mitigate
its fan-out tail with replicas, hedged requests and partial results.
</details>

## 6. [Deep] Recrawl policy

Page A changes every hour; page B every 30 days; page C never. You have budget for 30 fetches/month across the three.
Propose an allocation and justify it.

<details><summary>Answer</summary>

Fetching A 30 times a month still leaves it stale most of the time (it changes 720 times), so heavy investment buys
little freshness. B fetched weekly is fresh most of the time; C needs only rare checks (conditional GET). One reasonable
allocation: A ≈ 20 (only if A is important — importance weighting changes the answer), B ≈ 8, C ≈ 2. The point: optimal
policies depend on the objective (average freshness vs age, weighted by importance), and proportional-to-change-rate is
not automatically best.
</details>

## 7. [Interview] Spider traps

A calendar site generates `/calendar?date=…` for every day until year 9999. How does your crawler notice and contain it?

<details><summary>Answer</summary>

Signals: a host's frontier count growing without bound, deep or highly parameterised URLs, many URLs collapsing to a
few SimHash clusters. Containment: per-host URL budget and depth limit, parameter-pattern learning (drop parameters
that do not change content), prioritise by link importance rather than discovery order. Do not block the host: its
real pages should still be crawled.
</details>

## 8. [Interview] AI-crawler consent

The product team wants to reuse search-crawl pages for model training. What do you change?

<details><summary>Answer</summary>

Introduce a separate crawler product token for training and evaluate robots.txt per purpose; store the per-purpose
decision and fetch time with each page (provenance), so a page allowed for search but disallowed for training is
excluded from training exports, and so later opt-outs can be applied by deleting from derived datasets. Document how
other preference signals (e.g. IETF AIPREF, still drafts as of 2026-11) would be added. Reusing the search token for
training is the red flag.
</details>

## 9. [Lab] Per-host politeness with token buckets

Use [labs/10-apis-communication](../labs/10-apis-communication/) (token bucket vs sliding window). Model each host as
a key with a bucket of capacity 1 and refill 1 token/s; simulate 1,000 URLs from 10 hosts with skewed distribution
(one host has 50 %).

<details><summary>Answer</summary>

Observe that throughput is capped by the number of hosts with tokens, not by the number of workers: the hot host
saturates at 1 request/s and its queue grows, while the others drain quickly. A fetcher that blocks on the hot host
wastes capacity; a heap of hosts ordered by next allowed time (the frontier design) keeps workers busy on other hosts.
Report your observed numbers and lab version.
</details>

## 10. [Lab] Hybrid search recall

Use [labs/24-retrieval-vector-systems](../labs/24-retrieval-vector-systems/). Build BM25 and vector retrieval over the
lab corpus, then fuse them with RRF (`score = Σ 1/(60 + rank)`). Measure recall@10 for (a) BM25, (b) dense, (c) RRF
on queries containing exact identifiers and on paraphrased queries.

<details><summary>Answer</summary>

Expect BM25 to win on exact identifiers (product codes, rare names), dense to win on paraphrases, and RRF to be close
to the better of the two on each set without score calibration — which is the reason it is the default fusion. If RRF
underperforms on your data, try weighting the lists or a learned re-ranker, and report the measured recall with the
embedding model and versions used.
</details>
