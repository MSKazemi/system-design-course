# C05 — Exercises

Lesson: [course/04-case-studies/C05-ride-hailing-proximity.md](../course/04-case-studies/C05-ride-hailing-proximity.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Update rate and index size

800,000 couriers online at peak report every 5 s. Each index entry is 80 B. Compute updates/s and the in-memory index
size. What does the result tell you about how to partition?

<details><summary>Answer</summary>

Updates: 800,000 / 5 = **160,000 /s**. Index: 800,000 × 80 B = 64 MB. The whole index fits in one machine's memory many
times over, so you do *not* partition for size; you partition (by city or region) for **blast radius, locality and
write isolation**, and you replicate for availability. Interviewers look for this inversion.
</details>

## 2. [Core] H3 resolution and k-ring

Using the H3 table (resolution 8: average area 0.737 km², edge ≈ 0.531 km; resolution 9: 0.105 km², edge ≈ 0.201 km),
how many cells does a k-ring need to cover about 1.5 km at each resolution? How many drivers would you scan in a city
with 30 available drivers per km²?

<details><summary>Answer</summary>

Center-to-center spacing = √3 × edge: res 8 ≈ 0.92 km, res 9 ≈ 0.35 km. Use the lesson's two rules. *Typical* reach
≈ *k* × spacing: res 8 needs *k* = 2 (19 cells, ≈ 19 × 0.737 ≈ 14 km², ≈ 420 drivers); res 9 needs *k* = 4
(3·4·5 + 1 = 61 cells, ≈ 6.4 km², ≈ 190 drivers). *Guaranteed* radius ≈ 0.87 × *k* × spacing − edge/2 (any pickup
position, any direction): res 8 *k* = 2 gives only ≈ 1.3 km, so *k* = 3 (37 cells, ≈ 27 km², ≈ 820 drivers); res 9
*k* = 6 gives ≈ 1.7 km (127 cells, ≈ 13.4 km², ≈ 400 drivers). Res 9 gives a tighter shape (less wasted area) for more
cell lookups. Either is fine; in
both cases filter by exact distance afterwards and keep the closest 20 before computing road ETAs.
</details>

## 3. [Deep] Why hexagons?

Explain, with reference to neighbor distances, why hexagons simplify smoothing supply–demand counts compared to
square cells. Name two caveats of H3 you must handle in code.

<details><summary>Answer</summary>

A hexagon's center is equidistant from all six neighbors; squares have two neighbor distances (edge and corner
neighbors) and triangles three. Smoothing "average each cell with its neighbors" therefore needs no distance weights
on a hex grid, and k-rings approximate circles well. Caveats from the H3 docs: (1) **12 pentagons per resolution** —
neighborhood functions may return fewer cells, and some "unsafe" variants can fail near them; (2) **children only
approximately cover their parent geographically** (logical containment is exact), so rolling up counts by parent cell
is fine but polygon containment queries need care.
</details>

## 4. [Core] Stale and out-of-order updates

A driver's phone sends updates at t = 100, 104, 108 s (device time). The server receives them in the order 104, 100,
108, and the 100 update has 400 m GPS accuracy. What should the index hold after each arrival, and when should the
driver be excluded from matching?

<details><summary>Answer</summary>

After 104: position@104. After 100: ignore (older device timestamp; last-writer-wins on `ts`). After 108: position@108.
The 400 m-accuracy reading would be discounted anyway (don't let low-accuracy fixes move a driver far). Exclude the
driver once the newest update is older than the staleness threshold (≈ 15 s in the lesson) — absence of updates usually
means a tunnel, a dead phone or a closed app.
</details>

## 5. [Deep] The lost index

The location-service instance for a city of 60,000 drivers crashes. There is no replication of the in-memory index.
How long until matching works again, and what does that imply about durability requirements for the index versus
driver state?

<details><summary>Answer</summary>

A replacement instance (or standby already subscribed to the update stream) receives every online driver's next
update within one interval (4 s), so the index is essentially complete in ≈ 4–5 s plus failover detection. The index is
**soft state**: no WAL or synchronous replication needed. Driver *assignment* state is the opposite: losing "driver X
is on trip Y" would allow double assignment, so it lives in a durable, strongly consistent store with compare-and-set.
Matching should refuse to run on an index that has been up for less than one interval (it would miss drivers).
</details>

## 6. [Interview] Never double-assign

Two matcher instances (for neighboring sub-regions) pick the same driver for two riders at the same moment. Design the
protocol that guarantees only one wins, and handle a driver who never answers.

<details><summary>Answer</summary>

Driver state has a version. Each matcher issues `CAS(driver_id, expect: Available@v, set: Offered(offer_id,
expires_at = now + 15 s)@v+1)`. Exactly one succeeds; the loser moves to its next candidate. The offer is a lease: if
the driver does not accept by `expires_at`, a sweeper (or the next read) transitions `Offered → Available`. Accept is
`CAS(expect: Offered(offer_id), set: EnRoute)`, so a late accept fails cleanly and the app shows "offer expired".
Two matchers running for the same city by mistake (split brain) are harmless because the CAS, not matcher ownership,
provides mutual exclusion.
</details>

## 7. [Deep] Greedy vs batched

Riders A and B request 1 s apart. Driver X is 2 min from A and 3 min from B; driver Y is 4 min from A and 12 min from B.
Greedy assigns in arrival order. Compute total pickup time for greedy and for an optimal batch of both. What does the
batch cost?

<details><summary>Answer</summary>

Greedy: A takes X (2 min), B gets Y (12 min) → 14 min total. Batched optimum: A–Y (4) + B–X (3) = **7 min**. The batch
halves total pickup time here at the cost of waiting up to one batching window (≈ 1 s) before offering — affordable
inside a 2 s budget in dense cities, less useful in sparse markets where most requests have one reasonable driver.
</details>

## 8. [Core] Nearby cars at 600,000 views/s

Why not run a geo query per map refresh? Design the per-cell snapshot and size it for a city with 40,000 drivers, 200
bytes per approximate entry, refreshed every 2 s.

<details><summary>Answer</summary>

Per-refresh queries would spend location-service CPU on cosmetic views and compete with matching. Snapshot: every 2 s,
publish `cell → [approx positions, heading, product]` to a cache; the rider API reads the rider's cell and its ring.
Size: 40,000 × 200 B = 8 MB per city per snapshot — trivial to replicate to regional caches. Reads become ≈ 7–19 cache
key lookups per view. Approximate positions also serve privacy: riders see that cars are near, not exactly where each
driver is.
</details>

## 9. [Lab] Leases and failover

In [labs/09-coordination-consensus](../labs/09-coordination-consensus/), run Experiment 5 (`python3 -I lab.py fencing`,
a lease-based lock with the etcd revision as fencing token) and optional Experiment 7 (`etcdctl elect`). Relate what
you observe to driver offers and to matcher ownership of a city.

<details><summary>Answer</summary>

Record what you observe: while the lease is held no other client gets the lock, and with token checking the store
rejects the paused client's stale write. Driver offers work the same way, except the "lease holder" is a human who may
never answer — expiry is what keeps the system live. For matcher ownership, a lease decides which instance runs a
city's matcher; the CAS on driver state is the safety net if two instances briefly overlap.
</details>

## 10. [Interview] Privacy by design

Legal asks how long you keep precise trip traces and who can see driver positions. Propose a policy and the
mechanisms that enforce it.

<details><summary>Answer</summary>

Policy (example — confirm with counsel): full-resolution traces kept for a fixed dispute/safety window (e.g. a few
months), then downsampled or aggregated to H3 cells; analytics only on cell-level aggregates; riders see approximate
nearby cars until matched, exact location only for their assigned driver during the trip. Mechanisms: TTLs on
time-partitioned trace tables so deletion is automatic; separate access-controlled store for full traces with audit
logging; aggregation jobs that never read raw traces after the window. Location data is personal data under GDPR, so
purpose limitation and minimization apply (SYSDESIGN-19).
</details>
