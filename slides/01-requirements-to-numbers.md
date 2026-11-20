# 01 — Requirements to numbers (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Lesson: [course/00-orientation/01-requirements-to-numbers.md](../course/00-orientation/01-requirements-to-numbers.md)

## Slide 1 — Will one server survive launch day?

- 500,000 daily active users expected
- "Fast and reliable" is not a requirement
- At 95% utilisation, M/M/1 latency is 20× the unloaded latency

**Visual:** One server icon facing a crowd; the number "20×" large; icons `arch-server`, `arch-users`.

**Speaker notes:** Set up the chapter's question and the surprise from queueing. The rest of the deck turns the
adjectives into numbers.

## Slide 2 — Adjective → requirement

- Metric, threshold, population, window
- "Fast" → 99% of `GET /answer` from EU users < 300 ms over 30 days
- "Reliable" → 99.9% non-5xx over a rolling 30 days

**Visual:** Two-column table: adjective on the left, requirement sentence on the right; icon `ops-slo`.

**Speaker notes:** Every non-functional requirement converts the same way. If one of the four parts is missing,
the requirement can't be tested.

## Slide 3 — SLI, SLO, SLA, error budget

- SLI: a ratio of good events to valid events
- SLO: target for the SLI (99.9% over 30 days)
- SLA: a contract, set looser than the SLO
- Error budget = 1 − SLO: 43.2 min/month at 99.9%

**Visual:** A budget bar draining over a month; icons `ops-slo`, `ops-metrics`.

**Speaker notes:** Definitions from the Google SRE book. The budget aligns product and reliability: spend it on
change, and slow down when it runs out.

## Slide 4 — Alert on burn rate

- Burn rate = actual error rate ÷ allowed error rate
- 14.4× for 1 h = 2% of a 30-day budget gone
- Page when both the 1 h and 5 min windows burn at 14.4×

**Visual:** Line chart of budget remaining, with a steep 14.4× segment highlighted and labelled; icons `ops-alert`, `observability-pagerduty`.

**Speaker notes:** From the SRE Workbook. Budget-remaining alerts fire too late. Burn-rate alerts fire while there
is still budget to save.

## Slide 5 — Availability multiplies

- Three services in series at 99.9% each → ≈ 99.7%
- Two independent replicas at 99% → 99.99%
- "Independent" is doing all the work

**Visual:** Three boxes in a chain with 0.999 each, then a parallel pair; icons `arch-microservice`, `pattern-replication`.

**Speaker notes:** Shared configuration pushes, power and bugs make failures correlated, and the formula then
flatters you.

## Slide 6 — Estimation in five steps

- Users → actions → requests (one assumption per arrow)
- Average, then peak (busiest hour, busiest minute)
- Convert to cores, concurrency, storage, bandwidth
- Add headroom: utilisation, failures, growth

**Visual:** A funnel from "500k users" to "1,000 req/s" with each step labelled; icon `ops-throughput`.

**Speaker notes:** A day is about 10⁵ seconds. One million requests a day is about 12 per second. Systems fail at
the peak, so always apply a peak factor.

## Slide 7 — Launch day, worked

- 15 M requests/day → 174/s average → ≈ 1,000/s design peak
- 20 ms CPU → 20 cores busy → ≈ 34 cores at 60%
- L = λW = 1,000 × 0.08 = 80 in flight
- Capacity: one big box could do it. Availability: it can't

**Visual:** The worked table from the lesson, with the final answer "3 servers across zones"; icons `arch-server`, `arch-region`.

**Speaker notes:** Separate capacity from availability. That distinction is the strongest part of the answer.

## Slide 8 — Latency numbers drift

- Dean 2009: memory 100 ns, disk seek 10 ms, CA → NL → CA 150 ms
- NVMe today: ≈ 45 µs random read at QD1; 7,450 MB/s sequential (990 PRO datasheet)
- Fibre ≈ 204,000 km/s; London ↔ New York ≈ 70 ms (Nov 2026)
- Bandwidth improves; latency mostly doesn't

**Visual:** Log-scale ladder of latencies from ns to 100s of ms; icons `arch-memory`, `arch-storage-disk`, `arch-network`.

**Speaker notes:** Date every number you quote. Learn the ratios, and measure the values your design depends on.

## Slide 9 — Little's law: L = λW

- Holds for any stable system: no distribution assumptions
- Size pools: 1,000/s × 8 ms = 8 busy connections
- Detect trouble: λ flat but L climbing means W is climbing

**Visual:** A pipe with items inside; λ in, W the length, L the count; icon `arch-queue`.

**Speaker notes:** The proof is the area under N(t) counted two ways. Lab L01 measures both sides.

## Slide 10 — The hockey stick

- M/M/1: W = S / (1 − ρ), p99 ≈ 4.6 W
- 50% → 2S; 80% → 5S; 90% → 10S; 95% → 20S
- Target 50–70% for latency-sensitive services
- Kingman: queueing = utilisation × variability

**Visual:** Latency vs utilisation curve with labelled points at 50/80/90/95%; icons `ops-latency`, `pattern-backpressure`.

**Speaker notes:** The last 30% of capacity can be used only by accepting much worse latency. Bursty arrivals make
it worse, regular ones better.

## Slide 11 — The tail at scale

- Fan-out of 100, leaf p99 = 1 s → 63% of requests take > 1 s
- Leaves need p99.99 for the whole request to see p99
- Hedging: 1,800 ms → 74 ms at p99.9 for 2% more requests (Dean & Barroso)

**Visual:** One request fanning out to 100 leaves, one of them red and also marked with a clock symbol (not colour alone); icons `pattern-fan-out`, `ops-latency`.

**Speaker notes:** 0.99¹⁰⁰ ≈ 0.37. Explain hedging and its condition: only for idempotent reads, and capped.

## Slide 12 — Tokens, not requests

- 4 M generations/day → 167/s at peak
- 2,000 input + 350 output tokens → 334k prefill and 58k decode tokens/s
- 12.7 s per stream → ≈ 2,100 concurrent streams (Little's law)
- GPUs = decode tokens/s ÷ *measured* tokens/s per GPU at the SLO

**Visual:** Users → requests → tokens → streams pipeline; icons `domain-ai`, `domain-chat`, `pattern-batching`.

**Speaker notes:** Rule of thumb: a token is about ¾ of an English word, but count with the real tokenizer. The
per-GPU number must be measured (SYSDESIGN-21, SYSDESIGN-22).

## Slide 13 — Lab L01: find the knee

- One worker, 10 ms mean service: capacity 100 req/s
- Predict with `predict.py`, measure with k6 (open model)
- Watch p99 bend near ρ = 1; check L = λW on the server

**Visual:** Predicted vs measured p99 curves on one chart; icons `devops-docker`, `observability-grafana`, `observability-prometheus`.

**Speaker notes:** The lab README records the actual numbers observed, with versions and date.
