"""Client fleet for lab L11 (retry storm). Standard library only.

Open-loop load: RPS new logical requests per second, no matter how the server
is doing (users keep arriving). Each logical request is handled with one of
several client policies. A Toxiproxy latency toxic is the *trigger*: it is added
for TRIGGER_S seconds and then removed. The question each scenario answers:
once the trigger is gone, does the system recover -- or does it stay down?

Scenarios
  none     one attempt, no retries
  naive    up to 3 immediate retries (4 attempts)
  backoff  up to 3 retries, capped exponential backoff with full jitter
  budget   backoff + jitter + retry budget (token bucket, ~10%) + circuit breaker
  shed     naive retries, but the server sheds requests it cannot finish
           before the caller's deadline (deadline-aware admission control)

Usage: python fleet.py [scenario ...]      (default: all five, in order)
"""

import asyncio
import errno
import json
import os
import random
import socket
import sys
import time
import urllib.request

PROXY_HOST = os.environ.get("PROXY_HOST", "toxiproxy")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8666"))
TOXI_API = os.environ.get("TOXI_API", "http://toxiproxy:8474")
BACKEND_API = os.environ.get("BACKEND_API", "http://backend:8081")  # admin port
UPSTREAM = os.environ.get("UPSTREAM", "backend:8080")

RPS = float(os.environ.get("RPS", "125"))
TIMEOUT_MS = float(os.environ.get("TIMEOUT_MS", "200"))
TOXIC_LATENCY_MS = int(os.environ.get("TOXIC_LATENCY_MS", "300"))
BASELINE_S = float(os.environ.get("BASELINE_S", "5"))
TRIGGER_S = float(os.environ.get("TRIGGER_S", "5"))
AFTER_S = float(os.environ.get("AFTER_S", "15"))
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "4"))
BACKOFF_BASE_MS = float(os.environ.get("BACKOFF_BASE_MS", "100"))
BACKOFF_CAP_MS = float(os.environ.get("BACKOFF_CAP_MS", "2000"))
SEED = int(os.environ.get("SEED", "11"))

ALL = ["none", "naive", "backoff", "budget", "shed"]


# ---------------------------------------------------------------- control plane
def http(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        return e.code, None


def ensure_proxy():
    code, _ = http("POST", f"{TOXI_API}/proxies",
                   {"name": "backend", "listen": f"0.0.0.0:{PROXY_PORT}", "upstream": UPSTREAM})
    if code not in (200, 201, 409):
        raise SystemExit(f"could not create toxiproxy proxy (HTTP {code})")
    http("DELETE", f"{TOXI_API}/proxies/backend/toxics/trigger")  # clean slate


def add_trigger():
    return http("POST", f"{TOXI_API}/proxies/backend/toxics",
                {"name": "trigger", "type": "latency", "stream": "downstream",
                 "toxicity": 1.0, "attributes": {"latency": TOXIC_LATENCY_MS, "jitter": 0}})[0]


def remove_trigger():
    return http("DELETE", f"{TOXI_API}/proxies/backend/toxics/trigger")[0]


def backend_stats():
    return http("GET", f"{BACKEND_API}/stats")[1]


# ---------------------------------------------------------------- client policies
class RetryBudget:
    """Token bucket: every first attempt deposits RATIO tokens, every retry spends 1."""

    def __init__(self, ratio=0.1, cap=10.0):
        self.ratio, self.cap, self.tokens = ratio, cap, cap

    def on_request(self):
        self.tokens = min(self.cap, self.tokens + self.ratio)

    def try_spend(self):
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class Breaker:
    """Closed -> open when >=50% of the last-second attempts failed (min 20).
    Open for OPEN_S, then half-open: let PROBES attempts through; all succeed -> closed."""

    OPEN_S, PROBES, WINDOW_S, MIN_CALLS, RATIO = 1.0, 5, 1.0, 20, 0.5

    def __init__(self):
        self.state, self.opened_at, self.window = "closed", 0.0, []
        self.probes_left = self.probe_ok = 0
        self.transitions = []

    def _set(self, s, now):
        if s != self.state:
            self.transitions.append((round(now, 2), s))
        self.state = s

    def allow(self, now):
        if self.state == "open":
            if now - self.opened_at < self.OPEN_S:
                return False
            self._set("half-open", now)
            self.probes_left, self.probe_ok = self.PROBES, 0
        if self.state == "half-open":
            if self.probes_left == 0:
                return False
            self.probes_left -= 1
        return True

    def record(self, now, ok):
        if self.state == "half-open":
            if not ok:
                self._set("open", now)
                self.opened_at = now
            else:
                self.probe_ok += 1
                if self.probe_ok >= self.PROBES:
                    self._set("closed", now)
                    self.window = []
            return
        self.window.append((now, ok))
        cutoff = now - self.WINDOW_S
        while self.window and self.window[0][0] < cutoff:
            self.window.pop(0)
        fails = sum(1 for _, k in self.window if not k)
        if len(self.window) >= self.MIN_CALLS and fails / len(self.window) >= self.RATIO:
            self._set("open", now)
            self.opened_at = now
            self.window = []


def quiesce(run_id, max_wait_s=90.0):
    """Start a new run on the backend and wait until leftovers from the previous
    scenario (queued threads, connections still in the accept backlog) are gone."""
    http("POST", f"{BACKEND_API}/reset?run={run_id}")
    deadline = time.monotonic() + max_wait_s
    last = None
    while time.monotonic() < deadline:
        time.sleep(1.0)
        st = backend_stats()
        sig = (st["stale"], st["dropped_on_reset"])
        if st["queued"] == 0 and sig == last:
            break
        last = sig
    http("POST", f"{BACKEND_API}/reset?run={run_id}")  # zero counters again


RUN = {"id": ""}
FAILS = {}            # failure reason -> count, for the current scenario
PROXY_ADDR = {"ip": None}


def resolve_proxy():
    # Resolve once. Calling open_connection() with a hostname would run a DNS
    # lookup in asyncio's small default thread pool for *every* attempt, and that
    # pool -- not the backend -- would become the bottleneck under retry storms.
    PROXY_ADDR["ip"] = socket.gethostbyname(PROXY_HOST)


async def attempt():
    """One HTTP attempt through Toxiproxy. Returns True on HTTP 200 within the timeout."""
    deadline = time.time() * 1000.0 + TIMEOUT_MS  # absolute deadline, propagated to the server

    async def go():
        reader, writer = await asyncio.open_connection(PROXY_ADDR["ip"], PROXY_PORT)
        try:
            writer.write(f"GET /work HTTP/1.0\r\nHost: backend\r\nX-Deadline-Ms: {deadline:.0f}"
                         f"\r\nX-Run: {RUN['id']}\r\n\r\n".encode())
            await writer.drain()
            status = await reader.readline()
            code = (status.split()[1:2] or [b"none"])[0].decode()
            if code != "200":
                FAILS[f"http_{code}"] = FAILS.get(f"http_{code}", 0) + 1
            return code == "200"
        finally:
            writer.close()
    try:
        return await asyncio.wait_for(go(), TIMEOUT_MS / 1000.0)
    except asyncio.TimeoutError:
        FAILS["timeout"] = FAILS.get("timeout", 0) + 1
        return False
    except OSError as e:
        key = f"{type(e).__name__}:{errno.errorcode.get(e.errno, e.errno)}"
        FAILS[key] = FAILS.get(key, 0) + 1
        return False


async def run_scenario(name):
    rng = random.Random(SEED)
    budget = RetryBudget() if name == "budget" else None
    breaker = Breaker() if name == "budget" else None
    retries = name != "none"
    jitter = name in ("backoff", "budget")
    total = BASELINE_S + TRIGGER_S + AFTER_S

    ensure_proxy()
    resolve_proxy()
    FAILS.clear()
    RUN["id"] = f"{name}-{int(time.time())}"
    await asyncio.to_thread(quiesce, RUN["id"])
    http("POST", f"{BACKEND_API}/config?shed={'1' if name == 'shed' else '0'}")

    logical = []          # (start_s, ok, latency_ms)
    attempts = []         # start_s of each attempt actually sent
    fast_fail = [0]       # attempts refused locally by the breaker
    t0 = time.monotonic()

    def now():
        return time.monotonic() - t0

    async def one_logical():
        start = now()
        if budget:
            budget.on_request()
        ok = False
        for i in range(MAX_ATTEMPTS if retries else 1):
            if i > 0:
                if budget and not budget.try_spend():
                    break
                if jitter:  # full jitter: sleep U(0, min(cap, base * 2^i))
                    await asyncio.sleep(rng.uniform(0, min(BACKOFF_CAP_MS, BACKOFF_BASE_MS * 2 ** i)) / 1000)
            if breaker and not breaker.allow(now()):
                fast_fail[0] += 1
                break
            attempts.append(now())
            ok = await attempt()
            if breaker:
                breaker.record(now(), ok)
            if ok:
                break
        logical.append((start, ok, (now() - start) * 1000))

    snaps = {}
    tasks = []
    marks = {"baseline": 0.0, "trigger": BASELINE_S, "after": BASELINE_S + TRIGGER_S,
             "recovery": BASELINE_S + TRIGGER_S + 5.0, "end": total}
    pending = sorted(marks.items(), key=lambda kv: kv[1])
    n = int(RPS * total)
    for k in range(n):
        target = k / RPS
        while pending and pending[0][1] <= target:
            label, _ = pending.pop(0)
            snaps[label] = await asyncio.to_thread(backend_stats)
            if label == "trigger":
                await asyncio.to_thread(add_trigger)
            elif label == "after":
                await asyncio.to_thread(remove_trigger)
        delay = target - now()
        if delay > 0:
            await asyncio.sleep(delay)
        tasks.append(asyncio.create_task(one_logical()))
    snaps["end"] = await asyncio.to_thread(backend_stats)
    await asyncio.wait(tasks, timeout=15)

    def window(lo, hi):
        lg = [x for x in logical if lo <= x[0] < hi]
        at = [a for a in attempts if lo <= a < hi]
        okc = sum(1 for x in lg if x[1])
        return {"logical": len(lg), "success_pct": round(100 * okc / len(lg), 1) if lg else 0.0,
                "client_amp": round(len(at) / len(lg), 2) if lg else 0.0}

    def arrivals(a, b):
        return snaps[b]["arrivals"] - snaps[a]["arrivals"]

    lat = sorted(x[2] for x in logical if x[1])

    def pct(p):
        return round(lat[min(len(lat) - 1, int(p / 100 * len(lat)))], 1) if lat else None

    res = {
        "scenario": name,
        "baseline": window(0, BASELINE_S),
        "trigger": window(BASELINE_S, BASELINE_S + TRIGGER_S),
        "after_0_5s": window(BASELINE_S + TRIGGER_S, BASELINE_S + TRIGGER_S + 5),
        "after_5_15s": window(BASELINE_S + TRIGGER_S + 5, total),
        "backend_rps": {
            "baseline": round(arrivals("baseline", "trigger") / BASELINE_S),
            "trigger": round(arrivals("trigger", "after") / TRIGGER_S),
            "after_5_15s": round(arrivals("recovery", "end") / (total - marks["recovery"])),
        },
        "backend": {k: snaps["end"][k] for k in ("served", "wasted", "shed", "max_queued")},
        "ok_latency_ms": {"p50": pct(50), "p99": pct(99)},
        "attempt_failures": dict(FAILS),
        "breaker_fast_fails": fast_fail[0],
        "breaker_transitions": breaker.transitions[:12] if breaker else [],
    }
    for t in tasks:
        t.cancel()
    remove_trigger()
    return res


def print_table(results):
    cap = backend_stats()
    capacity = cap["workers"] * 1000 / cap["service_ms"]
    print(f"\nOffered load {RPS:.0f} logical req/s; backend capacity ~{capacity:.0f} req/s; "
          f"client timeout {TIMEOUT_MS:.0f} ms; trigger = +{TOXIC_LATENCY_MS} ms latency "
          f"for {TRIGGER_S:.0f} s\n")
    hdr = (f"{'scenario':9} | {'success % base/trig/after0-5/after5-15':38} | "
           f"{'backend req/s base/trig/after5-15':33} | {'amp trig':8} | {'wasted':7} | "
           f"{'shed':6} | {'maxQ':6} | {'p50/p99 ms (ok)':15}")
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        s = "/".join(str(r[w]["success_pct"]) for w in ("baseline", "trigger", "after_0_5s", "after_5_15s"))
        b = "/".join(str(r["backend_rps"][w]) for w in ("baseline", "trigger", "after_5_15s"))
        lat = f"{r['ok_latency_ms']['p50']}/{r['ok_latency_ms']['p99']}"
        print(f"{r['scenario']:9} | {s:38} | {b:33} | {r['trigger']['client_amp']:<8} | "
              f"{r['backend']['wasted']:<7} | {r['backend']['shed']:<6} | "
              f"{r['backend']['max_queued']:<6} | {lat:15}")
    print()


async def main(names):
    results = []
    for name in names:
        print(f"== running scenario '{name}' "
              f"({BASELINE_S:.0f}s baseline, {TRIGGER_S:.0f}s trigger, {AFTER_S:.0f}s after) ...", flush=True)
        r = await run_scenario(name)
        print(json.dumps(r), flush=True)
        results.append(r)
    print_table(results)


if __name__ == "__main__":
    chosen = sys.argv[1:] or ALL
    bad = [c for c in chosen if c not in ALL]
    if bad:
        raise SystemExit(f"unknown scenario(s) {bad}; choose from {ALL}")
    asyncio.run(main(chosen))
