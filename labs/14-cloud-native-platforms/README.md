# Lab L14 — A tiny platform on kind: autoscaling, rolling updates, canaries

Lesson: [SYSDESIGN-14 — Cloud-native & platform engineering](../../course/02-modern-requirements/14-cloud-native-platforms.md)

## Goal

Run a three-node Kubernetes cluster on your laptop with **kind** and use it to see, with your own eyes, the
mechanisms the lesson describes: a Horizontal Pod Autoscaler reacting to CPU load, a rolling update that drops no
requests, a broken rollout that is contained by `maxUnavailable: 0` and undone, and a replica-ratio canary whose
traffic share you can measure.

## What you will observe

- The HPA formula and its default scale-up and scale-down policies acting on a real Deployment.
- The difference between a *readiness* gate and "the pod is running".
- That a Deployment rollout with `maxSurge: 1, maxUnavailable: 0` keeps serving while a new version comes up — and
  while a broken one fails to come up.
- That a Service spreads connections roughly in proportion to ready endpoints, which is the cheapest (and coarsest)
  way to run a canary.

## Prerequisites

| Tool | Version used for the test run | Notes |
|---|---|---|
| Docker Engine | 29.10.0 | any recent Docker works |
| kind | 0.33.0 | node image pinned by digest in `kind-config.yaml` (Kubernetes v1.37.0) |
| kubectl | v1.37.1 | within one minor version of the server |
| Internet access | once | pulls `kindest/node`, `python:3.15.2-slim-trixie`, and `metrics-server:v0.9.1` |

About 3 GB free disk and 4 GB free RAM. No GPU, no cloud account.

Files:

```text
kind-config.yaml        cluster "sd-14": 1 control plane + 2 workers, kindest/node:v1.37.0@sha256:a1ed56cf...
app/server.py           the Lumen API stand-in (stdlib only): /, /work (burns CPU), /healthz, /readyz
app/client.py           load generator and probe client, shipped in the same image (no extra pulls)
app/Dockerfile          python:3.15.2-slim-trixie, non-root; build-arg APP_VERSION bakes v1 or v2 in
k8s/10-app.yaml         Namespace "lumen", Deployment "api" (stable track), Service "api"
k8s/20-hpa.yaml         HPA: 50% of the 100m CPU request, min 2, max 8, scale-down window 60 s
k8s/30-load.yaml        Job: 4 clients hammering /work for 180 s
k8s/40-canary.yaml      Deployment "api-canary": one v2 pod behind the same Service
k8s/50-probe.yaml       Pod: calls the Service 5x/s, prints "<unix-ts> <version|ERR>"
```

## Run

All commands from this directory. `K` is a shorthand so every command targets the lab cluster only.

```bash
K="kubectl --context kind-sd-14"

# 1. Cluster (about 30 s when the node image is cached)
kind create cluster --config kind-config.yaml

# 2. metrics-server (needed by the HPA); kind's kubelets use self-signed certs, hence the extra flag
$K apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.9.1/components.yaml
$K -n kube-system patch deployment metrics-server --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# 3. Build two versions of the app and side-load them into the kind nodes
docker build -t lumen-api:v1 --build-arg APP_VERSION=v1 app
docker build -t lumen-api:v2 --build-arg APP_VERSION=v2 app
kind load docker-image lumen-api:v1 lumen-api:v2 --name sd-14

# 4. Deploy the stable track and the HPA
$K apply -f k8s/10-app.yaml -f k8s/20-hpa.yaml
$K -n lumen rollout status deploy/api
$K -n lumen get hpa api        # TARGETS shows <unknown> for up to a minute until metrics arrive
```

## Experiments

1. **Autoscaling.** Start the load and watch the HPA every 15 s:

   ```bash
   $K apply -f k8s/30-load.yaml
   for i in $(seq 1 24); do $K -n lumen get hpa api --no-headers; sleep 15; done
   $K -n lumen describe hpa api | sed -n '/Events/,$p'
   ```

   Compute what the formula `ceil(replicas × current / target)` asks for at the first reading above target, and
   compare with what the HPA actually did. Why did it not jump straight there? (Hint: the default scale-up policy
   adds at most the larger of 100% or 4 pods per 15 s.) After the Job ends, note how long scale-down takes and
   relate it to `stabilizationWindowSeconds: 60` in `k8s/20-hpa.yaml` (the default is 300 s).

2. **Zero-error rolling update.** Start the probe, then roll v1 → v2:

   ```bash
   $K -n lumen scale deploy/api --replicas=4
   $K apply -f k8s/50-probe.yaml && $K -n lumen wait --for=condition=Ready pod/probe
   $K -n lumen set image deploy/api api=lumen-api:v2
   $K -n lumen rollout status deploy/api
   $K -n lumen logs probe | awk '{print $2}' | sort | uniq -c     # count v1 / v2 / ERR
   ```

3. **Break it: a rollout that cannot succeed.** Point the Deployment at an image that does not exist:

   ```bash
   $K -n lumen set image deploy/api api=lumen-api:v3-missing
   $K -n lumen rollout status deploy/api --timeout=30s            # times out
   $K -n lumen get pods -l app=api                                # old pods still Running, one new pod failing
   $K -n lumen logs probe --since=30s | awk '{print $2}' | sort | uniq -c
   $K -n lumen rollout undo deploy/api
   ```

   Which two fields in `k8s/10-app.yaml` guarantee that the old pods keep serving? What would change with
   `maxUnavailable: 50%`?

4. **Replica-ratio canary.** Go back to v1 on the stable track, pin it at 9 replicas, add one v2 canary pod and
   measure the share:

   ```bash
   $K apply -f k8s/10-app.yaml
   $K -n lumen patch hpa api --type=merge -p '{"spec":{"minReplicas":9,"maxReplicas":9}}'
   $K -n lumen rollout status deploy/api
   $K apply -f k8s/40-canary.yaml && $K -n lumen rollout status deploy/api-canary
   sleep 60; $K -n lumen logs probe --since=58s | awk '{print $2}' | sort | uniq -c
   ```

   Expect roughly 1/(9+1) = 10% v2. Why is this approach coarse (think of a 1% canary, or of the HPA scaling only
   the stable track)? How would a Gateway API `HTTPRoute` with weighted `backendRefs` change that?

5. **(Optional) Read the controllers at work.** `$K -n lumen get rs` after each experiment shows one ReplicaSet per
   template revision; `$K -n lumen rollout history deploy/api` shows the revisions the Deployment controller keeps.

## Expected results

- Experiment 1: CPU utilisation far above 50%, replicas rising in steps (not in one jump) to `maxReplicas`, then
  falling back to `minReplicas` after the load ends and the stabilisation window passes. `SuccessfulRescale` events
  explain each step.
- Experiment 2: only `v1` and `v2` lines, no `ERR`.
- Experiment 3: the rollout times out, the old ReplicaSet's pods stay `Running`, the new pod shows
  `ErrImageNeverPull`, and the probe records no errors; `rollout undo` restores the previous image.
- Experiment 4: a v2 share near 10%, varying from run to run because connection placement is random.

Your exact numbers will differ with CPU speed and background load.

## Clean up

```bash
kind delete cluster --name sd-14
docker rmi lumen-api:v1 lumen-api:v2
```

## Cost

€0 — everything runs locally.

## Test status

**runtime-tested** on 2026-11-20. Host: Ubuntu 24.04 (kernel 7.0.0-43-generic, x86_64), Docker 29.10.0, kind 0.33.0,
kubectl v1.37.1, server v1.37.0 (3 nodes), metrics-server v0.9.1. Observed:

- Experiment 1: HPA targets `<unknown>` for ~45 s after pod start, then `cpu: 312%/50%` with 2 replicas; rescaled
  2 → 6 → 8 in two consecutive 15 s periods (`SuccessfulRescale` events "New size: 6", "New size: 8"); stayed at 8
  (CPU 190–240%) while load ran; after the Job completed (4/4 clients, `ok=2656 err=0` for one client's summary
  line), scaled 8 → 5 → 2 about 60–75 s after CPU dropped.
- Experiment 2 (4 replicas, rollout took 21 s): probe recorded 86 `v1`, 89 `v2`, **0 `ERR`**.
- Experiment 3: `rollout status` timed out; 4 old pods `Running`, 1 new pod `ErrImageNeverPull`; probe recorded
  141 `v2`, **0 `ERR`**; `rollout undo` restored `lumen-api:v2`.
- Experiment 4 (9 stable v1 + 1 canary v2, 58 s window): 247 `v1`, 27 `v2` → **9.9%** canary share.
- Cluster deleted with `kind delete cluster --name sd-14` afterwards.

## Troubleshooting

- **HPA shows `<unknown>`** for more than two minutes: check `$K -n kube-system get pods | grep metrics-server`; the
  `--kubelet-insecure-tls` patch must be applied, and pods must have CPU *requests*.
- **`ErrImageNeverPull`** on the real versions: you skipped `kind load docker-image`, or rebuilt the image after
  loading it.
- **The canary share is 0%**: the canary pod is not ready yet, or its labels do not match the Service selector
  `app: api`.
- **kind fails to create the cluster**: another cluster may hold the same name (`kind get clusters`), or Docker has
  too little memory.
- **Port conflicts**: this lab publishes no host ports; everything is reached inside the cluster.
