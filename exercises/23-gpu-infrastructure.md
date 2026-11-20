# 23 — Exercises

Lesson: [course/03-ai-systems/23-gpu-infrastructure.md](../course/03-ai-systems/23-gpu-infrastructure.md).
Hardware figures are vendor datasheet values cited in the lesson (as of 2026-11); everything else is a labelled
assumption.

## 1. [Core] Dense vs sparse

A colleague says "the H100 does 3,958 TFLOPS of FP8, so prefill of a 2,000-token prompt on a 32.8 B model takes 33 ms."
What is wrong, and what is a better estimate at 40 % utilisation of the dense peak?

<details><summary>Answer</summary>

3,958 TFLOPS is the **with-sparsity** figure; dense FP8 ≈ 1,979 TFLOPS. And no real kernel runs at 100 %. FLOPs =
2 × 32.8 × 10⁹ × 2,000 = 1.31 × 10¹⁴. At 0.4 × 1.979 × 10¹⁵ ≈ 7.9 × 10¹⁴ FLOP/s → **≈ 166 ms** (vs the claimed 33 ms —
a 5× error from two mistakes).
</details>

## 2. [Core] Which GPU for chat?

For decode-bound chat with a 32B FP8 model, rank H100, H200 and MI300X by the *bandwidth* bound on tokens/s at a fixed
batch, and name one non-bandwidth reason that could change the ranking in practice.

<details><summary>Answer</summary>

By bandwidth: **MI300X (5.3 TB/s) > H200 (4.8 TB/s) > H100 (3.35 TB/s)** on the bandwidth term alone; memory
capacity follows the same order (192 > 141 > 80 GB), allowing larger batches. Practical reasons the ranking can change:
software maturity and kernel quality for your model and quantisation format (FP8 support, attention kernels), price
and availability, interconnect for multi-GPU setups, and operational familiarity. Benchmark, do not extrapolate.
</details>

## 3. [Deep] Tensor parallelism across nodes

You need TP = 16 for a model on two 8-GPU H100 nodes connected by 8 × 400 Gb/s NICs each. Estimate the slowdown of the
all-reduce bandwidth term versus TP = 8 inside one node, and propose a better layout.

<details><summary>Answer</summary>

Inside a node each GPU has 900 GB/s bidirectional NVLink (≈ 450 GB/s per direction). Across nodes, each GPU's share is
one 400 Gb/s NIC = 50 GB/s per direction — **≈ 9× less bandwidth** for the cross-node part of every all-reduce, plus
higher latency, on 2 all-reduces per layer per token. Better: **TP = 8 within each node and PP = 2 across nodes**
(vLLM's documented pattern), or quantise / pick a GPU with more memory so TP fits in one NVLink domain, or use a
rack-scale NVLink system if the model truly needs a 16+ GPU TP domain.
</details>

## 4. [Core] Sharing an 80 GB GPU

Five teams each need to serve a small embedding/reranking model (≈ 6 GB each, latency-sensitive) on one H100 80 GB.
Compare MIG, MPS and time-slicing and recommend one.

<details><summary>Answer</summary>

**MIG**: up to 7 × 1g.10gb instances, each with its own memory paths, L2 slice and fault isolation → predictable
latency and tenant isolation. Recommended for five latency-sensitive, multi-team services. **MPS**: shares SMs with
per-client memory/compute limits; better utilisation if loads are bursty, but weaker fault isolation and "experimental"
in the device plugin; not combinable with MIG there. **Time-slicing**: no memory isolation; one crash takes all down;
latency interference — fine for dev, wrong here. Caveat: 1g.10gb gives each model 1/7 of the SMs; check throughput.
</details>

## 5. [Core] Device plugin vs DRA

Write, in words, the scheduling request for: "one pod needing two GPUs with ≥ 80 GB each on the same NVLink island".
Which mechanism can express it as of 2026-11, and what is the caveat for NVIDIA GPUs?

<details><summary>Answer</summary>

The device plugin can only say `nvidia.com/gpu: 2` — no attributes, no topology. **DRA** (stable `resource.k8s.io/v1`
since Kubernetes v1.34) can express it with a ResourceClaim selecting devices by attributes via CEL (memory, model,
topology attributes published in ResourceSlices) — *if* the vendor's DRA driver publishes those attributes. Caveat:
NVIDIA's DRA driver (v0.5.1) officially supports ComputeDomains for multi-node NVLink but marks GPU allocation as not
yet officially supported (disabled by default). In practice many clusters still use the device plugin plus node labels
(GPU Feature Discovery) and node pools per GPU type.
</details>

## 6. [Deep] Gang scheduling deadlock

Two 32-GPU training jobs are submitted to a 48-GPU cluster without gang scheduling. Describe the failure and two fixes.

<details><summary>Answer</summary>

kube-scheduler places pods one by one: each job may get, say, 24 GPUs; neither can start its collective; both hold
GPUs forever (or until timeouts) — a **resource deadlock**. Fixes: (1) **Kueue** all-or-nothing admission with quotas:
only one job is admitted until 32 GPUs are free; (2) **Volcano** gang scheduling (PodGroup with minMember); (3) the
native Workload/PodGroup gang scheduling (beta in v1.37, disabled by default); (4) Slurm, which allocates jobs
atomically. Add **topology-aware** placement so the admitted job's pods land within the same rack/leaf.
</details>

## 7. [Core] Utilisation that lies

A dashboard shows `DCGM_FI_DEV_GPU_UTIL` = 98 % on every inference GPU, yet tokens/s per GPU is a third of the
capacity model. Which metrics do you check next, and what patterns indicate which problem?

<details><summary>Answer</summary>

GPU_UTIL only means "a kernel was running". Check **`PROF_DRAM_ACTIVE`** (decode should be high; low → small batches
or CPU-bound engine loop), **`PROF_PIPE_TENSOR_ACTIVE`** (prefill/training should be high), **`PROF_SM_ACTIVE`/
`SM_OCCUPANCY`** (small kernels not filling the GPU), and engine metrics: running sequences (small batch?), queue
depth (no traffic queued → under-loaded, not slow), preemptions. Also check host CPU saturation of the API
server/engine core. Typical finding: batch too small because of routing imbalance or a low `max_num_seqs`.
</details>

## 8. [Deep] Failure-driven checkpointing

Using the Llama 3 statistic of 419 unexpected interruptions in 54 days, compute the mean time between interruptions.
If a checkpoint takes 2 minutes to write (blocking) and a restart takes 10 minutes, estimate the checkpoint interval
that minimises lost time (use the Young/Daly approximation √(2 × C × MTBF)).

<details><summary>Answer</summary>

MTBF = 54 × 24 h ÷ 419 ≈ **3.09 h ≈ 185 min**. Optimal interval ≈ √(2 × 2 × 185) ≈ √740 ≈ **27 minutes**. Expected
loss per failure ≈ half an interval (≈ 14 min) + restart (10 min). The Young/Daly formula is a classical first-order
approximation (J. W. Young, CACM 17(9), 1974, https://doi.org/10.1145/361147.361115; J. T. Daly, Future
Generation Computer Systems 22(3), 2006, https://doi.org/10.1016/j.future.2004.11.016); asynchronous or in-memory checkpointing lowers C and therefore the optimal
interval. The point: at 16K-GPU scale, checkpointing is tuned like any other SLO.
</details>

## 9. [Interview] Slurm or Kubernetes?

A research lab with 256 GPUs runs large training jobs and wants to start serving its models internally. Recommend a
platform layout.

<details><summary>Answer</summary>

Clarify ratios (training vs serving), team skills and isolation needs. A defensible answer: keep **Slurm** semantics
for researchers (gang, fair-share, reservations), run **Kubernetes** for inference (vLLM stack, autoscaling, rollouts),
and share hardware either by partitioning nodes or by running Slurm on Kubernetes via **Slinky** (slurm-operator), with
Kueue/priorities to lend idle training capacity to batch inference at night. Mention monitoring (DCGM), Xid-driven
remediation, and that NVIDIA's acquisition of SchedMD (Dec 2025) came with a commitment to keep Slurm open-source and
vendor-neutral. Alternative: all-Kubernetes with Kueue + TAS if the team is cloud-native.
</details>

## 10. [Core] Xid triage

Map each to an action: Xid 13 once on one GPU; Xid 48; Xid 79; Xid 64; Xid 95.

<details><summary>Answer</summary>

Xid 13 (application fault): restart the app; investigate if repeated. Xid 48 (double-bit ECC): **cordon, drain,
reset GPU**, run diagnostics. Xid 79 (fallen off the bus): **node-level** — drain and restart/replace the machine.
Xid 64 (row-remapping failure): **reset; schedule replacement** — memory is degrading. Xid 95 (uncontained memory
error): **reset GPU before any app restarts**; drain immediately. Automate the mapping from NVIDIA's Xid catalog.
</details>

## 11. [Interview] Cost per token across generations

A provider prices an H100 at $P per hour and a B200 at $2.2P per hour. Using the lesson's bandwidth model
(≈ 4,960 vs ≈ 11,850 output tokens/s for the same workload), which is cheaper per token, and what else must you check?

<details><summary>Answer</summary>

Cost per token ∝ price ÷ throughput: H100 = P ÷ 4,960; B200 = 2.2P ÷ 11,850 = P ÷ 5,386 → **B200 ≈ 8 % cheaper per
token** on the bandwidth term. Check: real benchmarks (compute, kernels, FP4/FP8 support), larger batches enabled by
180 GB of HBM (favours B200 further), power and cooling (DGX B200 ~14.3 kW per system), availability, and whether
your SLO (TPOT) allows the batch size assumed.
</details>
