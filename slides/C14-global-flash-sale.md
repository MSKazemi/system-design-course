# C14 — Global flash sale (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- 100,000 units at 12:00:00 UTC; 20 M interested people; bots
- Zero oversell, one per customer, fair, rest of the store stays up
**Visual:** countdown clock above a crowd and a small box of stock. Icons: `domain-cart`, `ops-clock`, `arch-users`.
**Speaker notes:** Demand is 200× supply and arrives in seconds. The question is where the queue lives.

## Slide 2 — CLARIFY
- Waiting room, reservation, checkout within a time limit, release on timeout, prompt "sold out"
- Ask: what does "fair" mean? What is the payment provider's limit?
- Out of scope: fulfilment, returns, catalogue
**Visual:** requirement list. Icons: `ops-check`, `domain-payment`.
**Speaker notes:** Fairness and the payment limit are the two numbers that shape the design.

## Slide 3 — QUANTIFY the spike
- 6 M arrivals in the first minute → 100 k users/s (assumptions)
- ≈ 3.1 M edge req/s; ≈ 500 k join attempts/s with bots; ≈ 800 k polls/s
- Static and waiting traffic must stay at the edge
**Visual:** spike chart at T0. Icons: `arch-cdn`, `ops-throughput`.
**Speaker notes:** 800 k polls per second to an origin database is a self-inflicted outage.

## Slide 4 — Admission rate from the narrowest pipe
- Payment provider ≈ 2,000 authorisations/s (assumption — ask)
- 60 % of admitted users pay → admit ≈ 3,300 users/s
- ≈ 167 k admissions sell out in ≈ 50 s
**Visual:** funnel from 12 M waiting to 3,300/s admitted to 2,000/s paid. Icons: `pattern-backpressure`, `domain-payment`.
**Speaker notes:** Work backwards from downstream capacity; most people will only see "sold out" — tell them fast.

## Slide 5 — SKETCH
- CDN → edge waiting room (signed tickets) → admission controller
- Gateway requires admission token → reservation service → stock buckets + reservations (TTL)
- Checkout → payment provider; orders + outbox → events; expiry sweeper
**Visual:** the lesson flowchart. Icons: `arch-cdn`, `arch-queue`, `arch-api-gateway`, `arch-database`, `arch-event-stream`.
**Speaker notes:** It is a hot-key and flow-control problem, not a big-data problem.

## Slide 6 — The invariant
- held + confirmed ≤ total stock, always, including failover
- Conditional decrement `WHERE available > 0` — correct but one hot row
- Stock buckets: 100 rows × 1,000 units → ≈ 33 writes/s each
**Visual:** one hot row vs 100 cooler rows. Icons: `pattern-sharding`, `pattern-transaction`.
**Speaker notes:** Buckets keep the invariant because each bucket is disjoint and never goes below zero.

## Slide 7 — Why Redis is not the inventory
- DECR and Lua scripts are atomic on one node
- Replication is async; WAIT does not make Redis CP; acknowledged writes can be lost on failover
- Lost decrement → oversell; use Redis only as a soft gate
**Visual:** primary with DECRs, failover to a replica missing the last few. Icons: `cache-redis`, `pattern-failover`, `ops-error`.
**Speaker notes:** Caches may cause undersell or delay; they must never be able to cause oversell.

## Slide 8 — Reservations with TTL
- Reserve = decrement + reservation row in one transaction
- Pay → confirmed; expire → guarded transition, stock returned
- Reconcile after close: confirmed + held + available = initial
**Visual:** reservation state machine. Icons: `ops-clock`, `pattern-transaction`.
**Speaker notes:** A guarded state transition stops a late payment and the sweeper from both winning.

## Slide 9 — The waiting room
- Signed tickets verified at the edge; no database per poll
- Admission controller publishes a threshold from downstream health
- Short-lived admission token required by the gateway
**Visual:** edge node with cookies; controller dial. Icons: `arch-queue`, `security-token`, `pattern-rate-limiter`.
**Speaker notes:** The waiting room converts an outage into a line.

## Slide 10 — Fair ordering
- FIFO by millisecond rewards scripts on fast links
- Cloudflare offers FIFO and Random queueing methods
- Pre-queue window with random ranks, then FIFO; publish the policy
**Visual:** pre-queue lottery shuffle, then a line. Icons: `domain-ticket`, `arch-users`.
**Speaker notes:** Removing the incentive to refresh at 11:59:59.999 is also load control.

## Slide 11 — Idempotent checkout
- Idempotency-Key on every mutation; Stripe: ≤ 255 chars, saved response, 24 h pruning
- Order ID as the provider's idempotency key; webhooks are the truth; 3DS
- Reservation TTL > payment timeout; refund if paid after expiry
**Visual:** the checkout sequence diagram. Icons: `pattern-idempotency`, `pattern-saga`, `payments-stripe`.
**Speaker notes:** The IETF Idempotency-Key header is still a draft as of 2026-11.

## Slide 12 — Bots, pre-scaling, degradation
- Verified accounts, per-account/device/payment limits, challenges, unique (sale, user)
- Pre-scale before T0; load-test a step, not a ramp
- Flags: lower admissions, pause on provider errors, hold-all page, brownout the rest
**Visual:** degradation ladder. Icons: `domain-bot`, `security-ddos`, `pattern-autoscaling`.
**Speaker notes:** Autoscaling reacts in minutes; the spike arrives in seconds.

## Slide 13 — STRESS and multi-region
- SQL failover: pause admissions; synchronous replication for the sale DB
- Retry storms: jittered back-off, server-controlled poll interval
- Home region per sale vs stock allocated per region
**Visual:** two world maps. Icons: `arch-region`, `pattern-geo-distribution`, `pattern-retry`.
**Speaker notes:** Warehouse location often decides the multi-region model.

## Slide 14 — WRAP
- Junior: CDN, queue, atomic decrement, idempotency
- Senior: waiting room, admission from capacity, buckets, TTL, saga, bots, Redis failover risk
- Staff: invariant proof, published fairness, cells, multi-region, reconciliation, agentic shoppers
- Red flags: Redis as inventory, autoscale for spikes, queueing in the DB
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** Close with the invariant argument in four sentences.
