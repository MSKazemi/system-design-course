# C14 — Exercises

Lesson: [course/04-case-studies/C14-global-flash-sale.md](../course/04-case-studies/C14-global-flash-sale.md).
Numbers are assumptions unless the lesson gives a source.

## 1. [Core] Admission rate

The payment provider allows 800 authorisations/s; 50 % of admitted users pay; stock is 30,000. What admission rate,
and how long until enough users are admitted to sell out?

<details><summary>Answer</summary>

Admission ≤ 800 / 0.5 = 1,600 users/s. Stock is taken at reservation, so all 30,000 units are *held* after
30,000 / 1,600 ≈ 19 s. About 60,000 admissions are needed in total (30,000 / 0.5), but the second 30,000 cannot be
admitted at 1,600/s: they are admitted one per unit released as unpaid reservations expire, over the TTL tail. So
admit stock plus a small buffer at full rate, then pace by releases; tell everyone ranked beyond ≈ 60,000 "sold out"
at once. Add a margin below the limit (e.g. admit 1,400/s) because conversion varies and the provider may slow down;
the 800/s cap is conservative anyway, since think time spreads payments over minutes.
</details>

## 2. [Core] Poll interval

10 M users wait. Compare edge requests/s for a client that polls every 1 s vs every 20 s. What else should control the
interval?

<details><summary>Answer</summary>

10 M req/s vs 500 k req/s — a 20× difference in edge cost and load. The server should control the interval
(`poll_after_s`), lengthen it for users far back in the queue, and add jitter so polls do not synchronise. Push (SSE
or WebSockets) is possible but holding 10 M connections is usually more expensive than infrequent polls.
</details>

## 3. [Deep] Prove zero oversell

Write the argument that your bucket design cannot oversell, and name one change that would break it.

<details><summary>Answer</summary>

Stock is consumed only by `UPDATE … SET available = available − 1 WHERE … AND available > 0`, which cannot make a
bucket negative; buckets are disjoint and their initial values sum to total stock; the reservation row is inserted in
the same transaction as the decrement; releases increment only via a guarded `held → expired/released` transition;
the database is strongly consistent across failover. Breaking changes: making Redis the source of truth (async
replication can lose decrements on failover), releasing stock without the guarded transition, or using an
asynchronously replicated database whose failover can drop committed reservations.
</details>

## 4. [Deep] Bucket count

How many stock buckets for 100,000 units at 3,300 reservations/s? What happens near sell-out?

<details><summary>Answer</summary>

The row lock is held until commit, so buckets ≥ reservation rate × commit latency, plus headroom. With a same-region
synchronous replica (commit ≈ 1–2 ms, assumption) a row handles hundreds of decrements/s; 100 buckets at ≈ 33/s each
are ample. With synchronous commit to another region (assume 100–200 ms), one row sustains only 5–10/s, so 3,300/s
needs ≈ 330–660 buckets (say 1,000 of 100 units), or keep synchronous replicas in-region and replicate cross-region
asynchronously with reconciliation. Near sell-out many buckets are empty: a reservation tries a random non-empty
bucket, retries a bounded number of times, and refreshes the list of non-empty buckets (a small cached set). "No stock
now" is when the sum of `available` is 0; "sold out for good" also needs no held reservations. Push either state to
the edge.
</details>

## 5. [Interview] Fairness policy

Product says "first come, first served". Explain the problem and propose an alternative.

<details><summary>Answer</summary>

Millisecond FIFO at T0 rewards scripts, proximity and refresh-spamming, and creates a synchronised spike. Alternative:
a pre-queue window (e.g. 15 minutes before T0) in which everyone gets a random rank, then FIFO for later arrivals;
admission in rank order with a published policy. Cloudflare's waiting room, for example, offers both FIFO and Random
methods. Combine with verified accounts and per-account limits so one person cannot hold many tickets.
</details>

## 6. [Deep] Reservation TTL vs payment

A 3-D Secure challenge can take up to 6 minutes; your reservation TTL is 5 minutes. What goes wrong and how do you fix
it?

<details><summary>Answer</summary>

The sweeper can release the unit while the customer is still authenticating; the unit is resold and the first
customer's payment succeeds — a refund and an angry customer, or oversell if the confirmation does not re-check the
reservation. Fix: TTL longer than the worst payment path, extend the reservation when the provider returns
`requires_action`, and make confirmation conditional on the reservation still being `held` (otherwise refund
automatically).
</details>

## 7. [Interview] Redis failover

Your colleague implemented inventory with Redis `DECR` and Sentinel failover. What do you say?

<details><summary>Answer</summary>

Redis replication is asynchronous by default; even `WAIT` does not make it CP, and acknowledged writes can be lost on
failover. A lost decrement means the promoted replica reports more stock than exists → oversell. Keep Redis as a fast
soft gate (admission tokens, a "probably sold out" flag), and make strongly consistent SQL buckets the source of truth.
</details>

## 8. [Core] Multi-region

Stock is in two warehouses (EU 60 %, US 40 %). Choose a multi-region model and explain the trade-offs.

<details><summary>Answer</summary>

Allocate stock per region (EU 60,000, US 40,000), each with its own buckets and checkout, because fulfilment is
regional anyway; sell locally with low latency; after a period, rebalance leftovers only if cross-shipping is allowed.
Trade-off: a US customer may see "sold out" while EU still has stock — publish the rule. A home-region model is simpler
but adds cross-region latency and makes the home region a single point of failure.
</details>

## 9. [Lab] Per-account rate limits

Use [labs/10-apis-communication](../labs/10-apis-communication/). Configure a token bucket per account (capacity 3,
refill 1 per 10 s) on the join endpoint and drive it with one "bot" account sending 100 req/s and 50 normal accounts.

<details><summary>Answer</summary>

The bot account should be throttled to its bucket rate while normal accounts are unaffected; compare with a per-IP
limit when all accounts share one IP (shared NAT) to see why per-account limits are fairer. Record observed 429
counts and lab versions.
</details>

## 10. [Lab] Stampede on the sale config

Use [labs/04-caching](../labs/04-caching/). Let a hot cache key (the sale configuration) expire under load, with and
without request coalescing / early refresh.

<details><summary>Answer</summary>

Without coalescing, the expiry sends a burst of identical requests to the database (a stampede) and p99 spikes; with
coalescing or probabilistic early refresh, one request refreshes the key. Relate this to the sold-out flag and
admission threshold, which should be pushed to the edge rather than fetched on demand. Report your measurements.
</details>

## 11. [Lab] Idempotent order consumer

Use [labs/08-async-event-driven](../labs/08-async-event-driven/). Publish `payment_succeeded` webhooks to a queue
with duplicates and out-of-order delivery; implement the consumer that confirms reservations.

<details><summary>Answer</summary>

Deduplicate by provider event ID, apply a state machine (`pending → paid` only from `pending`), and confirm the
reservation only if it is still `held`; duplicates become no-ops and an out-of-order `payment_failed` after `paid` is
ignored or flagged. Verify that replaying the whole stream twice leaves the same final state.
</details>

## 12. [Lab] Retry storm at T0

Use [labs/11-reliability-engineering](../labs/11-reliability-engineering/). Inject a 5-second outage of the
reservation service and compare client retries without jitter, with exponential back-off and jitter, and with a
server-controlled retry-after.

<details><summary>Answer</summary>

Without jitter, retries synchronise and the recovered service is hit by a multiple of normal load, extending the
outage; with back-off and jitter the load spreads; with server-controlled retry-after (and the waiting room holding
admissions), the load returns at the controlled admission rate. Record observed request rates and recovery times.
</details>
