# 14 — Exercises

Lesson: [SYSDESIGN-14 — Cloud-native & platform engineering](../course/02-modern-requirements/14-cloud-native-platforms.md)

### 1. [Core] What is a container, really?

Explain to a colleague what makes a process "a container". Which isolation does it *not* provide, and what would
you use for untrusted customer code?

<details><summary>Answer</summary>

A container is an ordinary Linux process placed in its own **namespaces** (mount, PID, network, IPC, UTS, user,
cgroup, time — each giving a private view of one global resource), constrained by **cgroups** (CPU, memory, I/O and
PID limits plus accounting), started from a layered OCI **image**, and usually hardened with dropped capabilities,
seccomp and an LSM profile. It does **not** give a separate kernel: every container on the node shares it, so a
kernel vulnerability can break out of all of them. For untrusted code use a stronger boundary: a micro-VM
(Firecracker, Kata Containers), a user-space kernel (gVisor), a Wasm sandbox when the workload fits, and/or dedicated
nodes per tenant.
</details>

### 2. [Core] Compute the HPA's answer

An HPA targets 50% average CPU utilisation of a 200m request. Four pods use 320m, 300m, 280m and 300m. (a) What
replica count does the formula produce? (b) If two of those pods are not yet ready and the controller is scaling up,
how does it treat them? (c) Why might the actual first step be smaller than (a)?

<details><summary>Answer</summary>

(a) Average usage 300m = 150% of the 200m request. desired = ceil(4 × 150 / 50) = **12**. (b) When scaling up,
not-yet-ready pods and pods with missing metrics are treated conservatively — the controller assumes **0%** of the
target for missing metrics on scale-up (and sets aside unready pods' CPU samples), which reduces the computed scale-up.
(c) Default scale-up policies limit how fast replicas grow per 15 s period (the larger of +100% or +4 pods), so the
first step from 4 would be to 8, then 12 on the next period. The lab showed exactly this pattern (2 → 6 → 8).
</details>

### 3. [Core] Level-triggered vs edge-triggered

A teammate writes a script that listens for "pod deleted" events and creates a replacement. Why is Kubernetes'
ReplicaSet controller more robust? Give two failure scenarios.

<details><summary>Answer</summary>

The controller is **level-triggered**: on every pass it compares desired replicas with the pods that actually exist
and acts on the difference, regardless of which events it saw. The script is **edge-triggered**: it acts only on
events. Failures: (1) the script crashes or restarts and misses three delete events — those pods are never replaced;
the controller, on restart, simply counts and recreates them. (2) A network partition delays events, or two events
arrive out of order — the script may double-create; the controller converges because it recomputes from current
state and uses optimistic concurrency on writes. Levels also make the system self-healing after etcd restores or
manual edits.
</details>

### 4. [Deep] Design an operator

Lumen runs a vector index per tenant. Design a `VectorIndex` custom resource and the reconciler's main steps,
including deletion. What must every step satisfy?

<details><summary>Answer</summary>

`spec`: `replicas`, `embeddingModel`, `storageClass`, `snapshotSchedule`; `status`: `phase`, `readyReplicas`,
`builtModel`, `observedGeneration`, conditions. Reconcile: get the CR; if it carries a deletion timestamp, run a
**finalizer** (snapshot to object storage, then remove the finalizer); ensure an owned StatefulSet and Service exist
and match `spec.replicas`; if `spec.embeddingModel != status.builtModel`, start a rebuild **Job** if none is
running; update status; requeue periodically for drift. Every step must be **idempotent**, safe to interrupt at any
line, store progress only in the API (status/owned objects), push long work into Jobs, and use `resourceVersion`
conflicts as a signal to re-read and retry. Owner references let garbage collection clean up children.
</details>

### 5. [Core] Rolling update arithmetic

A Deployment has 40 replicas, `maxSurge: 25%`, `maxUnavailable: 0`, and pods take 45 s from creation to ready.
Roughly how long does a rollout take, and how much extra capacity does it need? What changes with
`maxUnavailable: 25%`?

<details><summary>Answer</summary>

maxSurge 25% of 40 = 10 extra pods at a time; with maxUnavailable 0 the controller creates 10 new pods, waits for
them to be ready, removes 10 old ones, and repeats: 40 / 10 = **4 waves × ~45 s ≈ 3 minutes**, needing capacity for
**50 pods** (125%) during the rollout. With maxUnavailable 25% it can also remove 10 old pods immediately, so each
wave replaces up to 20 pods: ≈ 2 waves ≈ 1.5 minutes, with no extra capacity needed beyond the surge, but serving
capacity can dip to 75% — acceptable only if you have headroom.
</details>

### 6. [Interview] Canary sample size

A service handles 500 req/s with a 0.2% error rate. You want a canary to detect a regression to 1% errors. With a 2%
canary, how long must you wait to see a clear signal? What if the regression is to 0.3%?

<details><summary>Answer</summary>

Canary traffic = 2% × 500 = 10 req/s. In 10 minutes it sees 6,000 requests: expected errors at 0.2% ≈ 12; at 1% ≈
60. A difference of 12 vs 60 is far outside Poisson noise (σ ≈ √12 ≈ 3.5), so **~10 minutes** suffices (even 3–5
minutes is likely clear). For 0.3% (18 expected vs 12), σ ≈ 3.5–4.2 makes the difference ~1.5σ — **not
detectable** in 10 minutes; you would need a much larger sample (roughly ten times more requests for a ~3σ
signal), a bigger canary share, or a longer bake time. Lesson: canaries catch big regressions fast; small
regressions need SLO burn-rate monitoring after full rollout.
</details>

### 7. [Core] GitOps principles in practice

For each OpenGitOps principle, give one concrete consequence for Lumen's delivery system.

<details><summary>Answer</summary>

**Declarative**: all manifests (Deployments, HTTPRoutes, HPAs) live as data; no imperative scripts in the deploy
path. **Versioned and immutable**: every change is a commit; image references are pinned (ideally by digest), so a
revision always means the same thing; rollback = `git revert`. **Pulled automatically**: Argo CD/Flux inside the
cluster pull from Git; CI never holds cluster-admin credentials. **Continuously reconciled**: a manual `kubectl edit`
in production is detected as drift and reverted (or alerted), so Git remains the source of truth. Consequence to
plan for: secrets need a separate mechanism (sealed/external secrets).
</details>

### 8. [Deep] Serverless or containers?

Lumen's PDF-thumbnail service gets about 2,000 requests per day in bursts, each taking 800 ms of CPU. The chat API
gets a steady 1,500 req/s. Which compute model for each, and why? What is the main risk of each choice?

<details><summary>Answer</summary>

Thumbnails: **functions or scale-to-zero containers** (Lambda, Cloud Run, Knative, or KEDA-scaled workers). Load is
tiny and bursty; idle containers would cost more than per-invocation pricing. Risk: **cold starts** on the first
request after quiet periods — acceptable for a background thumbnail, mitigated by async processing or SnapStart-like
snapshots. Chat API: **containers on Kubernetes** (or managed containers) with HPA; steady high load makes
always-on, well-utilised pods cheaper than per-request pricing, and gives control over connection handling and
latency. Risk: **operational complexity** and over-provisioning if requests are mis-sized. The break-even depends on
prices and utilisation — SYSDESIGN-16 builds the model.
</details>

### 9. [Frontier] Where does WebAssembly fit?

Give two Lumen use cases where a Wasm component is a better choice than a container, and one where it is worse.
What changed in WASI 0.3?

<details><summary>Answer</summary>

Better: (1) **customer-supplied plugins** (e.g. a tenant's custom document parser) — capability-based sandbox, nothing
accessible unless granted, small footprint, fast instantiation; (2) **edge request filters** (auth checks, header
rewriting) close to users (SYSDESIGN-15). Worse: the **embedding or LLM inference service** — needs GPUs, native
libraries and mature profiling that Wasm runtimes do not provide in the same way. WASI 0.3 (listed by wasi.dev as
the stable, current release as of 2026-11) adds native async to the Component Model — `async` functions,
`stream<T>` and `future<T>` — replacing the `wasi:io` polling approach of 0.2 and making network services
more natural to write.
</details>

### 10. [Interview] Design an internal developer platform

In 15 minutes, outline a platform that lets Lumen's 8 product teams create and run a new service in one day. What
does the platform API look like, and how do you measure success?

<details><summary>Answer</summary>

CLARIFY: team count, service types (HTTP APIs, workers, LLM-backed services), compliance, who is on call.
SKETCH: golden-path **templates** (repo, CI, Dockerfile, OTel instrumentation, SLO file) → a **platform API** —
e.g. a `LumenService` CRD or claim: `{name, team, exposure: public|internal, slo: 99.5, database: postgres-small,
scaling: {min, max, signal}}` — implemented by operators/compositions that create the namespace, RBAC, quotas,
network policies, GitOps application, HTTPRoute, HPA/KEDA object, dashboards and burn-rate alerts. Portal/CLI as
front ends. DEEPEN: secure defaults (Pod Security, workload identity, signed images), optional and composable
escape hatches. Measure: **time to first production deploy**, adoption (% services on the paved road), deploy
frequency, lead time, change-failure rate, MTTR, and developer satisfaction surveys — the CNCF white paper's
"platform as a product" attribute. Red flag: mandating a platform without measuring whether it reduces cognitive load.
</details>

### 11. [Lab] Explain the lab's HPA steps

In the lab's test run the HPA read `cpu: 312%/50%` (312% average utilisation of the CPU request, against a 50%
target) with 2 replicas, then went 2 → 6 → 8 in two consecutive 15 s periods. (a) What did the formula ask for at
the first reading? (b) Why 6 first?
(c) Why did scale-down take about a minute after the load stopped instead of 5 minutes?

<details><summary>Answer</summary>

(a) ceil(2 × 312 / 50) = ceil(12.48) = **13**, capped by `maxReplicas: 8`. (b) The default scale-up policy allows,
per 15 s period, the larger of +100% (2 → 4) or +4 pods (2 → 6): **6**. The next period allowed 6 → 12, capped at 8.
(c) The lab's HPA sets `behavior.scaleDown.stabilizationWindowSeconds: 60` instead of the default 300 s; the
controller uses the highest recommendation of the last 60 s, so it waits about a minute before acting, then the
default scale-down policy (up to 100% per period) brings it to the minimum in one or two steps (8 → 5 → 2 in the
test run).
</details>
