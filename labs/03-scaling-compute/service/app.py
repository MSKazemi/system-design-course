"""Lumen toy service (same as lab L01): a queue in front of a fixed number of workers.

Only the Python standard library is used. Every request to /work is placed in a
FIFO queue; WORKERS worker threads take jobs from it and "serve" each one for a
random service time with mean SERVICE_MS. This makes the service a textbook
queueing station whose capacity you can compute in advance:

    capacity (requests/s) = WORKERS / (SERVICE_MS / 1000)

Environment variables
    WORKERS     number of parallel workers (default 1)
    SERVICE_MS  mean service time in milliseconds (default 10)
    DIST        "exp" (exponential, default) or "const" (every job takes exactly SERVICE_MS)
    MODE        "sleep" (default: the worker waits, like a call to a slow dependency) or
                "cpu" (the worker burns SERVICE_MS of its own CPU time; Python's GIL then lets
                only one CPU-bound worker run at a time, whatever WORKERS says)
    NAME        identity returned in responses (default: hostname)
    DRAIN_S     on SIGTERM: report unhealthy, keep serving for DRAIN_S seconds, then exit
                (default 0 = exit immediately)
    PORT        listen port (default 8080)

Endpoints
    GET /work     queue one job; returns JSON with queue wait and service time
    GET /health   200 "ok", or 503 "draining" after SIGTERM when DRAIN_S > 0
    GET /stats    JSON: measured throughput, mean time in system W, time-averaged number in
                  system L, and utilisation, since start or since the last /reset
    GET /reset    reset the /stats window
    GET /metrics  Prometheus text exposition format
"""

import json
import os
import queue
import random
import signal
import socket
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

WORKERS = int(os.environ.get("WORKERS", "1"))
SERVICE_MS = float(os.environ.get("SERVICE_MS", "10"))
DIST = os.environ.get("DIST", "exp")
MODE = os.environ.get("MODE", "sleep")
NAME = os.environ.get("NAME", socket.gethostname())
DRAIN_S = float(os.environ.get("DRAIN_S", "0"))
PORT = int(os.environ.get("PORT", "8080"))

BUCKETS = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]

jobs: "queue.Queue[tuple[float, threading.Event, dict]]" = queue.Queue()
draining = threading.Event()


class Stats:
    """Counters for Little's law: L = lambda * W, measured independently."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.reset()
        # Lifetime counters for Prometheus (never reset).
        self.total_requests = 0
        self.total_busy = 0.0
        self.total_area = 0.0
        self.hist = [0] * (len(BUCKETS) + 1)
        self.hist_sum = 0.0

    def reset(self) -> None:
        now = time.monotonic()
        with getattr(self, "lock", threading.Lock()):
            self.t0 = now
            self.last = now
            self.in_system = getattr(self, "in_system", 0)
            self.area = 0.0          # integral of N(t) dt over the window
            self.completed = 0
            self.sum_w = 0.0         # sum of time-in-system of completed requests
            self.busy = 0.0          # sum of service times (worker-seconds)

    def _advance(self, now: float) -> None:
        dt = now - self.last
        self.area += self.in_system * dt
        self.total_area += self.in_system * dt
        self.last = now

    def arrive(self) -> None:
        with self.lock:
            self._advance(time.monotonic())
            self.in_system += 1

    def depart(self, w: float, service: float) -> None:
        with self.lock:
            self._advance(time.monotonic())
            self.in_system -= 1
            self.completed += 1
            self.sum_w += w
            self.busy += service
            self.total_requests += 1
            self.total_busy += service
            self.hist_sum += w
            for i, b in enumerate(BUCKETS):
                if w <= b:
                    self.hist[i] += 1
                    break
            else:
                self.hist[-1] += 1

    def snapshot(self) -> dict:
        with self.lock:
            now = time.monotonic()
            self._advance(now)
            elapsed = max(now - self.t0, 1e-9)
            lam = self.completed / elapsed
            w = self.sum_w / self.completed if self.completed else 0.0
            return {
                "name": NAME,
                "workers": WORKERS,
                "service_ms_mean": SERVICE_MS,
                "dist": DIST,
                "mode": MODE,
                "capacity_rps": WORKERS / (SERVICE_MS / 1000.0),
                "window_s": round(elapsed, 3),
                "completed": self.completed,
                "throughput_rps": round(lam, 3),
                "mean_w_ms": round(w * 1000, 3),
                "L_time_avg": round(self.area / elapsed, 3),
                "lambda_times_W": round(lam * w, 3),
                "utilisation": round(self.busy / (elapsed * WORKERS), 4),
                "in_system_now": self.in_system,
            }


stats = Stats()


def service_time() -> float:
    mean = SERVICE_MS / 1000.0
    return random.expovariate(1.0 / mean) if DIST == "exp" else mean


def worker() -> None:
    while True:
        enqueued, done, out = jobs.get()
        start = time.monotonic()
        s = service_time()
        if MODE == "cpu":
            # Burn s seconds of this thread's *CPU time*. Under the GIL only one thread runs
            # Python bytecode at a time, so CPU-bound workers share roughly one core.
            end = time.thread_time() + s
            x = 0
            while time.thread_time() < end:
                x += 1
        else:
            time.sleep(s)
        out["queued_ms"] = round((start - enqueued) * 1000, 3)
        out["service_ms"] = round((time.monotonic() - start) * 1000, 3)
        out["service_s"] = time.monotonic() - start
        done.set()


def prometheus_text() -> str:
    snap = stats.snapshot()
    with stats.lock:
        lines = [
            "# HELP lumen_requests_total Completed /work requests.",
            "# TYPE lumen_requests_total counter",
            f'lumen_requests_total{{name="{NAME}"}} {stats.total_requests}',
            "# HELP lumen_in_system Requests currently queued or in service.",
            "# TYPE lumen_in_system gauge",
            f'lumen_in_system{{name="{NAME}"}} {snap["in_system_now"]}',
            "# HELP lumen_in_system_seconds_total Integral of requests-in-system over time (for Little's law).",
            "# TYPE lumen_in_system_seconds_total counter",
            f'lumen_in_system_seconds_total{{name="{NAME}"}} {stats.total_area:.6f}',
            "# HELP lumen_busy_seconds_total Worker-seconds spent serving.",
            "# TYPE lumen_busy_seconds_total counter",
            f'lumen_busy_seconds_total{{name="{NAME}"}} {stats.total_busy:.6f}',
            "# HELP lumen_workers Configured workers.",
            "# TYPE lumen_workers gauge",
            f'lumen_workers{{name="{NAME}"}} {WORKERS}',
            "# HELP lumen_request_duration_seconds Time in system (queue + service) of /work requests.",
            "# TYPE lumen_request_duration_seconds histogram",
        ]
        cum = 0
        for b, c in zip(BUCKETS, stats.hist):
            cum += c
            lines.append(f'lumen_request_duration_seconds_bucket{{name="{NAME}",le="{b}"}} {cum}')
        cum += stats.hist[-1]
        lines.append(f'lumen_request_duration_seconds_bucket{{name="{NAME}",le="+Inf"}} {cum}')
        lines.append(f'lumen_request_duration_seconds_sum{{name="{NAME}"}} {stats.hist_sum:.6f}')
        lines.append(f'lumen_request_duration_seconds_count{{name="{NAME}"}} {cum}')
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"  # keep-alive, like real clients and proxies

    def log_message(self, fmt, *args):  # keep container logs quiet under load
        pass

    def _send(self, code: int, body: str, ctype: str = "application/json") -> None:
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if draining.is_set():
            self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/work":
            t0 = time.monotonic()
            stats.arrive()
            done, out = threading.Event(), {}
            jobs.put((t0, done, out))
            done.wait()
            w = time.monotonic() - t0
            stats.depart(w, out.pop("service_s"))
            out["name"] = NAME
            self._send(200, json.dumps(out))
        elif path == "/health":
            if draining.is_set():
                self._send(503, "draining\n", "text/plain")
            else:
                self._send(200, "ok\n", "text/plain")
        elif path == "/stats":
            self._send(200, json.dumps(stats.snapshot(), indent=1) + "\n")
        elif path == "/reset":
            stats.reset()
            self._send(200, "reset\n", "text/plain")
        elif path == "/metrics":
            self._send(200, prometheus_text(), "text/plain; version=0.0.4")
        else:
            self._send(404, "not found\n", "text/plain")


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 4096  # listen backlog; the default of 5 would refuse connections under load


def main() -> None:
    for _ in range(WORKERS):
        threading.Thread(target=worker, daemon=True).start()
    httpd = Server(("0.0.0.0", PORT), Handler)

    def on_sigterm(signum, frame):
        if DRAIN_S <= 0:
            print(f"{NAME}: SIGTERM, exiting immediately (DRAIN_S=0)", flush=True)
            os._exit(0)
        print(f"{NAME}: SIGTERM, draining for {DRAIN_S}s", flush=True)
        draining.set()

        def finish():
            time.sleep(DRAIN_S)
            print(f"{NAME}: drain complete, exiting", flush=True)
            os._exit(0)

        threading.Thread(target=finish, daemon=True).start()

    signal.signal(signal.SIGTERM, on_sigterm)
    cap = WORKERS / (SERVICE_MS / 1000.0)
    print(f"{NAME}: listening on :{PORT} workers={WORKERS} service_ms={SERVICE_MS} "
          f"dist={DIST} mode={MODE} capacity~{cap:.1f} rps", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    sys.exit(main())
