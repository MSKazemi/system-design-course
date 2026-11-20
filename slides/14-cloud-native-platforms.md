# 14 — Cloud-native & platform engineering (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement

- 40 engineers, 8 teams, ~50 deploys a day
- Bad deploys caught before more than a few % of users notice
- Traffic swings 10× between night and afternoon
- Most engineers never write a Kubernetes manifest

**Visual:** Teams → one shared fleet, with a day/night traffic curve. Icons: `arch-users`, `devops-kubernetes`, `ops-deploy`.

**Speaker notes:** Autonomy, safety and cognitive load collide. Cloud-native mechanisms give autonomy and safety;
platform engineering keeps the cognitive load manageable.

## Slide 2 — A container is a process

- Namespaces: mount, PID, net, IPC, UTS, user, cgroup, time
- cgroups v2: CPU, memory, I/O, PID limits and accounting
- OCI image: layered, content-addressed
- Shared kernel: not a boundary for hostile code

**Visual:** Host kernel with three processes, each wrapped in namespace/cgroup layers. Icons: `devops-linux`, `devops-docker`, `arch-containers`.

**Speaker notes:** For untrusted code use micro-VMs like Firecracker (under 125 ms boot, under 5 MB overhead per
the NSDI 2020 paper), gVisor, Wasm, or dedicated nodes.

## Slide 3 — Kubernetes architecture

- Declare desired state to the API server; etcd stores it
- Scheduler binds pods to nodes; kubelets run them
- Controllers watch and act — nobody calls "start container"
- Lineage: Borg → Omega → Kubernetes

**Visual:** API server hub with etcd, scheduler, controller manager, kubelets. Icons: `devops-kubernetes`, `nosql-etcd`, `arch-server`.

**Speaker notes:** Current minor release v1.37 (as of 2026-11). etcd uses Raft, so control-plane availability
follows quorum rules from SYSDESIGN-09.

## Slide 4 — Primitives that matter

- Pod, ReplicaSet, Deployment, StatefulSet, DaemonSet, Job
- Service: stable name over changing pods
- Gateway + HTTPRoute: role-oriented L7 entry
- Requests drive scheduling and autoscaling; limits protect neighbours

**Visual:** Object hierarchy Deployment → ReplicaSet → Pods ← Service ← HTTPRoute. Icons: `devops-kubernetes`, `arch-load-balancer`.

**Speaker notes:** Readiness gates traffic, liveness restarts, startup protects slow starters. A rollout is only as
safe as its readiness probe.

## Slide 5 — Reconciliation and operators

- Observe → diff → act → repeat (level-triggered)
- Missed events are corrected on the next pass
- Operator = CRD + controller = runbook as code
- Idempotent steps, progress in status, long work in Jobs

**Visual:** State loop Observe → Diff → Act. Icons: `pattern-health-check`, `devops-kubernetes`.

**Speaker notes:** Example: a `VectorIndex` operator that creates StatefulSets, rebuilds on model change, and
snapshots before deletion via a finalizer.

## Slide 6 — Autoscaling: four loops

- HPA: pods, every 15 s, ceil(replicas × current / target)
- VPA: right-size requests; in-place resize GA in v1.35
- KEDA: event-driven, scales to and from zero
- Cluster autoscaler / Karpenter: nodes

**Visual:** Four nested loops with reaction-time labels. Icons: `pattern-autoscaling`, `pattern-horizontal-scaling`, `pattern-vertical-scaling`.

**Speaker notes:** Defaults: 0.1 tolerance and a 300 s scale-down stabilisation window. CPU is the wrong signal for
queue consumers and LLM servers.

## Slide 7 — Releasing safely

- Rolling: maxSurge / maxUnavailable
- Blue-green: switch at once, 2× capacity
- Canary: small %, compare SLOs, auto-rollback
- Gateway API weighted backendRefs make % splits a field

**Visual:** Traffic bars for rolling, blue-green and canary. Icons: `ops-deploy`, `ops-ci-cd`, `pattern-failover`.

**Speaker notes:** Canary detection power depends on sample size; a 5% canary for 10 minutes at 2,000 req/s sees
about 60,000 requests — enough for big regressions, not small ones.

## Slide 8 — GitOps

- Declarative, versioned and immutable, pulled, continuously reconciled
- CI builds and signs; PR bumps the tag; agent applies
- Rollback = git revert; drift is reverted
- Argo CD and Flux: CNCF graduated (2022)

**Visual:** Sequence: engineer → CI → config repo → in-cluster agent → API. Icons: `devops-argo`, `devops-git`, `devops-github-actions`.

**Speaker notes:** Pull keeps cluster credentials inside the cluster and makes Git the audit log. Secrets need a
separate mechanism.

## Slide 9 — Serverless and cold starts

- Pay per request; scale to zero; platform patches
- Lambda lifecycle: Init → Invoke → Shutdown
- Provisioned concurrency: warm, pay for idle
- SnapStart: restore micro-VM snapshots (Java 11+, Python 3.12+, .NET 8+)

**Visual:** Timeline of a cold vs warm invocation. Icons: `arch-serverless`, `cloud-aws-lambda`, `cloud-gcp-cloud-run`.

**Speaker notes:** SnapStart is not compatible with provisioned concurrency and needs care with uniqueness (seeds,
IDs, connections). Knative brings scale-to-zero to your own clusters.

## Slide 10 — WebAssembly on the server

- Capability-based sandbox; tiny footprint
- WASI 0.2 (Jan 2024) → WASI 0.3 stable, current: native async
- Component Model: typed cross-language interfaces
- On Kubernetes: runwasi shims, SpinKube (CNCF Sandbox)

**Visual:** Container vs micro-VM vs Wasm component isolation layers. Icons: `arch-containers`, `arch-serverless`.

**Speaker notes:** Great for plugins and edge filters; not yet for GPU or native-library-heavy services.

## Slide 11 — Platform engineering

- "An integrated collection of capabilities" (CNCF white paper)
- Platform as a product, self-service, reduced cognitive load
- Golden paths, platform API, secure by default
- Measure adoption, lead time, change-failure rate

**Visual:** Portal/CLI → platform API → delivery, observability, security, data → fleet. Icons: `arch-api-gateway`, `ops-dashboard`, `devops-terraform`.

**Speaker notes:** The platform API is the key design move: a small opinionated interface that hides Kubernetes.

## Slide 12 — Multi-tenancy

- Multi-team vs multi-customer tenancy
- Namespace + RBAC + quotas + NetworkPolicy (soft)
- Node pools + sandboxed runtimes (stronger)
- Virtual control plane or cluster per tenant (strongest)

**Visual:** Isolation ladder from namespace to cluster per tenant. Icons: `security-authorization`, `security-lock`, `devops-kubernetes`.

**Speaker notes:** Kubernetes describes soft vs hard tenancy as a spectrum. Namespaces are not a security boundary
against hostile tenants.

## Slide 13 — Failure modes

- Bad rollout → canary analysis + auto-rollback
- Aggressive liveness probes → restart storms
- CPU limits → throttling with idle nodes
- Retired components (Ingress NGINX, March 2026) → no CVE fixes

**Visual:** Table failure → detect → mitigate. Icons: `ops-incident`, `ops-warning`.

**Speaker notes:** If etcd loses quorum, running pods keep running but nothing can be changed or healed.

## Slide 14 — Interview angle and lab

- CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP
- Quantify pods at peak/trough and rollout duration
- Red flags: "Kubernetes will autoscale it", liveness checks the DB
- Lab: kind cluster sd-14 — HPA 2 → 6 → 8, zero-error rollout, 9.9% canary

**Visual:** Lab cluster with load Job, probe Pod, stable and canary Deployments. Icons: `devops-kubernetes`, `pattern-autoscaling`.

**Speaker notes:** The lab numbers come from the recorded test run on 2026-11-20; yours will differ with hardware.
