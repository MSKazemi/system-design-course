# C13 — Telemetry & observability platform for a GPU/HPC cluster (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- 10,240 GPUs (1,280 nodes × 8; assumption), Slurm + Kubernetes
- GPU power, temperature and utilization at 1 s; the rest at 10–30 s
- Catch failing GPUs before they kill multi-day jobs
- Energy per job, user and project

**Visual:** Rack row with GPU nodes, a CDU and a heat-map overlay. Icons: arch-servers-cluster, arch-datacenter, ops-metrics.
**Speaker notes:** Here the infrastructure is the product. The hard parts are cardinality and attribution, not
raw bytes.

## Slide 2 — QUANTIFY
- ~1.43 M active series; ~503,000 samples/s; ~43.5 B samples/day
- Gorilla: 16 B → 1.37 B per point (12×); Prometheus: 1–2 B per sample
- Raw ≈ 60 GB/day; 14 days ≈ 0.8–1.2 TB
- 1-minute rollups ≈ 5 TB/year

**Visual:** Table of sources × series × interval, with a total row.
**Speaker notes:** Use Prometheus's formula: retention seconds × samples per second × bytes per sample. Series
counts are assumptions; bytes per sample are sourced.

## Slide 3 — The cardinality trap
- `job_id` as a label: 20,000 jobs/day × 16 GPUs × 40 metrics
- ≈ 12.8 M new series per day, ~9× the whole cluster's steady state
- Index, head memory and query fan-out scale with series, not samples
- Labels are stable hardware identity only

**Visual:** Series-count line flat at 1.4 M vs a second line climbing 12.8 M/day.
**Speaker notes:** This is the single most important design decision in the case.

## Slide 4 — SKETCH
- Node agent (dcgm-exporter, node_exporter, HCA counters) → Kafka
- BMC + facility (MQTT) → Kafka
- Kafka → TSDB hot tier → object storage; Kafka → stream processor
- Scheduler → job table; alerts → drain/cordon

**Visual:** SKETCH flowchart from the lesson. Icons: messaging-kafka, messaging-mqtt, observability-prometheus, observability-grafana, storage-aws-s3.
**Speaker notes:** dcgm-exporter defaults to a 30 s interval and has an optional Kubernetes pod-mapping mode.
1 s is a choice with a cost to measure.

## Slide 5 — Join jobs at query time
- Job table: job → (node, GPU, start, end) from Slurm or Kubernetes
- Query: allocation → selector → time range
- Stream processor writes per-job, per-minute rows to ClickHouse
- MIG and time-slicing: attribute by instance or share

**Visual:** Sequence: Slurm → job table; samples → processor → per-job rows.
**Speaker notes:** Users get "my job's power" without the TSDB ever seeing a job label.

## Slide 6 — Choosing the store (as of 2026-11)
- Prometheus + Thanos / Mimir / VictoriaMetrics for operations and alerting
- ClickHouse for per-job analytics and energy (TTL rollups)
- TimescaleDB when Postgres joins matter at moderate scale
- ExaMon precedent: MQTT plugins → Cassandra + KairosDB

**Visual:** Comparison table with "wins when" column. Icons: nosql-clickhouse, nosql-timescaledb, nosql-cassandra, observability-prometheus.
**Speaker notes:** Split stores by access pattern. Operators need recent selector queries; accounting needs joins
over long ranges.

## Slide 7 — Downsampling does not save space
- Thanos: 5 m after 40 h, 1 h after 10 days
- Its docs: downsampling "doesn't save you any space", and can add ~3×
- Savings come from shorter raw retention
- Keep max in rollups: thermal events are spikes

**Visual:** Three stacked blocks (raw, 5 m, 1 h) growing total height, then raw truncated.
**Speaker notes:** A favorite interview correction. Downsampling buys query speed; retention buys space.

## Slide 8 — Why failure detection pays
- Llama 3: 419 unexpected interruptions in 54 days; ~78% hardware; GPU 58.7%
- Delta: H100 memory MTBE 3.2× lower than A100; ~5% overprovisioning projected
- Titan: GPU reliability tied to heat dissipation and cooling details
- Telemetry feeds drain, checkpoint and restart

**Visual:** Three evidence cards with the source year.
**Speaker notes:** Delta is a preprint; say so. These numbers justify the platform's budget.

## Slide 9 — Layer 1: Xid rules
- 48 double-bit ECC → reset; with 63/64 drain first
- 79 fallen off the bus → drain, restart bare metal
- 94 contained vs 95 uncontained memory error
- 13/31/43 usually application faults → tag the job, not the node

**Visual:** Xid table with action icons. Icons: ops-error, ops-alert, arch-server.
**Speaker notes:** Meanings and actions come from NVIDIA's Xid catalog. Keep rules in version control with tests.

## Slide 10 — Layers 2 and 3: statistics and ML
- Thermal residual: expected temperature from power and coolant inlet
- Peer comparison inside a synchronous job finds stragglers
- Rack-level correlation points to the cooling loop
- ML (autoencoders) ranks nodes; it does not drain them

**Visual:** Scatter of temperature vs power with one GPU drifting above the band.
**Speaker notes:** ExaMon-based research evaluated deep-learning anomaly detection on compute nodes, and M100
ExaData includes Nagios-derived anomaly labels at 15-minute aggregation.

## Slide 11 — Energy per job
- Prefer GPU energy counters: end − start per GPU
- Otherwise integrate power, and report coverage
- Add shared node power by GPU share (Slurm IPMI/RAPL plugins)
- Example: 211 kWh GPU + 96 kWh node = 307 kWh IT; ×1.2 PUE ≈ 369 kWh

**Visual:** Stacked bar: GPU / node / facility overhead. Icons: ops-cost, ops-metrics.
**Speaker notes:** All example numbers are assumptions except the 700 W H100 TDP, which comes from the Llama 3
paper.

## Slide 12 — STRESS
- Metrics storm: series limits, edge drop rules, series-growth alert
- TSDB outage: agents buffer, Kafka replays, alerting reads Kafka
- Clock skew breaks job attribution: PTP/NTP plus offset metric
- ×10: recording rules, federation, shorter raw retention

**Visual:** Four mini incident cards.
**Speaker notes:** Rack-level thermal events must collapse 320 GPU pages into one incident.

## Slide 13 — WRAP by level
- Junior: exporters + Prometheus + Grafana; temperature alerts
- Senior: sourced math, no job labels, retention tiers, Xid drain automation
- Staff: split stores, physics-informed anomalies, energy attribution with coverage, overhead in GPU-equivalents
- Red flags: job labels, alerting via the long-term store, ML-only drains

**Visual:** Three-level ladder. CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Close with SLOs: completeness ≥ 99.9%, fault-to-drain ≤ 60 s, and meta-monitoring.
