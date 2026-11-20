# 17 — Exercises

Lesson: [course/02-modern-requirements/17-energy-carbon-aware.md](../course/02-modern-requirements/17-energy-carbon-aware.md).
All numeric inputs below are labelled assumptions unless a reference number from the lesson is given.

## 1. PUE is not productivity [Core]

Facility A reports PUE 1.10; its servers average 15% CPU utilisation. Facility B reports PUE 1.40 at 70%
utilisation. Both run the same service. Which one is more energy-efficient *per request*, and what should
you measure to be sure?

<details><summary>Answer</summary>

PUE only measures facility overhead: total facility energy divided by IT energy. The Green Grid explicitly
says it is not a productivity metric (lesson ref [3]). Facility A's IT equipment is mostly idle. Because
servers are least efficient at low utilisation and draw a large share of peak power when idle (Barroso &
Hölzle [17]), A's IT energy per request is likely much higher. That can outweigh the 1.10 vs 1.40
multiplier.

Illustration (assumed linear power model, idle 50% of peak, same peak power P): power per unit of work is
proportional to (0.5 + 0.5·u)/u. At u = 0.15 that is 3.83 P per unit of throughput; at u = 0.70 it is
1.21 P. Multiplying by PUE gives 4.2 (A) vs 1.7 (B). B is about 2.5× more efficient per request in this
model.

Measure **facility energy per request** (or SCI per functional unit), not PUE. Acceptable alternatives:
IT energy per request × PUE, if both are metered.
</details>

## 2. Back-of-envelope SCI [Core]

A search API serves 50 M requests/day on 40 CPU servers. Each draws 150 W idle and 400 W at full load
(linear), with average utilisation 35%. PUE 1.3, grid 250 gCO₂e/kWh. Embodied carbon is 1.5 tCO₂e per
server over 5 years (assumption). Compute energy per request and the SCI per 1,000 requests.

<details><summary>Answer</summary>

- Power per server: 150 + 250 × 0.35 = 237.5 W. Fleet: 40 × 237.5 = 9.5 kW.
- Facility energy per day: 9.5 × 24 × 1.3 = 296.4 kWh. Per request: 296.4 kWh / 50 M = **5.93 mWh ≈
  21.3 J**.
- Operational: 296.4 × 0.25 = 74.1 kg/day, so 74.1 kg / 50,000 (thousands of requests) = **1.48 g per
  1,000**.
- Embodied: 40 × 1,500 kg / (5 × 365) = 32.9 kg/day, so **0.66 g per 1,000**.
- **SCI ≈ 2.14 gCO₂e per 1,000 requests.**

Note that embodied is about 30% of the total even on a 250 g grid. On a 50 g grid it would exceed
operational (0.30 vs 0.66 g).
</details>

## 3. Average or marginal? [Deep]

Your team wants one carbon-intensity feed for two uses: (a) the quarterly SCI report to customers, and
(b) a scheduler that picks the hour to run a nightly batch. Which signal for each, and why must they not be
mixed?

<details><summary>Answer</summary>

(a) **Average (attributional)** intensity, for example from Electricity Maps. Footprint methods and SCI use
the emissions of the consumed mix, and average intensity is more verifiable (lesson [10]).

(b) Either can be defended. **Marginal** (for example WattTime MOER, 5-minute data with a 72-hour forecast
[11]) estimates which generator responds to your load change. **Average** is argued by Electricity Maps to
be a better long-term proxy [10]. The choice is a methodological position, so record it.

They must not be mixed in a single reported number. They answer different questions, can move in opposite
directions, and the result would be neither reproducible nor comparable. A defensible setup is average for
reporting, and either signal for decisions, but labelled.
</details>

## 4. When does embodied carbon dominate? [Deep]

Using the lesson's Lumen example after the batching change (16 nodes; 0.181 Wh/answer; embodied
21.9 g per 1,000 answers), find the grid intensity at which operational and embodied carbon are equal.
Which levers matter most below that intensity?

<details><summary>Answer</summary>

Operational per 1,000 answers = 0.181 Wh × 1,000 × I = 181 Wh × I. Setting 0.181 kWh × I = 21.9 g gives
**I ≈ 121 gCO₂e/kWh**.

Below about 120 g/kWh, embodied dominates. The levers that matter most are those that reduce hardware per
unit of work: higher utilisation (batching, bin-packing, sharing accelerators), right-sizing capacity
(fewer peak-provisioned nodes, for example by queueing or shedding non-urgent traffic at peak), and
extending hardware lifetime. Moving to an even cleaner grid then yields little (Gupta et al. [16]).
</details>

## 5. Temporal shifting with deadlines [Core]

A fine-tuning job needs 12 h of a 6 kW node and must finish within 48 h. The forecast for the next 48 h has
a 12-hour window averaging 120 gCO₂e/kWh and a "now" window averaging 380. Estimate the saving. What
could go wrong, and how do you guard against it?

<details><summary>Answer</summary>

Energy: 6 kW × 12 h = 72 kWh (IT; multiply by PUE if reporting facility energy). Now: 72 × 0.38 =
27.4 kg. Clean window: 72 × 0.12 = 8.6 kg. Saving **18.7 kg, about 68%**.

Risks:
- **Forecast error.** Re-plan as forecasts update.
- **Starvation.** The window slips, and the job misses its deadline. Use a deadline-aware policy that
  starts no later than deadline − runtime − margin.
- **Preemption cost.** If the job is split, checkpointing overhead adds energy.
- **Herding.** Every job targets the same window and capacity runs out. Randomise and cap.
- **Diminishing returns** on already-clean grids (Sukprasert et al. [14]).
</details>

## 6. Spatial shifting under constraints [Interview]

An interviewer suggests serving Lumen's EU chat traffic from a region with a much cleaner grid on another
continent "to cut carbon 70%". Respond.

<details><summary>Answer</summary>

Push back with constraints, then offer a better plan:

1. **Latency.** Interactive answers have a 2 s TTFT SLO. An intercontinental round trip plus queueing eats
   the budget and adds a failure domain (SYSDESIGN-15).
2. **Residency.** EU personal data in prompts and conversation history may be restricted to allowed
   jurisdictions (SYSDESIGN-19).
3. **Capacity and herding.** The clean region may lack GPUs, and everyone wants it.
4. **Data gravity.** Retrieval indexes and caches would have to move or be replicated, at an egress and
   energy cost.
5. **Limited real-world gains.** Practical spatial gains are well below ideal (Sukprasert et al. [14]).

Better plan: keep interactive traffic local and pull the efficiency and utilisation levers (−33% to −38% in
the lesson's example). Move **latency-tolerant, residency-free** work, such as training on licensed public
data, embedding refreshes of non-personal corpora or evaluation runs, to clean regions and clean hours.
</details>

## 7. Building the measurement pipeline [Deep]

Design the telemetry pipeline that produces "Wh per 1,000 answers" for a Kubernetes GPU inference fleet.
List the sources, their known accuracy limits, and how you validate the result.

<details><summary>Answer</summary>

Sources:
- **GPU:** `DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION` (counter) via dcgm-exporter; use `rate()`. Known
  limit: nvidia-smi/NVML power sampling covers only about 25% of runtime on A100/H100 per Yang et al.
  [37], so calibrate.
- **CPU/DRAM:** RAPL via powercap `energy_uj` (root-only since CVE-2020-8694 [25]). Handle wrap-around
  using `max_energy_range_uj` [24]. It does not cover PSU, fans, NIC or disks.
- **Per-pod attribution:** Kepler. Active power only (as of 2026-11), idle not attributed, GPU experimental
  [27].
- **Whole node:** BMC via IPMI/Redfish, or rack PDU, as the ground truth for the node.
- **Facility:** PUE from the provider or facility meters.
- **Work:** request counter `lumen_answers_total`.
- **Carbon:** hourly intensity time series.

Compute Σ node energy × PUE / answers, aggregated hourly.

Validation: monthly reconciliation of summed node energy × PUE against facility or invoice energy.
Synthetic-load calibration of DCGM against PDU readings. Check that per-pod attribution sums to node
energy, and track the residual "unattributed idle" explicitly.
</details>

## 8. EU reporting as a requirement [Core]

A colocation provider runs a 600 kW (installed IT) data centre in an EU member state. What must it do
under Directive (EU) 2023/1791 and Delegated Regulation (EU) 2024/1364, and what changed in September 2026?
(Not legal advice.)

<details><summary>Answer</summary>

- **Art. 12 of Directive (EU) 2023/1791**: member states require owners and operators of data centres with
  at least **500 kW** installed IT power demand to make the information in Annex VII publicly available,
  from 15 May 2024 and every year thereafter [7]. The Commission maintains a European database, public at
  aggregated level.
- **Delegated Regulation (EU) 2024/1364** sets the KPIs (for example installed IT power, total and IT energy
  measured per EN 50600-4-2, water input) and the deadlines: **by 15 September 2024, then by 15 May 2025 and
  every year thereafter** [8]. From these, indicators such as PUE, WUE, ERF and REF are derived.
- **Art. 26(6)**: data centres with total rated energy input above **1 MW** must use waste heat or other
  waste-heat recovery unless not technically or economically feasible [7]. This provider (600 kW IT) may or
  may not cross 1 MW of total rated input; check.
- **September 2026**: on 21 September the Commission adopted a delegated regulation creating a common
  **rating scheme** for data centres above 500 kW; its annexes grade PUE and WUE on an A to G scale [38].
  It is subject to two-month Parliament/Council scrutiny before entering into force, with first labels
  expected in 2027, and a consultation on minimum performance standards closes 14 December 2026 [9].

System implication: metering must exist at the boundaries the KPIs require, and the data pipeline must
produce auditable annual figures.
</details>

## 9. Training vs inference [Interview]

"Training our model cost 500 MWh. Inference is cheap. Should we focus on training efficiency?" Use the
lesson's sources to answer.

<details><summary>Answer</summary>

It depends on volume. Luccioni, Jernite and Strubell estimated that for BLOOMz models about 200–590 million
inferences match the training energy [18]. A service handling 10 M answers/day crosses 590 M in about
2 months. After that, inference dominates lifetime energy and keeps growing. For a popular product,
optimise inference first (batching, caching, quantisation, right-sized models). Do training efficiency and
temporal/spatial shifting of training as well, since training is the most shiftable load. The BLOOMz
range is only an order-of-magnitude illustration, because the break-even is training energy divided by
energy per answer: with the lesson's 0.27 Wh/answer, 500 MWh equals about 1.85 billion answers, about
185 days at 10 M/day. A strong answer also notes that the model choice itself (task-specific vs general-purpose) can change inference energy by
orders of magnitude [18].
</details>

## 10. Power capping trade-off [Deep]

Samsi et al. report that capping A100s from 250 W to 175 W for LLaMA-65B inference cut energy by about 23%
and increased inference time by about 6.7% [22]. Under what conditions would you adopt a cap in Lumen's
serving fleet, and how would you roll it out?

<details><summary>Answer</summary>

Adopt it when the fleet is **throughput-bound with SLO headroom**, for example when TTFT p99 is well below
2 s, or for batch and offline inference. Also adopt it when the site is power-constrained, since capping
lets more GPUs fit in the same power envelope. Avoid it for latency-critical paths without headroom: a
6.7% slowdown in decode may push TPOT/TTFT over the SLO at peak.

Roll out like any performance change: canary a subset of nodes, then compare energy per answer
(DCGM/BMC), TTFT/TPOT percentiles and throughput at fixed load. Automate rollback on SLO burn. Tune per
model and per GPU type, because the paper notes a static cap may not suit every task. Re-check capacity
planning, since lower per-node throughput may need more nodes, which raises embodied carbon. The net effect
must be computed, not assumed.
</details>
