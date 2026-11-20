# Lab L01 — Saturation point

Unit: [SYSDESIGN-01 — Requirements to numbers](../../course/00-orientation/01-requirements-to-numbers.md)

## Goal

Predict a service's latency curve from queueing theory *before* you measure it. Then measure it with an
open-model load test, find the **knee** (the highest load that still meets a latency target), and check
**Little's law** (L = λW) against the server's own measurements.

## What you will observe

- Latency stays almost flat up to about 60–70% utilisation, then rises steeply. Past 100% it grows without bound
  for as long as the test runs.
- p99 rises earlier and faster than p50.
- The server's time-averaged number of requests in the system (L) equals throughput × mean time in system
  (λ × W), to within rounding.
- Variability matters. With constant service times (`DIST=const`) the same utilisation produces far less
  queueing.
- A "4-worker" CPU-bound Python service does not have 4× the capacity, because of the GIL. Nominal capacity and
  real capacity differ, which is why you measure.

## Prerequisites

- Docker Engine 29.x and Docker Compose v5.x (tested with Docker 29.10.0, Compose v5.8.0)
- About 300 MB of disk for images. The core lab needs about 100 MB of RAM. The optional observability profile
  needs about 500 MB more.
- Python 3 on the host to run `predict.py` (standard library only)
- Images (pinned): `python:3.15.2-slim` (service build), `grafana/k6:2.4.0`, and optionally
  `prom/prometheus:v3.16.0` and `grafana/grafana:13.3.1`
- Host ports used (localhost only): 10101 (service), 10190 (Prometheus), 10130 (Grafana)

## The service

`service/app.py` is a deliberately simple Lumen service, built only from the Python standard library. Requests
to `/work` join a FIFO queue in front of `WORKERS` worker threads. Each worker "serves" a job for a random time
with mean `SERVICE_MS` (exponential by default). So the capacity is known in advance:

> capacity = WORKERS / SERVICE_MS = 1 / 0.010 s = **100 requests/s** with the defaults.

By default the worker *waits* (`time.sleep`), like a service waiting on a slow dependency. That makes the lab
independent of your laptop's CPU speed. `MODE=cpu` makes the worker spin the CPU instead. `/stats` reports
throughput, mean time in system W, time-averaged number in system L (integrated over time, not sampled), and
utilisation for the window since `/reset`.

## Run

```bash
cd labs/01-requirements-to-numbers

# 1. Predict first (no Docker needed)
python3 predict.py 10 20 40 60 70 80 90 95

# 2. Start the service
docker compose -p sd-01 up -d --build
curl -s localhost:10101/work; echo
curl -s localhost:10101/stats

# 3. Sweep arrival rates (30 s per step; about 5 minutes in total)
./sweep.sh 30s 20 40 60 70 80 90 95 110
```

Each step prints two lines:

```text
SERVER rate=<λ> throughput=<req/s> util=<ρ> W_ms=<mean time in system> L=<time-avg in system> lambdaW=<λ×W>
RESULT rate=<λ> achieved_rps=<req/s> p50_ms=… p90_ms=… p99_ms=… max_ms=… failed=…% dropped=<n>
```

`RESULT` is the client (k6) view and `SERVER` is the server view. Then compare with theory, *using the
utilisation the server measured*, since exponential draws and `sleep` overshoot shift the effective service time
by a few percent:

```bash
python3 predict.py --measured 80 <util at 80> 90 <util at 90>
```

**Optional: watch it live.** Start Prometheus and Grafana and stream k6's metrics to Prometheus:

```bash
docker compose -p sd-01 --profile observe up -d
K6_OUT=experimental-prometheus-rw ./sweep.sh 30s 40 80 90 95
# Grafana: http://localhost:10130  → dashboard "L01 - saturation point" (folder SYSDESIGN)
# Prometheus: http://localhost:10190
```

If you have the k6 binary installed on the host, `K6_BIN=k6 ./sweep.sh …` runs it locally against
`127.0.0.1:10101` instead of in a container.

## Experiments

1. **Find the knee.** Run the sweep. With a p99 target of 150 ms, what is the highest rate that meets it? What
   utilisation is that? Compare with the lesson's advice to plan for 50–70%.
2. **Check Little's law.** In every `SERVER` line, compare `L` (measured by integrating the number in the
   system over time) with `lambdaW` (computed from completed requests). Why do they agree, even when latency
   is exploding?
3. **Predict vs measure.** Run `predict.py --measured` with the utilisations from your sweep. Which model, M/M/1
   or D/M/1, is closer? Why does k6's `constant-arrival-rate` executor make this a D/M/1 system?
4. **Overload.** Look at the 110 requests/s step. What happens to achieved throughput, to latency, and to k6's
   `dropped` count? Run it for 60 s instead of 30 s. Does latency stabilise?
5. **Remove variability.** Restart with constant service times and repeat the top of the curve:
   `DIST=const docker compose -p sd-01 up -d service && ./sweep.sh 30s 90 95`. Explain the difference with
   Kingman's formula.
6. **Nominal vs real capacity.** `MODE=cpu WORKERS=4 docker compose -p sd-01 up -d service`, then
   `./sweep.sh 20s 80 150`. The configuration claims 400 requests/s. What do you measure, and why? (Hint: the GIL.)
7. **Repeatability.** Repeat the 90 requests/s step twice for 90 s each. How much do p99 and W vary between runs
   near saturation? What does that mean for capacity reports based on one short test?

Reset the service to defaults afterwards with `docker compose -p sd-01 up -d service`.

## Expected results

Look for the shape, not exact numbers. Your hardware, Docker networking and background load all shift the
values.

- At low utilisation (≤ 40%), mean W is close to the service time (about 10–11 ms). p99 is a few times that,
  because service times are exponential.
- Between 60% and 80%, mean W should track the **D/M/1** prediction closely. M/M/1 overestimates, because k6's
  arrivals are evenly spaced, not Poisson.
- Above about 90%, results get noisy, and a 30 s window is too short for a steady state. Single runs can land
  anywhere between the D/M/1 and M/M/1 predictions, or beyond.
- Above 100%, achieved throughput caps at about the service capacity, latency grows for the whole test, and k6
  may report dropped iterations.
- `L` and `lambdaW` agree to within rounding at every step.
- With `DIST=const`, latency at 90–95% is far lower than with exponential service.
- With `MODE=cpu WORKERS=4`, capacity is at most one core's worth (100 requests/s minus Python overhead), not 400.

## Clean up

```bash
docker compose -p sd-01 --profile observe --profile tools down -v
docker image rm sd-01-service:local   # optional
```

## Cost

€0. Everything runs locally. No cloud resources.

## Test status

**runtime-tested** on 2026-11-20. Host: Ubuntu 24.04.5 LTS, kernel 7.0.0-43-generic, 12 CPUs, 30 GB RAM,
Docker 29.10.0, Compose v5.8.0. Images: `python:3.15.2-slim`, `grafana/k6:2.4.0`
(digest `sha256:d41bb79c…`, the same as on Docker Hub, pulled through `mirror.gcr.io` because Docker Hub pulls
were stalling that day), `prom/prometheus:v3.16.0`, `grafana/grafana:13.3.1`.

**Caveats, so you can judge the numbers.** The host was shared with other workloads (load average 11–21 on
12 CPUs during the runs), which inflates tail latency. Because image pulls were stalling, the main sweep used the
**k6 v2.4.0 release binary on the host** (`K6_BIN`, same version as the pinned image), against the published
port. The containerised path (`./sweep.sh` with `grafana/k6:2.4.0` on the compose network) was run separately at
50 requests/s and gave matching results (W = 12.6 ms, p99 = 56.5 ms, L = λW = 0.63).

**Observed, default settings** (`WORKERS=1`, `SERVICE_MS=10`, `DIST=exp`, 30 s per step). The "D/M/1 mean"
column was computed with `predict.py --measured` from each run's measured utilisation:

| Rate (req/s) | Measured ρ | Server mean W | D/M/1 mean | k6 p50 | k6 p99 | L | λ × W |
|---|---|---|---|---|---|---|---|
| 20 | 0.198 | 10.5 ms | 10.0 ms | 9.6 ms | 56.2 ms | 0.21 | 0.21 |
| 40 | 0.388 | 10.9 ms | 10.7 ms | 9.1 ms | 47.3 ms | 0.436 | 0.436 |
| 60 | 0.596 | 15.2 ms | 14.6 ms | 11.7 ms | 93.7 ms | 0.91 | 0.911 |
| 70 | 0.701 | 18.1 ms | 18.9 ms | 14.7 ms | 79.9 ms | 1.269 | 1.269 |
| 80 | 0.813 | 27.4 ms | 29.1 ms | 22.6 ms | 95.5 ms | 2.192 | 2.193 |
| 90 | 0.939 | 154.8 ms | 87.8 ms | 93.5 ms | 522.9 ms | 13.924 | 13.925 |
| 95 | 0.952 | 88.8 ms | 106.6 ms | 78.3 ms | 313.3 ms | 8.435 | 8.436 |
| 110 | 0.996 | 1,290 ms | unstable | 1,246 ms | 2,219 ms | 128.3 | 128.3 |

What this shows:
- Up to ρ ≈ 0.8, the measured mean W is within about 6% of the D/M/1 prediction.
- At 90–95 requests/s, single 30 s runs are noisy (90 requests/s came out *slower* than 95).
- At 110 requests/s, throughput capped at 99.4 requests/s and k6 reported 120 dropped iterations.
- Little's law held at every step: L and λW agree to within 0.001.

**Other experiments, as run:**
- **Repeatability (experiment 7).** Two 90 s runs at 90 requests/s gave W = 177 ms (p99 1,225 ms) and W = 65 ms
  (p99 276 ms). That is a 2.7× spread between identical runs near saturation.
- **Constant service time (experiment 5, `DIST=const`).** At 90 requests/s, W = 11.4 ms and p99 = 24.9 ms. At
  95 requests/s, W = 15.7 ms and p99 = 46.0 ms. Compare W = 65–177 ms at 90 requests/s with exponential service.
- **Nominal vs real capacity (experiment 6, `MODE=cpu WORKERS=4`, nominal 400 requests/s).** 60 requests/s:
  W = 16.6 ms. 90 requests/s: throughput 84.7, W = 532 ms. 120 requests/s: throughput 79.6, W = 2.8 s, 359
  dropped iterations. Real capacity was about 80–85 requests/s.
- **Observability profile.** Prometheus scraped the service (target `up`). k6's `experimental-prometheus-rw`
  output wrote `k6_http_req_duration_{p50,p90,p99,avg}` series, which arrive in seconds. Grafana provisioned
  the "L01 - saturation point" dashboard and its Prometheus datasource. Both were checked through the Grafana
  HTTP API (dashboard search, and a datasource-proxied `histogram_quantile` query). The dashboard was *not*
  inspected visually in a browser.
- Torn down with `docker compose -p sd-01 --profile observe --profile tools down -v`. No sd-01 containers or
  volumes remained.

## Troubleshooting

- **`dropped_iterations` at low rates:** k6 ran out of pre-allocated VUs. The script allocates
  `max(50, RATE)` and allows up to 3,000. On a very slow machine, raise `preAllocatedVUs` in `k6/load.js`.
- **Image pulls hang:** a busy or rate-limited registry. Pull the images one at a time (`docker pull grafana/k6:2.4.0`).
  Registry mirrors of Docker Hub, such as `mirror.gcr.io/grafana/k6:2.4.0`, serve the same image digest.
- **Port already in use:** another process holds 10101, 10130 or 10190. Change the left-hand side of the `ports:`
  mapping in `compose.yaml`.
- **Results much worse than predicted at low load:** the host is busy, and thread wake-ups are being delayed.
  Close other load generators, or check with `docker stats`.
- **No k6 data in Grafana:** run the sweep with `K6_OUT=experimental-prometheus-rw` and make sure the `observe`
  profile is up *before* the sweep.
