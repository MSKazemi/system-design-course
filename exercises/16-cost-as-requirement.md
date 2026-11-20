# 16 — Exercises

Exercises for [SYSDESIGN-16 Cost as a requirement](../course/02-modern-requirements/16-cost-as-requirement.md).
Prices are the AWS us-east-1 list prices quoted in the lesson (read 2026-11-19/20). Treat them as inputs, not
truths: the method matters more than the dollar figure.

---

### 1. [Core] Unit cost vs total spend

Lumen's monthly bill rose from $40k to $52k while monthly requests went from 4.0B to 6.5B. The CFO calls it a
regression. Is it? Compute the unit cost before and after, and say what you would put on the dashboard instead of
the total.

<details><summary>Answer</summary>

Before: $40,000 / 4,000M requests = **$10.00 per million**. After: $52,000 / 6,500M = **$8.00 per million**. Unit cost
fell 20%, so the system became *more* efficient while total spend grew 30% because traffic grew 62.5%. The dashboard
should show the **unit-cost SLI** (USD per million requests, using amortised/effective cost) against its objective,
with total spend as context and a forecast of total spend from traffic × unit cost. A regression is a rise in unit
cost at constant quality, or total spend growing faster than the value metric.

An acceptable alternative is a business unit such as cost per active tenant or per answered question, if requests are
not the value metric. Requests are a proxy; for an LLM product, cost per resolved conversation may be better.
</details>

---

### 2. [Core] Billing shapes

Classify each component's billing shape (capacity, consumption, tiered, committed, interruptible) and say whether its
cost is fixed or variable with traffic: (a) three On-Demand VMs kept for N+1; (b) internet egress; (c) a function
billed per GB-second; (d) a 1-year Savings Plan; (e) burst workers on spot; (f) S3 Standard storage.

<details><summary>Answer</summary>

- (a) **Capacity-priced, fixed**: you pay 3 × 730 h whether or not traffic arrives. It is the availability floor.
- (b) **Tiered, variable**: linear within a band, cheaper per GB at higher volume ($0.09 → $0.085 → $0.07 → $0.05 per GB
  in us-east-1).
- (c) **Consumption-priced, variable**: linear in requests × memory × wall-clock duration.
- (d) **Committed, fixed**: a promised spend for the term, owed even if unused.
- (e) **Interruptible capacity, semi-variable**: it tracks the burst you choose to run, at a discount, with
  interruption risk.
- (f) **Tiered, effectively fixed in the short term**: it scales with data volume, not request rate.

The point is that architecture choice changes the *mix* of fixed and variable cost. That mix decides who wins at low
and at high volume.
</details>

---

### 3. [Core] Back-of-envelope: egress first

An API serves 500M requests/month with an average response of 45 KB to the internet. Using the us-east-1 tiers
(100 GB free, then $0.09/GB for the first 10 TB, $0.085/GB for the next 40 TB, $0.07/GB for the next 100 TB), estimate
monthly egress cost. Then estimate the saving from gzip at a 4:1 ratio on 80% of the bytes.

<details><summary>Answer</summary>

Volume: 500×10⁶ × 45 KB = 22,500 GB (decimal units, as in the lesson). Free: 100 GB, leaving 22,400 GB. Tier 1 is
10 TB = 10,240 GB at $0.09 = $921.60. The remaining 12,160 GB is at $0.085 = $1,033.60. **Total ≈ $1,955/month.**

With gzip, 80% of bytes shrink 4×: new volume = 22,500 × (0.2 + 0.8/4) = 22,500 × 0.4 = 9,000 GB. After the free
100 GB, 8,900 GB is all in tier 1 at $0.09 = **$801/month**. Saving ≈ **$1,150/month (≈ 59%)**, for the CPU cost of
compression, which is usually small relative to this. Payload diet is often the cheapest optimisation available.
</details>

---

### 4. [Deep] Serverless vs VMs break-even

A function is configured with 512 MB and runs 80 ms wall-clock per request. Prices: $0.0000166667 per GB-s, $0.20 per
million requests, and an HTTP API gateway at $1.00 per million. The VM alternative is a floor of 3 × m7i.xlarge
($0.2016/h) plus an ALB at about $20/month at low volume; one VM handles 80 req/s at target utilisation. Ignoring
egress and storage (identical in both), find the monthly volume where the two cost the same, assuming the VM floor is
enough capacity up to that point.

<details><summary>Answer</summary>

Serverless per million: compute = 10⁶ × 0.5 GB × 0.08 s × $0.0000166667 = $0.667, plus $0.20 requests and $1.00
gateway, which gives **$1.867 per million**, linear.

VM floor: 3 × 730 × $0.2016 = $441.50, plus $20 for the ALB, so **≈ $461.50/month fixed**.

Break-even: 461.5 / 1.867 ≈ **247M requests/month** (≈ 94 req/s average).

Check the capacity assumption: 3 VMs × 80 req/s = 240 req/s. With a peak-to-average ratio below about 2.5 the floor
suffices, so the assumption holds. Above about 250M requests/month VMs are cheaper, and the gap widens because
additional VMs cost about $0.70 per million at full utilisation.

Note that halving wall-clock time (a faster dependency) halves the compute part and moves break-even upwards, while
it changes nothing for VMs.
</details>

---

### 5. [Deep] How much to commit

Hourly demand over a typical day (nested intervals) needs at least 8 instances for all 24 h, at least 12 for 16 of
those hours, at least 18 for 6 of them, and 22 for 2 of them. On-Demand costs $0.20 per instance-hour. Compare committing to 8, 12 and 18 instances at (a) a 30%
discount and (b) a 55% discount. Use the waterline rule and then verify with the cost formula for one day.

<details><summary>Answer</summary>

**Waterline rule:** commit level *k* if P(demand ≥ k) > 1 − d.

- Levels 1–8 are reached 24/24 h (100%).
- Levels 9–12 are reached 16/24 (66.7%).
- Levels 13–18 are reached 6/24 (25%).
- Levels 19–22 are reached 2/24 (8.3%).

(a) d = 0.30, threshold 70%: 66.7% < 70%, so commit to **8**. (b) d = 0.55, threshold 45%: 66.7% > 45%, so commit to
**12**. 25% < 45%, so do not go to 18.

**Daily on-demand instance-hours above each level:**

- Above 8: 4×16 + 6×6 + 4×2 = 64 + 36 + 8 = 108. (Demand profile: 12 for 16 h, 18 for 6 of those h, 22 for 2 of
  those h. Excess over 8: 16 h × 4 = 64; 6 h × 6 more = 36; 2 h × 4 more = 8.)
- Above 12: 6×6 + 4×2 = 44.
- Above 18: 4×2 = 8.

| Commit | Committed cost (24 h) | On-Demand above | Total, d=0.30 | Total, d=0.55 |
|---|---|---|---|---|
| 8 | 8×24×0.2×(1−d) | 108 × 0.2 = 21.6 | 26.88 + 21.6 = **48.48** | 17.28 + 21.6 = **38.88** |
| 12 | 12×24×0.2×(1−d) | 44 × 0.2 = 8.8 | 40.32 + 8.8 = 49.12 | 25.92 + 8.8 = **34.72** |
| 18 | 18×24×0.2×(1−d) | 8 × 0.2 = 1.6 | 60.48 + 1.6 = 62.08 | 38.88 + 1.6 = 40.48 |

At 30% the best choice is 8 ($48.48). At 55% it is 12 ($34.72). The formula agrees with the rule. Committing to peak
(18 or more) is the worst choice in both cases. Forecast uncertainty argues for committing slightly *below* the
computed waterline.
</details>

---

### 6. [Deep] Kubernetes allocation and idle

A node costs $0.40/h and has 8 vCPU (assume cost is all CPU for simplicity). Team X's pods request 4 vCPU and use 1.5.
Team Y's pods request 1 vCPU and use 2 (they burst above request). Using the OpenCost rule *max(request, usage)*,
allocate one hour of node cost, compute idle cost, and name the remedy for each kind of waste.

<details><summary>Answer</summary>

Price per vCPU-hour = $0.40 / 8 = $0.05.

- X is charged max(4, 1.5) = 4 vCPU = **$0.20**.
- Y is charged max(1, 2) = 2 vCPU = **$0.10**.
- Allocated: 6 vCPU = $0.30. **Idle** = 8 − 6 = 2 vCPU = **$0.10** (25% of the node).

Waste analysis:

- X shows **workload idle**: it requested 4 vCPU and used 1.5. Remedy: right-size requests using measured usage
  (VPA recommendations, load tests).
- The 2 unallocated vCPU are **cluster idle**. Remedy: bin packing and consolidation, for example Karpenter's
  `WhenEmptyOrUnderutilized`, or smaller or fewer nodes.
- Y bursting above request is a *risk*, not waste. It is under-requested, which can cause CPU contention for
  neighbours. Raise its request towards real use.

Idle cost can then be shown separately or distributed to teams by a stated policy.
</details>

---

### 7. [Core] Which cost column?

Lumen buys a 3-year, all-upfront commitment for $36,000 in March. Explain what a unit-cost dashboard shows in March and
April if it uses FOCUS *Billed Cost* versus *Effective Cost*, and which one engineering should use.

<details><summary>Answer</summary>

**Billed Cost** shows the $36,000 purchase in March (a huge spike) and then near-zero compute charges for the covered
usage in April and later. March unit cost looks terrible and April looks unrealistically good.

**Effective Cost** amortises the prepayment over the term: about $1,000/month (36,000 / 36) is recognised on the covered
usage lines, and the purchase line carries zero effective cost. Unit cost stays smooth and reflects the real
economics of each month's usage.

Engineering unit-cost SLIs should use **Effective Cost**. Finance reconciles invoices with Billed Cost. Pricing
analysis may also look at List or Contracted Cost to separate engineering efficiency from discount effects.
</details>

---

### 8. [Interview] Self-host or API?

"Our product will generate 2 billion output-equivalent tokens per month. Should we self-host an open model or call an
API?" Outline your answer, including the formula you would use and the questions you would ask first.

<details><summary>Answer</summary>

**CLARIFY:** quality bar (can an open model meet it?), latency SLO (TTFT/TPOT), traffic shape (steady or spiky, peak
vs average), data-residency constraints, team capacity to operate GPUs.

**QUANTIFY:** 2×10⁹ tokens/month ≈ 760 tokens/s on average. Peak might be 3×, so about 2,300 tokens/s.

**Formula:** self-hosted cost per 1k tokens = GPU $/h / (tokens/s × 3.6 × utilisation). With the lesson's
*hypothetical* 1,500 tokens/s per $0.8048/h GPU, you need 2 GPUs for peak. The average utilisation of 2 GPUs is
760 / 3,000 ≈ 25%, giving ≈ $0.0006 per 1k tokens. The monthly cost is 2 × 730 × $0.8048 ≈ $1,175 plus
engineering time, versus 2×10⁶ × the API price per 1k.

**Decision logic:** self-hosting wins when utilisation is high and steady and operations capacity exists. The API wins
for spiky or small volumes, or when it reaches the quality bar more cheaply. A hybrid is common: route easy, high-volume
requests to a self-hosted small model and hard ones to an API (LLM gateway, SYSDESIGN-26).

**Must say:** measure throughput yourself (it depends on model, batch, context length and serving engine), account for
headroom and redundancy (N+1 GPUs), and set per-tenant token budgets.

**Red flags:** quoting peak GPU throughput as average, ignoring idle hours, or ignoring the people cost.
</details>

---

### 9. [Interview] "Cut the bill in half"

You are told: "Your design works, now cut its cost by 50% without hurting the SLO." Using Lumen's baseline from the
lesson (architecture A: compute $736, ALB $91, egress $801, cross-AZ $40, storage $230), give a prioritised plan with
estimated savings.

<details><summary>Answer</summary>

Start from the largest line items, and separate usage levers from rate levers. The baseline total is ≈ $1,898.

1. **Egress ($801), usage lever:** compress and trim payloads. Halving the bytes per response saves ≈ $400. Add a CDN
   for cacheable responses only if its per-GB price beats origin egress.
2. **Compute ($736), rate and usage levers:** autoscale instead of running the peak fleet all day, commit to the floor
   (the waterline), and run burst capacity on spot. The lab's architecture B cuts compute to ≈ $384 (−$352). Arm
   instances may cut a further ~19% at list price if benchmarks hold.
3. **Storage ($230), usage lever:** a lifecycle rule moving cold data to Standard-IA or Glacier IR saves $84–$152.
   Check retrieval patterns and minimum durations first.
4. **Cross-AZ ($40):** zone-aware routing; small at this volume.

Steps 1 and 2 together save ≈ $750, or 40%. Adding step 3 brings the saving to about 45–48%, and further payload work
or caching reaches 50%.

**Guard the SLO:** keep the CPU target that protects latency, keep N+1 on On-Demand, and verify with a load test.

**Strong candidates** state the unit cost before and after (≈ $6.33 → ≈ $3.2 per million) and say which lever they
would *not* pull. For example: "I would not reduce the number of AZs."
</details>

---

### 10. [Lab] Read the sensitivity table

Run `python3 cost_model.py --sensitivity` in `labs/16-cost-as-requirement/`. Explain why the wall-clock change moves
only architecture C, why the CPU change moves only B, and why the response-size change moves B more than C in
percentage terms.

<details><summary>Answer</summary>

- **Wall-clock (120 → 300 ms):** functions bill GB-seconds of *wall-clock*, so C's compute rises proportionally (the lab
  shows +44% total). VMs bill instance-hours. Waiting on I/O does not consume CPU, so the VM count in B is unchanged
  (+0%).
- **CPU (50 → 25 ms):** halving CPU per request doubles VM capacity and reduces the burst fleet in B (−5%). C's bill
  depends on wall-clock, not CPU, so it does not move. A real function would also get faster, but the model separates
  the two on purpose.
- **Response size (30 → 300 KB):** egress rises 10× for every architecture. In B, the ALB's LCU charge also scales with
  processed bytes, and B's baseline total is smaller, so the *percentage* increase is larger (+450% vs +311%). In
  absolute dollars, the increase is similar.

The lesson: know which quantity each line item is billed on. Optimisations that help one architecture can be
invisible to another.
</details>

---

### 11. [Deep] Design a cost guardrail

Lumen's agents feature lets tenants run multi-step LLM tasks. Design guardrails so that one runaway task or one tenant
cannot exhaust the monthly AI budget, and define the SLIs that would page someone.

<details><summary>Answer</summary>

**Layers:**

1. **Per-task budget:** a hard cap on tokens, tool calls and wall-clock per task. Abort with a clear error when it is
   reached, and log it.
2. **Per-tenant budget:** a monthly token or cost allowance enforced at the LLM gateway with a token-bucket rate limit
   (rate in tokens/min plus a monthly quota). Soft alert at 80% and hard stop or degrade (smaller model) at 100%.
3. **Global:** a daily spend burn-rate alert. If projected month-end spend exceeds the budget by more than X% with
   more than Y days left, page. A kill switch per feature flag.
4. **Platform:** `maxReplicas` and GPU quotas, so the serving fleet cannot scale without bound.

**SLIs:** cost per task (p50/p95), tokens per task, share of tasks hitting the cap, spend per tenant per day, and
burn rate vs budget. Use the gateway's real-time token counters for paging, because billing data lags by hours.
Reconcile with FOCUS-normalised billing data daily.

**Acceptable variations:** tenant-tier-specific budgets, and pre-paid credits instead of quotas.
</details>
