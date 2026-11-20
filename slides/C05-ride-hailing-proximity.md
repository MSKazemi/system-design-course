# C05 — Ride-hailing & proximity search (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C05-ride-hailing-proximity.md](../course/04-case-studies/C05-ride-hailing-proximity.md)

## Slide 1 — The requirement

- 600 cities; 2 M online drivers report every 4 s
- Riders see nearby cars live
- Match within 2 s at p99; never double-assign a driver
- Prices react to local supply and demand

**Visual:** City map with moving car dots and one rider pin.
Icons: `domain-car`, `domain-map`, `domain-map-pin`, `company-uber`.

**Speaker notes:** The data rewrites itself every few seconds, "nearby" is geometric, and assignment is mutual
exclusion with a human in the loop.

## Slide 2 — The numbers

- 500,000 location updates/s
- Whole live index ≈ 128 MB
- ≈ 600,000 nearby-car views/s; ≈ 1,000 ride requests/s
- Trip traces ≈ 3.5 TB/day

**Visual:** A tiny memory chip labelled 128 MB next to a huge "updates/s" counter.
Icons: `ops-throughput`, `arch-memory`.

**Speaker notes:** The index is small and soft — drivers re-send every 4 s, so a lost index heals itself.

## Slide 3 — Sketch

- Location gateway → per-city in-memory geo index
- Location event log → traces, supply–demand, pricing
- Rider API → per-cell nearby-cars cache
- Per-city matcher → ETA service + durable driver state

**Visual:** The lesson's 13-node flowchart.
Icons: `arch-api-gateway`, `arch-memory`, `arch-event-stream`, `arch-cache`, `arch-database`.

**Speaker notes:** Partition by city: matching never crosses cities and failures stay local.

## Slide 4 — Four spatial indexes

- Geohash: bit-interleaved key; Redis GEO uses a 52-bit geohash
- Quadtree: adapts to density
- S2: cube faces + Hilbert curve; levels 0–30; 64-bit IDs
- H3: hexagons, 16 resolutions, aperture 7

**Visual:** The same city tiled four ways.
Icons: `domain-map`, `cache-redis`, `company-google`, `company-uber`.

**Speaker notes:** Any works for candidate search; the choice matters for aggregation and for sharing cells across
systems.

## Slide 5 — Why hexagons

- One distance to every neighbor (squares have two, triangles three)
- k-rings approximate circles: 3k(k+1)+1 cells
- 12 pentagons per resolution — handle them
- Children cover the parent only approximately

**Visual:** Hexagon with six equal arrows vs square with two arrow lengths.
Icons: `domain-map`.

**Speaker notes:** Uber's H3 post makes the equal-distance argument; the docs give the caveats.

## Slide 6 — Choosing a resolution

- Res 7: 5.16 km², edge ≈ 1.41 km
- Res 8: 0.737 km², edge ≈ 0.53 km → neighbors ≈ 0.92 km apart
- Res 9: 0.105 km², edge ≈ 0.20 km
- Res 8, k = 2 → 19 cells ≈ 2 km radius; then exact-distance filter

**Visual:** Concentric k-rings at res 8 around a pickup pin.
Icons: `domain-map-pin`, `pattern-partitioning`.

**Speaker notes:** Numbers from the H3 resolution table; spacing is √3 × edge.

## Slide 7 — Ingesting moving points

- Per update: old cell → new cell, overwrite record
- Last-writer-wins on device timestamp; discount low-accuracy fixes
- Stale after ≈ 15 s → excluded from matching
- No WAL: history goes to the log in parallel

**Visual:** A car crossing a cell border; its ID hops between two cell sets.
Icons: `arch-memory`, `arch-event-stream`, `ops-clock`.

**Speaker notes:** Soft state is a design choice that removes a durability problem from the hottest path.

## Slide 8 — 600,000 map views without geo queries

- Every 1–2 s publish per-cell snapshots to a cache
- Rider reads own cell + ring
- Approximate positions: cheaper and more private
- Location-service CPU stays for matching

**Visual:** Snapshot fan-out from location service to regional caches.
Icons: `arch-cache`, `arch-pubsub`.

**Speaker notes:** Read fan-in exceeds writes here; cache it like any hot read.

## Slide 9 — Matching without double assignment

- Candidates: k-ring → available, fresh → 20 closest → road ETAs
- CAS: Available@v → Offered(lease 15 s)
- Accept is a CAS too; expiry returns the driver
- Split-brain matchers are safe — the CAS decides

**Visual:** The driver state machine from the lesson.
Icons: `pattern-transaction`, `security-lock`, `ops-clock`.

**Speaker notes:** Leases keep a human who never answers from blocking the system.

## Slide 10 — Greedy vs batched

- Greedy: fast, locally optimal
- Batch 1–2 s, solve assignment across requests × drivers
- Exercise 7: greedy 14 min vs batched 7 min total pickup
- Worth it in dense cities; less so in sparse ones

**Visual:** Two riders, two drivers; crossing vs uncrossed assignment lines.
Icons: `pattern-batching`, `domain-car`.

**Speaker notes:** State the trade-off, not a "correct" algorithm — matching policies are product decisions.

## Slide 11 — ETA and pricing

- DeepETA: learn the residual over the routing engine's ETA
- Hundreds of millions of parameters, ≈ 0.25 % used per prediction
- Supply/demand per hex per minute; smooth with neighbors
- Quote IDs: the accepted price is the charged price

**Visual:** Routing-engine ETA bar plus a small learned correction; a heat map of hexes.
Icons: `domain-ai`, `ops-metrics`, `domain-payment`.

**Speaker notes:** Baseline plus learned correction keeps the system working when the model doesn't.

## Slide 12 — Modern twist

- H3 cell IDs as the join key across matching, pricing, analytics, ML features
- H3 4.x API: `gridDisk`, `gridRing`, pentagon-aware
- ML models on hard real-time paths with classical fallbacks
- Location is personal data: approximate views, cell aggregates, executable retention

**Visual:** One hex ID linking a matching event, a pricing row and a feature table.
Icons: `domain-map`, `arch-data-warehouse`, `security-lock`.

**Speaker notes:** The biggest energy consumer is 2 M phones — adaptive reporting intervals help batteries and servers.

## Slide 13 — WRAP

- Junior: why lat/lng indexes fail; geohash/quadtree; periodic updates; nearest driver
- Senior: index comparison with numbers; soft state per city; cached map views; CAS + lease
- Staff: soft vs durable split, batching, per-city SLOs, baseline+ML, privacy and device energy
- Red flags: synchronous DB writes per update, global index, locks with no expiry

**Visual:** Staircase junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** Alert per city: a 1 % global error rate can hide a full outage in one city.
