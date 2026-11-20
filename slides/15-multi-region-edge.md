# 15 — Multi-region & edge (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/02-modern-requirements/15-multi-region-edge.md](../course/02-modern-requirements/15-multi-region-edge.md)

## Slide 1 — The requirement

- Lumen has tenants in Frankfurt, Virginia and Singapore
- p95 < 200 ms for interactive calls everywhere
- Survive a full region loss: RTO ≤ 5 min, RPO = 0 for billing
- EU tenants' data stays in the EU

**Visual:** World map with three region pins and three requirement callouts (latency, availability, sovereignty).
Icons: `arch-region`, `pattern-geo-distribution`, `ops-slo`, `security-lock`.

**Speaker notes:** Three sentences, three different pressures. Latency wants data near users, availability wants copies
far apart, and sovereignty forbids copying some data at all. The rest of the talk is about reconciling them.

## Slide 2 — Three drivers, three designs

- Latency → serve the critical path from nearby (edge + regional reads/writes)
- Availability → a second region that can take over
- Sovereignty → partition data by geography; control what replicates out
- First interview question: "Which of the three is it?"

**Visual:** Three-column table; each column ends in a different mini-architecture.
Icons: `ops-latency`, `pattern-failover`, `security-lock`.

**Speaker notes:** Latency alone can often be solved with a CDN and read replicas. Availability alone can be a warm
standby that never serves users. Sovereignty rules out "replicate everything everywhere".

## Slide 3 — The speed of light is a design constraint

- Fiber ≈ 2/3 c ≈ 200 km/ms (refractive index ≈ 1.47)
- RTT floor (ms) ≈ great-circle distance (km) / 100
- Frankfurt ↔ N. Virginia ≈ 6,550 km → ≈ 65 ms RTT floor
- London ↔ Sydney ≈ 16,990 km → ≈ 170 ms RTT floor
- Real paths are worse: median router path 2.3× the vacuum bound (Singla et al., HotNets 2014)

**Visual:** Globe arc between two cities with a light pulse; formula overlay.
Icons: `arch-network`, `ops-latency`.

**Speaker notes:** This is the most useful mental formula in the chapter. Count the wide-area round trips on the
critical path and multiply by the floor, and you know whether a design can meet the SLO before you build it.

## Slide 4 — A latency budget: Singapore user, Frankfurt origin

- Single region: TCP + TLS 1.3 + request ≈ 3 RTT ≈ 309 ms minimum → SLO broken by physics
- Edge PoP terminates TLS + warm origin connection → ≈ 113 ms floor
- Home region in Singapore → ≈ 50 ms with 30 ms server time (assumption)
- Synchronous 2-of-3 replication to EU/US → +100 ms per write

**Visual:** Stacked horizontal bars per design, with a 200 ms SLO line.
Icons: `arch-cdn`, `arch-region`, `ops-slo`.

**Speaker notes:** The four designs differ only in how many long round trips they put on the critical path. Moving
TLS termination to the edge removes two of the three.

## Slide 5 — The DR ladder

- Backup & restore → pilot light → warm standby → hot standby → active/active
- Pilot light cannot serve without action; warm standby can, at reduced capacity (AWS DR whitepaper)
- Cost and complexity rise as RTO/RPO fall
- Automatic regional failover: use with caution; automate the steps, keep a human trigger

**Visual:** Staircase diagram, with RTO/RPO decreasing and cost increasing per step.
Icons: `pattern-backup`, `pattern-failover`, `ops-cost`.

**Speaker notes:** These terms come from the AWS disaster recovery whitepaper. The key distinction to remember is
pilot light versus warm standby. False-alarm failovers cost real availability and data, which is why many teams keep a
human trigger.

## Slide 6 — Active-active: three write models

- Write global: one write region, local reads (Aurora Global Database, write forwarding)
- Write local: write anywhere, resolve conflicts (DynamoDB global tables MREC, last writer wins)
- Write partitioned: each record has a home region, so no conflicts by construction
- Write partitioned = the workhorse, and it matches residency

**Visual:** Three small diagrams with arrows from users to regions; conflicting arrows marked with an X shape (not
color only).
Icons: `arch-database`, `pattern-replication`, `pattern-partitioning`.

**Speaker notes:** "Active-active" is not a single design. Always say which write model you mean. For tenant data,
write partitioned is usually the right answer.

## Slide 7 — Give every row a home

- Regional data: tenant docs, chats, embeddings
- Global read-mostly: catalogs, flags (write slow, read fast everywhere)
- Global contended: unique names, balances (consensus, keep small)
- CockroachDB: `REGIONAL BY TABLE`, `REGIONAL BY ROW` (`crdb_region`), `GLOBAL`
- `SURVIVE REGION FAILURE`: ≥ 3 regions, replicas 3 → 5, +1 RTT on writes

**Visual:** Table rows colored by home region, with a hidden column labelled `crdb_region` (labels, not color only).
Icons: `sql-cockroachdb`, `pattern-partitioning`, `arch-region`.

**Speaker notes:** Geo-partitioning in practice is one keyword. The tension to point out is that region survival for
EU data means a second region inside the EU.

## Slide 8 — Conflict resolution, cheapest to most correct

- Avoid: single home per item
- Last writer wins: simple, silently drops a write, clock-skew sensitive
- CRDTs: commutative updates, strong eventual consistency
- Application merge: Dynamo's shopping cart; deleted items may resurface
- Consensus: no conflict, but every write pays a cross-region RTT

**Visual:** Ladder with five rungs, each with a one-word example (profile theme, presence, cart, balance).
Icons: `pattern-consistency`, `pattern-consensus`, `nosql-dynamodb`.

**Speaker notes:** DynamoDB MRSC sits in an interesting middle position. It rejects one of two concurrent writes with a
retryable error instead of silently dropping it.

## Slide 9 — Global databases, compared (as of 2026-11)

- Spanner: Paxos + TrueTime; ε ≈ 1–7 ms sawtooth; commit wait ≥ 2ε̄
- CockroachDB v26.4: Raft per range, per-row homes, `GLOBAL` tables with future-timestamp writes
- DynamoDB MREC: write anywhere, LWW; MRSC (GA 2025-06-30): exactly 3 regions, RPO 0
- Aurora Global Database: one writer, up to 10 secondaries, lag typically < 1 s

**Visual:** Four-row comparison card: writes-in, consistency, conflict handling.
Icons: `nosql-dynamodb`, `sql-cockroachdb`, `sql-aws-aurora`, `cloud-gcp`.

**Speaker notes:** Pick by data class, not by brand. Ask whether you need the latest value or a value with bounded
staleness, and whether a lost update is acceptable.

## Slide 10 — Steering users: geo-DNS vs anycast

- Geo-DNS (e.g., Route 53 latency/geolocation/failover policies): sees the resolver, cached by TTL
- EDNS Client Subnet (RFC 7871) improves accuracy, with privacy and cache costs
- Anycast (RFC 4786): one IP from many places; fails over at routing speed
- Anycast + long TCP flows = risk; terminate TCP at the edge

**Visual:** Left: DNS resolver returning different A records. Right: one IP announced from three PoPs with BGP arrows.
Icons: `arch-dns`, `network-aws-route53`, `arch-router`, `network-cloudflare`.

**Speaker notes:** Production front doors combine them. Anycast reaches the nearest PoP, the PoP terminates TLS, and
the edge chooses the origin region based on health and latency.

## Slide 11 — Edge compute: fast compute, slow state

- CloudFront Functions: submillisecond, 2 MB, 10 KB code, no body
- Lambda@Edge: up to 30 s, network and body access
- Cloudflare Workers: V8 isolates, 128 MB per isolate; no VM boot per function
- Rule: never pay the long round trip more than once per request
- Edge AI: small models at the edge; big-model generation stays regional

**Visual:** Three tiers (PoP, regional edge cache, region) with execution limits; a red-flag example of 3 sequential
DB calls (≈ 240 ms) marked with a warning icon.
Icons: `network-cloudflare-workers`, `cloud-aws-lambda`, `network-aws-cloudfront`, `ops-warning`, `domain-ai`.

**Speaker notes:** The edge is excellent for TLS, caching, auth and routing, and poor for chatty access to a
far-away database. For AI, the network round trip matters most for small, fast models.

## Slide 12 — Cells and shuffle sharding: limit the blast radius

- Cell = complete, independent copy of the workload; thin router by partition key
- 10 cells → one cell failure leaves 90% of requests unaffected (AWS guidance)
- Deploy in waves: cell by cell, region by region
- Shuffle sharding: 8 workers, pairs → 28 combinations → 1/28 impact; Route 53 → ~730 billion shards

**Visual:** Cell router fanning out to cells; a second panel with a grid of 8 workers and overlapping pairs.
Icons: `arch-servers-cluster`, `pattern-bulkhead`, `pattern-sharding`, `ops-deploy`.

**Speaker notes:** Regions protect you from infrastructure failure. Cells protect you from your own bad deploys and
poison requests, which regions alone will happily replicate everywhere.

## Slide 13 — Failover = detect, decide, fence, shift

- Detect from several vantage points; watch for gray failure
- Decide: automate the steps, keep the trigger deliberate
- Fence the old primary (leases, tokens) to avoid split brain
- Shift with data-plane operations; pre-provision capacity (static stability)
- Rehearse; failback is a planned switchover

**Visual:** Four-step state machine with a fence icon between decide and shift.
Icons: `pattern-health-check`, `pattern-failover`, `security-lock`, `ops-incident`.

**Speaker notes:** Most failover disasters happen at the fence and failback steps. Static stability means the surviving
region already has the capacity. It does not count on autoscaling during the outage.

## Slide 14 — Interview wrap

- CLARIFY the driver and RPO/RTO per data class
- QUANTIFY with distance/100 and round-trip counting; headroom u ≤ (N−1)/N
- SKETCH edge → home regions → data classes; DEEPEN write models and failover
- STRESS region loss, gray failure, split brain, residency of derived data
- WRAP: global agreement only where correctness needs it

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP ribbon.
Icons: `ops-check`, `arch-region`.

**Speaker notes:** The red flags to avoid are synchronous cross-ocean writes on a tight SLO, two-region consensus, and
treating DNS failover as instant.
