# 12 — Observability (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement

- Lumen answer API: 99.5% availability SLO over 30 days
- Page within minutes when the budget burns fast; never page for blips
- Alert → guilty span in under five minutes
- Observability bill stays a small fraction of infrastructure

**Visual:** Pager icon, clock, budget gauge. Icons: `ops-alert`, `ops-slo`, `ops-cost`.

**Speaker notes:** Three goals that pull against each other: speed wants short windows, precision wants long
windows, and detail costs money. The chapter is about resolving that tension with design, not tools.

## Slide 2 — Monitoring vs observability

- Monitoring: questions you knew in advance
- Observability: questions you did not anticipate, answered from outputs
- Both needed: monitoring says *that*, observability helps find *why*

**Visual:** Two panels — fixed dashboard vs ad-hoc slicing by tenant/build/region. Icons: `ops-dashboard`, `ops-metrics`.

**Speaker notes:** Observability is a property you design in through names, attributes and identifiers, not a
product you buy.

## Slide 3 — Four signals

- Metrics: cheap numbers, cost scales with series
- Logs: per-event records, cost scales with traffic
- Traces: span trees across services, sampled
- Profiles: stack samples, "which function burns CPU"

**Visual:** 2×2 grid with "best for / worst for". Icons: `ops-metrics`, `ops-logs`, `ops-tracing`, `arch-cpu`.

**Speaker notes:** OpenTelemetry tracing, metrics and logs are stable; profiles entered public Alpha in 2026 and its
protocol is still marked development (as of 2026-11).

## Slide 4 — Correlation is the point

- Resource attributes: `service.name`, `service.version`, `k8s.pod.name`
- Trace context in spans, logs and exemplars
- W3C `traceparent`: version–trace-id–parent-id–flags
- Semantic conventions: same names in every language

**Visual:** Flow: alert → dashboard → exemplar → trace → logs/profile. Icons: `observability-opentelemetry`, `ops-tracing`.

**Speaker notes:** Four tools without shared identity are four places to look. The exemplar is the bridge from
"p99 is bad" to "here is one bad request".

## Slide 5 — RED, USE, golden signals

- RED per service: Rate, Errors, Duration (Wilkie)
- USE per resource: Utilisation, Saturation, Errors (Gregg)
- Golden signals: latency, traffic, errors, saturation (SRE book)
- RED on every boundary, USE on every queue, SLOs on key journeys

**Visual:** Service box with RED gauges; connection pool with USE gauges. Icons: `ops-latency`, `ops-throughput`, `ops-error`.

**Speaker notes:** RED maps onto a single latency histogram: count gives rate, filtered count gives errors, buckets
give duration.

## Slide 6 — Cardinality

- Each label combination = one time series
- series ≈ product of label value counts × buckets
- 13 × 3 × 20 × 6 = 4,680 series; add user.id (1M) → billions
- High-cardinality detail belongs on spans and logs

**Visual:** Multiplication tree exploding when `user.id` is added. Icons: `ops-metrics`, `ops-warning`.

**Speaker notes:** The Prometheus documentation explicitly warns against user IDs and other unbounded values as
labels. The lab reproduces the explosion.

## Slide 7 — SLOs, budgets, burn rate

- SLI = good / valid events; SLO 99.5% / 30 days
- Budget 0.5% ≈ 259,000 failed requests at 20 req/s
- Burn rate 1 = spend exactly the budget; 10 = spend it in 3 days
- Time to exhaust = 30 days / burn rate

**Visual:** Budget bar draining at different slopes. Icons: `ops-slo`, `ops-clock`.

**Speaker notes:** Burn rate turns an error ratio into "how soon do we run out", which is what decides whether a
human should wake up.

## Slide 8 — Multi-window, multi-burn-rate alerts

- Page: 14.4× over 1 h (2% budget) AND over 5 min
- Page: 6× over 6 h (5%) AND over 30 min
- Ticket: 1× over 3 d (10%) AND over 6 h
- Short window = 1/12 of long: fast reset

**Visual:** Decision diagram from SLO to three conditions. Icons: `ops-alert`, `observability-pagerduty`, `observability-prometheus`.

**Speaker notes:** These are the Google SRE Workbook's recommended starting values. For 99.5%, the fast page fires
above 7.2% errors in both windows.

## Slide 9 — Pipeline and sampling

- SDK → collector agent → gateway → stores
- Head sampling: cheap, consistent, blind to errors
- Tail sampling: keep errors and slow traces; stateful
- All spans of a trace must reach the same gateway (route by trace ID)

**Visual:** Agent/gateway topology with load-balancing exporter. Icons: `observability-opentelemetry`, `arch-load-balancer`, `arch-servers-cluster`.

**Speaker notes:** Dapper ran at 1/1024 and still had enough data for high-volume services. If you tail-sample,
compute RED metrics before the sampler.

## Slide 10 — Deep dive: histograms, eBPF and profiling

- Never average percentiles: sum buckets, then `histogram_quantile`, with a bucket boundary at the SLO threshold (e.g. 300 ms)
- Native/exponential histograms: stable opt-in in Prometheus 3.8
- eBPF: verified programs in the kernel, zero code changes; OBI v1.0.0 (2026-10-30) gives RED metrics and spans from traffic
- OTel eBPF profiler: whole-system CPU profiles
- Limits: Linux-only, privileges, no business context

**Visual:** Left: four p99 values averaged (wrong) vs merged histogram (right). Right: kernel layer under processes with probes. Icons: `ops-latency`, `observability-grafana`, `devops-linux`, `arch-cpu`, `observability-opentelemetry`.

**Speaker notes:** The average of four p99s is meaningless; the lab's SLI uses the `le="0.3"` bucket directly. Use eBPF
for coverage, SDK instrumentation for meaning. Profiles are Alpha in OTel as of 2026-11.

## Slide 11 — Frontier: GenAI telemetry and AIOps

- GenAI conventions: `gen_ai.*` spans, `gen_ai.client.inference.duration`, time to first chunk, token counters
- All Development status; moved to own repo in 2026
- Prompts/completions are opt-in (privacy)
- AIOps: hypotheses with evidence, humans approve actions

**Visual:** LLM call span with token counters; assistant suggestion with "show evidence" link. Icons: `domain-ai`, `ops-tracing`.

**Speaker notes:** Pin instrumentation versions; names have already changed (inference no longer goes on `gen_ai.client.operation.duration`). A 2023 Microsoft study found LLM
root-cause suggestions promising but not a replacement for engineers.

## Slide 12 — Failure modes and cost

- Cardinality explosion, pipeline outage, alert fatigue
- Monitoring in the same failure domain = blind when needed
- Cost knobs: series, bytes, retention, queries
- Sample traces, tier retention, label allow-lists

**Visual:** Table of failure → detector → mitigation. Icons: `ops-incident`, `ops-cost`.

**Speaker notes:** Always have an external probe that pages when the monitoring itself goes silent.

## Slide 13 — From page to postmortem

- Declare early (second team, customer-visible, or unsolved after an hour); IC, Ops, Comms (and planning), one living incident doc
- Mitigate first (roll back, flag off, shed load); then troubleshoot: what changed, bisect, test one hypothesis at a time
- On-call: ≤ 25% of time, 8-person single-site minimum, ≤ 2 incidents per 12-hour shift
- Error-budget policy: freeze non-P0 changes on SLO miss; >20% budget in one incident → postmortem with a P0 item
- Practise: "Wheel of Misfortune" role plays, game days with a seeded fault (DiRT at company scale)

**Visual:** Flow: burn-rate page → triage → declare + severity → roles → mitigate → resolve → postmortem → tracked action items. Icons: `ops-incident`, `ops-alert`, `ops-slo`, `ops-budget`, `observability-pagerduty`.

**Speaker notes:** For Lumen, a total outage crosses the 20% trigger after about 43 minutes and pages after about 4,
so the team has roughly 39 minutes to mitigate. Blameless means the postmortem names contributing causes, not
culprits, and every action item has an owner, a tracking number and a verifiable end state.

## Slide 14 — Interview angle and lab

- CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP
- Red flags: CPU pages, averaged percentiles, user IDs as labels
- Lab: otel-lgtm + instrumented service + k6
- Watch burn-rate alerts fire and resolve; cause a cardinality explosion

**Visual:** Lab topology: k6 → lumen-api → otel-lgtm (Grafana, Prometheus, Tempo, Loki). Icons: `observability-grafana`, `devops-docker`.

**Speaker notes:** In interviews, observability is usually the follow-up question "how would you know it works?";
answer with SLOs and burn rates, not with a list of tools.
