# 15 — Exercises

Lesson: [course/02-modern-requirements/15-multi-region-edge.md](../course/02-modern-requirements/15-multi-region-edge.md)

Conventions: the fiber speed is 200 km/ms (≈ 2/3 c), so the RTT floor in ms ≈ great-circle km / 100. All server times
are labelled assumptions.

---

## 1. [Core] RTT floor and why reality is worse

Two regions are 8,000 km apart along a great circle. (a) What is the lower bound on round-trip time over fiber?
(b) Give three reasons a measured ping will be higher.

<details><summary>Answer</summary>

(a) 8,000 / 100 = **80 ms** (one way 40 ms). In vacuum it would be about 53 ms, and the gap is the ≈ 1.5× slowdown of
light in glass.

(b) (1) Cables do not follow great circles. They follow coastlines, landing stations and existing rights of way.
(2) Router hops, queuing and serialization add delay. (3) BGP picks policy-preferred paths, not the shortest ones.
Singla et al. measured the median router path at 2.3× the vacuum bound, and sometimes saw "hairpinning" through a
distant continent. For HTTPS rather than ping, add protocol round trips for TCP and TLS, plus server time.
</details>

## 2. [Core] Pilot light vs warm standby vs active-active

For each Lumen component, pick a DR strategy and justify it: (a) the public marketing site; (b) the chat API;
(c) the billing ledger (RPO = 0); (d) the nightly analytics warehouse.

<details><summary>Answer</summary>

- (a) **Static content on a CDN** with an origin bucket replicated cross-region. Backup & restore of the origin is
  enough, because the CDN keeps serving cached pages during an origin outage.
- (b) **Active-active, write partitioned** by tenant home region if latency is a driver. If it is not, **warm
  standby**, which can take traffic immediately at reduced capacity and then scale. Pilot light would need servers
  "switched on" first, which threatens a 5-minute RTO.
- (c) RPO = 0 rules out any asynchronous strategy. Use **synchronous cross-region consensus** (Spanner-style,
  CockroachDB `SURVIVE REGION FAILURE`, or DynamoDB MRSC), with three regions. Accept higher write latency for this
  small, critical data set.
- (d) **Backup & restore** (or pilot light). A day's delay in analytics is usually acceptable, and paying for a hot
  warehouse in a second region is hard to justify.

Acceptable alternative: some teams run (b) as hot standby to avoid conflict design entirely, at full duplicate cost.
</details>

## 3. [Interview] Latency budget for an Australian user

Lumen's only region is N. Virginia. A Sydney user's interactive call has a p95 SLO of 200 ms. Sydney ↔ N. Virginia is
about 15,700 km great-circle (haversine on city coordinates). The handler needs 40 ms of server time (assumption). Evaluate: (a) a
fresh HTTPS connection direct to the origin; (b) an edge PoP in Sydney 5 ms RTT away with a warm connection to the
origin; (c) an APAC home region in Sydney.

<details><summary>Answer</summary>

RTT floor ≈ 157 ms.

- (a) TCP (1 RTT) + TLS 1.3 (1 RTT) + request (1 RTT) ≈ 3 × 157 = 471 ms + 40 ms ≈ **511 ms minimum**. That fails, and
  physics alone is the cause.
- (b) Handshakes at the PoP ≈ 2 × 5 = 10 ms. The request rides the warm connection ≈ 5 + 157 = 162 ms, plus 40 ms ≈
  **212 ms floor**. It still fails at the floor, and real paths are longer. Edge termination helps but cannot fix a
  single long round trip on a tight SLO.
- (c) ≈ 10 ms (PoP) + a few ms to the region + 40 ms ≈ **55 ms**. That passes. The cost is an APAC region and a data
  model in which APAC tenants' data is homed there.

Strong answers also mention caching read-mostly responses at the edge and HTTP/3/QUIC 0-RTT resumption for returning
clients as partial mitigations.
</details>

## 4. [Deep] Quorum placement

You run a consensus-replicated table with five voters for a European product. Option A: Frankfurt, Paris, Virginia,
Oregon, Singapore (one each). Option B: Frankfurt ×2, Paris ×2, Ireland ×1. Compare write latency and what each
survives.

<details><summary>Answer</summary>

A majority is 3 of 5.

- **Option A.** From a Frankfurt leader, the nearest other voters are Paris (≈ 5 ms RTT floor) and Virginia
  (≈ 65 ms). A majority needs two acknowledgments besides the leader's own vote, so writes wait for ≈ 65 ms or more.
  This option survives the loss of any two regions, including losing the whole of Europe except one site, but every
  write pays a transatlantic round trip. It also probably violates EU residency.
- **Option B.** Leader in Frankfurt; its local peer acknowledges within ≈ 1 ms and Paris within ≈ 5 ms, so writes
  commit in a few ms. The loss of any single region (at most 2 voters) leaves 3 voters, so it survives one region. It
  does *not* survive an EU-wide event, and all data stays in the EU.

This is the same 2+2+1 shape that CockroachDB uses for `SURVIVE REGION FAILURE` across three regions. Choose B for an
EU product with residency, and add encrypted, EU-located backups for disasters.
</details>

## 5. [Core] Which conflict strategy?

Choose a conflict-resolution strategy for each and explain: (a) a user's UI theme preference; (b) "users currently
online in a workspace"; (c) a shared collaborative document; (d) remaining API credit balance; (e) a username that must
be globally unique.

<details><summary>Answer</summary>

- (a) **Last writer wins.** Losing one of two near-simultaneous theme changes is harmless.
- (b) **CRDT** (for example, an observed-remove set with timestamps or leases) or soft state with expiry. Presence is
  additive and tolerant of brief staleness.
- (c) **Sequence CRDT or operational transform**, or a **single home** per document (a single-writer object near its
  users, like a Durable Object). Avoid LWW, which would drop whole edits.
- (d) **Single home or consensus.** A lost decrement is lost money. If the regions are far apart, consider allocating
  each region a pre-approved slice of the budget (escrow) to avoid a round trip per request.
- (e) **Consensus / globally consistent table** (or one home region for the uniqueness index). LWW would let two people
  "own" the name until the merge, and then silently take it from one of them.
</details>

## 6. [Deep] DynamoDB MREC vs MRSC

A team proposes DynamoDB global tables for an order-placement service across us-east-1, eu-west-1 and ap-northeast-1.
(a) What happens with concurrent updates to the same order in two regions under MREC? Under MRSC? (b) List three MRSC
limitations that could affect the design.

<details><summary>Answer</summary>

(a) **MREC:** both writes succeed locally. Replication resolves the conflict per item by last writer wins (latest
internal timestamp), so one update is silently discarded. Strongly consistent reads are only guaranteed to be up to
date for writes made in the same region. **MRSC:** a write is synchronously replicated to at least one other region
before success. A concurrent write to an item already being modified in another region fails with
`ReplicatedWriteConflictException`, which the client can retry. Writes and strong reads pay cross-region latency.

(b) Any three of: exactly three regions (three replicas, or two plus a witness); the table must be empty when converted;
no TTL; no local secondary indexes; no transactions (`TransactWriteItems` errors); the mode cannot be changed after
creation; no `ReplicationLatency` metric. The missing transactions in particular may force a redesign of
multi-item order updates.
</details>

## 7. [Core] Edge function anti-pattern

An edge function in a PoP 5 ms from users personalizes a page by making three *sequential* queries to a database in a
region 80 ms RTT from the PoP. Estimate the latency and propose two fixes.

<details><summary>Answer</summary>

≈ 5 ms (user↔PoP) + 3 × 80 ms = **≈ 245 ms**, plus query time. Running the whole handler in the region would cost
roughly 5 + 80 = 85 ms plus intra-region queries of about 1 ms each.

Fixes: (1) move the logic to the data: the edge forwards one request to a regional endpoint that runs the three
queries locally; (2) move the data to the edge: cache or replicate the read-mostly personalization data into an edge
KV store; (3) batch the three queries into one round trip if the database API allows it. The principle is to pay the
long round trip at most once per request.
</details>

## 8. [Interview] Region-failure headroom

Lumen runs active-active in N regions at equal load. What is the maximum safe steady-state utilization per region if
the system must absorb the loss of one region without overload? Compute for N = 2, 3, 5 and explain why AWS calls
pre-provisioning "static stability".

<details><summary>Answer</summary>

After one region fails, the remaining N−1 must carry the total load, so u ≤ (N−1)/N.
N = 2 → 50%; N = 3 → ≈ 67%; N = 5 → 80%. More regions mean less idle headroom per unit of capacity, which is one
reason three regions can be cheaper than two for the same survivability.

Static stability: the surviving regions already have enough provisioned capacity, so recovery does not depend on
control-plane actions (launching instances, autoscaling) that may themselves be impaired or congested during a large
event. The system behaves the same during the failure as before it.
</details>

## 9. [Deep] Residency and auto-rehoming

Lumen uses a CockroachDB `REGIONAL BY ROW` table for EU and US tenants, with auto-rehoming enabled. An EU tenant's
admin travels to New York and edits a document from there. What can go wrong, and how do you design against it?

<details><summary>Answer</summary>

With auto-rehoming, an `UPDATE` or `UPSERT` can move the row's home (`crdb_region`) to the region of the gateway that
served the write. Here that is a US region, so EU data now has its home and leaseholder in the US, which breaks a
residency commitment. Fixes: disable auto-rehoming for regulated tables. Set `crdb_region` explicitly from the
tenant's contractual home region, held by the control plane (not inferred from traffic). Route all writes for that
tenant to EU gateways, and accept higher latency for travelling users. Audit replication targets, and remember that
indexes, backups, logs and embeddings derived from the data must also stay in the EU.
</details>

## 10. [Core] Anycast vs DNS failover

Explain why anycast fails over faster than DNS-based failover, and why RFC 4786 warns about anycast for some
workloads.

<details><summary>Answer</summary>

DNS failover changes the *answer*, but resolvers and clients cache the old answer for at least the record's TTL, and
some keep it longer, so traffic drains gradually. Anycast keeps the *same* address and lets BGP withdraw the failed
site's route, which shifts packets at routing convergence speed without client cooperation.

The warning: if routing changes mid-flow, packets of an ongoing connection can reach a different node that has no
state for it. RFC 4786 asks that node selection be stable for substantially longer than the expected transaction time,
and singles out TCP and long-running flows. Hence the common pattern of anycast to an edge proxy that terminates TCP,
then unicast to origins.
</details>

## 11. [Interview] Full design sketch

In 10 minutes, sketch Lumen's multi-region design that meets the chapter's requirement (p95 < 200 ms in EU/US/APAC,
region-loss RTO ≤ 5 min, billing RPO = 0, EU data in EU). Use CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP.

<details><summary>Answer</summary>

- **CLARIFY:** confirm the data classes: tenant content (regional, residency-bound), billing (global, RPO 0), catalog
  and flags (global read-mostly), and LLM inference (stateless, GPU-bound).
- **QUANTIFY:** Singapore↔Frankfurt ≈ 103 ms floor, so a single-region design fails, and APAC needs a home region.
  Headroom with 2 regions per geography is 50%.
- **SKETCH:** anycast to edge PoPs (TLS, auth, cache, small-model classification) → geography-specific home regions
  (EU: Frankfurt + Paris; US: Virginia + Oregon; APAC: Singapore + Tokyo). Each region contains several cells keyed by
  tenant.
- **DEEPEN:** tenant data is write-partitioned to its home geography, replicated synchronously to the paired region in
  the same jurisdiction. Billing goes in a consensus-replicated store across three regions (for example, three
  regions of one jurisdiction for EU billing records), accepting higher write latency off the chat critical path.
  Catalog data uses global read-optimized tables.
- **STRESS:** losing Frankfurt shifts EU traffic to Paris, which is pre-provisioned (static stability) and fenced
  before it accepts writes. Bad deploys are contained by cell waves. For gray failure, use traffic dials and
  multi-vantage probes. Check residency for logs, indexes and backups.
- **WRAP:** global agreement only for billing and uniqueness; everything else is regional with nearby replicas, edge
  for the first hop, and cells for blast radius.
</details>
