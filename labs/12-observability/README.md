# Lab L12 — Observability: RED metrics, traces, exemplars and burn-rate alerts

Lesson: [SYSDESIGN-12 — Observability](../../course/01-foundations/12-observability.md)

## Goal

Run a complete OpenTelemetry backend on your laptop, point a small instrumented Lumen "answer" service at it, and
practise the operational loop the lesson teaches: an SLO, multi-window multi-burn-rate alerts that fire and resolve,
the jump from a slow histogram bucket (exemplar) to the guilty span, logs correlated by trace ID, and a deliberate
cardinality explosion.

## What you will observe

- RED metrics (rate, errors, duration) from one `http.server.request.duration` histogram that follows the stable
  OpenTelemetry HTTP semantic conventions.
- The two burn-rate alerts from the Google SRE Workbook (14.4× and 6×), with every window **divided by 12** so they
  fire and resolve in minutes: 1 h → 5 min, 5 min → 25 s, 6 h → 30 min, 30 min → 150 s. Thresholds are unchanged.
- Why the short window matters: the fast-burn alert resolves seconds after errors stop.
- Exemplars: trace IDs attached to histogram buckets, leading to a trace whose `generate` span explains the latency.
- Log lines carrying `trace_id`/`span_id`.
- The series count of one metric jumping from tens to tens of thousands when `user.id` becomes a metric label.

## Prerequisites

| Tool | Version used for the test run |
|---|---|
| Docker Engine | 29.10.0 |
| Docker Compose | v5.8.0 |
| Python 3 on the host (for `slo_status.py`, stdlib only) | 3.12 or newer |

Images (pulled on first run; `grafana/otel-lgtm` is about 1 GB compressed, 3.8 GB on disk):

| Image | Contents |
|---|---|
| `grafana/otel-lgtm:0.41.0` | OpenTelemetry Collector v0.165.0, Prometheus v3.16.0, Tempo v3.1.1, Loki v3.7.9, Pyroscope v2.4.3, Grafana v13.3.0 (versions printed at start-up) |
| `python:3.15.2-slim-trixie` | base for the app; installs `opentelemetry-sdk` / `-api` / `-exporter-otlp-proto-http` 1.45.2 |
| `grafana/k6:2.4.0` | load generator (constant arrival rate) |

`grafana/otel-lgtm` is a development/demo image, not a production deployment [upstream README].

Ports (bound to 127.0.0.1 only): Grafana **11200**, Prometheus **11290**, the service **11280**, OTLP/HTTP **11218**.

Files:

```text
compose.yaml              project "sd-12": lgtm, api, load (profile "load")
app/app.py                instrumented service: traces, metrics (with exemplars), logs; /admin/fault for injection
config/prometheus.yaml    lgtm's own Prometheus config + evaluation_interval 5s + rule_files
config/slo-rules.yaml     SLI recording rules, burn rates, two multi-window burn-rate alerts (lab-speed windows)
load/answer.js            k6 script: RATE req/s for DURATION over USERS distinct users
slo_status.py             prints request rate, error ratios, burn rates, p99, series count and alert states
```

## Run

```bash
docker compose -p sd-12 up -d --build          # first run: image pulls + pip install
docker compose -p sd-12 ps                     # lgtm and api should be "healthy"

# In a second terminal: steady load, 20 req/s for 25 minutes (Ctrl-C to stop early)
DURATION=25m docker compose -p sd-12 run --rm load

# In a third terminal: the SLO view, refreshed every 5 s
python3 slo_status.py --watch
```

Open Grafana at <http://localhost:11200> (anonymous admin is enabled for the lab). Useful places:
**Explore → Prometheus** (queries below), **Explore → Tempo** (search `service.name = lumen-api`), **Explore →
Loki** (`{service_name="lumen-api"}`), and **Alerting → Alert rules** (the Prometheus-evaluated rules appear under
the Prometheus data source). The Prometheus UI is at <http://localhost:11290/alerts>.

Fault injection (any time):

```bash
curl -X POST 'http://localhost:11280/admin/fault?error_rate=0.10'    # 10% of answers return 503
curl -X POST 'http://localhost:11280/admin/fault?extra_ms=300'       # +300 ms in the "generate" step
curl -X POST 'http://localhost:11280/admin/fault?cardinality=on'     # add user.id as a metric label (bad!)
curl -X POST 'http://localhost:11280/admin/fault?error_rate=0&extra_ms=0&cardinality=off'   # reset
```

## Experiments

1. **Baseline RED.** With load running and no faults, find rate, errors and duration in Prometheus:

   ```promql
   sum(rate(http_server_request_duration_seconds_count{job="lumen-api"}[1m]))
   sum(rate(http_server_request_duration_seconds_count{job="lumen-api",http_response_status_code=~"5.."}[1m]))
   histogram_quantile(0.99, sum by (le) (rate(http_server_request_duration_seconds_bucket{job="lumen-api"}[1m])))
   ```

   Note how OTLP names were translated (`http.server.request.duration` with unit `s` →
   `http_server_request_duration_seconds_*`; `service.name` → `job`).

2. **Fast burn: page, then reset.** Inject `error_rate=0.10` and note the time. Predict: burn rate 0.10 / 0.005 =
   20×; the fast-burn rule needs the 5-minute ratio above 7.2%, which a step to 10% reaches after about
   5 × 7.2 / 10 ≈ 3.6 minutes. Watch `slo_status.py`. When `LumenErrorBudgetFastBurn` is firing, reset
   `error_rate=0` and time how long it takes to resolve. Which window made it resolve, and why does the slow-burn
   alert keep firing longer?

3. **Fresh series fool long windows.** If you inject errors soon after starting the stack, the *slow*-burn alert
   (30-minute window) may fire **before** the fast one. Explain: `rate()` over 30 minutes on a series that is only
   five minutes old averages over the data that exists, so the "long" window behaves like a short one. What does
   this imply for alerting on new services, or right after a metrics backend restart?

4. **From slow bucket to guilty span.** Inject `extra_ms=300`. After a minute, compare the p99 query and
   `lumen:sli_latency_bad:ratio_rate5m` (the share of requests slower than the 300 ms bucket). Then fetch exemplars
   for a slow bucket — in Grafana enable *Exemplars* on a histogram panel, or:

   ```bash
   now=$(date +%s); curl -s 'http://localhost:11290/api/v1/query_exemplars' \
     --data-urlencode 'query=http_server_request_duration_seconds_bucket{job="lumen-api",le="0.5"}' \
     --data-urlencode "start=$((now-60))" --data-urlencode "end=$now"
   ```

   Paste a `trace_id` into Tempo. Which span is slow? Now search Loki for the same trace ID.

5. **Cardinality explosion.** Reset faults, note `series for metric` in `slo_status.py`, then set
   `cardinality=on` for two minutes. Compare the series count and Prometheus's head series
   (`curl -s localhost:11290/api/v1/status/tsdb`). Count the distinct label values:

   ```promql
   count(count by (user_id) (http_server_request_duration_seconds_count{job="lumen-api"}))
   ```

   Where does `user.id` belong instead? (Look at the span attribute `lumen.user.id` in Tempo.)

6. **(Optional, not part of the recorded test) Head sampling.** Restart the service with
   `HEAD_SAMPLE_RATIO=0.1 docker compose -p sd-12 up -d api`, repeat experiment 2, and check how many error traces
   Tempo still has. Metrics stay complete because they are recorded independently of the trace sampler. Why would
   *tail* sampling (the Collector's `tail_sampling` processor) keep all error traces, and what would you need in
   front of it if you ran several gateway collectors?

## Expected results

- Baseline: request rate close to the configured `RATE`, zero 5xx, p99 around 0.2 s (the service's simulated work
  is ~80 ms mean with jitter; your numbers depend on the host).
- Experiment 2: burn rate (25 s) near 20 within half a minute; the fast-burn alert firing a few minutes after
  injection, close to the 3.6-minute estimate; after reset, the fast-burn alert resolving within tens of seconds
  while the 5-minute burn rate is still well above 14.4.
- Experiment 4: p99 rising above 0.5 s; exemplar trace whose `generate` span is ~0.3–0.4 s.
- Experiment 5: the series count of the metric growing by orders of magnitude (≈ 11 bucket series per distinct
  user), roughly proportional to the number of distinct users seen.

Your exact timings will differ by a few export (5 s) and evaluation (5 s) intervals.

## Clean up

```bash
# stop the k6 terminal first (Ctrl-C), then:
docker compose -p sd-12 --profile load down -v --remove-orphans
docker rmi sd-12-lumen-api:lab
# optional, frees ~3.8 GB:
docker rmi grafana/otel-lgtm:0.41.0
```

## Cost

€0 — everything runs locally.

## Test status

**runtime-tested** on 2026-11-20. Host: Ubuntu 24.04 (kernel 7.0.0-43-generic, x86_64), Docker 29.10.0, Compose
v5.8.0, `grafana/otel-lgtm:0.41.0` (Collector v0.165.0, Prometheus v3.16.0, Tempo v3.1.1, Loki v3.7.9, Grafana
v13.3.0), OpenTelemetry Python SDK 1.45.2 on Python 3.15.2. The full run used `grafana/k6:1.8.3`; the compose file
was then moved to `grafana/k6:2.4.0` (latest release) and the same script was re-run for 5 s against a stub server
on k6 2.4.0 without errors — the full experiment sequence was **not** repeated on 2.4.0. Observed:

- Baseline: 20.0 req/s, no 5xx, p99 0.194 s, 11 bucket series for the histogram.
- Experiment 2: errors injected at 00:31:12; 25 s burn rate 8.6–24 within 15–30 s; `LumenErrorBudgetFastBurn`
  firing at 00:34:59 (≈ 3 min 47 s after injection; 5-minute ratio 7.7%); reset at 00:36:50; at 00:37:00 the
  fast-burn alert had resolved (25 s burn rate 10.5, 5-minute burn rate 19.2) while `LumenErrorBudgetSlowBurn`
  kept firing (still firing at 00:37:51).
- Experiment 3 (observed by accident in the same run): `LumenErrorBudgetSlowBurn` fired at 00:32:27, ≈ 75 s after
  injection and before the fast-burn alert, because the stack had been running for only about five minutes.
- Experiment 4: with `extra_ms=300`, p99 0.733 s and `lumen:sli_latency_bad:ratio_rate5m` 0.19 after 75 s; an
  exemplar on the `le="0.5"` bucket (value 0.377 s) led to a Tempo trace with spans `retrieve` 19.1 ms, `generate`
  355.3 ms, `GET /api/answer` 376.7 ms. Loki returned the matching ERROR log lines with `trace_id` and `span_id`
  during experiment 2.
- Experiment 5: series of the histogram went from 33 (three service instances after restarts, 11 each) to 20,845
  after 120 s with `cardinality=on`; Prometheus head series 219 → 24,815; 1,893 distinct `user_id` values.
- Experiment 6 was not run.
- Two defects were found and fixed during testing: the error-ratio rules returned *no data* (instead of 0) before
  the first 5xx (fixed with `or vector(0)`), and exemplars were missing because the histogram was recorded after
  the span ended (fixed by recording inside the span). Experiments 4–5 ran on the fixed app.
- Stack removed with `docker compose -p sd-12 down -v` afterwards.

## Troubleshooting

- **`slo_status.py` shows `-` for everything**: no data yet — wait for two 5 s export intervals; check
  `docker compose -p sd-12 logs api`.
- **Rules show errors**: `curl -s localhost:11290/api/v1/rules`; after editing `config/slo-rules.yaml`, reload
  Prometheus by restarting the container (`docker compose -p sd-12 restart lgtm`).
- **No exemplars**: exemplars are only recorded for sampled spans; with `HEAD_SAMPLE_RATIO` below 1 there are
  fewer.
- **Port already in use**: change the left-hand side of the port mappings in `compose.yaml` (keep 11200–11299).
