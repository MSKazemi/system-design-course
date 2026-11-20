# 17 — Energy- & carbon-aware design (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement

- Customers ask for "carbon per 1,000 assistant answers, with method"
- Target: −40% in 12 months, TTFT SLO (2 s) untouched
- Hard because: nobody measures it; grid, building and hardware are outside the software team
- Treat it like latency or cost: an SLI, a target, a budget

**Visual:** Lumen chat bubble → GPU rack → power plant; question mark on "g CO₂e per answer". Icons: `domain-chat`, `arch-servers-cluster`, `ops-slo`.

**Speaker notes:** Energy and carbon arrive as a procurement requirement, not a moral one. The aim of this chapter is to make it measurable and then actionable.

## Slide 2 — Why now

- IEA: data centres about 415 TWh in 2024 (about 1.5% of global electricity), about 945 TWh by 2030 (Base Case)
- EU: about 68 TWh (2024) → about 114 TWh (2030), per IEA figures cited by the Commission
- EU law: ≥ 500 kW data centres report KPIs annually (by 15 May); rating scheme adopted 21 September 2026, A to G classes for PUE and WUE, under scrutiny
- SCI published as ISO/IEC 21031:2024; SCI for AI ratified December 2025

**Visual:** Bar pair 2024 vs 2030 (global TWh), labelled "IEA Base Case". Icons: `arch-datacenter`, `ops-metrics`.

**Speaker notes:** Three shifts: AI-driven demand growth, mandatory reporting, and a standard method. All numbers are from the IEA and the Commission, as cited in the lesson.

## Slide 3 — The chain from work to carbon

- Work → IT energy (software's lever)
- × PUE → facility energy (building's lever)
- × grid intensity → operational carbon (location and time lever)
- + embodied ÷ lifetime → total (hardware lever)
- ÷ functional unit → SCI

**Visual:** Left-to-right chain diagram from the lesson's first Mermaid figure. Icons: `arch-cpu`, `arch-datacenter`, `arch-region`.

**Speaker notes:** Each arrow has a different owner. A strong design names all four and says which ones this team controls.

## Slide 4 — PUE: useful, and limited

- PUE = total facility energy / IT energy (The Green Grid); ideal 1.0
- Uptime 2025 survey: respondents' average 1.54, as quoted by Google (flat six years); Google fleet 1.09 (2025)
- "Not a data center productivity metric"; idle servers can have great PUE
- Also reported in the EU: WUE, ERF, REF

**Visual:** Two stacked bars for a 1 MW IT load: overhead 540 kW (PUE 1.54) vs 90 kW (PUE 1.09). Icons: `arch-datacenter`, `ops-dashboard`.

**Speaker notes:** Use PUE as a multiplier in estimates. Never make it the software team's KPI.

## Slide 5 — Carbon intensity: place, time, method

- Place: EU 213 vs US 361 gCO₂/kWh (Ember, 2024 averages)
- Time: German grid −25.9% on weekends vs workdays (2020 data, Wiesner et al.)
- Average (Electricity Maps) vs marginal (WattTime MOER, 5-minute data)
- Reporting usually uses average; SCI allows either if stated; decisions may use either; never mix

**Visual:** Two-row table, average vs marginal, "question it answers". Icons: `arch-region`, `ops-clock`.

**Speaker notes:** The average vs marginal choice is a genuine methodological debate and each provider argues its own side. Write the choice down.

## Slide 6 — Embodied carbon and idle hardware

- Manufacturing emits before the first request (Gupta et al., HPCA 2021): manufacturing share of iPhone life-cycle emissions 49% (3GS) → 86% (iPhone 11)
- Amortise over lifetime ÷ work done
- A GPU at 20% utilisation carries 5× the embodied carbon per request of one at 100%
- Clean grid → embodied dominates

**Visual:** Pie that flips from "operational-heavy" (300 g grid) to "embodied-heavy" (50 g grid). Icons: `arch-servers-cluster`, `ops-warning`.

**Speaker notes:** This is the most overlooked term in interviews. It is also why utilisation is a carbon lever, not just a cost lever.

## Slide 7 — SCI in one line

- SCI = ((E × I) + M) per R
- A rate, not a total; R = functional unit (per 1,000 answers)
- Offsets and market-based measures do not reduce SCI
- SCI for AI: provider and consumer scores; tokens, inferences, FLOPs

**Visual:** The formula with each symbol pointing to its owner. Icons: `ops-slo`, `ops-metrics`.

**Speaker notes:** SCI has the right shape for an SLO. "Buy offsets" is a red-flag answer because it cannot move this number.

## Slide 8 — Worked example: Lumen

- 10 M answers/day, peak 2×, 10 answers/s per 8-GPU node → 24 nodes, 48% utilisation
- 0.27 Wh per answer (PUE 1.2), 81.5 g operational + 32.9 g embodied
- SCI ≈ 114 gCO₂e per 1,000 answers (all inputs are assumptions)

**Visual:** Step ladder: nodes → kW → kWh/day → Wh/answer → g/1k. Icons: `arch-servers-cluster`, `ops-throughput`.

**Speaker notes:** Every input is labelled as an assumption in the lesson. The method is the point; replace the inputs with measurements.

## Slide 9 — Pulling the levers

- Batching/prefix caching (15/s per node): 16 nodes, SCI 76 (−33%)
- + power cap (−20% active power): SCI 71 (−38%)
- Instead: 50 g/kWh grid: SCI 31 (−73%), embodied now 71% of the total
- PUE 1.5 instead of 1.2: SCI 135 (+18%)

**Visual:** Waterfall chart from 114 to 76 to 71, with a side bar for 31. Icons: `pattern-batching`, `pattern-geo-distribution`.

**Speaker notes:** The software lever cuts energy and embodied carbon at the same time. The grid lever is large but constrained by latency and residency.

## Slide 10 — Shifting: real but bounded

- Temporal: flexible batch work to clean hours or weekends (>5% across all four regions for next-day slack; >20% for weekends in most regions)
- Google: day-ahead forecasts → hourly cluster capacity limits
- Spatial: limited by latency, data gravity, capacity, residency
- 123-region study: practical gains far from ideal; shrink as grids decarbonise

**Visual:** 24-hour carbon-intensity curve with a batch job block sliding into the trough. Icons: `ops-calendar`, `arch-queue`, `arch-cron`.

**Speaker notes:** Shifting is cheap for batch work and dangerous for interactive work. Sukprasert et al. give the sober bound.

## Slide 11 — Measuring it

- CPU/DRAM: RAPL via powercap `energy_uj` (root-only since CVE-2020-8694)
- GPU: DCGM energy counter; nvidia-smi samples only about 25% of runtime on A100/H100
- Kubernetes: Kepler (CNCF Sandbox), active power per pod, idle not yet attributed
- Node truth: BMC/PDU; reconcile monthly
- SLI: Wh and gCO₂e per 1,000 answers on the service dashboard

**Visual:** Pipeline diagram RAPL/DCGM/BMC → Prometheus → join → SLI. Icons: `observability-prometheus`, `observability-grafana`, `devops-kubernetes`.

**Speaker notes:** Every source has an accuracy limit, and the lesson lists them. Reconciliation against a meter is what makes a published number defensible.

## Slide 12 — HPC lesson: telemetry at plant scale

- ExaMon (Univ. Bologna, deployed at CINECA): MQTT plugins → Cassandra/KairosDB → online analytics
- M100 ExaData: about 2.5 years of Marconi100 telemetry, 49.9 TB, public
- Out-of-band power sampling down to 20 µs (DiG)
- Transfer: bus between sensors and storage, shared time axis, scheduler as actuator

**Visual:** Sensor fan-in to an MQTT broker, then a store, then analytics and the scheduler. Icons: `messaging-mqtt`, `nosql-cassandra`, `arch-servers-cluster`.

**Speaker notes:** HPC centres solved facility-plus-job energy telemetry years ago. Case study C13 applies the same pattern to a GPU cluster.

## Slide 13 — Interview angle

- CLARIFY: functional unit, boundary, signal, flexible work, residency
- QUANTIFY: peak → nodes → power → × PUE → × intensity → + embodied → ÷ volume
- DEEPEN: efficiency and utilisation first; shift batch; spatial only where allowed
- STRESS: forecast error, herding, starvation, rebound; WRAP: SCI as an SLO
- Red flags: offsets, PUE as an app metric, ignoring idle or embodied

**Visual:** The six-step framework strip with energy annotations. Icons: `ops-check`, `ops-slo`.

**Speaker notes:** Interviewers reward stated assumptions and named trade-offs, not precise-sounding numbers.
