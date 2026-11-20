# C12 — Real-time fraud detection (and recommendations) (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- Score every card payment inline: approve, challenge or decline
- 15,000 payments/s peak; p99 ≤ 100 ms contract, ≤ 50 ms internal (assumptions)
- Adversary adapts; labels arrive weeks later
- Variant: the same platform serving recommendations

**Visual:** Card terminal → processor → fraud service → network, with a stopwatch over the fraud hop. Icons: payments-visa, payments-mastercard, ops-latency.
**Speaker notes:** Lumen Pay is fictional. State the latency budget as an assumption in an interview; the
card network and issuer own the end-to-end time.

## Slide 2 — CLARIFY
- Inline vs after the fact: inline
- Error costs are asymmetric and depend on amount
- Labels: few analyst feedbacks fast, most labels via disputes or default-after-wait
- Out of scope: ledger (C06), network protocols, KYC

**Visual:** Two-column table: false decline vs missed fraud costs.
**Speaker notes:** Asking about error costs early is what turns this from a classifier question into a system
design question.

## Slide 3 — QUANTIFY
- ~260 M payments/day; 6 MB/s events average, 30 MB/s peak
- Online store ~1.1 TB RAM with 3 replicas
- 60,000 feature writes/s average, 300,000/s peak: writes size the store
- Decision log ~780 GB/day uncompressed; it is the training set

**Visual:** Four stat tiles with the numbers.
**Speaker notes:** Analyst capacity (~12,000 reviews/day assumed) sets the review threshold, so measure alert
precision at k, as Dal Pozzolo et al. recommend.

## Slide 4 — SKETCH
- Decision service orchestrates features, model and rules
- Kafka → Flink → online feature store
- Decisions + labels → lakehouse → training → registry → model server
- Every box answers "why is this here?"

**Visual:** SKETCH flowchart from the lesson. Icons: messaging-kafka, data-flink, cache-redis, arch-server, arch-data-warehouse.
**Speaker notes:** The decision service owns the latency budget, the fallbacks and the log. It doesn't do heavy
compute.

## Slide 5 — Velocity features done right
- Event time + watermarks; allowed lateness for stragglers
- Per-minute buckets summed for sliding behavior
- Pre-aggregate in Flink; flush every few hundred ms
- Backfill with the same job in bounded mode

**Visual:** Timeline of per-minute buckets with a late event landing inside allowed lateness.
**Speaker notes:** Flink drops late elements by default once the watermark passes the window end. Allowed
lateness keeps state alive.

## Slide 6 — The latency budget
- Ingress 3, enrichment 2, features 10, model 5, rules 2 → 22 ms
- Shadow scoring and logging off the critical path
- Tail amplification: 5 parallel calls, so 1 − 0.99⁵ ≈ 4.9% exceed a per-call p99
- Batch, hedge and co-locate feature groups

**Visual:** Stacked horizontal bar of the budget against a 50 ms line.
**Speaker notes:** All budget numbers are assumptions to validate with load tests. The tail math is the
interview gem.

## Slide 7 — Fallbacks decided in advance
- One feature group down: defaults + missing indicator
- Feature store down: rules-only, challenge above an amount
- Model down: conservative rules profile
- Decision service down: gateway static policy

**Visual:** Decision tree of dependency failures to fallbacks. Icons: pattern-circuit-breaker, pattern-timeout.
**Speaker notes:** The fallback rate is an SLI. A fallback decision counts as available but must be visible.

## Slide 8 — Rules + ML
- Hard rules first (sanctions, block lists)
- Model score → policy thresholds by amount and segment
- Analyst rules patch new attacks within hours
- Investigators edit rules; the model is retrained (Dal Pozzolo et al.)

**Visual:** Rules → model → policy → rules pipeline from the lesson.
**Speaker notes:** Stripe Radar documents rules that block, review, allow or request 3-D Secure, and warns that
allow rules override everything else.

## Slide 9 — Shadow → canary → champion
- Shadow: score 100%, act on 0%
- Canary: act on 1–5%, bucketed so that retries match
- Promote by alias; keep the old champion warm
- Radar's traffic allocation at 0% is shadow mode for rules

**Visual:** Three-step ramp with traffic percentages. Icons: ops-deploy, pattern-failover.
**Speaker notes:** Shadow scores are computed after the response from the same feature snapshot, so they cost
no latency.

## Slide 10 — Labels arrive late
- Feedbacks: few, recent, biased toward likely fraud
- Delayed samples: most labels, after several days (e.g., one month)
- Declined payments never get labels: selection bias
- Exploration slice: challenge instead of decline, capped by amount

**Visual:** Timeline: payment at day 0, analyst feedback at hours, dispute at weeks, default-genuine later.
**Speaker notes:** Dal Pozzolo et al. train separate classifiers on feedbacks and on delayed samples. Evaluate
only on matured weeks.

## Slide 11 — Explain and audit
- Log the features, rules, versions and score for every decision
- Reason codes from SHAP, computed asynchronously
- GDPR Art. 22: human intervention and contestation safeguards
- AI Act Annex III excludes fraud detection from the credit-scoring high-risk point

**Visual:** Decision-log row expanding into reason codes. Icons: ops-logs, domain-document.
**Speaker notes:** Not legal advice. Design the review and contest workflow regardless.

## Slide 12 — Variant: recommendations
- Same skeleton: streams, feature store, decision log, shadow/canary
- Adds two-tower retrieval + ANN index + ranking
- Labels in seconds, but popularity-bias feedback loops
- One platform, two products

**Visual:** Side-by-side table, fraud vs recsys.
**Speaker notes:** The interesting difference is the feedback loop. Fraud loses labels on declines;
recommenders lose labels on unshown items.

## Slide 13 — WRAP by level
- Junior: pipeline, precomputed features, right metrics
- Senior: point-in-time training, watermarks, budget + fallbacks, shadow/canary
- Staff: alert budget as objective, bias from feedback and blocking, ×10 log sampling, legal boundaries
- Red flags: range scans on the hot path, nightly retrain on immature labels

**Visual:** Three-level ladder. CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Close with SLOs and the business metrics (fraud loss in basis points, false-decline rate).
