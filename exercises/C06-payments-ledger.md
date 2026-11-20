# C06 — Exercises

Lesson: [course/04-case-studies/C06-payments-ledger.md](../course/04-case-studies/C06-payments-ledger.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Volumes and the hot account

3 M payments/day, peak 8× average, 8 postings per payment, 250 B per posting, 7-year retention. Compute peak
postings/s, storage over the retention period, and writes/s on the platform-fee account at peak.

<details><summary>Answer</summary>

Average payments ≈ 34.7 /s → peak ≈ 278 /s. Postings peak ≈ 278 × 8 ≈ **2,200 /s**. Storage = 3 M × 8 × 250 B = 6 GB/day →
≈ 2.2 TB/year → ≈ 15 TB over 7 years (before replicas). The fee account receives one posting per payment → ≈ 278
writes/s at peak on one balance row — enough to cause lock contention if the balance is updated synchronously. Sub-
accounts (e.g. 16) cut it to ≈ 17 /s each.
</details>

## 2. [Core] Why integers?

Show what goes wrong if amounts are stored as binary floating point, using €0.10 + €0.20. What representation do you
use instead, and how do you handle currencies with different minor units?

<details><summary>Answer</summary>

In IEEE 754 double precision, 0.1 + 0.2 = 0.30000000000000004; repeated across millions of postings, sums drift and
zero-sum checks fail. Store **integers in minor units** (cents) plus an ISO currency code; keep a per-currency exponent
(most currencies 2, some 0 or 3). Never add amounts of different currencies; FX is an explicit journal entry with a
recorded rate.
</details>

## 3. [Deep] The idempotency race

Two identical `POST /v1/payments` requests with the same `Idempotency-Key` arrive 5 ms apart on different API servers.
Walk through what each does with (a) a naive "check then insert" and (b) an `in_progress` row with a lease. What
happens if the first server crashes after calling the PSP?

<details><summary>Answer</summary>

(a) Both check, both find nothing, both call the PSP → a possible double charge (unless the PSP key saves you). (b) The
first inserts `(key, in_progress, lease_expiry)` with a unique constraint; the second's insert fails and it returns
`409 Conflict` (retry later). If the first crashes after the PSP call, the key stays `in_progress` until the lease
expires; a retry then proceeds and re-calls the PSP **with the same PSP idempotency key** stored in the attempt row
(written before the call), so the PSP returns the original result. Safety requires both layers: our key for concurrency,
the PSP key for the external effect.
</details>

## 4. [Core] Build a journal entry

A buyer pays €80.00 for an order; the platform keeps 12 %; the PSP charges €1.20 at settlement. Write the capture and
settlement journal entries with signed minor units and verify each sums to zero.

<details><summary>Answer</summary>

Capture: `psp_receivable +8,000`; `seller_payable −7,040`; `platform_fee_revenue −960` → 8,000 − 7,040 − 960 = 0.
Settlement (the PSP pays the gross minus its fee): `bank_cash +7,880`;
`psp_fees_expense +120`; `psp_receivable −8,000` → 7,880 + 120 − 8,000 = 0. (A hold/authorization entry before capture
is optional depending on how you model holds. In the lesson's model the +8,000 sits on `buyer_hold` until capture and
`psp_receivable` was debited, as pending, at authorization; this answer collapses E1 + E2 into one capture entry.) The check "each entry sums to zero per currency" belongs in the write
path.
</details>

## 5. [Deep] Timeout = unknown

The relay calls the PSP to authorize; after 10 s it times out. The buyer's app shows "Payment failed, try again" and
the buyer taps Pay again, creating a new payment. Explain the double charge and redesign the flow.

<details><summary>Answer</summary>

The first authorization may have succeeded at the PSP; the retry is a *new* payment with a new idempotency key, so
nothing de-duplicates it → two authorizations. Redesign: the timeout moves the payment to `Unknown`, the API returns
`202 processing` with the payment ID, the app polls or waits for a push; a resolver queries the PSP for the attempt's
status (or waits for the webhook) and moves the payment to `Authorized` or `Failed`. Only a definite failure allows a
new attempt. Also make the server's PSP timeout shorter than the client's so the server can always respond.
</details>

## 6. [Core] Out-of-order webhooks

A hypothetical PSP (event names are illustrative; Stripe, for example, has no `charge.authorized` event) sends
`charge.captured` and then `charge.authorized`, and later re-sends `charge.captured`. How does your
receiver handle each event?

<details><summary>Answer</summary>

Dedupe by provider event ID first: the re-sent `captured` is dropped. For ordering, apply events as state-machine
transitions with optimistic concurrency: `captured` arriving while we are in `Authorizing` is a valid jump only if
the state machine has an `Authorizing → Captured` transition (the lesson's diagram does not — you would add it, implying
authorization), otherwise hold the event until we query the PSP; the
late `authorized` is then a no-op because the payment is already past that state. Never apply events in arrival order
as raw updates.
</details>

## 7. [Deep] Strong or eventual?

For each read, choose strong or eventual consistency and justify: (a) checking a wallet balance before a withdrawal;
(b) the buyer's payment history page; (c) looking up an existing authorization hold before creating another; (d) the
finance dashboard of daily revenue.

<details><summary>Answer</summary>

(a) **Strong** — a stale read allows overspending. (b) **Eventual** — a few seconds of delay only affects display.
(c) **Strong** — Uber's LedgerStore uses strongly consistent indexes for authorization holds because a stale read could
cause a duplicate charge. (d) **Eventual** — computed from the posting stream. Rule: strong where a stale read moves
money, eventual where it only shows money.
</details>

## 8. [Interview] Reconciliation breaks

The PSP report lists a €45.00 capture that is not in your ledger, and your ledger has a €30.00 refund the PSP report
does not show. Classify each break, list likely causes, and say what the system does automatically.

<details><summary>Answer</summary>

€45 capture missing in ledger: *in report, not in ledger* — likely a lost or delayed webhook, or a capture made outside
our flow (dashboard). Automatic action: query the PSP for the payment, apply the transition through the state machine
(which writes the journal entry), re-match. €30 refund missing at PSP: *in ledger, not in report* — likely a timing
difference (refund after the report cut-off) or a refund that failed at the PSP while we recorded success. Automatic:
wait one cycle for timing; if still missing, query status; if failed, write a reversing entry and alert. Never edit
past entries; corrections are new entries with references to the break.
</details>

## 9. [Lab] Retries with jitter against a flaky provider

In [labs/11-reliability-engineering](../labs/11-reliability-engineering/), run the retry experiments without and with
jitter and with the circuit breaker. Treat the backend as a PSP. Report what you observe about load on the backend
during an outage and recovery, and explain why idempotency keys are a prerequisite for any of these retry policies.

<details><summary>Answer</summary>

Report your observed request rates: retries without jitter tend to arrive in synchronized waves; jitter spreads them;
the breaker stops calls during the outage and probes during recovery. Idempotency keys are the prerequisite because
every retry of a non-idempotent payment call risks a second charge — a retry policy without them trades availability
for correctness, which is unacceptable in payments.
</details>

## 10. [Interview] 24/7 instant payments

Your current design reconciles and runs batch jobs nightly, with a weekly maintenance window. The business must
support SEPA Instant sending by the regulatory deadline. List the design changes and the regulatory facts that drive
them.

<details><summary>Answer</summary>

Facts (Regulation (EU) 2024/886): instant transfers available 24 hours a day on any calendar day; funds available to
the payee within 10 s; verification of payee before the payer authorizes; charges no higher than standard transfers;
euro-area PSPs had to send by 9 October 2025 (non-euro member states: 9 July 2027). Changes: remove the maintenance
window (online migrations, rolling upgrades); move fraud scoring and payee verification onto the synchronous path
within a seconds-level budget; continuous reconciliation per transfer; real-time liquidity positions from ledger
balances; on-call and SLOs that cover nights and weekends. Also watch the EU payments package (PSR/PSD3), politically
agreed in November 2025 and close to formal adoption as of late 2026, for fraud-related obligations.
</details>
