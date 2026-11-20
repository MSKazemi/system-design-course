# 16 — Cost as a requirement (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/02-modern-requirements/16-cost-as-requirement.md](../course/02-modern-requirements/16-cost-as-requirement.md).
Prices are AWS us-east-1 list prices read 2026-11-19/20 or labelled assumptions.

## Slide 1 — The requirement

- Lumen API: 300M requests/month (≈ 114 req/s average, ≈ 196 at peak)
- Target: ≤ $6 per million requests, all-in
- Finance wants per-tenant cost (200 tenants) within 24 h
- Hard because the bill lags, the biggest line item is a surprise, and idle capacity is invisible

**Visual:** requirement card with three numbers; icons `ops-cost`, `ops-slo`, `arch-users`.

**Speaker notes:** Cost is a requirement like latency. It has a target, it can be measured, and it can be broken. This
chapter shows how to design for it before the invoice arrives.

## Slide 2 — Cost is quantity × rate

- Every bill line = quantity × rate, summed
- Usage lever (engineering): bytes, seconds, replicas
- Rate lever (finance/procurement): commitments, spot, contracts
- Architecture decides the *shape* of the quantities

**Visual:** equation Σ qᵢ × rᵢ with two arrows: "engineering owns q", "finance owns r".

**Speaker notes:** The FinOps Framework separates Usage Optimization and Rate Optimization. In a design review you
mostly argue about quantities. The rate conversation comes later, and it only works if quantities are stable.

## Slide 3 — Cost SLO: SLI, objective, budget

- SLI = unit cost: USD per 1M requests, per tenant, per 1k tokens
- Objective comes from price and margin, not last month's bill
- Budget + burn rate, like an error budget
- Total spend rising can be good news; unit cost tells you which

**Visual:** SLO gauge reading "$5.15 / 1M (target $6)"; icons `ops-slo`, `ops-dashboard`, `ops-alert`.

**Speaker notes:** "Cost SLO" is this course's framing. The FinOps Foundation's Unit Economics capability gives the
metric examples: cost per token, per tenant, per transaction, per API call.

## Slide 4 — Five billing shapes

- Capacity-priced: per hour, used or not (VMs, GPUs)
- Consumption-priced: per request or GB-second (functions, gateways, tokens)
- Tiered: cheaper per unit at volume (egress, storage)
- Committed: 1–3 years, discounted, owed regardless
- Interruptible: spot, deep discount, revocable (2-minute notice on AWS)

**Visual:** five small cost-vs-traffic curves: step, line, concave, flat, dashed step.

**Speaker notes:** Recognising the billing shape of each box is the core skill. "Up to 66/72/90%" discounts are
ceilings published by the provider, not typical values.

## Slide 5 — The drivers people miss

- Internet egress: $0.09/GB (first 10 TB, us-east-1)
- Cross-AZ: $0.01/GB in each direction
- NAT processing and public IPv4 ($0.005/h per address)
- Cold-tier fine print: minimum duration (30/90 days), 128 KB minimum, retrieval fees
- Idle: N+1 floors, autoscaling lag, over-sized requests, dev environments running all weekend

**Visual:** a request path drawn as a "toll road" with toll booths at internet, AZ boundary and NAT; icons
`arch-internet`, `arch-region`, `arch-network`, `arch-object-storage`.

**Speaker notes:** The numbers are AWS us-east-1 list prices from the public Price List API, read in November 2026.
Other providers price egress differently; Cloudflare R2, for example, charges no egress.

## Slide 6 — Lumen, worked: egress beats compute

- Egress: 300M × 30 KB = 9,000 GB, so $801/month
- VM compute (fixed fleet of 5 sized for peak): $736/month
- Functions: 36M GB-s + requests + gateway = $960/month ($3.20 per 1M)
- Storage 10 TB: $230; cross-AZ: $40

**Visual:** horizontal bar chart of the five line items for architecture A; egress bar highlighted with a label (not
colour alone).

**Speaker notes:** The cheapest optimisation here is a payload diet, not a new architecture. Sort the bill by driver
before optimising anything.

## Slide 7 — Three architectures, one table

- A fixed On-Demand fleet: $1,898/month, $6.33 per 1M
- B autoscaled, committed floor + spot burst: $1,546, $5.15 per 1M (only one under target)
- C serverless + API gateway: $2,031, $6.77 per 1M
- Break-even C vs B ≈ 110M requests/month (≈ 42 req/s)

**Visual:** three stacked bars (compute, front door, egress, cross-AZ, storage) plus a sweep chart with the crossover
marked; icons `arch-servers-cluster`, `pattern-autoscaling`, `arch-serverless`.

**Speaker notes:** These are outputs of lab L16 with stated assumptions. Serverless wins below the crossover because
it has no minimum fleet. Above it, its per-request premium exceeds the cost of idle headroom.

## Slide 8 — How much to commit: the waterline

- Commit the k-th instance only if demand reaches k in more than (1 − d) of hours
- d = 30%: commit only to levels reached at least 70% of the time
- Deeper discount means committing higher up the curve
- Track commitment coverage and commitment utilisation

**Visual:** a daily demand curve with a horizontal "waterline" at the 70%-of-hours level; spot fills the peaks.

**Speaker notes:** This is the newsvendor condition applied to capacity. In the lab profile, demand needs 3 instances
all day, 4 for half the day and 5 for 9 hours: commit to 3 at a 30% discount and to 4 at 60%.

## Slide 9 — Kubernetes: requests, usage, idle

- OpenCost rule: a workload is charged max(request, usage)
- Idle = capacity bought but not allocated to any workload
- Datadog 2024 (vendor data): 83% of container costs associated with idle (≈ 54% cluster idle, 29% workload idle)
- Fix workload idle by right-sizing; fix cluster idle with bin packing and consolidation

**Visual:** node box split into Team X request, Team Y request and an "idle" area; icons `devops-kubernetes`,
`arch-servers-cluster`.

**Speaker notes:** OpenCost is a CNCF Incubating project with a public allocation specification. The Datadog figure
comes from its own customer telemetry. Present it as indicative.

## Slide 10 — Which "cost"? Billed vs Effective

- FOCUS 1.4 columns: List, Contracted, Billed, Effective Cost
- Billed: an upfront commitment appears as a spike in the month it is bought
- Effective: the commitment is amortised across the usage it covers
- Engineering unit-cost SLIs use Effective Cost

**Visual:** two line charts for the same year, one spiky (billed) and one smooth (effective); icon `ops-metrics`.

**Speaker notes:** FOCUS is the FinOps Foundation's open billing schema, now covering AI, SaaS and data centre
vendors as well as cloud. Mixing cost columns is how engineering and finance end up arguing about different numbers.

## Slide 11 — Cost per token

- USD per 1k tokens = GPU $/h ÷ (tokens/s × 3.6 × utilisation)
- g6.xlarge $0.8048/h; with an *assumed* 1,500 tok/s: $0.00015 at 100%, $0.0015 at 10%
- Cost per token is inversely proportional to utilisation
- Self-host vs API: break-even utilisation, then add people and redundancy

**Visual:** hyperbola of cost per 1k tokens vs utilisation with the API price as a horizontal line; icons `domain-ai`,
`arch-cpu`.

**Speaker notes:** The throughput number is hypothetical. Measure it in lab L22 for your model and engine. The formula
is what you bring to an interview.

## Slide 12 — Cost incidents

- Runaway autoscaling: guard with maxReplicas, quotas and burn-rate alerts
- Retry storms multiply billed requests: use retry budgets and breakers
- Slow dependency on functions: wall-clock billing
- Chatty cross-AZ calls, egress surprises, logging explosions, idle GPUs, unbounded agent loops

**Visual:** incident board with six cards, each with an SLI; icons `ops-incident`, `pattern-retry`, `ops-logs`.

**Speaker notes:** Cost failures deserve runbooks and postmortems. Prime Video's 2023 redesign is a public example
where per-operation orchestration charges and S3 traffic for intermediate data dominated the bill. They reported a
90% cost reduction after consolidating the components.

## Slide 13 — Interview angle

- CLARIFY a cost target; QUANTIFY egress and compute-seconds per request
- SKETCH with a billing shape on each box; DEEPEN on the dominant line item
- STRESS: cost at 10×, runaway scaling; WRAP: unit cost + biggest unpulled lever
- Red flags: "serverless is always cheaper", committing to peak, no unit cost

**Visual:** the six-step framework strip with a dollar sign on QUANTIFY and STRESS.

**Speaker notes:** The cost question usually comes as a follow-up ("now halve it"). Answer from the largest line item
and distinguish usage levers from rate levers.

## Slide 14 — Lab L16

- Python standard library only; €0; runs offline
- Three architectures, sweep, sensitivity, tenant allocation, cost per token
- Every input labelled list-price (with source and date) or assumption
- Runtime-tested 2026-11-20, 18 unit tests passing

**Visual:** terminal screenshot spec of `python3 cost_model.py --sweep` output; icon `language-python`.

**Speaker notes:** Change one assumption at a time and watch which architecture moves. The goal is intuition for
which quantity each line item is billed on.
