# C13 — Exercises

Case: [course/04-case-studies/C13-gpu-cluster-telemetry.md](../course/04-case-studies/C13-gpu-cluster-telemetry.md)

## 1. [Core] Series and samples

A cluster has 512 nodes with 4 GPUs each. You collect 30 GPU metrics at 1 s and 400 node metrics at 15 s.
Compute the active series, samples/s and raw storage per day at 1.37 bytes/sample.

<details><summary>Answer</summary>

- GPU: 512 × 4 × 30 = 61,440 series at 1 s → 61,440 samples/s.
- Node: 512 × 400 = 204,800 series at 15 s → ~13,650 samples/s.
- Total ≈ 266,000 series, ≈ 75,100 samples/s.
- Per day: 75,100 × 86,400 ≈ 6.49 B samples × 1.37 B ≈ **8.9 GB/day** (Gorilla's average [Pelkonen et al.]). At
  Prometheus's 1–2 B/sample, 6.5–13 GB/day.

Note that the GPU metrics are under a quarter of the series but over 80% of the samples, because of the 1 s
interval. Resolution, not series count, drives storage here.
</details>

## 2. [Core] Why not `job_id` as a label?

Your team wants `job_id` on every DCGM series "so dashboards are easy". With 15,000 jobs/day averaging 8 GPUs and
40 metrics per GPU, how many new series per day is that? What do you do instead?

<details><summary>Answer</summary>

15,000 × 8 × 40 = **4.8 M new series per day**, each short-lived. TSDB memory for the head block, index size and
query fan-out scale with series count, so this churn degrades ingestion and queries even if the samples fit
easily.

Instead: keep labels to stable hardware identity (node, GPU index, UUID), store job allocations
(job → node/GPU/time interval) in a job table fed by Slurm or Kubernetes, and join at query time. For common per-job
aggregates, have a stream processor write per-job, per-minute rows to a columnar store keyed by `job_id`.
</details>

## 3. [Deep] Downsampling and space

A colleague enables Thanos downsampling to "cut storage by 90%" and keeps all resolutions forever. What actually
happens, and what should they change?

<details><summary>Answer</summary>

Storage grows. The Thanos compactor *adds* 5 m blocks (for raw data older than 40 h) and 1 h blocks (for 5 m data
older than 10 days), and the documentation states that downsampling doesn't save any space, and with all
resolutions retained can increase storage by about 3×.

To save space, set per-resolution retention, for example `--retention.resolution-raw=14d`,
`--retention.resolution-5m=400d`, and `--retention.resolution-1h=0s` (which means no expiry). Downsampling's real
benefit is fast long-range queries. Also check that rollups keep max (not only average), or thermal spikes vanish
from history.
</details>

## 4. [Core] Read the Xid

For each event, choose an automated action: (a) Xid 13 on one GPU during one job; (b) Xid 79; (c) Xid 48 followed
by Xid 64; (d) Xid 94; (e) Xid 95.

<details><summary>Answer</summary>

Per NVIDIA's Xid catalog:
(a) **Tag the job, no node action.** Graphics engine exceptions are usually application faults. Alert only if the
same GPU shows it across different jobs.
(b) **Drain the node**, restart bare metal, check PCIe logs. The GPU has fallen off the bus.
(c) **Drain the node, then reset the GPU.** A double-bit ECC error with a remapping failure. Run field
diagnostics and follow the RMA flow if thresholds are exceeded.
(d) **Contained memory error:** only the affected application needs restarting. Reset the GPU when convenient,
for example after the current job.
(e) **Uncontained memory error:** reset the GPU before any application restarts.
</details>

## 5. [Deep] A thermal anomaly detector

Design a detector that catches a GPU whose cooling is degrading, without paging on every hot, busy GPU.

<details><summary>Answer</summary>

Use a **residual**, not an absolute threshold. Fit expected temperature as a function of power draw and coolant
inlet temperature (per GPU model, and possibly per rack position). A linear model is a reasonable start. Compute
residual = actual − expected, smooth it with an EWMA over minutes, and alert when the residual exceeds k standard
deviations of the fleet's residual distribution for a sustained period.

Then correlate: if many GPUs in one rack or cooling loop drift together, raise one cooling-loop incident instead
of per-GPU pages. Feed confirmed cases back as labels. Survival analysis on Titan linked GPU reliability to heat
dissipation and cooling details [Ostrouchov et al.], which is why this signal is worth building.
</details>

## 6. [Core] Energy for one job

A job ran on 32 GPUs (4 nodes) from 08:00 to 20:00. The GPU energy counters show a total increase of 210 kWh
across its GPUs. Each node's non-GPU baseline averages 1.8 kW. The facility PUE for the period was 1.25. Compute
IT and facility energy. Why prefer counters over integrating 30 s power samples?

<details><summary>Answer</summary>

- GPU: 210 kWh (counter deltas, summed).
- Node baseline: 4 nodes × 1.8 kW × 12 h = 86.4 kWh (the job holds whole nodes, so 100% attribution).
- IT total: 296.4 kWh; facility: 296.4 × 1.25 ≈ **370.5 kWh**.

Counters (`DCGM_FI_DEV_GPU_ENERGY_JOULES_TOTAL`, energy since driver reload) integrate in hardware, so they are
immune to sampling gaps and miss no bursts. 30 s samples can miss short power spikes and dips (checkpoint I/O,
communication stalls). If you must integrate, report coverage (received vs expected samples) next to the
number, and handle counter resets.
</details>

## 7. [Interview] Choose the stores

You must support (a) on-call dashboards and alerts on the last 24 h, (b) monthly energy reports per project
over 13 months, and (c) researchers exporting 2 years of raw node data. Pick storage for each and justify.

<details><summary>Answer</summary>

(a) A Prometheus-compatible TSDB (Prometheus + Thanos, Mimir or VictoriaMetrics): label-selector queries, PromQL
alerting and recording rules, with recent data in memory and on fast disk.
(b) A columnar store (ClickHouse) holding per-job, per-minute rows written by the stream processor and joined
with the job table. SQL group-bys over months are its strength, and TTL rules can roll up old data.
(c) Object storage with Parquet exports partitioned by month/plugin/metric. That is the format choice the M100
ExaData dataset made for public distribution. Cheap, and readable by any analytics engine.

One TSDB for all three either overloads the operational store with analytical scans, or makes alerting depend on
an analytics system.
</details>

## 8. [Deep] Surviving a TSDB outage

The TSDB cluster is down for 40 minutes. What keeps working, what is lost, and what must the design include?

<details><summary>Answer</summary>

Kept working (if designed): **hard-fault alerting**, because the stream processor reads Kafka directly; local
agent buffering; Kafka retention, which holds all samples.

Lost temporarily: dashboards and PromQL-based alerts.

Required: Kafka retention well beyond the expected outage; TSDB ingestion that accepts out-of-order or backfilled
samples for the replay; consumer lag dashboards; meta-monitoring outside the TSDB (a small independent Prometheus)
so that "no data" alerts fire; and replay rate limits so recovery does not overload the TSDB.
</details>

## 9. [Interview] Scale ×10

The cluster grows to 102,400 GPUs. What breaks first in your design, and what do you change?

<details><summary>Answer</summary>

Roughly 5 M samples/s and 14 M series. First pressure points: TSDB ingesters' memory (series count), cluster-wide
queries that fan out over millions of series, and raw storage (~600 GB/day).

Changes: shard ingestion by node hash and scale ingesters horizontally; precompute rack and cluster aggregates
with recording rules so dashboards never read raw series; federate per cluster or site, with a global query layer
and local alerting; shorten raw retention (for example 7 days) or keep 1 s only for a small fast set; enforce
per-source series limits. Hardware events grow linearly, so drain/RMA automation must handle the routine cases
without humans.
</details>

## 10. [Core] Agent overhead budget

Each node agent uses 0.8% of one node's CPU at 1 s DCGM collection. What does that cost across 1,280 nodes, and
how could you reduce it?

<details><summary>Answer</summary>

0.8% × 1,280 ≈ **10.2 nodes' worth** of CPU, which on 8-GPU nodes is roughly 80 GPUs' worth of servers whose host
CPU is partly consumed. GPUs still run, but CPU-bound data loading or communication threads can slow down, and
the overhead is a real cost.

Reductions: collect only the fast set (power, temperature, utilization, clocks) at 1 s and everything else at
10–30 s; drop unused series at the agent; batch and compress before sending; and measure overhead per exporter
version, because defaults change (dcgm-exporter's documented default interval is 30 s).
</details>
