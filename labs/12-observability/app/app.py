"""Lumen 'answer' API stand-in for lab L12, instrumented with the OpenTelemetry SDK.

Emits all three stable OTel signals over OTLP/HTTP to the collector inside grafana/otel-lgtm:
  * traces  - one SERVER span per request, with child spans "retrieve" and "generate"
  * metrics - http.server.request.duration (histogram, seconds), following the stable HTTP
              semantic conventions; exemplars link slow buckets to trace IDs
  * logs    - Python logging bridged to OTel, so every log line carries trace_id/span_id

Endpoints
  GET  /api/answer?user=<id>        the "product" endpoint
  GET  /healthz                     liveness (not instrumented)
  POST /admin/fault?error_rate=0.1&extra_ms=0&cardinality=off
                                    change behaviour at runtime (fault injection)
  GET  /admin/fault                 show the current fault settings
"""
from __future__ import annotations

import json
import logging
import os
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import extract
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from opentelemetry.trace import SpanKind, Status, StatusCode

# ---------------------------------------------------------------------------------------------
# SDK setup. Endpoint and service name come from the standard OTEL_* environment variables.
# ---------------------------------------------------------------------------------------------
resource = Resource.create(
    {
        "service.name": os.environ.get("OTEL_SERVICE_NAME", "lumen-api"),
        "service.version": os.environ.get("APP_VERSION", "1.0.0"),
        "deployment.environment.name": "lab",
    }
)

head_ratio = float(os.environ.get("HEAD_SAMPLE_RATIO", "1.0"))  # 1.0 = keep every trace
tracer_provider = TracerProvider(resource=resource, sampler=ParentBasedTraceIdRatio(head_ratio))
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("lumen.api")

# Bucket boundaries chosen around the 300 ms latency SLO threshold used in the lab.
latency_view = View(
    instrument_name="http.server.request.duration",
    aggregation=ExplicitBucketHistogramAggregation(
        [0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 2.0, 5.0]
    ),
)
export_ms = int(os.environ.get("OTEL_METRIC_EXPORT_INTERVAL", "5000"))
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(), export_interval_millis=export_ms)],
    views=[latency_view],
)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter("lumen.api")
request_duration = meter.create_histogram(
    "http.server.request.duration", unit="s", description="Duration of HTTP server requests."
)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
set_logger_provider(logger_provider)
log = logging.getLogger("lumen.api")
log.setLevel(logging.INFO)
log.addHandler(LoggingHandler(level=logging.INFO, logger_provider=logger_provider))
log.addHandler(logging.StreamHandler())

# ---------------------------------------------------------------------------------------------
# Fault-injection state, changed at runtime through /admin/fault.
# ---------------------------------------------------------------------------------------------
_lock = threading.Lock()
fault = {
    "error_rate": float(os.environ.get("ERROR_RATE", "0.0")),
    "extra_ms": float(os.environ.get("EXTRA_MS", "0")),
    "cardinality": os.environ.get("HIGH_CARDINALITY", "off"),  # "on" adds user.id to metrics (bad!)
}


def _sleep_ms(mean_ms: float) -> None:
    time.sleep(max(0.0, random.gauss(mean_ms, mean_ms * 0.3)) / 1000.0)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _reply(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args) -> None:  # silence the default access log
        pass

    # -- admin ------------------------------------------------------------------------------
    def do_POST(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        if url.path != "/admin/fault":
            return self._reply(404, {"error": "not found"})
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        with _lock:
            if "error_rate" in q:
                fault["error_rate"] = min(1.0, max(0.0, float(q["error_rate"])))
            if "extra_ms" in q:
                fault["extra_ms"] = max(0.0, float(q["extra_ms"]))
            if "cardinality" in q:
                fault["cardinality"] = "on" if q["cardinality"] == "on" else "off"
            snapshot = dict(fault)
        log.warning("fault settings changed: %s", snapshot)
        self._reply(200, snapshot)

    # -- product ----------------------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        url = urlparse(self.path)
        if url.path == "/healthz":
            return self._reply(200, {"ok": True})
        if url.path == "/admin/fault":
            with _lock:
                return self._reply(200, dict(fault))
        if url.path != "/api/answer":
            return self._reply(404, {"error": "not found"})

        user = parse_qs(url.query).get("user", ["anonymous"])[0]
        with _lock:
            cfg = dict(fault)
        start = time.perf_counter()
        status = 200
        ctx = extract(dict(self.headers))  # honour an incoming W3C traceparent
        with tracer.start_as_current_span(
            "GET /api/answer",
            context=ctx,
            kind=SpanKind.SERVER,
            attributes={"http.request.method": "GET", "http.route": "/api/answer", "url.path": url.path},
        ) as span:
            # High-cardinality data belongs on spans and logs, not on metric labels.
            span.set_attribute("lumen.user.id", user)
            with tracer.start_as_current_span("retrieve") as s:
                s.set_attribute("lumen.retrieve.k", 8)
                _sleep_ms(20)
            with tracer.start_as_current_span("generate"):
                _sleep_ms(60 + cfg["extra_ms"])
            if random.random() < cfg["error_rate"]:
                status = 503
                span.set_status(Status(StatusCode.ERROR, "injected failure"))
                span.set_attribute("error.type", "503")
                log.error("answer failed for user=%s (injected)", user)
            else:
                log.info("answered user=%s", user)
            span.set_attribute("http.response.status_code", status)

            attrs = {"http.request.method": "GET", "http.route": "/api/answer", "http.response.status_code": status}
            if status >= 500:
                attrs["error.type"] = str(status)
            if cfg["cardinality"] == "on":
                attrs["user.id"] = user  # the anti-pattern this lab demonstrates
            # Recorded while the span is still current, so the SDK's trace-based exemplar filter
            # attaches this request's trace_id/span_id as an exemplar on the histogram bucket.
            request_duration.record(time.perf_counter() - start, attrs)

        if status == 200:
            self._reply(200, {"answer": "42", "user": user})
        else:
            self._reply(status, {"error": "temporarily unavailable"})


def main() -> None:
    port = int(os.environ.get("PORT", "8080"))
    log.info("lumen-api listening on :%d", port)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
