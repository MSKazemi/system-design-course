"""Lumen 'api' stand-in for lab L14.

Stdlib only, so the image is small and needs no package index.
  GET /          -> {"version": ..., "pod": ...}   (cheap; used to count canary traffic)
  GET /work      -> burns a little CPU, then answers  (used to drive the HPA)
  GET /healthz   -> liveness
  GET /readyz    -> readiness (503 for READY_DELAY_S seconds after start)
"""
import hashlib
import json
import os
import signal
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "v1")
POD = os.environ.get("POD_NAME", "unknown")
READY_DELAY_S = float(os.environ.get("READY_DELAY_S", "3"))
WORK_ROUNDS = int(os.environ.get("WORK_ROUNDS", "20000"))
STARTED = time.monotonic()
draining = threading.Event()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        if self.path == "/healthz":
            self._send(200, {"ok": True})
        elif self.path == "/readyz":
            ready = (time.monotonic() - STARTED) >= READY_DELAY_S and not draining.is_set()
            self._send(200 if ready else 503, {"ready": ready})
        elif self.path == "/work":
            h = b"lumen"
            for _ in range(WORK_ROUNDS):
                h = hashlib.sha256(h).digest()
            self._send(200, {"version": VERSION, "pod": POD, "digest": h.hex()[:8]})
        else:
            self._send(200, {"version": VERSION, "pod": POD})

    def log_message(self, *args) -> None:  # keep container logs quiet
        pass


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)

    def on_term(signum, frame):
        # Fail readiness first so endpoints drop this pod, then stop.
        draining.set()
        threading.Timer(5.0, server.shutdown).start()

    signal.signal(signal.SIGTERM, on_term)
    print(f"lumen-api {VERSION} listening on :8080", flush=True)
    server.serve_forever()
    sys.exit(0)


if __name__ == "__main__":
    main()
