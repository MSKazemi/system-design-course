---
id: SYSDESIGN-I03
title: "Question bank & rubrics: 90 questions by category and level, what good looks like, red flags"
part: "V — Interview track"
level: [core, deep, frontier]
status: SOURCES_CHECKED
prerequisites: [SYSDESIGN-I01, SYSDESIGN-I02]
estimated_time: "Reference unit — 1h to read the rubric; 45–60 min per practice question"
requirement: "Practice any system design prompt you might be asked in 2026, know which unit of this course prepares you for it, and score your answer the way an interviewer would."
learning_objectives:
  - "Select practice questions by category and level, and map each one to the course units that prepare for it"
  - "Score a design answer against a six-dimension rubric with level-specific anchors"
  - "Recognize the ten most common red flags and the ten strongest signals in system design interviews"
  - "Plan a 4- or 8-week preparation schedule tied to course units and timed mocks"
  - "Prepare for agentic prompts with the expected numbers, red flags and follow-up probes of each agentic question"
last_reviewed: 2026-11-20
---

# I03 — Question bank & rubrics

> **The requirement.** You have four to eight weeks before a loop of interviews. You need to practice prompts like the
> ones you will get, know which material prepares you for each one, and score yourself honestly. Many question lists
> give you prompts without saying what "good" looks like. This unit gives you 90 prompts with what each one tests,
> its key trade-offs, the course units that cover it, and a scoring rubric for each.

## In one minute

The bank has seven categories: **classical**, **data-intensive**, **real-time**, **infrastructure and platform**,
**AI/LLM**, **agentic**, and **security and compliance**. Every question has a one-line prompt, the skill it
tests, the trade-offs a strong answer must address, the units that teach the material, and a rubric with four
outcomes: **No hire**, **Lean**, **Hire** and **Strong hire**. The rubric is this course's own synthesis of public
interviewer guidance [1][2][3] and of the step-by-step signals defined in [I01](I01-interview-playbook.md). No company
publishes its internal rubric, and each company weighs the dimensions differently. Use the scores for practice
feedback, not as a prediction of any specific hiring decision. Every prompt is written for this course: many are
classic problem *domains* that every interviewer uses (a short-link service, a chat system), but the framing,
constraints and rubrics are original.

## Why this matters now

Question pools have widened. Classical prompts remain common because they test fundamentals in a familiar domain.
AI-era prompts now sit beside them: LLM serving, retrieval, gateways, agents and GPU capacity. Security and
compliance constraints (residency, the EU AI Act, supply-chain integrity) increasingly appear as *twists* on classical
prompts rather than as standalone questions. The categories below reflect that mix. The agentic category has grown
to 21 questions because agent prompts combine all the others: a distributed runtime, an LLM workload, and a
security problem whose attacker writes part of the input. Agentic answers also have their own numbers (tokens per
task, exposure, eval-gate size), so those questions carry a *Numbers to expect* line.

## How to use this bank

1. **Pick by level and category.** Each question shows a level band, for example "M → S" for mid to senior. The same
   prompt can be asked at several levels; the rubric anchors shift (see the level calibration table below).
2. **Time-box.** 45 minutes, using the [I01](I01-interview-playbook.md) budget. Record yourself.
3. **Score** with the six-dimension rubric first, then with the question's own rubric.
4. **Study the gaps** in the linked units, then re-run the same prompt a week later with one constraint changed.

**Level key:** J = junior (new grad), M = mid, S = senior, St = staff, P = principal. The band shows the lowest and
highest level at which the prompt is asked; the first letter is the entry level.

**Questions by category and entry level** (counted from the `Level:` lines below):

| Category | J | M | S | St | Total |
|---|---|---|---|---|---|
| Classical (CL) | 8 | 5 | 3 | 0 | 16 |
| Data-intensive (DI) | 1 | 2 | 6 | 1 | 10 |
| Real-time (RT) | 1 | 4 | 4 | 1 | 10 |
| Infrastructure and platform (IP) | 1 | 1 | 8 | 1 | 11 |
| AI/LLM (AI) | 1 | 2 | 9 | 1 | 13 |
| Agentic (AG) | 2 | 6 | 12 | 1 | 21 |
| Security and compliance (SC) | 1 | 1 | 6 | 1 | 9 |
| **All** | **15** | **21** | **48** | **6** | **90** |

**Junior track.** Fifteen questions start at junior level: CL-01, CL-02, CL-04, CL-05, CL-10, CL-12, CL-14, CL-16,
DI-03, RT-10, IP-08, AI-06, AG-20, AG-21 and SC-01. Each has a **Junior scope** line that narrows the prompt (fewer regions,
smaller scale, fewer features) and a **Junior hire** anchor that says what a hire looks like on that narrower scope.
Run the junior scope first; the full prompt and its four rubric outcomes then show what the next level adds. The
junior anchors are course judgment, aligned with the junior row of the level calibration table below.
**Unit links** use this course's canonical paths. Some linked units may still be in draft.

## The course rubric: six dimensions

Each dimension maps to one step of the framework. Score each from 1 to 4, then use the question rubric to check the
domain-specific signals.

| Dimension (step) | 1 — No hire | 2 — Lean | 3 — Hire | 4 — Strong hire |
|---|---|---|---|---|
| **Problem framing** (CLARIFY) | Starts drawing immediately; solves a different problem | Lists requirements but does not rank them; misses the shaping constraint | Ranked NFRs, explicit scope, finds the hidden requirement | Reframes the problem usefully; ties NFRs to business impact; scopes tightly and on time |
| **Quantitative reasoning** (QUANTIFY) | No numbers, or wrong by ≥ 1,000× | Numbers computed but not used | Peak load, state size and one capacity unit drive decisions | Finds the dominant number (cost, KV memory, fan-out factor) and builds the design around it |
| **Architecture** (SKETCH) | Incoherent or incomplete request path | Works end to end but boxes are unjustified | Clean design, each box justified, API and data model match access patterns | Minimal design; knows what not to build; clear evolution path |
| **Depth** (DEEPEN) | Stays at box names under probing | One mechanism explained, no alternatives | Two deep dives at trade-off level, with edge cases | Expert depth where risk lives; quantified trade-offs; switching triggers |
| **Resilience and operations** (STRESS) | No failure discussion | "Add replicas"; generic | Specific failures with detection and mitigation; overload behavior; SLOs | Correlated failures, blast radius, cost of reliability, rollout and recovery |
| **Communication** (all, WRAP) | Hard to follow; ignores hints | Follows but does not drive | Drives with check-ins; follows redirects; clear summary | Runs the session like a design review; trade-off sentences with triggers throughout |

**Level calibration.** For a **hire** decision, a reasonable expectation (course synthesis) is:

| Level | Minimum typical profile |
|---|---|
| Junior | ≥ 2 on all dimensions, 3 on Architecture with help, and coachable under hints |
| Mid | ≥ 3 on Framing, Quantitative and Architecture; ≥ 2 elsewhere |
| Senior | ≥ 3 on all six; at least one 4, usually Depth |
| Staff | ≥ 3 on all six; 4 on Framing or Quantitative, *and* on Resilience or Depth |
| Principal | Mostly 4; framing that changes the problem; credible multi-year evolution and organizational view |

## Classical (CL)

#### CL-01 · Short links with custom domains and click analytics
**Level:** J → S · **Units:** [C01](../04-case-studies/C01-url-shortener-rate-limiter.md), [04](../01-foundations/04-caching.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** Lumen lets customers create short links on their own domains (`go.example.com/abc`) with click counts per day.
- **Tests:** ID generation, read-heavy caching, write path vs analytics path separation, multi-tenant routing.
- **Key trade-offs:** random vs sequential IDs (enumeration risk vs simplicity); synchronous vs asynchronous click counting; cache TTL vs link edits; per-tenant domain TLS certificates.
- **Junior scope:** one Lumen-owned domain (`go.example.com`) instead of customer domains, and daily click totals only; skip certificate automation.
- **Rubric.** *No hire:* counts clicks with a synchronous database update on the redirect path. *Lean:* caches redirects but has no plan for ID collisions or analytics volume. *Hire:* 301 vs 302 trade-off explained, async click events, collision-free ID scheme, cache sized from QPS. *Strong hire:* custom-domain certificate automation, abuse (phishing) controls, and analytics as a stream with late events.
- **Junior hire (on the junior scope):** a cache in front of the link store on the redirect path, an ID scheme with a stated collision check, and clicks recorded off the redirect path (an event queue aggregated later).

#### CL-02 · A distributed rate limiter for a public API
**Level:** J → S · **Units:** [C01](../04-case-studies/C01-url-shortener-rate-limiter.md), [10](../01-foundations/10-apis-communication.md), [11](../01-foundations/11-reliability-engineering.md)
- **Prompt:** Enforce per-key limits (e.g. 100 requests/s, 1 M/day) across 40 gateway nodes in 3 regions.
- **Tests:** algorithms (token bucket, sliding window), shared state, accuracy vs latency, failure behavior.
- **Key trade-offs:** central counter (exact, slow) vs local buckets with periodic sync (fast, approximate); fail open vs fail closed; per-region vs global limits.
- **Junior scope:** one region and one gateway cluster, a single per-key limit of 100 requests/s; skip daily quotas and cross-region sync.
- **Rubric.** *No hire:* one counter in one database on every request with no failure plan. *Lean:* knows token bucket but not how to share it across nodes. *Hire:* compares algorithms, uses an atomic increment or script in an in-memory store, states the over-admission bound. *Strong hire:* hierarchical limits, local pre-allocation of tokens, explicit fail-open policy by endpoint risk, and headers that let clients back off.
- **Junior hire (on the junior scope):** explains token bucket or a sliding window, keeps counters in a shared in-memory store with an atomic increment and an expiry, and says what happens to requests when that store is down.

#### CL-03 · Home timeline with creator accounts
**Level:** M → St · **Units:** [C02](../04-case-studies/C02-news-feed.md), [04](../01-foundations/04-caching.md), [08](../01-foundations/08-async-event-driven.md)
- **Prompt:** A social feature in Lumen where users follow people and teams; some creators have 5 M followers.
- **Tests:** fan-out on write vs read, the celebrity problem, ranking vs chronology, cache memory sizing.
- **Key trade-offs:** write amplification vs read latency; hybrid fan-out threshold; precomputed vs on-demand ranking.
- **Rubric.** *No hire:* one SQL join over all followed users on every feed read at scale. *Lean:* fan-out on write without addressing large accounts. *Hire:* hybrid fan-out with a stated follower threshold, timeline cache sized in GB, pagination. *Strong hire:* quantified threshold choice, backfill when following someone new, ranking stage separated from candidate retrieval, and deletion/visibility propagation.

#### CL-04 · Group chat with presence and offline delivery
**Level:** J → S · **Units:** [C03](../04-case-studies/C03-chat-presence.md), [10](../01-foundations/10-apis-communication.md), [06](../01-foundations/06-replication-consistency.md)
- **Prompt:** Lumen workspaces get chat channels of up to 50,000 members, read receipts and online status.
- **Tests:** long-lived connections, per-channel ordering, delivery to offline devices, presence fan-out cost.
- **Key trade-offs:** WebSocket gateway stickiness vs rebalancing; per-channel sequence numbers vs global order; presence accuracy vs fan-out traffic.
- **Junior scope:** one-to-one chats and small groups (up to 100 members), no read receipts; online status optional.
- **Rubric.** *No hire:* polling the database for new messages. *Lean:* WebSockets but no ordering or reconnection story. *Hire:* connection gateway plus message service, per-channel sequence, sync-from-cursor on reconnect, push for offline. *Strong hire:* presence throttled or aggregated for large channels, Little's-law connection sizing, multi-device read state, and gateway drain during deploys.
- **Junior hire (on the junior scope):** persistent connections (for example WebSockets) through a gateway, messages stored with a per-chat sequence number, and a reconnecting client fetching everything after its last-seen sequence.

#### CL-05 · Video upload, transcoding and adaptive streaming
**Level:** J → St · **Units:** [C04](../04-case-studies/C04-video-streaming.md), [13](../01-foundations/13-data-at-scale.md), [16](../02-modern-requirements/16-cost-as-requirement.md)
- **Prompt:** Lumen adds recorded meeting videos: upload, transcode into several renditions, and stream worldwide.
- **Tests:** resumable uploads, async pipelines, object storage, CDN economics.
- **Key trade-offs:** transcode all renditions upfront vs on demand; storage tiers by popularity; CDN vs origin egress cost.
- **Junior scope:** upload and playback in one region with one or two renditions; leave out worldwide delivery economics.
- **Rubric.** *No hire:* uploads through the application servers into a database. *Lean:* object storage and a queue, but no idea of egress scale. *Hire:* presigned multipart uploads, a DAG of transcode jobs, HLS/DASH renditions, CDN; bandwidth estimated. *Strong hire:* cost model of storage vs egress, popularity-based tiering, idempotent job retries, and per-region processing for residency.
- **Junior hire (on the junior scope):** uploads go straight to object storage through a presigned URL, a queue triggers transcode workers, the user sees processing status, and playback is served from object storage behind a CDN.

#### CL-06 · Proximity matching for field technicians
**Level:** M → S · **Units:** [C05](../04-case-studies/C05-ride-hailing-proximity.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** Match a customer request to the nearest available technician among 200 k who report location every 5 s.
- **Tests:** geospatial indexing, high-rate location writes, consistency of "available" state.
- **Key trade-offs:** geohash vs quadtree vs H3-style cells; in-memory index vs database; optimistic matching vs locking a technician.
- **Rubric.** *No hire:* scans all technicians with a distance formula per request. *Lean:* a geo index but no write-rate estimate (40 k updates/s). *Hire:* in-memory cell index partitioned by region, TTL on stale locations, an atomic reserve step. *Strong hire:* hot-cell splitting, double-dispatch prevention via lease/fencing, and ETA from road graph vs straight line.

#### CL-07 · Payments with a double-entry ledger
**Level:** S → St · **Units:** [C06](../04-case-studies/C06-payments-ledger.md), [08](../01-foundations/08-async-event-driven.md), [05](../01-foundations/05-choosing-storage.md)
- **Prompt:** Lumen charges seat-based subscriptions through two external payment providers and keeps its own ledger.
- **Tests:** idempotency, external side effects, reconciliation, strong consistency where money moves.
- **Key trade-offs:** synchronous provider call vs async with state machine; single ledger database vs sharded; outbox vs dual writes.
- **Rubric.** *No hire:* "exactly-once" asserted without idempotency keys. *Lean:* idempotency at the API but no reconciliation. *Hire:* payment state machine, idempotency keys end to end, append-only double-entry entries, outbox for events, daily reconciliation. *Strong hire:* the unknown-outcome timeout case, provider failover rules, audit and immutability, and correction entries instead of updates.

#### CL-08 · A Dynamo-style key-value store
**Level:** S → St · **Units:** [C07](../04-case-studies/C07-distributed-kv-store.md), [06](../01-foundations/06-replication-consistency.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** Build an internal KV store for session and cart data: 1 M ops/s, single-digit ms p99, tolerates a zone loss.
- **Tests:** partitioning, replication, quorum math, conflict resolution, membership.
- **Key trade-offs:** consistent hashing with virtual nodes vs range partitioning; N/R/W choices; last-writer-wins vs vector clocks or CRDTs.
- **Rubric.** *No hire:* one primary with replicas and no partitioning. *Lean:* consistent hashing but no quorum reasoning. *Hire:* R + W > N explained, hinted handoff, read repair or anti-entropy, rebalancing. *Strong hire:* conflict semantics per data type, tail-latency mitigation (hedged reads), zone-aware replica placement and the cost of each choice.

#### CL-09 · A crawler for a vertical search engine
**Level:** M → St · **Units:** [C08](../04-case-studies/C08-web-crawler-search.md), [13](../01-foundations/13-data-at-scale.md)
- **Prompt:** Crawl 500 M technical documentation pages, refresh popular ones daily, and respect site policies.
- **Tests:** URL frontier design, politeness, dedup, freshness scheduling.
- **Key trade-offs:** BFS vs priority frontier; per-host queues; exact vs near-duplicate detection; re-crawl frequency vs cost.
- **Rubric.** *No hire:* a single queue of URLs with no politeness. *Lean:* politeness, but no estimate of pages/s or storage. *Hire:* per-host back queues, robots handling, content hashing, frontier persisted, throughput estimate. *Strong hire:* change-rate-based recrawl scheduling, near-duplicate detection (e.g. SimHash-style), spider-trap defenses, and cost per refreshed page.

#### CL-10 · Typeahead for workspace search
**Level:** J → S · **Units:** [13](../01-foundations/13-data-at-scale.md), [04](../01-foundations/04-caching.md)
- **Prompt:** Suggest completions within 50 ms as users type, mixing popular queries and the user's own documents.
- **Tests:** prefix structures, precomputation, personalization, latency budgets.
- **Key trade-offs:** trie vs sorted prefix index in a search engine; global vs per-user suggestions; update frequency vs freshness.
- **Junior scope:** global suggestions from popular queries only, without the user's own documents; keep the 50 ms target.
- **Rubric.** *No hire:* `LIKE 'abc%'` on the primary database per keystroke. *Lean:* a trie, but no plan for updates or memory. *Hire:* precomputed top-k per prefix, client debouncing, cache at the edge for global suggestions, per-tenant isolation. *Strong hire:* blending global and private results without leaking private titles across tenants, and offline popularity aggregation.
- **Junior hire (on the junior scope):** top-k completions precomputed per prefix and served from memory, client-side debouncing, and a scheduled job that rebuilds popularity counts.

#### CL-11 · File sync and sharing
**Level:** M → St · **Units:** [05](../01-foundations/05-choosing-storage.md), [08](../01-foundations/08-async-event-driven.md), [13](../01-foundations/13-data-at-scale.md)
- **Prompt:** Desktop and mobile sync of Lumen workspace files, with sharing and offline edits.
- **Tests:** chunking and dedup, metadata vs blob separation, conflict handling, change notification.
- **Key trade-offs:** fixed vs content-defined chunking; last-writer-wins vs conflict copies; push vs long-poll for changes.
- **Rubric.** *No hire:* re-uploads whole files on every change. *Lean:* chunks but no conflict policy. *Hire:* metadata service with versioned file tree, content-addressed chunks, per-user change journal with cursor. *Strong hire:* conflict copies with a clear rule, dedup economics, and permission changes propagating to offline clients.

#### CL-12 · Notification platform
**Level:** J → St · **Units:** [I01 mock](I01-interview-playbook.md#worked-mock-interview-a-notification-service-for-lumen), [08](../01-foundations/08-async-event-driven.md), [11](../01-foundations/11-reliability-engineering.md)
- **Prompt:** A shared service that delivers push, email, SMS and in-app notifications for every Lumen team.
- **Tests:** priority isolation, preferences, dedup, provider failure, cost.
- **Key trade-offs:** one queue vs priority lanes; at-least-once plus idempotent send vs best-effort; per-user caps vs producer freedom.
- **Junior scope:** email and push only, one priority level, no quiet hours.
- **Rubric.** *No hire:* synchronous send in the producer's request. *Lean:* a queue but no priority isolation. *Hire:* priority lanes, preference lookups with cache, dedup keys, per-channel senders with circuit breakers. *Strong hire:* unknown-outcome send handling, quiet-hours scheduling with jitter, cost (SMS) as a first-class constraint.
- **Junior hire (on the junior scope):** producers enqueue a request instead of sending, workers look up preferences and call the provider, retries use backoff, and a dedup key stops a retry from sending twice.

#### CL-13 · Ticket booking with seat holds
**Level:** M → St · **Units:** [C14](../04-case-studies/C14-global-flash-sale.md), [05](../01-foundations/05-choosing-storage.md), [09](../01-foundations/09-coordination-consensus.md)
- **Prompt:** A conference ticket sale for 20 k seats, opening to 2 M waiting users at once.
- **Tests:** contention, holds with expiry, fairness, overload protection.
- **Key trade-offs:** pessimistic locks vs conditional updates; virtual waiting room vs open admission; hold duration vs abandoned inventory.
- **Rubric.** *No hire:* no concurrency control on seat assignment. *Lean:* row locks without considering the burst. *Hire:* waiting room with admission rate, conditional updates per seat, hold TTLs, idempotent checkout. *Strong hire:* hot-row sharding of inventory counters, bot defense, and fairness definition tied to queue position.

#### CL-14 · Unique IDs at a million per second
**Level:** J → S · **Units:** [09](../01-foundations/09-coordination-consensus.md)
- **Prompt:** Generate sortable, unique 64-bit IDs for messages across 3 regions without a central bottleneck.
- **Tests:** ID layout, clocks, coordination avoidance.
- **Key trade-offs:** time-ordered layouts (timestamp + node + sequence) vs random UUIDs; clock skew handling; ID space exhaustion.
- **Junior scope:** one region; design the 64-bit layout and explain how each generator gets its node ID.
- **Rubric.** *No hire:* database auto-increment shared by all regions. *Lean:* timestamp + random, without collision math. *Hire:* bit layout with stated years of headroom, node ID assignment, sequence per millisecond. *Strong hire:* clock rollback behavior, leased node IDs with fencing, and when a 128-bit UUIDv7 (RFC 9562 [4]) is acceptable because the 64-bit requirement can be relaxed.
- **Junior hire (on the junior scope):** a timestamp + node + sequence layout with bits per field and the years of headroom computed, and a stated rule for a clock that moves backwards (wait, or refuse to issue IDs).

#### CL-15 · A distributed job scheduler
**Level:** S → St · **Units:** [09](../01-foundations/09-coordination-consensus.md), [08](../01-foundations/08-async-event-driven.md)
- **Prompt:** Run 10 M scheduled jobs per day (cron-style and one-off) for Lumen services, each at least once and on time.
- **Tests:** time-bucketed storage, leader election, exactly-once effects, backlog recovery.
- **Key trade-offs:** polling buckets vs timer wheels; single leader vs partitioned schedulers; missed-run policy after an outage.
- **Rubric.** *No hire:* one machine running cron. *Lean:* a database table polled every second without partitioning. *Hire:* partitioned time buckets, lease-based ownership, idempotent job execution, misfire policy. *Strong hire:* thundering-herd control at the top of the hour, fencing tokens, and backpressure to downstream systems.

#### CL-16 · Live leaderboard
**Level:** J → M · **Units:** [04](../01-foundations/04-caching.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** A weekly leaderboard for a Lumen learning challenge: 5 M participants, rank lookups and top-100 views.
- **Tests:** sorted structures, sharding of ranks, approximate vs exact.
- **Key trade-offs:** single sorted set vs sharded with merge; exact rank vs percentile buckets.
- **Junior scope:** one region and one leaderboard; exact rank for the top 100 and for the user's own entry.
- **Rubric.** *No hire:* `ORDER BY score` over the full table per request. *Lean:* sorted set but no persistence or scale plan. *Hire:* in-memory sorted set with persistence, sized in memory, top-k cached. *Strong hire:* shard-by-score-range or approximate rank for the tail, anti-cheat, and weekly reset without downtime.
- **Junior hire (on the junior scope):** an in-memory sorted set with its memory estimated from entries × bytes per entry, scores also persisted to a database, and the top 100 cached.

## Data-intensive (DI)

#### DI-01 · Ad-click aggregation with correct counts
**Level:** S → St · **Units:** [20](../02-modern-requirements/20-real-time-streaming.md), [08](../01-foundations/08-async-event-driven.md)
- **Prompt:** Count clicks per ad per minute for billing, from 50 k events/s, with late and duplicate events.
- **Tests:** stream processing semantics, windows, watermarks, reconciliation with batch.
- **Key trade-offs:** event time vs processing time; allowed lateness vs latency; exactly-once processing vs idempotent sinks.
- **Rubric.** *No hire:* increments a database counter per click. *Lean:* stream job but processing-time windows. *Hire:* event-time windows with watermarks, dedup by click ID, idempotent upserts, raw log retained. *Strong hire:* batch reconciliation for billing, late-data corrections, and fraud filtering before billing counts.

#### DI-02 · Metrics and alerting platform
**Level:** S → St · **Units:** [12](../01-foundations/12-observability.md), [13](../01-foundations/13-data-at-scale.md)
- **Prompt:** Ingest 20 M samples/s from Lumen's fleet, keep 13 months, and evaluate 50 k alert rules.
- **Tests:** time-series storage, cardinality, downsampling, query fan-out.
- **Key trade-offs:** pull vs push collection; cardinality limits vs flexibility; raw retention vs rollups.
- **Rubric.** *No hire:* one relational table of samples. *Lean:* a TSDB but no cardinality control. *Hire:* sharded ingestion, compressed chunks, rollups for old data, rule evaluation separated from queries. *Strong hire:* per-tenant cardinality budgets, alerting that survives the outage it reports on, and burn-rate alerts.

#### DI-03 · Log ingestion and search
**Level:** J → S · **Units:** [13](../01-foundations/13-data-at-scale.md), [12](../01-foundations/12-observability.md)
- **Prompt:** 5 TB/day of application logs, searchable within 30 s, kept 30 days hot and 1 year cold.
- **Tests:** buffering, indexing cost, tiered storage.
- **Key trade-offs:** full-text index vs label index plus brute-force scan; hot vs cold tiers; sampling.
- **Junior scope:** about 50 GB/day from a handful of services, searchable within a minute, 7 days of retention, no cold tier.
- **Rubric.** *No hire:* writes logs synchronously from apps into a search cluster with no buffer. *Lean:* a buffer, but storage cost not estimated. *Hire:* agent → log → indexers, index sizing, object-storage cold tier. *Strong hire:* cost per GB ingested and retained, label-only indexing as a cheaper option, and PII scrubbing at ingestion.
- **Junior hire (on the junior scope):** agents ship logs to a buffer (a queue or log), an indexer writes to a search store, indexes are dropped by age, and storage is estimated as GB/day × retention days × replicas.

#### DI-04 · Product analytics lakehouse
**Level:** S → St · **Units:** [13](../01-foundations/13-data-at-scale.md), [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md)
- **Prompt:** Give Lumen's analysts SQL over 3 years of product events (2 B/day) with daily and hourly freshness.
- **Tests:** table formats, partitioning, compaction, governance.
- **Key trade-offs:** warehouse vs lakehouse; partition granularity vs small files; streaming ingest vs batch.
- **Rubric.** *No hire:* runs analytics on the production database. *Lean:* a lake of files with no table format or compaction. *Hire:* open table format, partitioning by date, compaction, schema evolution. *Strong hire:* deletion for GDPR at table level, cost of scans, and data contracts with producers.

#### DI-05 · CDC to search index and cache
**Level:** M → S · **Units:** [20](../02-modern-requirements/20-real-time-streaming.md), [08](../01-foundations/08-async-event-driven.md), [04](../01-foundations/04-caching.md)
- **Prompt:** Keep a search index and a cache in sync with Lumen's primary database within 2 s.
- **Tests:** dual-write problems, ordering, replays.
- **Key trade-offs:** dual writes vs CDC vs outbox; per-key ordering; full reindex strategy.
- **Rubric.** *No hire:* application writes to database, cache and index separately with no failure handling. *Lean:* CDC but no ordering or reindex plan. *Hire:* log-based CDC, per-key partitioning, idempotent upserts, backfill. *Strong hire:* schema changes in the stream, lag SLO, and how to rebuild the index with zero downtime (alias swap).

#### DI-06 · GDPR erasure across a distributed estate
**Level:** S → P · **Units:** [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md), [13](../01-foundations/13-data-at-scale.md)
- **Prompt:** Delete one user's personal data within GDPR's one-month response window (Art. 12(3), extendable by two further months where necessary [8]) across databases, caches, search, logs, backups and ML training sets.
- **Tests:** data inventory, propagation, proof of deletion, backups.
- **Key trade-offs:** physical deletion vs crypto-shredding; backup rewrite vs expiry; retaining legally required records.
- **Rubric.** *No hire:* "run DELETE in the user table". *Lean:* lists stores but no propagation mechanism. *Hire:* deletion events with per-system acknowledgements, audit trail, per-user keys for crypto-shredding where it fits. *Strong hire:* lineage to derived datasets and models, legal-hold exceptions, and a verifiable completion report.

#### DI-07 · Multi-tenant SaaS database strategy
**Level:** S → St · **Units:** [07](../01-foundations/07-partitioning-sharding.md), [05](../01-foundations/05-choosing-storage.md), [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** 20 k Lumen tenants from 5 users to 50 k users each. Choose the data layout.
- **Tests:** isolation vs efficiency, noisy neighbors, migrations.
- **Key trade-offs:** shared schema with tenant ID vs schema-per-tenant vs database-per-tenant; tenant moves between shards.
- **Rubric.** *No hire:* no tenant isolation in queries. *Lean:* picks one model without discussing large tenants. *Hire:* shared tables partitioned by tenant for small tenants, dedicated cells for large ones, row-level security. *Strong hire:* online tenant migration, per-tenant backup and restore, and cost allocation.

#### DI-08 · Global profile store with read-your-writes
**Level:** S → St · **Units:** [06](../01-foundations/06-replication-consistency.md), [15](../02-modern-requirements/15-multi-region-edge.md)
- **Prompt:** User profiles read worldwide in < 20 ms; a user must always see their own edits.
- **Tests:** replication topologies, session consistency, conflict handling.
- **Key trade-offs:** single home region per user vs multi-leader; sticky reads vs version tokens.
- **Rubric.** *No hire:* synchronous replication across all regions on every write. *Lean:* async replicas, with read-your-writes not handled. *Hire:* home region per user, replicas elsewhere, version tokens in the session for read-your-writes. *Strong hire:* moving a user's home region, conflict rules for rare multi-region writes, and residency constraints.

#### DI-09 · Object storage service
**Level:** St → P · **Units:** [13](../01-foundations/13-data-at-scale.md), [06](../01-foundations/06-replication-consistency.md), [09](../01-foundations/09-coordination-consensus.md)
- **Prompt:** Build Lumen's internal blob store: 50 PB, eleven-nines-style durability target, strong read-after-write.
- **Tests:** metadata vs data plane, erasure coding, durability math, repair.
- **Key trade-offs:** replication vs erasure coding (cost vs repair traffic); metadata consistency model; placement across failure domains.
- **Rubric.** *No hire:* files on a shared NFS server. *Lean:* replication without durability math. *Hire:* separate metadata service (strongly consistent), erasure-coded data across zones, background scrubbing and repair. *Strong hire:* durability estimate from failure and repair rates, repair bandwidth budgeting, and a large-object multipart protocol.

#### DI-10 · Trending topics (heavy hitters)
**Level:** M → S · **Units:** [20](../02-modern-requirements/20-real-time-streaming.md), [13](../01-foundations/13-data-at-scale.md)
- **Prompt:** Show the top 50 trending searches in Lumen per region over the last hour, updated every minute.
- **Tests:** approximate algorithms, windowing, merge across partitions.
- **Key trade-offs:** exact counts vs count-min sketch / space-saving; sliding vs tumbling windows; trending (velocity) vs popular (volume).
- **Rubric.** *No hire:* GROUP BY over all searches each minute. *Lean:* streaming counts but no memory bound. *Hire:* partitioned local top-k with a global merge, approximate counting with error bounds. *Strong hire:* trend defined as velocity against a baseline, spam resistance, and cold-start for new terms.

## Real-time (RT)

#### RT-01 · Collaborative document editing
**Level:** S → St · **Units:** [06](../01-foundations/06-replication-consistency.md), [10](../01-foundations/10-apis-communication.md)
- **Prompt:** Lumen documents with 50 simultaneous editors, offline edits and cursor presence.
- **Tests:** OT vs CRDT, sync protocol, persistence of operation logs.
- **Key trade-offs:** server-ordered OT vs CRDT merge; operation log vs snapshots; per-document server affinity.
- **Rubric.** *No hire:* last-writer-wins on the whole document. *Lean:* names CRDTs but cannot explain merge or storage growth. *Hire:* one approach explained with its convergence property, document session routing, snapshots plus op log. *Strong hire:* offline merge semantics, tombstone compaction, and permission changes during a live session.

#### RT-02 · Live scores to 50 M clients
**Level:** M → St · **Units:** [10](../01-foundations/10-apis-communication.md), [15](../02-modern-requirements/15-multi-region-edge.md)
- **Prompt:** Push score changes to 50 M connected app users within 2 s during a final.
- **Tests:** fan-out trees, edge delivery, connection density.
- **Key trade-offs:** WebSocket vs SSE vs push notifications vs polling a CDN object; per-match topics; message coalescing.
- **Rubric.** *No hire:* a single server broadcasting to everyone. *Lean:* pub/sub, but connection count never estimated. *Hire:* edge connection tier sized by Little's law, hierarchical fan-out, coalescing of rapid updates. *Strong hire:* CDN-cached snapshot plus delta stream for reconnect storms, and graceful degradation to polling.

#### RT-03 · Real-time fraud scoring
**Level:** S → St · **Units:** [C12](../04-case-studies/C12-realtime-fraud-recsys.md), [20](../02-modern-requirements/20-real-time-streaming.md), [27](../03-ai-systems/27-ml-platforms.md)
- **Prompt:** Score every Lumen payment and sign-up in < 100 ms using fresh behavioral features.
- **Tests:** online feature computation, model serving latency, feedback labels.
- **Key trade-offs:** streaming vs on-request features; rules vs model; block vs step-up vs allow thresholds.
- **Rubric.** *No hire:* nightly batch scoring. *Lean:* online model but stale features. *Hire:* streaming feature pipeline into an online store, low-latency model, rules fallback, label feedback loop. *Strong hire:* train-serve skew controls, delayed-label handling, and threshold tuning as a cost trade-off between losses and friction.

#### RT-04 · Order matching engine
**Level:** St → P · **Units:** [09](../01-foundations/09-coordination-consensus.md), [11](../01-foundations/11-reliability-engineering.md)
- **Prompt:** A matching engine for an internal marketplace with strict price-time priority and 100 µs p99.
- **Tests:** single-threaded deterministic core, replication via log, latency engineering.
- **Key trade-offs:** in-memory sequencer vs database; active-passive via replicated log vs consensus per order.
- **Rubric.** *No hire:* a database transaction per order. *Lean:* in-memory matching without a recovery plan. *Hire:* sequenced input log, deterministic single-threaded matcher per instrument, replay for recovery. *Strong hire:* hot standby replaying the same log, mechanical sympathy (no GC pauses, pinned cores), and fairness on the ingress path.

#### RT-05 · Live location tracking and ETA
**Level:** M → S · **Units:** [C05](../04-case-studies/C05-ride-hailing-proximity.md), [20](../02-modern-requirements/20-real-time-streaming.md)
- **Prompt:** Show a customer the live position and ETA of an assigned technician, updated every 3 s.
- **Tests:** high-rate small writes, subscription routing, smoothing.
- **Key trade-offs:** store every point vs latest only plus sampled history; push vs poll; client interpolation.
- **Rubric.** *No hire:* writes every point to a relational table and polls it. *Lean:* in-memory latest location but no subscription design. *Hire:* location stream, latest-state store, per-trip channel to the customer, history sampled to cold storage. *Strong hire:* battery and bandwidth trade-off on the device, map-matching, and privacy expiry after the trip.

#### RT-06 · Multiplayer state synchronization
**Level:** S → St · **Units:** [10](../01-foundations/10-apis-communication.md), [15](../02-modern-requirements/15-multi-region-edge.md)
- **Prompt:** A real-time collaborative whiteboard game for 8 players per room, 60 ms target for remote updates.
- **Tests:** authoritative server, UDP vs TCP, region selection, rooms as units of scale.
- **Key trade-offs:** authoritative server vs peer-to-peer; client prediction vs consistency; room placement.
- **Rubric.** *No hire:* central database round trip per move. *Lean:* WebSockets to one global server. *Hire:* room servers in the region nearest the players, authoritative state, snapshot plus deltas. *Strong hire:* lag compensation, room migration on server failure, and matchmaking that accounts for latency.

#### RT-07 · Live reactions on a broadcast
**Level:** M → S · **Units:** [C02](../04-case-studies/C02-news-feed.md), [10](../01-foundations/10-apis-communication.md)
- **Prompt:** 2 M viewers of a Lumen all-hands send emoji reactions and comments, shown live to everyone.
- **Tests:** write aggregation, sampling for display, fan-out.
- **Key trade-offs:** show every comment vs sample; aggregate counts at the edge; moderation latency.
- **Rubric.** *No hire:* broadcasts every reaction to every viewer. *Lean:* pub/sub, but no aggregation. *Hire:* edge aggregation of counts per second, sampled comment stream, rate limits per viewer. *Strong hire:* moderation in the path with a latency budget, and a fair sampling policy that is explicitly not random spam.

#### RT-08 · IoT telemetry with alerting
**Level:** M → S · **Units:** [20](../02-modern-requirements/20-real-time-streaming.md), [12](../01-foundations/12-observability.md)
- **Prompt:** 2 M sensors in Lumen's office-energy product report every 10 s; alert on anomalies within 1 minute.
- **Tests:** ingestion protocol, partitioning, stateful stream processing.
- **Key trade-offs:** MQTT vs HTTP ingestion; per-device state in the stream job vs external store; edge filtering.
- **Rubric.** *No hire:* devices write straight into a relational database. *Lean:* a broker but no partitioning or late-data handling. *Hire:* broker → log → stateful stream processing keyed by device, TSDB for history, alert dedup. *Strong hire:* device auth and certificate rotation, backfill after connectivity loss, and alert fatigue control.

#### RT-09 · Real-time personalization features
**Level:** S → St · **Units:** [20](../02-modern-requirements/20-real-time-streaming.md), [27](../03-ai-systems/27-ml-platforms.md)
- **Prompt:** Update "recently viewed" and "session intent" features within 5 s so the Lumen home page reflects the current session.
- **Tests:** feature freshness, online/offline consistency, point-in-time correctness.
- **Key trade-offs:** stream-computed vs request-time features; feature TTLs; backfill for training.
- **Rubric.** *No hire:* features recomputed nightly only. *Lean:* streaming features with no plan for training data. *Hire:* one feature definition for streaming and batch, online store, logged features at serving time. *Strong hire:* point-in-time joins for training, freshness SLOs, and the cost of keeping features fresh vs measured lift.

#### RT-10 · Webhook delivery platform
**Level:** J → S · **Units:** [08](../01-foundations/08-async-event-driven.md), [11](../01-foundations/11-reliability-engineering.md)
- **Prompt:** Deliver Lumen events to 30 k customer endpoints with retries, ordering per subscription and signatures.
- **Tests:** retry policies, isolation from slow endpoints, security.
- **Key trade-offs:** per-endpoint queues vs shared; ordering vs throughput; retry duration vs storage.
- **Junior scope:** 500 endpoints, at-least-once delivery, no ordering requirement.
- **Rubric.** *No hire:* synchronous calls from the producing service. *Lean:* a queue with retries but a slow endpoint blocks others. *Hire:* per-endpoint isolation, exponential backoff with jitter, DLQ, signed payloads, replay API. *Strong hire:* automatic endpoint disabling with notification, SSRF protection on customer URLs, and ordering only where subscribers ask for it.
- **Junior hire (on the junior scope):** events in a durable queue, delivery workers with exponential backoff and a maximum retry period, a dead-letter store the customer can replay from, and HMAC signatures so receivers can verify the sender.

## Infrastructure and platform (IP)

#### IP-01 · Deployment platform with progressive delivery
**Level:** S → St · **Units:** [14](../02-modern-requirements/14-cloud-native-platforms.md), [12](../01-foundations/12-observability.md)
- **Prompt:** Let 300 Lumen services deploy many times a day with automated canaries and rollback.
- **Tests:** GitOps, canary analysis, blast radius, platform as a product.
- **Key trade-offs:** rolling vs canary vs blue-green; automated vs human gates; per-team flexibility vs golden paths.
- **Rubric.** *No hire:* scripts that SSH into servers. *Lean:* rolling deploys without health-based rollback. *Hire:* declarative desired state, canary with SLO-based analysis, automatic rollback, audit trail. *Strong hire:* change freeze and dependency-aware ordering, database migration choreography, and adoption metrics for the platform.

#### IP-02 · API gateway for 500 services
**Level:** S → St · **Units:** [10](../01-foundations/10-apis-communication.md), [14](../02-modern-requirements/14-cloud-native-platforms.md), [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** One public entry point for Lumen with auth, rate limits, routing and versioning.
- **Tests:** edge vs internal concerns, config distribution, failure isolation.
- **Key trade-offs:** centralized gateway vs per-team gateways; gateway vs service mesh responsibilities; config push vs pull.
- **Rubric.** *No hire:* every service exposed directly. *Lean:* a gateway, but no plan for config safety. *Hire:* auth and rate limits at the edge, route config with validation and staged rollout, per-route timeouts. *Strong hire:* bad-config blast-radius control, tenant-aware limits, and deprecation of API versions with traffic data.

#### IP-03 · Make an existing service active-active across regions
**Level:** St → P · **Units:** [15](../02-modern-requirements/15-multi-region-edge.md), [06](../01-foundations/06-replication-consistency.md), [11](../01-foundations/11-reliability-engineering.md)
- **Prompt:** Lumen's single-region service must survive a region loss with RTO < 5 min and minimal data loss.
- **Tests:** migration planning, data replication choices, routing, cost.
- **Key trade-offs:** active-passive vs active-active; synchronous vs async replication (RPO vs latency); cost of idle capacity.
- **Rubric.** *No hire:* "deploy to two regions" with no data plan. *Lean:* replicas in a second region but no failover procedure. *Hire:* per-data-class replication choice, health-based global routing, regular failover drills. *Strong hire:* phased migration from today's system, conflict avoidance by partitioning ownership, and cost compared with the business value of the RTO.

#### IP-04 · Feature-flag and configuration service
**Level:** M → S · **Units:** [09](../01-foundations/09-coordination-consensus.md), [14](../02-modern-requirements/14-cloud-native-platforms.md)
- **Prompt:** Flags evaluated 1 M times/s across Lumen, changes visible in 5 s, safe to fail.
- **Tests:** local evaluation, push distribution, consistency, safety.
- **Key trade-offs:** remote evaluation vs local SDK evaluation; streaming updates vs polling; default-on-failure behavior.
- **Rubric.** *No hire:* a remote call per flag check. *Lean:* local cache, no change-safety story. *Hire:* local evaluation with streamed rule updates from a consistent store, last-known-good fallback. *Strong hire:* staged flag rollouts with automated kill, flag debt cleanup, and audit of who changed what.

#### IP-05 · Build cache and artifact store
**Level:** S → St · **Units:** [14](../02-modern-requirements/14-cloud-native-platforms.md), [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** Cut Lumen's CI time by sharing build outputs across 2,000 engineers while keeping artifacts trustworthy.
- **Tests:** content addressing, cache poisoning, provenance.
- **Key trade-offs:** remote cache trust boundaries; eviction vs hit ratio; signing every artifact vs speed.
- **Rubric.** *No hire:* shared writable cache with no integrity. *Lean:* content-addressed storage but anyone can write. *Hire:* only CI writes, developers read, artifacts signed with provenance. *Strong hire:* SLSA-style provenance levels, cache partitioning by trust, and measured hit ratio vs storage cost.

#### IP-06 · Observability for a GPU cluster
**Level:** S → St · **Units:** [C13](../04-case-studies/C13-gpu-cluster-telemetry.md), [12](../01-foundations/12-observability.md), [23](../03-ai-systems/23-gpu-infrastructure.md)
- **Prompt:** Monitor 4,000 GPUs used for training and inference: utilization, errors, job efficiency, energy.
- **Tests:** high-cardinality metrics, correlating hardware with jobs, alerting on failures that kill long jobs.
- **Key trade-offs:** sampling rate vs storage; per-GPU vs per-job aggregation; on-node processing.
- **Rubric.** *No hire:* only host CPU and memory metrics. *Lean:* GPU metrics but no link to jobs. *Hire:* per-GPU telemetry with job labels, error counters, scheduler integration, tiered retention. *Strong hire:* predicting failing nodes, goodput metrics for training jobs, and energy per job.

#### IP-07 · Autoscaler for mixed workloads
**Level:** S → St · **Units:** [03](../01-foundations/03-scaling-compute.md), [14](../02-modern-requirements/14-cloud-native-platforms.md)
- **Prompt:** Autoscale Lumen's web, queue-worker and GPU-inference services, each with different signals.
- **Tests:** scaling signals, lag, stability, cold starts.
- **Key trade-offs:** CPU vs queue depth vs custom SLI signals; reactive vs predictive; scale-to-zero vs cold-start latency.
- **Rubric.** *No hire:* CPU threshold for everything. *Lean:* different signals but no stability controls. *Hire:* per-workload signal (RPS, queue age, KV-cache usage or waiting requests for LLMs), cooldowns, min capacity. *Strong hire:* predictive scaling for diurnal load, GPU cold-start cost analysis, and capacity reservations.

#### IP-08 · A distributed cache fleet
**Level:** J → S · **Units:** [04](../01-foundations/04-caching.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** A shared cache service for Lumen: 20 TB of data, 5 M ops/s, p99 < 2 ms.
- **Tests:** sharding, hot keys, failure behavior, consistency with the source.
- **Key trade-offs:** client-side vs proxy sharding; replication vs none; invalidation vs TTL.
- **Junior scope:** one cache cluster in front of one service's database (for example 50 GB and 50 k ops/s), no multi-tenancy.
- **Rubric.** *No hire:* one big cache server. *Lean:* sharding but no hot-key or failure plan. *Hire:* consistent hashing, replica for hot shards, stampede protection, node-failure warm-up. *Strong hire:* per-tenant quotas, local near-caches for very hot keys, and stale-while-revalidate during source outages.
- **Junior hire (on the junior scope):** cache-aside reads with TTLs, keys spread across nodes (consistent hashing or a managed cluster), and a check that the database survives the miss rate when a cache node is lost.

#### IP-09 · Secrets and workload identity
**Level:** S → St · **Units:** [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** Remove long-lived credentials from Lumen's 300 services and CI pipelines.
- **Tests:** identity issuance, short-lived credentials, rotation, bootstrap trust.
- **Key trade-offs:** central secrets store vs workload identity federation; token lifetime vs availability of the issuer.
- **Rubric.** *No hire:* environment variables in the repository. *Lean:* a vault but static secrets. *Hire:* workload identity (OIDC/SPIFFE-style), short-lived credentials, automated rotation, audit. *Strong hire:* issuer outage behavior, CI federation to clouds, and the migration path with metrics on remaining static secrets.

#### IP-10 · Cost attribution platform
**Level:** S → St · **Units:** [16](../02-modern-requirements/16-cost-as-requirement.md)
- **Prompt:** Show each Lumen team its daily cost per feature and per customer, including shared GPU and data costs.
- **Tests:** allocation models, metering, data joins.
- **Key trade-offs:** tagging vs metering; allocation of shared costs (proportional vs reserved); accuracy vs effort.
- **Rubric.** *No hire:* the cloud bill split evenly. *Lean:* tags, but shared costs ignored. *Hire:* usage metering per tenant and feature, allocation rules for shared clusters, daily pipeline. *Strong hire:* unit-economics metrics (cost per request, per token), anomaly alerts, and incentives that change team behavior.

#### IP-11 · Carbon-aware batch scheduling
**Level:** S → St · **Units:** [17](../02-modern-requirements/17-energy-carbon-aware.md), [23](../03-ai-systems/23-gpu-infrastructure.md)
- **Prompt:** Shift Lumen's flexible batch jobs (re-embedding, evals, analytics) to lower-carbon hours and regions.
- **Tests:** deadline-aware scheduling, signals, data movement cost.
- **Key trade-offs:** time-shifting vs location-shifting; deadline risk; egress cost of moving data.
- **Rubric.** *No hire:* "use a green region". *Lean:* time-shifting without deadlines. *Hire:* jobs with deadlines and flexibility windows, carbon-intensity forecasts as input, fallback to run on time. *Strong hire:* quantifies savings vs added latency and egress, and reports emissions per job.

## AI/LLM (AI)

#### AI-01 · LLM chat service
**Level:** M → St · **Units:** [C09](../04-case-studies/C09-llm-chat-service.md), [21](../03-ai-systems/21-llm-inference-anatomy.md), [22](../03-ai-systems/22-serving-llms-at-scale.md)
- **Prompt:** A chat product for 10 M DAU with streamed answers, two model sizes and paid tiers.
- **Tests:** token-based capacity planning, streaming, KV cache, routing.
- **Key trade-offs:** self-host vs API; model routing; prefix caching and cache-aware load balancing; TTFT vs throughput.
- **Rubric.** *No hire:* treats the model as a normal stateless HTTP service sized by requests/s. *Lean:* streaming and a GPU tier but no token math. *Hire:* tokens/s and KV cache estimated, SSE through the stack, continuous batching, quotas in tokens. *Strong hire:* prefix-cache-aware routing, small/large model routing as the main cost lever, and TTFT/ITL SLOs with admission control. See [I04](I04-ml-llm-interviews.md).

#### AI-02 · Enterprise RAG assistant
**Level:** S → St · **Units:** [C10](../04-case-studies/C10-enterprise-rag-assistant.md), [24](../03-ai-systems/24-retrieval-vector-systems.md)
- **Prompt:** Answer employees' questions over their company's documents with citations, honoring document permissions.
- **Tests:** ingestion, chunking, hybrid retrieval, ACL filtering, evaluation.
- **Key trade-offs:** pre- vs post-filtering for ACLs; chunk size; hybrid vs dense only; reranking cost.
- **Rubric.** *No hire:* puts all documents into one shared index with no permissions. *Lean:* vector search, with permission checks and evaluation missing. *Hire:* ACL-aware retrieval, hybrid search plus rerank, citation grounding, an offline eval set. *Strong hire:* permission-change propagation SLO, freshness pipeline, prompt-injection from documents, and cost per answer.

#### AI-03 · LLM gateway
**Level:** S → St · **Units:** [26](../03-ai-systems/26-llm-gateways-llmops.md), [10](../01-foundations/10-apis-communication.md)
- **Prompt:** One internal endpoint for all Lumen teams to call multiple model providers and self-hosted models.
- **Tests:** routing, fallback, token-based quotas, observability, key management.
- **Key trade-offs:** proxy vs SDK; fallback policy (quality vs availability); caching; streaming passthrough.
- **Rubric.** *No hire:* a thin proxy with no quotas or fallback. *Lean:* routing and keys but request-based limits. *Hire:* token-based quotas per team, provider fallback with circuit breakers, usage metering, streaming support. *Strong hire:* semantic-cache trade-offs with privacy, eval-gated model upgrades, and GenAI tracing conventions.

#### AI-04 · Multi-LoRA serving
**Level:** S → St · **Units:** [22](../03-ai-systems/22-serving-llms-at-scale.md), [27](../03-ai-systems/27-ml-platforms.md)
- **Prompt:** Serve 2,000 customer-specific fine-tuned adapters on one base model with acceptable latency.
- **Tests:** adapter loading, batching across adapters, memory budget, routing.
- **Key trade-offs:** adapters vs full fine-tunes; GPU-resident adapter count vs swap latency; routing by adapter affinity.
- **Rubric.** *No hire:* one GPU deployment per customer. *Lean:* adapters, but no memory or swap-cost reasoning. *Hire:* multi-LoRA batching, adapter cache with LRU, affinity routing, adapter size estimated. *Strong hire:* cold-adapter latency SLO, per-tenant isolation of adapters, and an eval gate before adapter publication.

#### AI-05 · GPU cluster scheduler for training and inference
**Level:** St → P · **Units:** [23](../03-ai-systems/23-gpu-infrastructure.md), [14](../02-modern-requirements/14-cloud-native-platforms.md)
- **Prompt:** Share 2,000 GPUs between long training jobs and latency-sensitive inference.
- **Tests:** gang scheduling, topology, preemption, quotas.
- **Key trade-offs:** static partitioning vs shared pool with preemption; Slurm vs Kubernetes; MIG/time-slicing for small models.
- **Rubric.** *No hire:* first-come-first-served without gang scheduling. *Lean:* quotas, but no topology awareness. *Hire:* gang scheduling, topology-aware placement, priority with checkpoint-aware preemption, inference reserved capacity. *Strong hire:* goodput as the objective, failure recovery for 1,000-GPU jobs, and an internal pricing model for fair sharing.

#### AI-06 · Semantic cache for LLM responses
**Level:** J → S · **Units:** [26](../03-ai-systems/26-llm-gateways-llmops.md), [04](../01-foundations/04-caching.md)
- **Prompt:** Cut Lumen Help's LLM cost by reusing answers to semantically similar questions.
- **Tests:** similarity thresholds, correctness risk, invalidation, privacy.
- **Key trade-offs:** exact-match vs embedding similarity; threshold vs wrong-answer rate; per-tenant vs global cache.
- **Junior scope:** an exact-match cache (normalized question text → answer) for one tenant; no embeddings.
- **Rubric.** *No hire:* caches any answer globally by embedding with no threshold reasoning. *Lean:* similarity cache without invalidation. *Hire:* threshold tuned on a labelled set, tenant scoping, TTL plus invalidation on source updates. *Strong hire:* measures false-hit rate as an SLI, never caches personalized answers, and compares the result with prefix caching.
- **Junior hire (on the junior scope):** text normalization, a key that includes tenant, model and prompt version, a TTL, a hit-rate metric, and one sentence on why similarity matching is riskier.

#### AI-07 · Vector search over a billion items
**Level:** S → St · **Units:** [24](../03-ai-systems/24-retrieval-vector-systems.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** Similarity search over 1 B embeddings (768 dims) at 5,000 QPS with filters and daily updates.
- **Tests:** ANN index choice, memory math, sharding, filtered search.
- **Key trade-offs:** HNSW in RAM vs IVF-PQ vs disk-based indexes; recall vs latency vs cost; pre- vs post-filtering.
- **Rubric.** *No hire:* brute force on one machine. *Lean:* names HNSW without memory math (≈ 3 TB raw float32). *Hire:* memory estimated per index type, sharding with scatter-gather, quantization, recall measured. *Strong hire:* filtered search strategy, index rebuild vs incremental insert, and cost per million queries.

#### AI-08 · LLM evaluation platform
**Level:** S → St · **Units:** [26](../03-ai-systems/26-llm-gateways-llmops.md), [27](../03-ai-systems/27-ml-platforms.md)
- **Prompt:** Let every Lumen team evaluate prompts and models offline and online before shipping changes.
- **Tests:** dataset management, judges, reproducibility, online metrics.
- **Key trade-offs:** human vs LLM-as-judge; golden sets vs production sampling; cost of eval runs.
- **Rubric.** *No hire:* "we look at a few outputs". *Lean:* datasets and scores but no reproducibility. *Hire:* versioned datasets, pinned model/prompt versions, judges calibrated against humans, CI gates. *Strong hire:* judge bias controls, online A/B with guardrail metrics, and eval cost budgeting. See [I04](I04-ml-llm-interviews.md).

#### AI-09 · Fine-tuning platform
**Level:** S → St · **Units:** [27](../03-ai-systems/27-ml-platforms.md), [23](../03-ai-systems/23-gpu-infrastructure.md)
- **Prompt:** Self-service fine-tuning for Lumen teams and enterprise customers, from data upload to deployed adapter.
- **Tests:** data validation, job orchestration, GPU memory math, registry and promotion.
- **Key trade-offs:** LoRA vs full fine-tune; shared vs dedicated GPUs; customer data isolation.
- **Rubric.** *No hire:* a notebook per request. *Lean:* job queue, but no memory math or eval gate. *Hire:* data validation, LoRA by default with memory estimate, checkpointing, registry, eval before promotion. *Strong hire:* tenant isolation of data and weights, deletion requests reaching trained adapters, and cost per job.

#### AI-10 · Recommendation system for a content feed
**Level:** S → St · **Units:** [C12](../04-case-studies/C12-realtime-fraud-recsys.md), [27](../03-ai-systems/27-ml-platforms.md), [24](../03-ai-systems/24-retrieval-vector-systems.md)
- **Prompt:** Recommend Lumen community articles on the home page for 20 M DAU.
- **Tests:** multi-stage retrieval and ranking, features, metrics, feedback loops.
- **Key trade-offs:** candidate generation recall vs ranking cost; engagement vs quality metrics; exploration.
- **Rubric.** *No hire:* one model scoring all items per request. *Lean:* two stages, with metrics never defined. *Hire:* candidate generation + ranking + re-ranking, online/offline metrics, feature store, A/B testing. *Strong hire:* feedback-loop and popularity-bias controls, cold start, and the latency budget split by stage. See [I04](I04-ml-llm-interviews.md).

#### AI-11 · LLM content moderation
**Level:** S → St · **Units:** [28](../03-ai-systems/28-ai-trust-safety-governance.md), [26](../03-ai-systems/26-llm-gateways-llmops.md)
- **Prompt:** Moderate user posts and AI outputs in Lumen across 12 languages with an appeals process.
- **Tests:** classifier cascades, precision/recall per policy, human review, latency.
- **Key trade-offs:** blocking vs post-hoc review; cheap classifier vs LLM judge; per-policy thresholds.
- **Rubric.** *No hire:* one LLM call per item with no cost math. *Lean:* classifiers, but no human loop. *Hire:* cascade (rules → small classifier → LLM), per-policy thresholds, review queues, appeals. *Strong hire:* adversarial adaptation, measuring both false positives and negatives, and audit obligations. See [I04](I04-ml-llm-interviews.md).

#### AI-12 · Streaming voice assistant
**Level:** S → St · **Units:** [21](../03-ai-systems/21-llm-inference-anatomy.md), [10](../01-foundations/10-apis-communication.md)
- **Prompt:** A voice mode for Lumen: speech in, spoken answer out, aiming to start responding within 800 ms.
- **Tests:** pipelined streaming (ASR → LLM → TTS), latency budgets, barge-in.
- **Key trade-offs:** cascaded vs end-to-end speech models; partial transcripts; region placement.
- **Rubric.** *No hire:* waits for full audio, full answer, then full speech synthesis. *Lean:* streaming, but no latency budget. *Hire:* per-stage budget, streaming at every stage, endpointing, interruption handling. *Strong hire:* speculative starts on partial transcripts, GPU co-location, and cost per minute of conversation.

#### AI-13 · Model registry and safe rollout
**Level:** M → S · **Units:** [27](../03-ai-systems/27-ml-platforms.md), [14](../02-modern-requirements/14-cloud-native-platforms.md)
- **Prompt:** Track every model and prompt version in Lumen, and roll out new ones with canaries and instant rollback.
- **Tests:** lineage, promotion workflow, shadow and canary for models.
- **Key trade-offs:** prompts as code vs config; shadow vs canary; automated vs manual promotion.
- **Rubric.** *No hire:* model files copied to servers by hand. *Lean:* registry, but no rollout safety. *Hire:* versioned artifacts with lineage, eval gates, shadow then canary on quality and latency SLIs, rollback. *Strong hire:* prompt and model versions pinned together, audit for regulated use, and rollback of downstream caches.

## Agentic (AG)

Every agentic question has two extra fields: **Numbers to expect** (the estimates a hire-level answer produces, with
the unit that derives them) and **Red flags / Follow-ups** (what an interviewer listens for and where they push).
Unless a source is given, the numbers are labelled assumptions from the linked units. [I01 §17](I01-interview-playbook.md#17-when-the-prompt-is-agentic)
describes how the framework shifts for these prompts. Most agentic prompts start at mid or senior level; AG-20 and
AG-21 are the junior on-ramp, with a **Junior scope** and a **Junior hire** line like the rest of the junior track.

#### AG-01 · Coding-agent platform
**Level:** S → P · **Units:** [C11](../04-case-studies/C11-coding-agent-platform.md), [25](../03-ai-systems/25-agentic-systems.md), [31](../03-ai-systems/31-securing-agentic-systems.md), [33](../03-ai-systems/33-agent-platform-runtime.md)
- **Prompt:** Run thousands of concurrent coding agents that edit repositories, run tests and open pull requests.
- **Tests:** sandboxing, durable execution, tool access, cost caps.
- **Key trade-offs:** container vs microVM isolation; long-lived vs ephemeral sandboxes; autonomy vs approval gates.
- **Numbers to expect:** C11's 40 steps × 40 k input tokens ≈ 1.6 M input tokens and ≈ $1.50 per task at its placeholder prices (≈ $1.70 with the cache-write premium); concurrency from Little's law on wall time (task arrival rate × 20 minutes), not on model time.
- **Rubric** (matches the C11 WRAP levels: Junior ≈ Lean, Senior ≈ Hire, Staff ≈ Strong hire). *No hire:* agent code runs in the app's process or in plain shared-kernel containers across tenants, or a token sits in the sandbox environment. *Lean:* a task queue, a container per task, an LLM loop with a step cap and timeouts, a PR at the end, but no durability, no egress control, or a budget checked only after the task. *Hire:* hostile-code threat model with microVM or gVisor chosen for a reason, egress proxy with an allowlist and credential injection, scoped short-lived credentials, durable workflow that replays recorded LLM and tool results with idempotent tools, budgets reserved before each call, loop detection, approvals bound to the exact action, traces, per-org quotas. *Strong hire:* injection-driven threat model (approval for writes others can read), quadratic context cost with cache write premium and TTL, durable-engine history limits, snapshot-and-release economics for paused tasks, fairness and priority classes, an internal eval suite as the release gate (public benchmarks such as SWE-bench Verified are contaminated and partly broken: as of 2026-11, per OpenAI's 2026-02-23 audit as summarised by Epoch AI [23] and in C11), and cost per merged change.
- **Red flags:** a repository token in the sandbox's environment; open internet from the sandbox; the budget checked after the task ends; side effects re-run on retry.
- **Follow-ups:** At 10× tasks, what breaks first? An approval is never answered: what does the paused task hold, and for how long?

#### AG-02 · Tool registry and gateway (MCP)
**Level:** S → St · **Units:** [31](../03-ai-systems/31-securing-agentic-systems.md), [25](../03-ai-systems/25-agentic-systems.md), [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** Expose about 300 of Lumen's internal and third-party APIs to agents as tools, with discovery, per-user authority and audit.
- **Tests:** protocol choice, authorization on behalf of users, rate limits, audit, tool-description trust.
- **Key trade-offs:** central gateway vs direct tool servers; user-delegated vs service credentials; loading every tool definition vs loading on demand.
- **Numbers to expect:** chapter 31 (assumed 240 third-party tools, 3 % changing per week, 15 minutes of review per diff): ≈ 7 description diffs a week, about 1.8 hours of review, so re-review on change is affordable; tool definitions cost context on every call (chapter 30 puts 5,000 tokens of tool schemas in its 10,000-token prefix).
- **Rubric.** *No hire:* agents get admin API keys. *Lean:* a registry but no per-user authorization. *Hire:* delegated user identity, per-tool scopes, tokens audience-bound to each server and never forwarded (the MCP authorization spec requires servers to validate the audience and forbids accepting or passing on other tokens [18]), rate limits per user and per agent, a full audit log. *Strong hire:* tool descriptions pinned by hash and re-reviewed when they change, on-demand tool loading or tool search to bound context cost, consent UX for sensitive tools, schema versioning, and trust tiers for third-party servers.
- **Red flags:** one admin key for all tools; forwarding the user's token to tool servers; every tool definition in every prompt; trusting a tool's self-declared "read-only" annotation.
- **Follow-ups:** A third-party MCP server changes a tool description after approval: what happens? How do you rate-limit one runaway agent without blocking its user?

#### AG-03 · Durable execution for long-running agents
**Level:** S → St · **Units:** [33](../03-ai-systems/33-agent-platform-runtime.md), [C17](../04-case-studies/C17-workflow-automation-agent.md), [25](../03-ai-systems/25-agentic-systems.md), [08](../01-foundations/08-async-event-driven.md)
- **Prompt:** Agent tasks run for hours across many LLM and tool calls and must survive restarts and deploys.
- **Tests:** workflow engines, idempotent steps, replay, timeouts.
- **Key trade-offs:** event-sourced workflows vs checkpointed state; deterministic replay constraints; LLM non-determinism.
- **Numbers to expect:** chapter 33's runaway of 300 steps writes ≈ 276 MB of history if full contexts are activity inputs, over five times a 50 MB execution-history limit (Temporal: 51,200 events or 50 MB [20]); with claim checks (references to stored contexts) the same run stays under 1 MB.
- **Rubric.** *No hire:* agent loop in one process's memory. *Lean:* periodic checkpoints but no idempotency. *Hire:* durable workflow with recorded LLM and tool results, idempotent tool calls, timeouts and retries per step, large payloads stored by reference. *Strong hire:* versioning workflows in flight (pin and drain), compensation for side effects, human-in-the-loop waits that last days, and engine history limits handled by continuing a run as a new execution.
- **Red flags:** agent state only in memory; asking the model again after a crash; no per-step timeout; "the engine guarantees exactly once".
- **Follow-ups:** You deploy while 5,000 tasks are mid-flight: which code runs their next step? An approval waits three days: what is stored, and what expires?

#### AG-04 · Agent memory service
**Level:** M → S · **Units:** [30](../03-ai-systems/30-context-engineering-memory.md), [24](../03-ai-systems/24-retrieval-vector-systems.md), [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md)
- **Prompt:** Give Lumen's assistant long-term memory of user preferences and past tasks.
- **Tests:** memory types, retrieval, write policy, privacy.
- **Key trade-offs:** summarize vs store raw; automatic vs user-confirmed memories; retrieval by recency vs relevance.
- **Numbers to expect:** chapter 30's 1 M users × 50 memories × ≈ 5.5 KB ≈ 275 GB and ≈ 14 writes/s on average: small data, so the design effort goes to correctness, isolation and erasure, not throughput.
- **Rubric.** *No hire:* appends all history to every prompt. *Lean:* vector store of memories with no write policy. *Hire:* typed memories (facts, episodes), salience-based writes with provenance, retrieval blending recency and relevance, tenant and user scope on every read, user view and delete, and erasure that reaches embeddings, summaries and traces. *Strong hire:* poisoning defenses (taint on memories written from untrusted content, quarantine, rollback), memory conflicts with validity intervals, and cost/latency of memory retrieval per turn.
- **Red flags:** all history in every prompt; no delete path; memories written from untrusted content without review; no tenant id in the memory schema.
- **Follow-ups:** The user says "forget this": what exactly is erased, and from which tiers? Two memories contradict: which wins?

#### AG-05 · Support agent with human handoff
**Level:** M → S · **Units:** [C15](../04-case-studies/C15-support-agent-platform.md), [31](../03-ai-systems/31-securing-agentic-systems.md), [28](../03-ai-systems/28-ai-trust-safety-governance.md)
- **Prompt:** An AI agent resolves Lumen support tickets, can issue refunds up to $50, and escalates to humans.
- **Tests:** tool permissions, identity, escalation criteria, auditability, evaluation.
- **Key trade-offs:** autonomy limits; confidence-based vs rule-based escalation; resolution rate vs error cost.
- **Numbers to expect:** exposure = volume × limit: C15's 5 % of 400 k conversations asking for refunds (20,000 a day) × $50 ≈ $1 M a day of worst-case automatic payout; ≈ $0.10 of platform cost per conversation; a full failover to humans needs about 2.5× the staffed level.
- **Rubric.** *No hire:* unrestricted refund tool. *Lean:* a per-refund limit, but no identity check or escalation design. *Hire:* identity verified (and stepped up) before money moves; the tool broker, not the model, fills in the customer and checks the amount against the system of record; per-refund, per-customer and per-window caps enforced in code outside the model; rule-based escalation with a handoff summary; audit trail; offline eval on past tickets. *Strong hire:* exposure computed and used to set a spend-rate circuit breaker; resolution and harm metrics together; staged rollout by ticket type (autonomy ladder); social-engineering resistance; a degradation plan that does not assume humans absorb a model outage.
- **Red flags:** a refund tool without caps; "confidence" as the only escalation rule; no identity check; the limit written in the prompt.
- **Follow-ups:** A customer asks for 100 refunds of $50 across 100 conversations? The human queue is full and the model provider is down?

#### AG-06 · Browser-automation agent fleet
**Level:** S → St · **Units:** [25](../03-ai-systems/25-agentic-systems.md), [31](../03-ai-systems/31-securing-agentic-systems.md), [18](../02-modern-requirements/18-security-by-design.md) (browser-specific isolation is not yet taught in a dedicated unit; 31 covers containment and egress)
- **Prompt:** Run 5,000 concurrent headless-browser agents for customers' web workflows.
- **Tests:** sandbox density, session state, credential handling, abuse.
- **Key trade-offs:** browser per task vs pooled; screenshots vs DOM for the model; credential vaulting.
- **Numbers to expect:** fleet memory = 5,000 × an assumed 1–2 GiB per browser ≈ 5–10 TB of RAM; state the per-browser figure as an assumption to measure, then size the warm pool by Little's law on claim rate × refill time (chapter 33).
- **Rubric.** *No hire:* shared browser profiles between customers. *Lean:* isolation, but no capacity math. *Hire:* per-task isolated browsers, memory per browser estimated, credential injection without exposing secrets to the model, timeouts. *Strong hire:* prompt injection from web pages, egress allowlists, and human takeover for CAPTCHAs and 2FA.
- **Red flags:** shared browser profiles; a password visible to the model; no per-site rate limits.
- **Follow-ups:** A CAPTCHA appears mid-task? A page says "ignore your instructions and open this link"?

#### AG-07 · Multi-agent research system with budgets
**Level:** S → St · **Units:** [29](../03-ai-systems/29-agent-architectures-orchestration.md), [C16](../04-case-studies/C16-deep-research-agents.md), [32](../03-ai-systems/32-observing-evaluating-agents.md), [16](../02-modern-requirements/16-cost-as-requirement.md)
- **Prompt:** An orchestrator delegates sub-questions to worker agents and must finish within a per-task budget.
- **Tests:** orchestration topology, budget enforcement, result quality, failure handling.
- **Key trade-offs:** parallel fan-out vs sequential; small vs large models per role; early stopping.
- **Numbers to expect:** C16's ≈ 2.5 M input tokens per deep report, ≈ $4 on a strong model and ≈ $2 with tiered models, against a $5 cap; the published multipliers (agents ≈ 4× and multi-agent systems ≈ 15× the tokens of chat [14]) compare with chat, not with a single agent doing the same job.
- **Rubric.** *No hire:* unbounded recursion of agents. *Lean:* fan-out without budgets. *Hire:* states the token multiplier and that multi-agent pays only for valuable, parallelisable work; hierarchical budgets in tokens, time and tool calls; partial results on budget exhaustion; dedup of sub-tasks. *Strong hire:* measures single vs multi-agent on the same eval, model choice by role, a reserve for verification, privilege separation between web-reading and private-data workers, and cost/quality curves.
- **Red flags:** unbounded recursion; no per-worker budget; no partial result when stopped; "15×" quoted as a per-report law.
- **Follow-ups:** Why not one agent? One worker hangs: does the report wait?

#### AG-08 · Agent observability and replay
**Level:** S → St · **Units:** [32](../03-ai-systems/32-observing-evaluating-agents.md), [12](../01-foundations/12-observability.md), [26](../03-ai-systems/26-llm-gateways-llmops.md)
- **Prompt:** Let engineers debug why an agent took a wrong action three days ago.
- **Tests:** tracing of LLM and tool spans, payload capture, privacy, replay.
- **Key trade-offs:** capture full prompts vs privacy and cost; deterministic replay vs re-execution.
- **Numbers to expect:** chapter 32: recording the full history on every model span stores ≈ 828 KB per 15-step run, storing each message once ≈ 114 KB (7.3× less); keeping all failures, all expensive runs and 10 % of the rest keeps ≈ 28 % of runs.
- **Rubric.** *No hire:* only application logs. *Lean:* traces but without prompts or tool payloads. *Hire:* span per LLM and tool call with inputs and outputs (redacted, stored by reference), versions recorded, replay with recorded results. *Strong hire:* run-level sampling and retention by risk, PII handling, and linking traces to eval datasets.
- **Red flags:** prompts and tool payloads not captured; unredacted traces; replay by calling the model again; head sampling that drops most failures.
- **Follow-ups:** Debug a wrong action from three days ago when PII retention is 24 hours? The tool had a side effect: how do you replay safely?

#### AG-09 · Runaway spend and loop control
**Level:** S → St · **Units:** [33](../03-ai-systems/33-agent-platform-runtime.md), [25](../03-ai-systems/25-agentic-systems.md), [26](../03-ai-systems/26-llm-gateways-llmops.md), [C11](../04-case-studies/C11-coding-agent-platform.md) (deep dive 3: budgets reserved before each call, loop detection)
- **Prompt:** Lumen's agent bill grew 40× over one weekend. Design the controls so that no task, user or tenant can overspend, and a looping agent is stopped early.
- **Tests:** budget hierarchy, reserve-then-reconcile, loop detection, stop semantics, retry amplification.
- **Key trade-offs:** hard stop vs a wrap-up step near the cap; per-step vs per-task vs per-tenant caps; loop detectors that kill legitimate retries vs cost.
- **Numbers to expect:** quadratic growth: at a 3,000-token base and 1,500 tokens per step, doubling a task from 40 to 80 steps multiplies input tokens by ≈ 3.9; a 100-step loop reads ≈ 7.7 M input tokens (≈ $7.8 at $1/$4 per million, with 300 output tokens per step) against ≈ $0.22 for 15 steps (chapter 25's illustrative assumptions).
- **Rubric.** *No hire:* "ask the model to be brief", or a monthly billing alert. *Lean:* a max-steps limit only. *Hire:* caps on tokens, money, wall time and tool time, enforced by the runtime **before** each call (reserve, then reconcile); per-tenant token quotas and concurrency; loop detectors (repeated tool and arguments, repeated state, no new information); a graceful stop that leaves a resumable partial result. *Strong hire:* caps set from the context-growth curve; alerts on spend *rate*; retries counted across SDK, gateway and agent layers because they multiply; budgets inherited down a sub-agent tree; a kill switch per tenant, tool and model version; cost per successful task as the reported metric.
- **Red flags:** the budget lives only in the prompt; spend checked after the task ends; one global cap; a stopped task cannot resume.
- **Follow-ups:** How much do you reserve when output length is unknown? How do you tune a loop detector without killing honest retries? You raise a cap: what happens to tasks already stopped by it?

#### AG-10 · Tool calls with unknown outcomes
**Level:** M → S · **Units:** [33](../03-ai-systems/33-agent-platform-runtime.md), [C17](../04-case-studies/C17-workflow-automation-agent.md), [08](../01-foundations/08-async-event-driven.md), [C06](../04-case-studies/C06-payments-ledger.md)
- **Prompt:** An agent sends emails and issues refunds. A worker crashes after a tool call returned but before the result was stored. Design what happens on resume.
- **Tests:** intent and result records, idempotency keys, the unknown-outcome state, not re-planning.
- **Key trade-offs:** key derived from (run, step) vs random per attempt; dedup inside the tool vs at a broker; lookup-before-retry vs trusting the key.
- **Numbers to expect:** at an assumed 30 k tasks a day, one side-effecting call per task and 0.1 % of calls crashing in that window, about 30 ambiguous side effects a day; C17's 8 side-effecting calls per run give 160 k calls and ≈ 160 ambiguous outcomes a day.
- **Rubric.** *No hire:* "retry the step" or "ask the model again". *Lean:* idempotency keys, but generated per attempt. *Hire:* intent written before the call and result after; key derived from run and step; resume retries with the **same** key and never asks the model to decide again; the tool or broker deduplicates. *Strong hire:* tools without idempotency support handled by lookup-before-write and a reconciler; an explicit "unknown outcome" state with an owner; key retention longer than the retry horizon; compensation for steps that cannot be undone.
- **Red flags:** the model re-decides after a crash; a timestamp or attempt number inside the key; "exactly-once delivery" claimed for the queue.
- **Follow-ups:** The key store is down: fail open or closed for refunds, and for emails? The payment provider has no idempotency header?

#### AG-11 · Containing prompt injection in a tool-connected agent
**Level:** S → St · **Units:** [31](../03-ai-systems/31-securing-agentic-systems.md), [28](../03-ai-systems/28-ai-trust-safety-governance.md), [C16](../04-case-studies/C16-deep-research-agents.md)
- **Prompt:** A Lumen research agent reads web pages and tool results, can query private CRM data, and can send email. Stop it leaking data without making it useless. (Complements SC-07.)
- **Tests:** session-level threat model, privilege separation, outbound channels, tool-description trust.
- **Key trade-offs:** capability restriction vs usefulness; approval friction; detection classifiers vs deterministic controls.
- **Numbers to expect:** chapter 31: if 1,000 exfiltration attempts a month reach a classifier that misses 5.7 % of them (stage-2 false-negative rate on 1,000 synthetic exfiltration attempts, one product, vendor measurement [21]), about 57 get through, and only an egress allowlist stops those calls.
- **Rubric.** *No hire:* "the system prompt says to ignore instructions". *Lean:* an injection classifier as the main control. *Hire:* names the three properties of the Rule of Two (untrusted input, private data, external communication or state change [17]) and removes one per session or workflow; least-privilege delegated tokens; egress allowlist; approval when a value derived from untrusted content reaches an outbound sink. *Strong hire:* separate zones for the web-reading and private-data parts of the task (privilege-separated sub-agents or a planner that never sees raw untrusted text), tool descriptions treated as untrusted and pinned, an attack suite as a CI regression, residual risk stated with the monitoring that catches it.
- **Red flags:** one session holds all three properties with no human gate; rendering markdown images from arbitrary domains; trusting tool annotations.
- **Follow-ups:** How do you test it? What utility does your design cost the user? How do approvals scale when there are thousands a day?

#### AG-12 · Agent evaluation and release gating
**Level:** S → St · **Units:** [32](../03-ai-systems/32-observing-evaluating-agents.md), [C15](../04-case-studies/C15-support-agent-platform.md), [I04](I04-ml-llm-interviews.md)
- **Prompt:** How does Lumen know that a new model, prompt, tool or harness version did not make a 30-step support agent worse before it reaches all users?
- **Tests:** environment-based tasks, final-state grading, repeated trials, gate statistics, canaries, eval cost.
- **Key trade-offs:** average capability vs consistency; programmatic graders vs judges; suite size vs eval cost.
- **Numbers to expect:** 0.98³⁰ ≈ 0.55 task success from a 0.98 step rate; chapter 32: a 200-task suite at 85 % success has a 95 % interval of ≈ ±4.9 points, and detecting a 3-point drop needs ≈ 870 paired tasks (assuming 10 % of tasks change outcome between versions; measure yours with an A/A run). At 900 tasks the gate blocks when the paired difference is below about −2.1 points (1.96 × √(0.10/900)), which catches ≈ 81 % of true 3-point drops and blocks ≈ 2.5 % of neutral changes; a "lower bound above −3" rule would instead block ≈ 19 % of neutral changes. Gate cost for *this* 30-step agent, on chapter 25's assumptions (3,000-token base, +1,500 tokens and 300 output tokens per step, $1/$4 per million, cache writes 1.25×, reads 0.1×): 742,500 input tokens per task, ≈ $0.16 cached (≈ $0.78 uncached), so a full gate of 900 tasks × 3 trials × 2 versions = 5,400 runs costs ≈ $880 with a warm cache and ≈ $4,200 uncached. Chapter 32's ≈ $356 is the same gate for its 15-step task.
- **Rubric.** *No hire:* "try a few prompts". *Lean:* a static question-and-answer set, one run per task. *Hire:* tasks in a resettable environment graded on the **final state**; repeated trials with pass^k (introduced with τ-bench [15]); trajectory metrics (steps, cost, tool errors); a CI gate with an interval, not a point score. *Strong hire:* paired comparisons sized for the regression that matters; simulated users; judges calibrated against humans for open-ended parts; contamination awareness; shadow then canary online with guardrail metrics and outcome delays; failures flowing back into the suite; an eval budget (smoke suite per change, full gate per release).
- **Red flags:** one trial per task; an uncalibrated judge; a public benchmark as the only gate; "the suite passed" with 50 tasks.
- **Follow-ups:** A 2-point drop on 50 tasks: ship or not? How do you pin model and tool versions so a run is reproducible? Outcomes arrive a week late: what gates the canary?

#### AG-13 · Approvals for risky agent actions
**Level:** M → S · **Units:** [31](../03-ai-systems/31-securing-agentic-systems.md), [C17](../04-case-studies/C17-workflow-automation-agent.md), [C11](../04-case-studies/C11-coding-agent-platform.md)
- **Prompt:** A Lumen finance agent can pay supplier invoices and email customers. Design the approval flow.
- **Tests:** risk tiers, exact-action display, binding, durable waits, approval fatigue.
- **Key trade-offs:** friction vs safety; approve each action vs approve the plan; who may approve.
- **Numbers to expect:** chapter 31 (assumed 1.2 M tool calls a day, 25 % outbound or state-changing, half of those in tainted sessions, 10 s per approval): gating every outbound call in tainted sessions gives ≈ 150,000 approvals a day (≈ 417 person-hours a day); plan-level approval plus destinations bound to the tenant's own domains cuts that to ≈ 5,600. In one vendor's measurement users accepted 93 % of permission prompts [21].
- **Rubric.** *No hire:* the model asks "are you sure?" in the chat. *Lean:* approval of everything. *Hire:* risk-tiered policy; the approver sees the **exact** call or diff, rendered by the runtime, not the model's paraphrase; approval bound to a hash of the action; durable wait with expiry; audit. *Strong hire:* approval rate and time-to-approve tracked to detect rubber-stamping; requester ≠ approver enforced by the platform; allowlists reviewed periodically; delegation when the approver is away; defined behaviour on timeout.
- **Red flags:** approving a summary; an approval reused for a changed action; no expiry.
- **Follow-ups:** 98 % of approvals are "yes": what do you change? The approver is on holiday for two weeks?

#### AG-14 · Choosing a sandbox for untrusted agent code
**Level:** S → St · **Units:** [31](../03-ai-systems/31-securing-agentic-systems.md), [33](../03-ai-systems/33-agent-platform-runtime.md), [C11](../04-case-studies/C11-coding-agent-platform.md), [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** Pick the isolation technology for 8,000 concurrent sandboxes running model-written code for many tenants.
- **Tests:** threat model, kernel boundary, start latency, density, warm pools, egress.
- **Key trade-offs:** container vs gVisor vs microVM vs WebAssembly vs a managed service; start time vs isolation; syscall overhead on build-and-test workloads.
- **Numbers to expect:** 8,000 × an assumed 2 vCPU and 4 GiB = 16,000 vCPU and 32,000 GiB (≈ 31 TiB) of RAM; warm pool ≥ claim rate × refill time: at an assumed 20-minute mean task (C11), 8,000 concurrent sandboxes means 8,000 / 1,200 s ≈ 6.7 claims/s, and with a 20 s refill (chapter 33's assumption) about 133 ready sandboxes, ≈ 267 for 2× bursts (chapter 33 applies the same formula to a smaller fleet of 675 sandboxes: ≈ 28).
- **Rubric.** *No hire:* shared-kernel containers for hostile multi-tenant code. *Lean:* microVMs without start-latency or egress thinking. *Hire:* threat model first; a VM boundary (or gVisor where nested virtualisation is unavailable) chosen for a reason; snapshot-based or pooled start; egress proxy; no cloud metadata endpoint; sandboxes never reused across tenants. *Strong hire:* fleet sized from the numbers; per-tenant host pools for regulated tenants; patch cadence; measured syscall cost of the chosen boundary; build vs buy.
- **Red flags:** "Docker is isolated"; credentials in environment variables; warm sandboxes recycled between tenants.
- **Follow-ups:** Your cloud offers no nested virtualisation? A tenant needs GPUs inside the sandbox?

#### AG-15 · Cross-organisation agent delegation and identity
**Level:** St → P · **Units:** [31](../03-ai-systems/31-securing-agentic-systems.md), [29](../03-ai-systems/29-agent-architectures-orchestration.md), [18](../02-modern-requirements/18-security-by-design.md), [C17](../04-case-studies/C17-workflow-automation-agent.md)
- **Prompt:** Lumen's procurement agent must delegate quote requests to a supplier's agent and call Lumen's own tools. Design discovery, authentication, trust and failure semantics.
- **Tests:** MCP vs A2A, delegated identity, contracts, long-running remote tasks.
- **Key trade-offs:** an opaque agent vs a tool you control; token forwarding vs token exchange; trust tiers per counterparty.
- **Numbers to expect:** none dominate; quantify the remote task's duration and your timeout, and the blast radius of each credential (chapter 31: a per-task token for one repository for 30 minutes versus a tenant-wide token over an assumed 2,000 repositories for 8 hours is a 32,000-fold reduction in repository-hours).
- **Rubric.** *No hire:* forwards the end user's token to the partner. *Lean:* names both protocols without a rule for choosing. *Hire:* MCP for capabilities you control, A2A for opaque agents you do not; discovery through published agent descriptions; audience-bound, scoped, short-lived credentials from token exchange, with the delegation chain recorded (RFC 8693's `act` claim [22]); task lifecycle with polling or push; timeouts, version pinning, audit. *Strong hire:* trust tiers and data-sharing contracts; what you log about a counterparty you cannot inspect; liability and a kill switch; failure semantics when the partner is slow, wrong or compromised.
- **Red flags:** secrets passed in messages; the partner's output treated as trusted input.
- **Follow-ups:** The partner's agent is compromised: what is the blast radius? How do you test against a counterparty you do not own?

#### AG-16 · Single agent or multi-agent?
**Level:** M → S · **Units:** [29](../03-ai-systems/29-agent-architectures-orchestration.md), [32](../03-ai-systems/32-observing-evaluating-agents.md), [C16](../04-case-studies/C16-deep-research-agents.md)
- **Prompt:** A team proposes six specialised agents for Lumen's code-review workflow. Decide whether to build it that way.
- **Tests:** orchestration trade-offs, cost, shared context, measurement.
- **Key trade-offs:** parallelism vs coordination; shared context vs isolation; value per task vs token multiplier.
- **Numbers to expect:** chapter 29's vendor brief: a serial single agent ≈ $1.41 and ≈ 381 s, orchestrator-workers with isolated contexts ≈ $0.43 and ≈ 114 s uncached (same 40 research steps); prompt caching shrinks the cost gap from about 3.3× to about 1.1–1.3×, so choose multi-agent for latency and context limits, not for dollars alone. That brief is read-only and parallel; for a shared-context review pipeline, say what changes: isolation saves quadratic re-reads only if the subtasks are independent.
- **Rubric.** *No hire:* "more agents is better". *Lean:* lists patterns without choosing. *Hire:* starts from the least agentic design that meets the need; states the cost and latency arithmetic; decides by parallelisability, shared context and whether agents *write*. *Strong hire:* proposes evaluating single vs multi on the same suite with cost per success; uses sub-agents for read-only parallel work and context isolation; gives the counter-argument that actions carry implicit decisions and conflicting decisions produce bad results [16]; keeps writes single-threaded; caps workers in code.
- **Red flags:** agents negotiating in free text with no shared state; parallel writers on one artefact; no budget per agent.
- **Follow-ups:** Which two of the six would you merge first? How would you detect two agents making conflicting decisions?

#### AG-17 · Context management for long-running agents
**Level:** M → S · **Units:** [30](../03-ai-systems/30-context-engineering-memory.md), [C11](../04-case-studies/C11-coding-agent-platform.md), [25](../03-ai-systems/25-agentic-systems.md)
- **Prompt:** Lumen's contract-review agent runs 150 steps per task. Keep its quality and cost under control.
- **Tests:** quadratic growth, compaction and its loss, caching, notes outside the window, sub-agent isolation.
- **Key trade-offs:** summarise vs truncate vs offload to files; a stable prefix for the cache vs editing the prompt; sub-agents vs one long context.
- **Numbers to expect:** chapter 30 (10 k-token prefix, +1.2 k tokens per step, $3 / $15 per million, illustrative): 150 steps read ≈ 14.9 M input tokens, ≈ $45 per task uncached, ≈ $5.80 cached, ≈ $4.11 with two compactions; caches expire (as of 2026-11, a 5-minute default lifetime and writes at 1.25× in one provider's pricing [19]), so a 20-minute approval pause at step 100 re-pays the prefix (≈ $0.48 without compaction, ≈ $0.16 with).
- **Rubric.** *No hire:* append everything. *Lean:* drop the oldest turns. *Hire:* compaction of old tool output, a stable prefix ordered from stable to volatile, tool results truncated at the tool, notes kept outside the window. *Strong hire:* cache lifetime and write premium in the cost model; compaction triggers tied to measured quality; sub-agents for context isolation; a regression test that compaction kept every constraint.
- **Red flags:** a timestamp at the top of the prompt (it breaks the cache); compaction that drops error evidence; "use a 1 M-token window".
- **Follow-ups:** How do you prove compaction did not drop a user's constraint?

#### AG-18 · Workflow agent with multi-day approvals
**Level:** S → St · **Units:** [C17](../04-case-studies/C17-workflow-automation-agent.md), [33](../03-ai-systems/33-agent-platform-runtime.md), [08](../01-foundations/08-async-event-driven.md)
- **Prompt:** An agent runs purchase workflows across Lumen's ERP and CRM. Approvals take days, and audit and segregation of duties are mandatory.
- **Tests:** durable timers and signals, plan-approve-execute, compensation, delegated identity, in-flight versioning.
- **Key trade-offs:** an agent loop vs a fixed workflow with model steps; saga vs distributed transaction; approve the plan vs each step.
- **Numbers to expect:** C17: 20 k runs a day × 2 days elapsed ≈ 40 k runs in flight (state, not compute); ≈ $0.22 of model cost per run; three reversible steps at 1 % failure each ≈ 3 % of runs (≈ 590 a day) needing compensation; up to ≈ 14 code versions alive at once with daily deploys.
- **Rubric.** *No hire:* the loop runs in a request handler. *Lean:* a queue plus polling, no compensation. *Hire:* durable workflow; a typed plan validated by policy and approved before execution; approval bound to the plan; idempotent steps with keys from run and step; delegated scoped tokens; audit with the agent's identity. *Strong hire:* in-flight versioning; a saga with the irreversible step last and a reconciler; segregation of duties enforced by the platform and rechecked at decision time; target-system rate limits in the plan; approval-fatigue controls.
- **Red flags:** a service account with ERP admin rights; the model re-plans after approval; audit equal to workflow history.
- **Follow-ups:** You change the prompt with 40 k runs in flight? The approver leaves the company mid-run?

#### AG-19 · Agentic data analyst
**Level:** S → St · **Units:** [30](../03-ai-systems/30-context-engineering-memory.md), [24](../03-ai-systems/24-retrieval-vector-systems.md), [13](../01-foundations/13-data-at-scale.md), [31](../03-ai-systems/31-securing-agentic-systems.md), [26](../03-ai-systems/26-llm-gateways-llmops.md), [18](../02-modern-requirements/18-security-by-design.md) (no case study teaches SQL agents end to end; the rubric applies these units' mechanisms to a warehouse and is course judgment)
- **Prompt:** Lumen's analysts ask questions in plain English over a 50,000-table warehouse and get SQL, results and charts.
- **Tests:** schema retrieval, safe execution, identity, cost guards, evaluation.
- **Key trade-offs:** curated metric definitions vs raw schema; execute-and-repair loop depth; the asker's identity vs a service account.
- **Numbers to expect:** with assumed 60 columns per table and 15 tokens per column, 50 k tables × 60 × 15 ≈ 45 M tokens of schema, so schema retrieval is mandatory (chapter 30: retrieve just in time); a careless 10 TB scan at an assumed $5 per TB costs $50 per question, while projection and partition pruning cut bytes scanned by orders of magnitude (chapter 13's example: ≈ 600×).
- **Rubric.** *No hire:* paste the schema into the prompt. *Lean:* table retrieval without permissions or cost control. *Hire:* schema retrieval by relevance (chapters 24, 30); queries run read-only under the asker's delegated identity, not a service account (chapter 31); bytes scanned estimated before execution and the query refused or narrowed above a per-question cap (chapter 13's estimate, enforced like any agent budget); a bounded repair loop with a step cap; the SQL shown to the user. *Strong hire:* a versioned golden set of questions with known results, graded on the result, not the SQL text, and run in CI (chapter 26 offline evaluation, chapter 32 final-state grading); clarifying questions for ambiguous metrics; result handles instead of raw rows in the context (chapter 30); PII redaction on results that reach the model (chapter 28); caches keyed by the asker's identity as well as the query, never by query text alone (chapter 31).
- **Red flags:** a service account with warehouse-wide read; answers with no SQL shown; no limit on bytes scanned.
- **Follow-ups:** Two teams define "revenue" differently: what does the agent answer? A question would scan 10 TB: what does the user see?

#### AG-20 · A help-chat agent with two read-only tools
**Level:** J → S · **Units:** [25](../03-ai-systems/25-agentic-systems.md), [C15](../04-case-studies/C15-support-agent-platform.md), [33](../03-ai-systems/33-agent-platform-runtime.md), [11](../01-foundations/11-reliability-engineering.md)
- **Prompt:** Lumen's help chat should answer "where is my order?" by calling two read-only tools: list the logged-in customer's orders, and get the shipment status of one order. Design the loop, the tools, and what happens when a tool fails.
- **Tests:** the agent loop, tool schemas and argument validation, identity binding, step caps, timeouts and retries.
- **Key trade-offs:** an agent loop vs a fixed two-call workflow; a step cap vs letting the model finish; retrying a tool vs telling the user it is unavailable.
- **Numbers to expect:** chapter 25's illustrative assumptions (3,000-token base, +1,500 tokens and 300 output tokens per step, $1/$4 per million): a 3-step answer reads 3 × 3,000 + 1,500 × 3 = 13,500 input tokens, ≈ $0.017 per question against ≈ $0.22 for the chapter's 15-step task; a cap of 5 steps bounds the worst case at 30,000 input tokens (≈ $0.036); at [I01 §17](I01-interview-playbook.md#17-when-the-prompt-is-agentic)'s 8.5 s per step (0.5 s to first token, 6 s decoding, 2 s tool), 3 steps take ≈ 26 s, so the chat streams progress.
- **Junior scope:** one tenant, the two read-only tools only, no refunds or account changes, no long-term memory.
- **Rubric.** *No hire:* the model is given a database connection or picks which customer to look up. *Lean:* a working loop with tools, but no step cap, no timeout, or tool errors passed to the model as raw stack traces. *Hire:* a loop with a step cap and a per-tool timeout; JSON Schema for each tool's arguments, validated by the runtime, not trusted from the model (chapter 25); the runtime fills in the customer from the logged-in session, so the model can never ask for another customer's orders, and order lookups are checked against the session's customer, not just filled in; one retry with backoff for a transient tool error, then a clear "can't check right now" answer; traces of each step. *Strong hire:* questions whether it needs an agent at all (two fixed calls may do), tokens per question quantified, a small set of past questions as an offline test, and a handoff to a human when the order is not found (C15).
- **Junior hire (on the junior scope):** draws the loop (model proposes a call, runtime validates and runs it, result goes back), writes the two tool schemas with an `order_id` argument but no customer argument, has the runtime check that the order belongs to the logged-in customer before calling the shipment API, sets a step cap and a timeout, and says what the user sees when the shipment tool is down.
- **Red flags:** the customer id as a model-chosen argument; no step cap; retrying forever; "the model will know when to stop".
- **Follow-ups:** The shipment API takes 30 s to answer? A customer types another customer's order number?

#### AG-21 · Ticket triage: workflow or agent?
**Level:** J → S · **Units:** [29](../03-ai-systems/29-agent-architectures-orchestration.md), [25](../03-ai-systems/25-agentic-systems.md), [08](../01-foundations/08-async-event-driven.md), [26](../03-ai-systems/26-llm-gateways-llmops.md)
- **Prompt:** Every new Lumen support ticket should get a category, a priority and a draft reply that a human edits before sending. Design it.
- **Tests:** the workflow-or-agent decision, structured output, queue-based processing, human in the loop, offline evaluation.
- **Key trade-offs:** one model call in a fixed workflow vs an agent loop; validated structured output vs free text; synchronous on ticket creation vs a queue.
- **Numbers to expect:** at an assumed 20,000 tickets a day (≈ 0.23/s on average, ≈ 0.7/s at a 3× peak), one call of ≈ 3,000 input and 300 output tokens at chapter 25's illustrative $1/$4 per million is ≈ $0.004 per ticket, ≈ $84 a day; running the same job as chapter 25's 15-step agent at ≈ $0.22 per task would be ≈ $4,400 a day, about 50× more for a task whose steps are known in advance (a 3-step agent would be ≈ $0.017 per ticket, ≈ $340 a day, about 4×; 50× is the case of a 15-step loop).
- **Junior scope:** one queue, one model call per ticket, no auto-send; the human always sends.
- **Rubric.** *No hire:* an autonomous agent that replies to customers directly, with no review step. *Lean:* one model call, but its output parsed as free text and no plan for bad output. *Hire:* applies chapter 29's decision test (the steps can be written down, so a workflow with one model step); a queue with retries and an idempotent write keyed by ticket id (chapter 08); the category and priority returned as structured output validated against a schema, with a fallback queue for invalid output; the draft never sent without a human; a labelled set of past tickets as the offline eval (chapter 26). *Strong hire:* cost per ticket quantified; accuracy per category tracked from the humans' edits; the switching trigger for adding an agent step (for example, the draft needs a lookup the workflow cannot predict).
- **Junior hire (on the junior scope):** says "this is a workflow, not an agent" with a reason, draws queue → model call → schema check → human review, uses the ticket id as the idempotency key, and names one metric (share of drafts sent with few edits).
- **Red flags:** "use an agent" with no reason; auto-sending drafts; parsing free text with string matching.
- **Follow-ups:** The model returns a category that does not exist? The model provider is down for an hour: what happens to new tickets?

## Security and compliance (SC)

#### SC-01 · Authentication and session service
**Level:** J → S · **Units:** [18](../02-modern-requirements/18-security-by-design.md), [10](../01-foundations/10-apis-communication.md)
- **Prompt:** Login, SSO, MFA and sessions for Lumen's web, mobile and API clients.
- **Tests:** token design, revocation, availability of auth, account takeover defenses.
- **Key trade-offs:** stateless tokens vs server sessions (revocation); token lifetime; central vs edge validation.
- **Junior scope:** email-and-password login with sessions for the web app only; no SSO or API clients.
- **Rubric.** *No hire:* long-lived tokens with no revocation. *Lean:* short tokens but no refresh or revocation design. *Hire:* short access tokens plus refresh tokens, revocation list, SSO via a standard protocol, rate limiting on login. *Strong hire:* auth outage behavior, credential-stuffing defenses, and step-up auth for sensitive actions.
- **Junior hire (on the junior scope):** passwords stored with a slow salted hash (for example Argon2 or bcrypt), server-side sessions or short-lived tokens with a logout that really revokes, login rate limiting, and secure cookie flags.

#### SC-02 · Tamper-evident audit log
**Level:** S → St · **Units:** [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md), [18](../02-modern-requirements/18-security-by-design.md)
- **Prompt:** Record every admin and AI-agent action in Lumen so that changes to past records are detectable.
- **Tests:** append-only storage, hash chaining, retention, query.
- **Key trade-offs:** hash chains vs Merkle trees vs WORM storage; retention vs erasure duties.
- **Rubric.** *No hire:* a normal table that admins can edit. *Lean:* append-only by convention. *Hire:* hash-chained entries, periodic anchoring, WORM storage, separate access controls. *Strong hire:* reconciling erasure requests with immutability (pseudonymous IDs), and verification tooling for auditors.

#### SC-03 · EU-resident AI platform
**Level:** St → P · **Units:** [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md), [28](../03-ai-systems/28-ai-trust-safety-governance.md), [15](../02-modern-requirements/15-multi-region-edge.md)
- **Prompt:** Lumen must keep EU customers' data and AI processing in the EU and meet its AI Act obligations.
- **Tests:** residency architecture, data flows, provider choices, documentation duties.
- **Key trade-offs:** separate EU cell vs global with controls; model providers' regional availability; logging vs data minimization.
- **Rubric.** *No hire:* "enable encryption". *Lean:* EU region, but telemetry and support flows leak data out. *Hire:* cell-based EU deployment, data-flow inventory, EU-only model endpoints, access controls for support staff. *Strong hire:* maps specific obligations to system features (logging, transparency, human oversight), and handles global features (search, analytics) without breaking residency.

#### SC-04 · Multi-tenant isolation
**Level:** S → St · **Units:** [18](../02-modern-requirements/18-security-by-design.md), [07](../01-foundations/07-partitioning-sharding.md)
- **Prompt:** Guarantee that no Lumen tenant can ever read another tenant's data, including through caches and AI features.
- **Tests:** defense in depth, tenant context propagation, testing isolation.
- **Key trade-offs:** logical vs physical isolation; cost vs assurance; shared caches and indexes.
- **Rubric.** *No hire:* relies on every query remembering a WHERE clause. *Lean:* row-level security but caches and search not considered. *Hire:* tenant context in identity, enforced at data layer, tenant-scoped cache keys and indexes, isolation tests. *Strong hire:* physical isolation tiers for regulated tenants, KV/prefix-cache sharing risks in LLM serving, and continuous isolation verification.

#### SC-05 · Build provenance and artifact signing
**Level:** S → St · **Units:** [18](../02-modern-requirements/18-security-by-design.md), [14](../02-modern-requirements/14-cloud-native-platforms.md)
- **Prompt:** Ensure only code built by Lumen's CI from reviewed commits can run in production.
- **Tests:** provenance, signing, admission control, key management.
- **Key trade-offs:** keyless vs long-lived signing keys; enforcement point (registry vs cluster admission); break-glass.
- **Rubric.** *No hire:* trusts any image in the registry. *Lean:* signs images but does not verify at deploy. *Hire:* provenance generated in CI, signatures verified at admission, SBOMs stored, dependency pinning. *Strong hire:* break-glass with audit, base-image patch SLAs, and model artifacts treated as supply-chain artifacts too.

#### SC-06 · PII redaction for LLM prompts
**Level:** M → S · **Units:** [28](../03-ai-systems/28-ai-trust-safety-governance.md), [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md)
- **Prompt:** Remove or tokenize personal data before Lumen prompts reach external model providers, then restore it in answers.
- **Tests:** detection accuracy, latency, reversible tokenization, logging hygiene.
- **Key trade-offs:** regex vs NER vs LLM detectors; redact vs pseudonymize; streaming restoration.
- **Rubric.** *No hire:* no redaction, "the provider is trusted". *Lean:* regex only, with no evaluation. *Hire:* layered detectors, reversible tokens in a vault scoped to the request, logs store only redacted text, measured recall. *Strong hire:* restoration during streaming, failure policy when the detector is down, and per-tenant policy.

#### SC-07 · Prompt-injection-resistant email assistant
**Level:** S → St · **Units:** [28](../03-ai-systems/28-ai-trust-safety-governance.md), [25](../03-ai-systems/25-agentic-systems.md)
- **Prompt:** An assistant reads users' email and can draft replies and create calendar events.
- **Tests:** untrusted input handling, privilege separation, confirmation flows.
- **Key trade-offs:** capability restriction vs usefulness; confirmation friction; dual-model patterns.
- **Rubric.** *No hire:* the model reads email and can send mail with no checks. *Lean:* a system prompt telling the model to ignore instructions in email. *Hire:* treats email as untrusted data, tool permissions enforced outside the model, user confirmation for side effects, exfiltration channels blocked. *Strong hire:* privilege-separated planner and reader, attack-based evaluation, and monitoring for injection attempts.

#### SC-08 · Abuse and bot defense
**Level:** S → St · **Units:** [10](../01-foundations/10-apis-communication.md), [C12](../04-case-studies/C12-realtime-fraud-recsys.md)
- **Prompt:** Stop scripted sign-ups and free-tier LLM abuse on Lumen without hurting real users.
- **Tests:** layered signals, rate limiting by identity, adaptive challenges, cost protection.
- **Key trade-offs:** friction vs abuse; IP-based vs account/device-based limits; block vs degrade.
- **Rubric.** *No hire:* CAPTCHA on everything. *Lean:* IP rate limits only. *Hire:* risk scoring from multiple signals, tiered responses (allow, challenge, limit, block), token budgets for free tier. *Strong hire:* attacker adaptation loop, measurement of false positives, and quantified cost saved.

#### SC-09 · Per-tenant encryption and key management
**Level:** S → St · **Units:** [18](../02-modern-requirements/18-security-by-design.md), [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md)
- **Prompt:** Enterprise tenants want their Lumen data encrypted with keys they control and can revoke.
- **Tests:** envelope encryption, KMS integration, performance, revocation.
- **Key trade-offs:** customer-managed vs provider-managed keys; key caching vs revocation latency; search and AI features on encrypted data.
- **Rubric.** *No hire:* one global key. *Lean:* per-tenant keys without envelope encryption. *Hire:* envelope encryption with per-tenant key-encryption keys in a KMS, cached data keys with TTL, documented revocation behavior. *Strong hire:* impact on indexes, caches and embeddings; key-loss recovery; and audit for key use.

## Ten red flags

These patterns can turn a "hire" into a "lean" or worse. The list is course synthesis: items 1–3 echo the public
guidance cited in [I01](I01-interview-playbook.md) [1][2][3]; the rest are course judgment.

1. **Designing before clarifying.** Drawing in the first minute, then discovering the real requirement at minute 30.
2. **Boxes without reasons.** Components named by brand with no requirement behind them.
3. **No numbers, or numbers that are never used.**
4. **Orders-of-magnitude errors left uncorrected** (ms vs µs, GB vs TB, ignoring peak).
5. **"Exactly-once" or "strongly consistent" asserted without mechanism.**
6. **Single point of failure in the critical path, unacknowledged.**
7. **"Add replicas" as the answer to every failure**, with no detection or overload behavior.
8. **Ignoring the interviewer's redirects or hints.**
9. **Bluffing specific facts** (limits, versions, benchmarks) rather than bounding them.
10. **For AI systems: treating the model as a stateless microservice**, sized by requests rather than tokens and GPU
    memory, with no evaluation plan.

## Ten strong signals

1. **Ranks non-functional requirements** and uses the ranking to decide trade-offs later.
2. **Finds the shaping constraint** (the celebrity account, the SMS cost, the KV-cache budget) early.
3. **Turns numbers into decisions** ("so a single primary is out").
4. **Justifies every box** in one sentence.
5. **Uses four-part trade-off sentences** (choice, reason, cost, switching trigger).
6. **Goes two levels below the box** in deep dives, raising edge cases unprompted.
7. **Pairs every mitigation with detection** (an SLI or alert).
8. **Names the true bottleneck at ×10** and it is not "more servers".
9. **Knows what not to build** and keeps the design minimal.
10. **Summarizes decisions and risks clearly** at the end, and asks good questions about the interviewer's real system.

## Self-study plans

**How the hours are computed.** Each week's load is the sum of: the `estimated_time` reading figure in each unit's
front matter for units marked **read** (labs are optional and not counted); 1 hour for each unit marked **skim**
(Core ideas, Numbers that matter and Interview angle only, a labelled assumption); and 1 hour per 45-minute mock,
including scoring (assumption). With those rules the 4-week plan needs **≈ 8–11 hours per week** and the 8-week plan
**≈ 8.5–11 hours per week**; the optional agentic week 9 adds **≈ 10 hours**. If you have less time, drop the skims
first, never the mocks. Each week ends with timed
mocks from this bank, scored with the six-dimension rubric. Track your scores in a table and repeat questions with
changed constraints. Junior candidates should draw their mocks from the junior track above and run the junior scope.

### 4-week plan (you already work on distributed systems)

| Week | Read / skim | Practice (45-min mocks) | Hours |
|---|---|---|---|
| 1 — Method and numbers | Read [I01](I01-interview-playbook.md) (2.5 h), [I02](I02-numbers-cheat-sheets.md) (1.5 h); skim [01](../00-orientation/01-requirements-to-numbers.md), [06](../01-foundations/06-replication-consistency.md), [07](../01-foundations/07-partitioning-sharding.md) (3 h) | CL-01, CL-12 (compare with the I01 mock), CL-14 (3 h) | ≈ 10 |
| 2 — Classical depth | Skim [04](../01-foundations/04-caching.md), [08](../01-foundations/08-async-event-driven.md), [11](../01-foundations/11-reliability-engineering.md) (3 h); read cases [C02](../04-case-studies/C02-news-feed.md) (2 h), [C06](../04-case-studies/C06-payments-ledger.md) (2.5 h) | CL-03, CL-07, DI-05 (3 h) | ≈ 10.5 |
| 3 — AI-era systems | Read [21](../03-ai-systems/21-llm-inference-anatomy.md) (3 h), [I04](I04-ml-llm-interviews.md) (3 h); skim [22](../03-ai-systems/22-serving-llms-at-scale.md), [24](../03-ai-systems/24-retrieval-vector-systems.md), [C10](../04-case-studies/C10-enterprise-rag-assistant.md) (3 h) | AI-01, AI-02 (2 h) | ≈ 11 |
| 4 — Your target mix | Skim two units for your target role (2 h): platform [14](../02-modern-requirements/14-cloud-native-platforms.md), [15](../02-modern-requirements/15-multi-region-edge.md); AI [25](../03-ai-systems/25-agentic-systems.md), [26](../03-ai-systems/26-llm-gateways-llmops.md); agents [29](../03-ai-systems/29-agent-architectures-orchestration.md), [31](../03-ai-systems/31-securing-agentic-systems.md); security [18](../02-modern-requirements/18-security-by-design.md), [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md). Read one matching case, for example [C09](../04-case-studies/C09-llm-chat-service.md) or, for agent roles, [C15](../04-case-studies/C15-support-agent-platform.md) (2–2.5 h) | Four mocks from the target category; two with a peer as interviewer. Agent roles: AG-05, AG-09, AG-12, AG-16 (4 h) | ≈ 8–8.5 |

### 8-week plan (building foundations, or targeting staff+)

| Week | Read / skim | Practice | Hours |
|---|---|---|---|
| 1 — Method | Read [00](../00-orientation/00-how-to-use-this-course.md) (1 h), [01](../00-orientation/01-requirements-to-numbers.md) (3 h), [I01](I01-interview-playbook.md) (2.5 h), [I02](I02-numbers-cheat-sheets.md) (1.5 h) | Estimation drills from exercises/I02 (1 h); CL-16 (1 h) | ≈ 10 |
| 2 — Request path and compute | Read [02](../01-foundations/02-anatomy-of-a-request.md) (2.5 h), [04](../01-foundations/04-caching.md) (3 h), [C01](../04-case-studies/C01-url-shortener-rate-limiter.md) (2 h); skim [03](../01-foundations/03-scaling-compute.md) (1 h) | CL-01, CL-10 (2 h) | ≈ 10.5 |
| 3 — Data | Read [05](../01-foundations/05-choosing-storage.md) (3.5 h), [06](../01-foundations/06-replication-consistency.md) (3.5 h); skim [07](../01-foundations/07-partitioning-sharding.md), [C07](../04-case-studies/C07-distributed-kv-store.md) (2 h) | CL-08, IP-08 (2 h) | ≈ 11 |
| 4 — Async, coordination, APIs | Read [08](../01-foundations/08-async-event-driven.md) (3 h), [C03](../04-case-studies/C03-chat-presence.md) (2 h); skim [09](../01-foundations/09-coordination-consensus.md), [10](../01-foundations/10-apis-communication.md) (2 h) | CL-04, CL-15, RT-10 (3 h) | ≈ 10 |
| 5 — Reliability, observability, data at scale | Read [11](../01-foundations/11-reliability-engineering.md) (3 h); skim [12](../01-foundations/12-observability.md), [13](../01-foundations/13-data-at-scale.md), [20](../02-modern-requirements/20-real-time-streaming.md) (3 h) | DI-01, DI-02, RT-03 (3 h) | ≈ 9 |
| 6 — Modern requirements | Skim [14](../02-modern-requirements/14-cloud-native-platforms.md), [15](../02-modern-requirements/15-multi-region-edge.md), [16](../02-modern-requirements/16-cost-as-requirement.md), [18](../02-modern-requirements/18-security-by-design.md), [19](../02-modern-requirements/19-privacy-compliance-sovereignty.md) (5 h); read [C14](../04-case-studies/C14-global-flash-sale.md) (2 h) | IP-03, SC-03, CL-13 (3 h) | ≈ 10 |
| 7 — AI systems | Read [21](../03-ai-systems/21-llm-inference-anatomy.md) (3 h), [I04](I04-ml-llm-interviews.md) (3 h); skim [22](../03-ai-systems/22-serving-llms-at-scale.md), [24](../03-ai-systems/24-retrieval-vector-systems.md), [C09](../04-case-studies/C09-llm-chat-service.md) (3 h) | AI-01, AI-02 (2 h) | ≈ 11 |
| 8 — Agents, governance, full mocks | Skim [25](../03-ai-systems/25-agentic-systems.md), [26](../03-ai-systems/26-llm-gateways-llmops.md), [28](../03-ai-systems/28-ai-trust-safety-governance.md), [C11](../04-case-studies/C11-coding-agent-platform.md) (4 h) | AG-01, AG-03 (2 h), plus two 60-minute mocks with a peer (≈ 2.5 h) | ≈ 8.5 |
| 9 (optional) — Agentic depth, for agent-heavy roles | Skim [29](../03-ai-systems/29-agent-architectures-orchestration.md), [30](../03-ai-systems/30-context-engineering-memory.md), [31](../03-ai-systems/31-securing-agentic-systems.md), [32](../03-ai-systems/32-observing-evaluating-agents.md), [33](../03-ai-systems/33-agent-platform-runtime.md) (5 h); read one case for your target role: [C15](../04-case-studies/C15-support-agent-platform.md) support, [C16](../04-case-studies/C16-deep-research-agents.md) research or [C17](../04-case-studies/C17-workflow-automation-agent.md) workflow automation (2 h) | Three AG mocks matching the case: AG-05, AG-12, AG-13 for C15; AG-07, AG-11, AG-16 for C16; AG-10, AG-18, AG-15 for C17 (3 h) | ≈ 10 |

Units not listed (for example [17](../02-modern-requirements/17-energy-carbon-aware.md), [23](../03-ai-systems/23-gpu-infrastructure.md),
[27](../03-ai-systems/27-ml-platforms.md) and most case studies) are for after the plan, or replace a skim in the
week where they match your target role. Week 9 is the only place the 8-week plan covers chapters 29–33 and the
agentic cases C15–C17; reading those five chapters in full instead of skimming them would take 16 h (3 + 3.5 + 3 + 3
+ 3.5) and needs a second week. In the 4-week plan, agent roles get two of these chapters as skims and one agentic
case in week 4.

**Staff and principal add-on.** In weeks 6–8, for every mock, finish with a five-minute "evolution" segment. Explain
how you would get from a simpler existing system to your design, what you would build first, and what you would
*not* build. Practice the phrase "here is what I'd decline to build, and why".

## Numbers that matter

Practice-time arithmetic: 90 questions × 45 minutes = 67.5 hours, more than either plan allows (the 4-week plan has 12
mock slots, the 8-week plan 20, or 23 with the optional week 9). Choose ≈ 15–25 questions
that cover every category at your target level, and repeat 5–8 of them with changed constraints. Repetition with
variation builds more skill than one pass through everything (a practice heuristic, not a measured result).

## Design choices and trade-offs

| Practice choice | Wins when | Costs |
|---|---|---|
| Breadth (many questions once) | Early in preparation; finding weak categories | Shallow depth |
| Depth (few questions, repeated with twists) | Final weeks; fixing specific rubric dimensions | Narrow coverage |
| Solo recorded mocks | Any time; cheap | No outside probing |
| Peer mocks | You need realistic redirects | Scheduling; peer quality varies |

## Frontier [Frontier]

As of 2026-11, the AI/LLM and agentic categories move fastest. Tool-calling prompts such as AG-02 are framed
around a standard protocol, the Model Context Protocol, whose current specification is dated 2026-07-28 [11]; for EU-facing prompts
(SC-03), the AI Act as published applies from 2 August 2026, with its prohibitions in force since 2 February 2025 [9].
Regulation (EU) 2026/1744 (the "Digital Omnibus on AI", in force 27 July 2026) moved the high-risk obligations to
2 December 2027 for Annex III systems and 2 August 2028 for Annex I systems [13]; quote those dates, not the original
2 August 2026 one, for high-risk prompts. Re-check the versions you quote, and expect the categories to shift again within a year.

## Failure modes and operations

Self-scoring goes wrong in predictable ways (course observations, not measured results):

| Failure | Symptom | Guard |
|---|---|---|
| Generous self-scores | Every mock scores "hire" while real interviews do not | Score from the recording, not memory; ask a peer to score one mock a week |
| Practicing only favourite categories | Strong in CL, blank on AI or SC prompts | Pick mocks by the count table, at least one per category |
| Reading rubrics before answering | Answers recite the rubric's words | Answer first, read the rubric only when scoring |
| Wrong level | Junior candidates drown in staff-level scope; seniors coast | Run the junior scope at junior level; add the full prompt's twists at senior+ |
| No repeats | Same weak dimension in every mock | Re-run one prompt a week with a changed constraint |

## Interview angle

How to pick and run a question from this bank as an interviewer or a practice partner:

1. **Choose by level.** Use the entry level in the count table; for juniors, give the junior scope.
2. **Read only the prompt aloud.** Keep the trade-offs and rubric hidden until scoring.
3. **Probe the shaping constraint.** Each question's *Key trade-offs* line lists where to push.
4. **Change one constraint at minute 30** (region, scale ×10, cost cap) and watch whether the design changes visibly.
   For agentic questions, the *Follow-ups* line gives ready-made changes, and the *Red flags* line tells you what to
   write down when you hear it.
5. **Score the six dimensions first,** then the question's own four outcomes, and write one sentence of evidence per
   score.

## Common mistakes

- Practicing only classical prompts for an AI-heavy role, or the reverse.
- Reading model answers instead of producing your own first.
- Scoring yourself generously on Resilience and Communication, which are the hardest to self-assess. Ask a peer.
- Never re-running a question with a changed constraint.

## Check yourself

1. Which rubric dimension usually separates senior from staff candidates?
2. Pick any AI/LLM question and name the unit that teaches its core estimate.
3. Name three red flags that concern numbers.
4. What is the difference between a "lean" and a "hire" on CL-12?
5. For AG-05, why is the exposure line (volume × limit) a hire-level number, and which control does it size?

Exercises with answers: [exercises/I03-question-bank-rubrics.md](../../exercises/I03-question-bank-rubrics.md).

## Lab

No lab for this unit. The practice loop (mock, score, study, repeat with a twist) is the lab.

## Further reading

- The public guidance cited in [I01](I01-interview-playbook.md): Meta [1], Amazon [2], Google SRE Workbook [3].

**Further sources by question** (primary sources for facts the rubrics rely on; all accessed 2026-11-20):

| Question | Fact in the rubric | Source |
|---|---|---|
| CL-01 | 301 (Moved Permanently) vs 302 (Found) semantics | RFC 9110 §15.4.2–15.4.3 [5] |
| CL-08 | Quorum rule R + W > N, sloppy quorum and hinted handoff | DeCandia et al., Dynamo, SOSP 2007 [6] |
| CL-04, RT-02 | Little's law for connection sizing | Little, 1961 [7] |
| CL-14 | UUIDs are 128 bits; UUIDv7 layout | RFC 9562 [4] |
| DI-06 | One-month response window (Art. 12(3)); right to erasure (Art. 17) | GDPR, Regulation (EU) 2016/679 [8] |
| SC-03 | AI Act application dates as published (2 Feb 2025 prohibitions; 2 Aug 2026 general application); later amendments may move high-risk dates | Regulation (EU) 2024/1689, Art. 113 [9] |
| IP-05, SC-05 | Supply-chain levels and build provenance | SLSA specification v1.2 [10] |
| AG-02 | Tool and resource protocol (JSON-RPC 2.0 based) | Model Context Protocol specification, 2026-07-28 [11] |
| IP-09 | Workload identity documents (X.509-SVID, JWT-SVID) | SPIFFE overview [12] |
| AG-07, AG-16 | Agents ≈ 4× and multi-agent systems ≈ 15× the tokens of chat; token usage explained 80 % of variance on BrowseComp | Anthropic engineering, 2025-06-13 [14] |
| AG-12 | pass^k proposed as a reliability metric over repeated trials | Yao et al., τ-bench, 2024 [15] |
| AG-16 | "Actions carry implicit decisions, and conflicting decisions carry bad results" | Cognition, 2025-06-12 (perspective) [16] |
| AG-11 | Rule of Two: no more than two of untrustworthy input, sensitive data, state change or external communication, until injection can be reliably detected and refused | Meta, 2025-10-31 [17] |
| AG-11 | Stage-2 false-negative rate 5.7 % on 1,000 synthetic exfiltration attempts | Anthropic, 2026-03-25 [21] |
| AG-02 | MCP servers must validate the token audience and must not accept or transit other tokens | MCP Authorization, 2026-07-28 [18] |
| AG-17 | 5-minute default cache lifetime; cache writes 1.25×, reads 0.1× base input price (0.05× or 0.025× on some models), as of 2026-11 | Anthropic prompt-caching docs [19] |
| AG-03 | Execution history limited to 51,200 events or 50 MB | Temporal documentation [20] |
| AG-13 | Users accepted 93 % of permission prompts (one product, vendor measurement) | Anthropic, 2026-03-25 [21] |
| AG-15 | `act` claim records delegation; nested `act` claims record prior actors | RFC 8693 [22] |
| AG-01 | SWE-bench Verified rated "Flawed": flawed tests and training-data exposure (OpenAI audit, 2026-02-23) | Epoch AI, 2026-09-03 [23] |
- Each linked unit's **Interview angle** section: model answer outlines and follow-ups for its topic.

## References

1. Meta Careers, *Preparing for your Software Engineering Interview at Meta*, updated 2022-10-06.
   https://www.metacareers.com/blog/preparing-for-your-software-engineering-interview-at-meta/ (accessed 2026-11-20; archived copy:
   https://web.archive.org/web/20260610131027/https://www.metacareers.com/blog/preparing-for-your-software-engineering-interview-at-meta/)
2. Amazon, *SDE III/Sr. SDE Interview Prep*. https://amazon.jobs/content/en/how-we-hire/sde-iii-interview-prep (accessed 2026-11)
3. S. Virji et al., "Non-Abstract Large System Design", *The Site Reliability Workbook*, ch. 12.
   https://sre.google/workbook/non-abstract-design/ (accessed 2026-11)
4. K. Davis, B. Peabody, P. Leach, *Universally Unique IDentifiers (UUIDs)*, RFC 9562, May 2024 (UUIDv7, referenced in CL-14).
   https://www.rfc-editor.org/rfc/rfc9562 (accessed 2026-11-20)
5. R. Fielding, M. Nottingham, J. Reschke (eds.), *HTTP Semantics*, RFC 9110, June 2022, §15.4.
   https://www.rfc-editor.org/rfc/rfc9110 (accessed 2026-11-20)
6. G. DeCandia et al., "Dynamo: Amazon's Highly Available Key-value Store", SOSP 2007.
   https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf (accessed 2026-11-20)
7. J. D. C. Little, "A Proof for the Queuing Formula: L = λW", *Operations Research* 9(3):383–387, 1961.
   https://doi.org/10.1287/opre.9.3.383 (publisher blocks automated fetches; metadata confirmed via
   https://api.crossref.org/works/10.1287/opre.9.3.383, accessed 2026-11-20)
8. Regulation (EU) 2016/679 (General Data Protection Regulation), Art. 12(3) and Art. 17.
   https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng (accessed 2026-11-20)
9. Regulation (EU) 2024/1689 (Artificial Intelligence Act), Art. 113 and recital 179 (application dates).
   https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng (accessed 2026-11-20)
10. SLSA project, *SLSA specification*, version 1.2. https://slsa.dev/spec/v1.2/ (accessed 2026-11-20)
11. *Model Context Protocol specification*, version 2026-07-28. https://modelcontextprotocol.io/specification/2026-07-28 (accessed 2026-11-20)
12. SPIFFE project, *SPIFFE overview*. https://spiffe.io/docs/latest/spiffe-about/overview/ (accessed 2026-11-20)
13. Regulation (EU) 2026/1744 of 8 July 2026 (Digital Omnibus on AI), amending Regulation (EU) 2024/1689, OJ L, 24.7.2026. https://eur-lex.europa.eu/eli/reg/2026/1744/oj (accessed 2026-11)
14. Anthropic Engineering, *How we built our multi-agent research system*, 2025-06-13. https://www.anthropic.com/engineering/multi-agent-research-system (accessed 2026-11-20)
15. S. Yao, N. Shinn, P. Razavi, K. Narasimhan, *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*, arXiv:2406.12045, 2024 (preprint). https://arxiv.org/abs/2406.12045 (accessed 2026-11-20)
16. W. Yan (Cognition), *Don't Build Multi-Agents*, 2025-06-12 (blog; perspective). https://cognition.com/blog/dont-build-multi-agents (accessed 2026-11-20)
17. Meta AI, *Agents Rule of Two: A Practical Approach to AI Agent Security*, 2025-10-31. https://ai.meta.com/blog/practical-ai-agent-security/ (accessed 2026-11-20)
18. Model Context Protocol, *Specification 2026-07-28: Authorization*. https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization (accessed 2026-11-20)
19. Anthropic, Claude docs, *Prompt caching*. https://platform.claude.com/docs/en/build-with-claude/prompt-caching (accessed 2026-11-20)
20. Temporal documentation, *Workflow Execution limits*. https://docs.temporal.io/workflow-execution/limits (accessed 2026-11-20)
21. Anthropic, *Claude Code auto mode* (research post), 2026-03-25 ("users accept 93% of them anyway"). https://www.anthropic.com/research/claude-code-auto-mode (accessed 2026-11-20)
22. M. Jones et al., *OAuth 2.0 Token Exchange*, RFC 8693, January 2020, §4.1. https://www.rfc-editor.org/rfc/rfc8693.html (accessed 2026-11-20)
23. Epoch AI, *SWE-bench Verified* benchmark review (verdict "Flawed"; summarises OpenAI's 2026-02-23 audit and training-data exposure), reviewed 2026-09-03. https://epoch.ai/benchmarks/swe-bench-verified/review (accessed 2026-11-20)
