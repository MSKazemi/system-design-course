"""Capacity-limited HTTP backend for lab L11 (retry storm).

Standard library only. The server has WORKERS "worker slots" (a semaphore).
Every request waits for a slot, then "works" for SERVICE_MS milliseconds.
The wait for a slot is an unbounded queue by default, which is exactly the
hidden queue that turns a short trigger into a sustained overload.

Every request carries the caller's absolute deadline (header X-Deadline-Ms,
Unix epoch milliseconds; all containers share the host clock). Absolute time
matters: it also counts the time a connection waited in the kernel's accept
backlog, a queue the application cannot see.

Optional server-side protection (switched on per scenario by the fleet via
POST /config): when shedding is on, a request that cannot get a worker slot
early enough to finish before its deadline is rejected with 503 instead of
being served late -- deadline-aware admission control.

Endpoints on PORT (the data plane)
  GET  /work    the protected operation

Endpoints on ADMIN_PORT (a separate listener: a bulkhead, so the lab can still
read counters while the data-plane listener is drowning in connections)
  GET  /stats   JSON counters (arrivals, served, wasted, shed, queue depth)
  POST /reset   ?run=ID  drop the queued backlog (new generation), zero counters,
                and accept only /work requests carrying header X-Run: ID
  POST /config  ?shed=1|0  enable/disable deadline-aware shedding
"""

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

WORKERS = int(os.environ.get("WORKERS", "4"))
SERVICE_MS = float(os.environ.get("SERVICE_MS", "20"))
PORT = int(os.environ.get("PORT", "8080"))
ADMIN_PORT = int(os.environ.get("ADMIN_PORT", "8081"))

slots = threading.Semaphore(WORKERS)
lock = threading.Lock()
state = {"generation": 0, "shed": False, "run": ""}
stats = {}


def zero_stats():
    stats.update(arrivals=0, served=0, wasted=0, shed=0, dropped_on_reset=0,
                 stale=0, queued=0, max_queued=0)


zero_stats()


def bump(key, delta=1):
    with lock:
        stats[key] += delta
        if key == "queued" and stats["queued"] > stats["max_queued"]:
            stats["max_queued"] = stats["queued"]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def log_message(self, *args):  # keep container logs quiet
        pass

    def reply(self, code, body):
        data = body.encode()
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client already gave up; the work was wasted

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/stats" and self.server.server_address[1] == ADMIN_PORT:
            with lock:
                body = dict(stats, workers=WORKERS, service_ms=SERVICE_MS,
                            shed_enabled=state["shed"])
            return self.reply(200, json.dumps(body))
        if path != "/work":
            return self.reply(404, '{"error":"not found"}')

        if self.headers.get("X-Run", "") != state["run"]:
            # A connection left over from an earlier scenario (it sat in the kernel's
            # accept backlog). Drop it without work so scenarios start clean.
            bump("stale")
            return self.reply(503, '{"error":"stale run"}')
        gen = state["generation"]
        deadline_ms = float(self.headers.get("X-Deadline-Ms", "0") or 0)
        bump("arrivals")
        bump("queued")
        got = False
        try:
            if state["shed"] and deadline_ms > 0:
                # Wait at most until the caller's deadline minus the work itself;
                # if that moment has already passed, reject without waiting.
                budget = (deadline_ms - SERVICE_MS - time.time() * 1000.0) / 1000.0
                got = budget > 0 and slots.acquire(timeout=budget)
            else:
                # Unbounded FIFO wait: the hidden queue. (A /reset is noticed once the
                # slot is granted; stale work is then skipped instantly, so a backlog
                # drains quickly.)
                got = slots.acquire()
        finally:
            bump("queued", -1)

        if state["generation"] != gen:
            if got:
                slots.release()
            bump("dropped_on_reset")
            return self.reply(503, '{"error":"reset"}')
        if not got:
            bump("shed")
            return self.reply(503, '{"error":"shed: deadline cannot be met"}')

        try:
            time.sleep(SERVICE_MS / 1000.0)  # the "work"
        finally:
            slots.release()
        bump("served")
        if deadline_ms > 0 and time.time() * 1000.0 > deadline_ms:
            bump("wasted")  # finished after the caller's deadline: throughput, not goodput
        return self.reply(200, '{"ok":true}')

    def do_POST(self):
        url = urlparse(self.path)
        if self.server.server_address[1] != ADMIN_PORT:
            return self.reply(404, '{"error":"admin endpoints are on the admin port"}')
        if url.path == "/reset":
            with lock:
                state["generation"] += 1
                state["run"] = parse_qs(url.query).get("run", [""])[0]
            with lock:
                queued = stats["queued"]
                zero_stats()
                stats["queued"] = queued
            return self.reply(200, '{"reset":true}')
        if url.path == "/config":
            q = parse_qs(url.query)
            state["shed"] = q.get("shed", ["0"])[0] == "1"
            return self.reply(200, json.dumps({"shed": state["shed"]}))
        return self.reply(404, '{"error":"not found"}')


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 4096  # large listen backlog: queueing happens in the app


if __name__ == "__main__":
    print(f"backend: {WORKERS} workers x {SERVICE_MS} ms "
          f"=> capacity ~{WORKERS * 1000 / SERVICE_MS:.0f} req/s on :{PORT}", flush=True)
    admin = Server(("0.0.0.0", ADMIN_PORT), Handler)
    threading.Thread(target=admin.serve_forever, daemon=True).start()
    print(f"backend: admin endpoints on :{ADMIN_PORT}", flush=True)
    Server(("0.0.0.0", PORT), Handler).serve_forever()
