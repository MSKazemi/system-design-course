# C06 — Payments & ledger (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C06-payments-ledger.md](../course/04-case-studies/C06-payments-ledger.md)

## Slide 1 — The requirement

- 10 M payments/day: cards + instant bank transfers
- Never charge twice; every cent in a double-entry ledger
- Reconcile daily with providers and banks
- Instant transfers in seconds, 24/7

**Visual:** A checkout button, a ledger book, and a clock showing 3 a.m. Sunday.
Icons: `domain-payment`, `payments-stripe`, `ops-clock`, `pattern-transaction`.

**Speaker notes:** "Exactly once" must be built from parts that only promise at least once or at most once — and some
provider outcomes are simply unknown.

## Slide 2 — The numbers

- ≈ 1,200 payments/s and ≈ 12,000 postings/s at peak
- ≈ 7.3 TB/year of postings; ≈ 73 TB over 10 years
- ≈ 30 M webhooks/day, duplicates expected
- One fee account takes a posting per payment (hot row)

**Visual:** Modest throughput bars; one red-hot account row.
Icons: `ops-throughput`, `arch-database`, `ops-warning`.

**Speaker notes:** Labelled assumptions. Throughput is ordinary; correctness under failure is the job.

## Slide 3 — Sketch

- API + idempotency store → payment state machine
- Payments DB + outbox → relay → PSP/bank adapter
- Webhook receiver → state machine
- Ledger service (journal + postings) → balances; reconciliation

**Visual:** The lesson's 14-node flowchart.
Icons: `pattern-api`, `pattern-idempotency`, `arch-database`, `arch-queue`, `pattern-webhook`.

**Speaker notes:** You cannot put an HTTP call to a PSP inside a database transaction — that is why the outbox exists.

## Slide 4 — Idempotency on every hop

- Client → API: `Idempotency-Key`, replay stored response
- Relay → PSP: stable key per attempt
- PSP → webhooks: dedupe on event ID
- Payment → ledger: unique external reference per entry

**Visual:** Four arrows, each with a key icon.
Icons: `pattern-idempotency`, `security-key`, `pattern-webhook`.

**Speaker notes:** A single missing hop is enough for a double charge.

## Slide 5 — Semantics worth copying

- Stripe v1: saves status + body after execution begins, replays incl. 500s
- Keys ≤ 255 chars; prunable after ≥ 24 h; parameter mismatch is an error
- Concurrent duplicates: `in_progress` + lease → 409
- Airbnb Orpheus: row lock = lease; pre-RPC / RPC / post-RPC; retryable vs not

**Visual:** Timeline of two identical requests; the second bounces with 409.
Icons: `payments-stripe`, `company-airbnb`, `security-lock`.

**Speaker notes:** Never mint a new downstream key because the last call timed out.

## Slide 6 — Double-entry in one table

- Journal entry = postings that sum to zero per currency
- Append-only; fix with correcting entries (Square Books, TigerBeetle)
- Capture: receivable +4,999 / seller payable −4,499 / fee revenue −500
- Settlement clears the receivable — reconciliation checks it

**Visual:** The worked entry table with a Σ = 0 badge per entry.
Icons: `domain-ledger`, `pattern-transaction`.

**Speaker notes:** Integers in minor units, never floats.

## Slide 7 — Balances are projections

- Truth = postings; balance = cached sum
- Synchronous balance only where a check is needed (wallets)
- Hot accounts: sub-accounts or async projection
- Holds = pending postings (two-phase)

**Visual:** One hot balance row split into 32 sub-accounts.
Icons: `pattern-sharding`, `arch-cache`.

**Speaker notes:** Updating one fee balance row at 1,200 writes/s serializes all payments.

## Slide 8 — Strong where money moves

- Uber LedgerStore: strongly consistent (2PC) indexes for authorization holds
- Eventually consistent indexes for history pages
- Rule: strong if a stale read moves money; eventual if it only shows money
- Ask of every read: does a stale answer move money?

**Visual:** Two read paths: hold lookup (lock icon) vs history page (clock icon).
Icons: `company-uber`, `pattern-consistency`.

**Speaker notes:** Consistency is chosen by consequence, not by fashion.

## Slide 9 — Exactly-once effects

- One DB transaction: state + attempt row + outbox record
- Relay calls PSP with the attempt's key; crash → same key again
- Timeout → `Unknown`, resolved by status query or webhook
- Buyer sees "processing", never "failed, try again"

**Visual:** The lesson's payment state machine with Unknown highlighted.
Icons: `pattern-saga`, `pattern-retry`, `ops-warning`.

**Speaker notes:** Most real double charges come from treating Unknown as Failed.

## Slide 10 — Reconciliation

- Three views: ledger, PSP settlement report, bank statement
- Breaks: missing either side, amount mismatch, timing
- Fix with new entries, never edits
- SLO: 99.9 % matched by T+1; no unexplained break > 3 days

**Visual:** Three columns matched by reference with a break queue below.
Icons: `ops-check`, `ops-dashboard`.

**Speaker notes:** Internal correctness is necessary, not sufficient — providers are separate systems of record.

## Slide 11 — Failures and ×10

- PSP timeouts → Unknown backlog → resolver + breaker
- PSP outage → secondary PSP for *new* attempts only
- Ledger shard down → ledger lags via outbox, never diverges
- ×10: cross-shard entries as short sagas; sub-accounts everywhere

**Visual:** Failover arrow labelled "new attempts only".
Icons: `pattern-circuit-breaker`, `pattern-failover`, `pattern-saga`.

**Speaker notes:** Never re-send an Unknown attempt to a different provider.

## Slide 12 — Modern twist: instant and regulated

- EU Reg. 2024/886: 24/7, payee funds within 10 s, verification of payee
- Euro area: receive by 9 Jan 2025, send by 9 Oct 2025
- FedNow live since July 20, 2023 (24x7x365)
- PSR/PSD3: deal 27 Nov 2025; "close to adoption" (EP, Oct 2026)

**Visual:** Calendar with deadlines; a 10-second stopwatch.
Icons: `ops-calendar`, `ops-clock`, `domain-payment`.

**Speaker notes:** No maintenance windows, fraud checks inline, continuous reconciliation, real-time liquidity.

## Slide 13 — WRAP

- Junior: idempotency key, integer amounts, states, PSP call, refunds
- Senior: every-hop idempotency, outbox, Unknown, webhook dedupe, double-entry, reconciliation
- Staff: consistency by consequence, hot accounts, cross-shard ledger, safe PSP failover, PCI scope, 24/7 regulation
- Red flags: floats, in-place balances, PSP call in a transaction, new key on retry

**Visual:** Staircase junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** End with the SLOs that matter: zero double charges, zero invariant violations, Unknowns resolved
within 15 minutes.
