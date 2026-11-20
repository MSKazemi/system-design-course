# 23 — GPU & accelerator infrastructure (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/03-ai-systems/23-gpu-infrastructure.md](../course/03-ai-systems/23-gpu-infrastructure.md).
Hardware numbers are vendor datasheet values (as of 2026-11) cited in the lesson.

## Slide 1 — The requirement

- 64 shared GPUs: inference fleet + weekly fine-tuning
- Predictable tail latency; all-or-nothing starts for 32-GPU jobs
- Detect and drain failing GPUs; report cost per token and per run
- "GPUs as big CPUs in a pod spec" fails all four

**Visual:** eight servers, half labelled "inference", half "training", a red X on one GPU. Icons: `arch-servers-cluster`, `arch-datacenter`, `ops-incident`.

**Speaker notes:** This chapter is the layer under chapters 21 and 22: hardware, interconnect, scheduling, monitoring and
failure handling.

## Slide 2 — A GPU for system designers

- Tensor cores (FLOPs), HBM (capacity + bandwidth), on-chip SRAM, links
- Datasheet tensor peaks are "with sparsity": halve them for dense work
- H100 80 GB / 3.35 TB/s; H200 141 GB / 4.8 TB/s; B200 ≈ 180 GB / 8 TB/s per GPU
- MI300X 192 GB / 5.3 TB/s; MI355X 288 GB / 8 TB/s; TPU7x 192 GiB / 7.38 TB/s

**Visual:** a GPU die surrounded by HBM stacks; a bar chart of memory and bandwidth per accelerator. Icons: `arch-gpu`, `arch-memory`.

**Speaker notes:** The spec race moved to memory because inference is bandwidth-bound. B200 per-GPU values are DGX B200
system totals divided by eight.

## Slide 3 — Ridge points

- H100 FP8 ≈ 591, H200 FP8 ≈ 412, B200 FP8 ≈ 562, TPU7x FP8 ≈ 625 FLOP/byte
- Decode sits far below all of them
- Compare bandwidth per dollar for chat; FLOPs per dollar for training/prefill
- Benchmark your workload; never compare sparse peaks across vendors

**Visual:** roofline with each accelerator's ridge marked. Icons: `ops-metrics`.

**Speaker notes:** Ties straight back to chapter 21's roofline.

## Slide 4 — The interconnect hierarchy

- HBM (TB/s) → NVLink 900 GB/s (H100) – 1.8 TB/s (B200) → PCIe Gen5 128 GB/s → 400 Gb/s NIC = 50 GB/s
- Units: GB/s vs Gb/s; bidirectional vs per direction
- InfiniBand (lossless fabric) vs RoCE v2 (RDMA over Ethernet, needs congestion control)
- Rail-optimised fabrics; Ultra Ethernet 1.0 (June 2025)

**Visual:** the lesson's node diagram: GPUs on NVSwitch, PCIe to CPU and NIC, fabric to the next node. Icons: `arch-gpu`, `arch-network`, `arch-router`.

**Speaker notes:** Each tier is roughly an order of magnitude slower than the one above. Design so the chattiest
traffic stays highest.

## Slide 5 — Why TP stays on NVLink

- TP = 2 all-reduces per layer; Llama 3 70B, 4,096-token prefill, TP 8: 112 MiB per GPU per all-reduce
- NVLink ≈ 42 ms per prefill; PCIe ≈ 294 ms; one 400 Gb/s NIC ≈ 376 ms (bandwidth term)
- Decode: 160 latency-bound collectives per token
- Rule: TP inside a node, PP across nodes

**Visual:** three bars for the three link types. Icons: `arch-network`, `ops-latency`.

**Speaker notes:** This is vLLM's documented guidance, and the arithmetic shows why.

## Slide 6 — Kubernetes and GPUs

- Device plugin: `nvidia.com/gpu: N` — opaque counts
- GPU Operator (v26.7.3): driver, toolkit, device plugin, GFD labels, DCGM exporter, MIG manager
- DRA: ResourceSlices, DeviceClasses, ResourceClaims with CEL — GA in v1.34
- NVIDIA DRA driver v0.5.1: ComputeDomains supported; GPU allocation not yet official

**Visual:** the lesson's operator/scheduler diagram. Icons: `devops-kubernetes`, `devops-helm`.

**Speaker notes:** As of 2026-11 most production clusters still allocate GPUs via the device plugin and use DRA first
for multi-node NVLink.

## Slide 7 — Sharing a GPU

- MIG: up to 7 hardware instances; isolated memory paths, L2, QoS, fault isolation
- MPS: space partitioning with limits; experimental in the device plugin; not with MIG
- Time-slicing: no isolation, shared fault domain
- H100 profiles 1g.10gb … 7g.80gb; single vs mixed MIG strategy

**Visual:** three GPUs: one cut into 7 boxes (MIG), one with overlapping translucent tenants (MPS), one with a clock (time-slicing). Icons: `arch-gpu`, `pattern-bulkhead`.

**Speaker notes:** Pick MIG for multi-tenant latency-sensitive services, time-slicing only for dev.

## Slide 8 — Gang and topology-aware scheduling

- 31 of 32 GPUs = a deadlocked job holding hardware hostage
- Kueue v0.20.7: quotas, fair sharing, all-or-nothing, topology-aware scheduling
- Volcano (CNCF incubating): batch scheduler with gang
- Native PodGroup gang scheduling: beta in v1.37, off by default

**Visual:** two half-placed jobs deadlocked vs one fully placed job. Icons: `arch-queue`, `pattern-consensus`.

**Speaker notes:** Topology-aware placement puts communicating pods on one rack or leaf; schedulers are converging on
kube-scheduler's workload-aware API.

## Slide 9 — Slurm vs Kubernetes

- Slurm: gang by default, fair-share, reservations; researcher-friendly
- Kubernetes: services, autoscaling, rollouts, ecosystem
- Slinky slurm-operator v1.3.0: Slurm on Kubernetes
- NVIDIA acquired SchedMD (Dec 2025), committed to open-source, vendor-neutral Slurm

**Visual:** two scheduler icons merging into one cluster. Icons: `devops-kubernetes`, `arch-cron`.

**Speaker notes:** Common pattern: Kubernetes for inference and platform, Slurm (native or via Slinky) for big training.

## Slide 10 — "GPU utilisation" lies

- GPU_UTIL = time at least one kernel was running
- Use DCGM profiling: GR_ENGINE_ACTIVE, SM_ACTIVE, PIPE_TENSOR_ACTIVE, DRAM_ACTIVE
- Decode: high DRAM_ACTIVE, modest TENSOR_ACTIVE; prefill/training: the reverse
- Business view: tokens/s per GPU vs the capacity model; MFU for training

**Visual:** gauge at 98 % next to a tensor-activity gauge at 20 %. Icons: `observability-grafana`, `observability-prometheus`, `ops-dashboard`.

**Speaker notes:** The interview question "dashboards say 95 % but throughput is poor" is answered on this slide.

## Slide 11 — Failures at scale

- Llama 3: 466 interruptions in 54 days on up to 16K H100s; 419 unexpected
- ≈ 78 % hardware; GPUs 58.7 %; HBM3 72 interruptions (17.2 %)
- ≈ one unexpected interruption every 3.1 hours → checkpoint ≈ every 27 min (Young/Daly, 2-min checkpoints)
- Diurnal 1–2 % throughput swing; power swings of tens of megawatts

**Visual:** a 54-day timeline with 419 tick marks. Icons: `ops-incident`, `pattern-backup`.

**Speaker notes:** At this scale you design for fast detection and restart, not for avoiding failure.

## Slide 12 — Xid triage

- 13/31: app faults → restart app
- 48 (double-bit ECC), 95 (uncontained memory) → drain and reset
- 64 (remap failure) → reset, plan replacement; 74 NVLink; 79 off the bus → node-level
- Automate Xid → action → cordon → reschedule

**Visual:** a triage flowchart from Xid code to action. Icons: `ops-alert`, `ops-warning`.

**Speaker notes:** Actions follow NVIDIA's Xid catalog. A failed GPU kills its whole TP group or training job.

## Slide 13 — Power, cooling, other accelerators, cost

- 8× H100 GPUs ≈ 5.6 kW at TDP; DGX B200 ~14.3 kW; GB200 NVL72 liquid-cooled
- AMD (ROCm), Google TPU (JAX/XLA, cloud-only), AWS Trainium (Neuron, cloud-only)
- Cost per token = $/GPU-hour ÷ useful tokens per GPU-hour
- Bandwidth model: B200 cheaper per token than H100 if its hourly price < ≈ 2.4×

**Visual:** rack with power meter and coolant loop; three vendor chips side by side. Icons: `arch-datacenter`, `ops-cost`, `cloud-gcp`, `cloud-aws`.

**Speaker notes:** Rack power density is often the real capacity limit. Compare vendors with your benchmark, not peak
numbers.

## Slide 14 — Interview angle

- CLARIFY workload mix, isolation, NVLink domains, team skills
- QUANTIFY memory, TP degree, interconnect, failure rate → checkpoints, power per rack
- SKETCH GPU Operator + device plugin/DRA + Kueue + DCGM + Xid remediation
- Red flags: GPU_UTIL as KPI, cross-node TP over Ethernet, no gang scheduling, time-slicing for tenants

**Visual:** the six-step framework strip. Icons: `ops-check`.

**Speaker notes:** Close by connecting to C13 (telemetry platform for a GPU cluster) as the full case study.
