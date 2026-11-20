# 12 — Exercises

Lesson: [SYSDESIGN-12 — Observability](../course/01-foundations/12-observability.md)

### 1. [Core] Pick the signal

For each question, name the signal you would reach for first and why: (a) "Is checkout slower than yesterday?"
(b) "Why did request `7f3a…` take 4 s?" (c) "Which function got more expensive after build 2.14?" (d) "Did user 812
receive an error at 10:03?"

<details><summary>Answer</summary>

(a) **Metrics** — a latency histogram per route compared across days; cheap, pre-aggregated, made for trends.
(b) **Traces** — the span tree shows which hop and which child span consumed the 4 s. (c) **Profiles** — a flame
graph diff between builds points at functions, which no other signal resolves to. (d) **Logs** (or traces if that
request was sampled) — a per-event record with the user attribute; metrics must not carry user IDs as labels.
Acceptable alternative for (d): a wide structured event store, which serves both (b) and (d).
</details>

### 2. [Core] Count the series

A latency histogram has 12 explicit bucket boundaries. Labels: `http.route` (25 values), `http.response.status_code`
(8), `k8s.pod.name` (30). (a) How many series does it produce? (b) How many if you replace the status code with a
status *class* (2xx…5xx, 4 values seen)? (c) Someone adds `tenant.id` with 2,000 tenants. What now, and what would
you do?

<details><summary>Answer</summary>

Each label combination produces 12 + 1 (`+Inf`) bucket series plus `_sum` and `_count` = **15 series**.
(a) 15 × 25 × 8 × 30 = **90,000**. (b) 15 × 25 × 4 × 30 = **45,000** — status class halves it with almost no loss
for alerting. (c) 45,000 × 2,000 = **90 million** potential series — a cardinality explosion. Remove `tenant.id`
from the metric; keep it on spans and logs; if per-tenant SLOs are needed, aggregate per tenant *without* pod and
route (15 × 2,000 = 30,000), or compute them from traces/wide events. Also drop `k8s.pod.name` from long-retention
aggregates: per-pod detail is a debugging need, not an SLO need.
</details>

### 3. [Core] Burn-rate thresholds

An SLO is 99.9% over 30 days. (a) What error ratio corresponds to burn rate 14.4? (b) How much of the monthly budget
has been spent when a 1-hour-window alert at that rate fires? (c) At burn rate 14.4, when is the budget exhausted?

<details><summary>Answer</summary>

Budget B = 0.001. (a) 14.4 × 0.001 = **1.44%** errors. (b) 14.4 × 1 h / 720 h = **2%** of the budget — the SRE
Workbook's design point for the fastest page. (c) 30 days / 14.4 ≈ **2.08 days** (≈ 50 hours). The alert gives you
roughly two days of warning even if nobody acts, and pages early enough that most of the budget is still there.
</details>

### 4. [Deep] Why two windows?

Explain with a timeline why the Workbook pairs a 1-hour window with a 5-minute window, using a 30-minute total
outage that then fully recovers.

<details><summary>Answer</summary>

With only the 1-hour window, the alert fires during the outage (the 1-hour error ratio crosses the threshold after a
few minutes of 100% errors) but **keeps firing for up to an hour after recovery**, because the long window still
contains the bad 30 minutes. That is a bad *reset time*: on-call cannot tell whether a mitigation worked. Adding the
condition "and the 5-minute ratio is also above the threshold" makes the alert resolve about 5 minutes after errors
stop, while the long window still prevents paging on a 30-second blip (the 1-hour ratio would not cross the
threshold). The lab shows the same effect with windows divided by 12: the fast-burn alert resolves within about the
25-second short window after errors stop.
</details>

### 5. [Deep] Tail sampling design

You want 100% of error traces, 100% of traces slower than 1 s, and 5% of the rest, at 50,000 spans/s. Sketch the
collector topology and estimate the memory needed per gateway replica with `decision_wait` = 20 s, 800 bytes per
span in memory, and 4 gateway replicas. What breaks if you put a plain round-robin load balancer in front of the
gateways?

<details><summary>Answer</summary>

Topology: SDKs → per-node collector agents → **load-balancing exporter with `routing_key: traceID`** → N gateway
collectors running the `tail_sampling` processor with policies `status_code: ERROR`, `latency: threshold_ms 1000`,
and `probabilistic: 5%` → trace store. Compute span-derived RED metrics in the agents (before sampling).
Memory: 50,000 spans/s × 20 s × 800 B = 800 MB in flight in total, ≈ **200 MB per replica** with 4 replicas, plus
headroom (2–3×) for bursts and slow traces. With round-robin, spans of one trace land on different gateways; each
sees a partial trace, so error/latency policies make inconsistent decisions and you keep fragments. The tail
sampling processor's documentation states that all spans of a trace must reach the same instance.
</details>

### 6. [Core] RED and USE

Lumen's retrieval service calls a vector database over a connection pool of 50 connections. List the RED metrics for
the service and the USE metrics for the pool. Which would you alert on?

<details><summary>Answer</summary>

RED (service): request **rate** per route; **errors** per second (5xx, timeouts) or error ratio; **duration**
histogram per route. USE (pool): **utilisation** = connections in use / 50; **saturation** = callers waiting for a
connection (queue length, wait-time histogram); **errors** = connection failures/timeouts. Page on the service's SLO
burn rate (RED-derived), not on pool utilisation; use pool saturation as a diagnostic dashboard and maybe a ticket
alert, because a full pool only matters when users feel it.
</details>

### 7. [Interview] "Design monitoring for a new service"

You have 10 minutes in an interview to describe observability for a new chat service. Give your outline.

<details><summary>Answer</summary>

CLARIFY the key journeys (send message, load history) and their SLOs (e.g. 99.9% of sends acknowledged < 300 ms).
QUANTIFY traffic → spans/s and log bytes/s, and the error budget in messages per month. SKETCH: OTel SDK in every
service, collector agents per node, a gateway for tail sampling and redaction, metrics/logs/traces stores, Grafana-
style dashboards; correlation by `service.name` and trace ID; exemplars on latency histograms. DEEPEN: burn-rate
alerts (14.4/1h+5m, 6/6h+30m page; 1/3d+6h ticket), RED per service, USE for queues and WebSocket connection
counts. STRESS: monitoring outage (external probe, dead-man's switch), cardinality (no user/room IDs as labels),
cost at 10×. WRAP: trade-offs (sampling rate, retention, build vs buy). Strong candidates mention monitoring the
monitoring and alerting on symptoms.
</details>

### 8. [Deep] Percentiles across instances

Four pods report p99 latencies of 120, 130, 140 and 900 ms. Your dashboard shows "p99 = 322 ms". What went wrong,
and how should the fleet p99 be computed?

<details><summary>Answer</summary>

322.5 ms is the **average of four p99s**, which has no statistical meaning: the fleet p99 depends on how many
requests each pod served and on the shape of each distribution. If the 900 ms pod serves 25% of traffic, the fleet
p99 is likely near 900 ms, not 322. Compute it from **summed histogram buckets**:
`histogram_quantile(0.99, sum by (le) (rate(http_server_request_duration_seconds_bucket[5m])))`. This is why
histograms (or native/exponential histograms) are preferred over client-side summaries for anything aggregated.
</details>

### 9. [Frontier] GenAI telemetry

You instrument Lumen's LLM calls with OpenTelemetry GenAI conventions. Name three attributes or metrics you would
use, state their stability as of 2026-11, and list two risks.

<details><summary>Answer</summary>

Examples: span attributes `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`; metrics
`gen_ai.client.operation.duration`, `gen_ai.server.time_to_first_token`, `gen_ai.client.inference.usage.input_tokens`
/ `output_tokens`. As of 2026-11 they are all **Development** status, defined in the separate
`semantic-conventions-genai` repository, which had no tagged release when checked. Risks: (1) **names change** —
older instrumentations emit `gen_ai.client.token.usage`; pin versions and plan dashboard migrations; (2) **privacy and
cost** — prompt and completion content are opt-in attributes for a reason (personal data, secrets, large payloads);
keep them off by default and redact at the collector. A third acceptable risk: per-model label cardinality if
fine-tuned model names are unbounded.
</details>

### 10. [Lab] Read the burn-rate alert

In the lab you inject `error_rate=0.10` with an SLO of 99.5% and lab windows of 5 min / 25 s for the fast-burn rule.
(a) What burn rate do you expect? (b) Roughly how long after injection should `LumenErrorBudgetFastBurn` fire, and
why not immediately? (c) After you set `error_rate=0`, about how long until it resolves?

<details><summary>Answer</summary>

(a) 0.10 / 0.005 = **20×**. (b) The 25 s window crosses 7.2% within about half a minute, but the 5-minute window's
average must also exceed 7.2%: with a step from 0% to 10% that takes about 5 min × 7.2 / 10 ≈ **3.6 minutes**, plus
up to one rule-evaluation and metric-export interval (5 s each in the lab); the recorded run fired after
about 3 min 47 s. (c) The 25-second window falls below
7.2% within roughly **10–30 seconds** (about 10 s in the recorded test run), so the alert resolves even though the 5-minute window is still above the
threshold — the reset-time benefit of the short window. Your measured times will vary by a few export intervals.
</details>
