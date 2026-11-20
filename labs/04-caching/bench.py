#!/usr/bin/env python3
"""bench.py — caching experiments for SYSDESIGN-04 (lab L04).

Experiments (run inside the `bench` container):
  aside     no cache vs cache-aside on a Zipf workload: hit ratio, p50/p99, database calls
  policy    Redis allkeys-lru vs allkeys-lfu under memory pressure, with and without a scan
  stampede  one hot key expiring under load: naive vs lock vs probabilistic early expiration (XFetch)
  race      the classic cache-aside stale-set race, then the same interleaving with a lease token
  all       everything above, in order

Everything printed is measured on your machine; nothing is hard-coded.
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import os
import random
import statistics
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import psycopg
import redis

PGURL = os.environ.get("PGURL", "postgresql://lumen:lumen-lab-only@localhost:10432/catalog")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379" if REDIS_HOST != "localhost" else "10479"))
N_ITEMS = 100_000

_local = threading.local()


def pg() -> psycopg.Connection:
    c = getattr(_local, "pg", None)
    if c is None:
        c = psycopg.connect(PGURL, autocommit=True)
        _local.pg = c
    return c


R = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True,
                max_connections=256, health_check_interval=0)


class Counter:
    def __init__(self):
        self.lock = threading.Lock()
        self.n = 0
        self.inflight = 0
        self.max_inflight = 0

    def enter(self):
        with self.lock:
            self.n += 1
            self.inflight += 1
            self.max_inflight = max(self.max_inflight, self.inflight)

    def leave(self):
        with self.lock:
            self.inflight -= 1


def pct(xs, p):
    if not xs:
        return float("nan")
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(math.ceil(p / 100 * len(xs))) - 1)]


class Zipf:
    """Zipf(s) over ranks 1..n, mapped through a fixed random permutation to product ids."""

    def __init__(self, n: int, s: float, seed: int = 42):
        w = [1.0 / (r ** s) for r in range(1, n + 1)]
        tot, acc, self.cdf = sum(w), 0.0, []
        for x in w:
            acc += x
            self.cdf.append(acc / tot)
        ids = list(range(1, n + 1))
        random.Random(seed).shuffle(ids)
        self.ids = ids

    def sample(self, rng: random.Random) -> int:
        return self.ids[bisect.bisect_left(self.cdf, rng.random())]


# --------------------------------------------------------------------------------------------
# Experiment 1: no cache vs cache-aside
# --------------------------------------------------------------------------------------------
def load_from_db(pid: int, calls: Counter) -> dict:
    calls.enter()
    try:
        row = pg().execute("SELECT * FROM get_product(%s)", (pid,)).fetchone()
    finally:
        calls.leave()
    return {"id": row[0], "name": row[1], "price": str(row[2]), "payload": row[3]}


def get_cache_aside(pid: int, calls: Counter, ttl: int) -> tuple[dict, bool]:
    key = f"product:{pid}"
    v = R.get(key)
    if v is not None:
        return json.loads(v), True
    obj = load_from_db(pid, calls)
    R.set(key, json.dumps(obj), ex=ttl)
    return obj, False


def run_workload(mode: str, n_req: int, threads: int, zipf: Zipf, ttl: int, seed: int) -> dict:
    calls, lat, hits = Counter(), [], [0]
    lk = threading.Lock()

    def worker(wid: int):
        rng = random.Random(seed * 1000 + wid)   # fresh request sequence per run
        mine, h = [], 0
        for _ in range(n_req // threads):
            pid = zipf.sample(rng)
            t0 = time.perf_counter()
            if mode == "nocache":
                load_from_db(pid, calls)
            else:
                _, hit = get_cache_aside(pid, calls, ttl)
                h += hit
            mine.append((time.perf_counter() - t0) * 1000)
        with lk:
            lat.extend(mine)
            hits[0] += h

    t0 = time.perf_counter()
    with ThreadPoolExecutor(threads) as ex:
        list(ex.map(worker, range(threads)))
    wall = time.perf_counter() - t0
    return {"mode": mode, "requests": len(lat), "db_calls": calls.n, "hit_ratio": hits[0] / len(lat),
            "p50_ms": pct(lat, 50), "p99_ms": pct(lat, 99), "throughput_rps": len(lat) / wall}


def exp_aside(a) -> None:
    print(f"# Experiment 1 - no cache vs cache-aside. Zipf s={a.zipf} over {N_ITEMS} ids, "
          f"{a.requests} requests, {a.threads} threads, DB call = 20 ms delay + PK lookup")
    R.config_set("maxmemory", "256mb")
    R.config_set("maxmemory-policy", "allkeys-lru")
    R.flushall()
    z = Zipf(N_ITEMS, a.zipf)
    print(f"{'run':<22}{'hit ratio':>10}{'DB calls':>10}{'p50 ms':>9}{'p99 ms':>9}{'req/s':>9}")
    rows = [("no cache", run_workload("nocache", a.requests, a.threads, z, 300, 1)),
            ("cache-aside, run 1", run_workload("aside", a.requests, a.threads, z, 300, 2)),
            ("cache-aside, run 2", run_workload("aside", a.requests, a.threads, z, 300, 3)),
            ("cache-aside, run 3", run_workload("aside", a.requests, a.threads, z, 300, 4))]
    for label, r in rows:
        print(f"{label:<22}{r['hit_ratio']:>10.1%}{r['db_calls']:>10}{r['p50_ms']:>9.2f}"
              f"{r['p99_ms']:>9.2f}{r['throughput_rps']:>9.0f}")
    print("# each run uses a fresh request sequence; the cache keeps what earlier runs loaded (TTL 300 s).\n"
          "# while more than 1% of requests miss, the p99 is a miss: compare it with the no-cache p50.")


# --------------------------------------------------------------------------------------------
# Experiment 2: eviction policy under memory pressure (synthetic 300-byte values, no DB)
# --------------------------------------------------------------------------------------------
def policy_run(policy: str, maxmem: str, zipf: Zipf, n_req: int, scan_frac: float) -> float:
    R.flushall()
    R.config_set("maxmemory", maxmem)
    R.config_set("maxmemory-policy", policy)
    R.config_resetstat()
    rng = random.Random(7)
    value = "x" * 300
    scan_id = 0
    hits = total = 0
    for i in range(2 * n_req):
        if rng.random() < scan_frac:
            scan_id += 1
            R.set(f"scan:{scan_id}", value)          # one-touch keys, never read again
            continue
        key = f"p:{zipf.sample(rng)}"
        v = R.get(key)
        measuring = i >= n_req                       # first half warms the cache
        if v is None:
            R.set(key, value)
        if measuring:
            total += 1
            hits += v is not None
    return hits / max(total, 1)


def exp_policy(a) -> None:
    z = Zipf(a.policy_keys, a.zipf)
    n = a.policy_requests
    print(f"# Experiment 2 - eviction policy. Zipf s={a.zipf} over {a.policy_keys} keys, 300-byte values, "
          f"{n} warm-up + {n} measured iterations")
    print(f"{'maxmemory':<11}{'workload':<30}{'allkeys-lru':>12}{'allkeys-lfu':>12}")
    for mem in a.policy_mem.split(","):
        for scan in (0.0, 0.5):
            lru = policy_run("allkeys-lru", mem, z, n, scan)
            lfu = policy_run("allkeys-lfu", mem, z, n, scan)
            label = "zipf only" if scan == 0 else f"zipf + {scan:.0%} one-touch writes"
            print(f"{mem:<11}{label:<30}{lru:>12.1%}{lfu:>12.1%}")
    R.config_set("maxmemory", "64mb")
    R.config_set("maxmemory-policy", "allkeys-lru")
    print("# hit ratios on the Zipf reads only; one-touch keys are written once and never read again\n"
          "# (a crawler, a batch export). LFU keeps frequently read keys; LRU lets the scan push them out.")


# --------------------------------------------------------------------------------------------
# Experiment 3: stampede on one hot key
# --------------------------------------------------------------------------------------------
def recompute(calls: Counter, cost_s: float) -> str:
    calls.enter()
    try:
        pg().execute("SELECT pg_sleep(%s)", (cost_s,))
    finally:
        calls.leave()
    return f"report@{time.time():.3f}"


def stampede_run(strategy: str, threads: int, duration: float, ttl: float, cost: float, beta: float,
                 think: float):
    key, lock_key = "hot:report", "lock:hot:report"
    R.delete(key, lock_key)
    calls, lat, misses = Counter(), [], [0]
    lk = threading.Lock()
    stop = time.time() + duration

    def get_naive():
        v = R.get(key)
        if v is None:
            with lk:
                misses[0] += 1
            v = recompute(calls, cost)
            R.set(key, v, px=int(ttl * 1000))
        return v

    def get_lock():
        for _ in range(200):
            v = R.get(key)
            if v is not None:
                return v
            if R.set(lock_key, "1", nx=True, px=int((cost + 1) * 1000)):
                v = R.get(key)                       # re-check: another client may have just refilled it
                if v is not None:
                    R.delete(lock_key)
                    return v
                with lk:
                    misses[0] += 1
                v = recompute(calls, cost)
                R.set(key, v, px=int(ttl * 1000))
                R.delete(lock_key)
                return v
            time.sleep(0.01)                         # someone else is recomputing: wait and re-read
        return recompute(calls, cost)                # give up waiting (should not happen here)

    def get_xfetch(rng: random.Random):
        raw = R.get(key)
        now = time.time()
        if raw is not None:
            obj = json.loads(raw)
            # Vattani et al. (2015): recompute early with probability rising as expiry nears.
            if now - obj["delta"] * beta * math.log(rng.random()) < obj["expiry"]:
                return obj["value"]
        else:
            with lk:
                misses[0] += 1
        t0 = time.time()
        v = recompute(calls, cost)
        delta = time.time() - t0
        R.set(key, json.dumps({"value": v, "delta": delta, "expiry": time.time() + ttl}), px=int(ttl * 1000))
        return v

    # Warm the key first so the experiment measures expiry, not the cold start (which XFetch cannot help).
    warm = recompute(Counter(), cost)
    if strategy == "xfetch":
        R.set(key, json.dumps({"value": warm, "delta": cost, "expiry": time.time() + ttl}), px=int(ttl * 1000))
    else:
        R.set(key, warm, px=int(ttl * 1000))
    stop = time.time() + duration

    def worker(wid: int):
        rng = random.Random(wid)
        mine = []
        while time.time() < stop:
            t0 = time.perf_counter()
            if strategy == "naive":
                get_naive()
            elif strategy == "lock":
                get_lock()
            else:
                get_xfetch(rng)
            mine.append((time.perf_counter() - t0) * 1000)
            time.sleep(think)
        with lk:
            lat.extend(mine)

    with ThreadPoolExecutor(threads) as ex:
        list(ex.map(worker, range(threads)))
    cycles = duration / ttl
    return {"strategy": strategy, "recomputes": calls.n, "per_ttl": calls.n / cycles,
            "max_parallel": calls.max_inflight, "misses": misses[0], "p99": pct(lat, 99),
            "p50": pct(lat, 50), "requests": len(lat)}


def exp_stampede(a) -> None:
    print(f"# Experiment 3 - stampede. One hot key, TTL {a.ttl}s, recompute cost {a.cost * 1000:.0f} ms, "
          f"{a.stampede_threads} clients for {a.duration}s (about {a.duration / a.ttl:.0f} expiries)")
    print(f"{'strategy':<10}{'requests':>9}{'recomputes':>11}{'per TTL':>9}{'max parallel':>13}"
          f"{'hard misses':>12}{'p50 ms':>8}{'p99 ms':>8}")
    for s in ("naive", "lock", "xfetch"):
        r = stampede_run(s, a.stampede_threads, a.duration, a.ttl, a.cost, a.beta, a.think)
        print(f"{s:<10}{r['requests']:>9}{r['recomputes']:>11}{r['per_ttl']:>9.1f}{r['max_parallel']:>13}"
              f"{r['misses']:>12}{r['p50']:>8.1f}{r['p99']:>8.1f}")
    print("# naive: every client that misses during the recompute window recomputes too.\n"
          "# lock: one recompute per expiry, but waiters block (p99 ~ recompute cost).\n"
          "# xfetch: the value is refreshed *before* expiry, so requests almost never miss; at high request\n"
          "#         rates several readers can draw an early refresh in the same window (pair it with a lock).")


# --------------------------------------------------------------------------------------------
# Experiment 4: stale-set race and the lease fix
# --------------------------------------------------------------------------------------------
LEASE_SET = """
if redis.call('GET', KEYS[2]) == ARGV[1] then
  redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[3])
  redis.call('DEL', KEYS[2])
  return 1
end
return 0
"""


def exp_race(a) -> None:
    pid, key, lease = 1, "product:1", "lease:product:1"
    print("# Experiment 4 - stale set. Reader misses and reads the DB, pauses 300 ms (GC, slow network),\n"
          "# meanwhile a writer updates the DB and deletes the cache key; then the reader writes its old copy.")
    lease_set = R.register_script(LEASE_SET)
    for use_lease in (False, True):
        conn = psycopg.connect(PGURL, autocommit=True)
        conn.execute("UPDATE products SET price = 10.00 WHERE id = %s", (pid,))
        R.delete(key, lease)
        token = str(uuid.uuid4())

        def reader():
            assert R.get(key) is None                # miss
            if use_lease:
                R.set(lease, token, nx=True, px=5000)
            c = psycopg.connect(PGURL, autocommit=True)
            price = c.execute("SELECT price FROM products WHERE id = %s", (pid,)).fetchone()[0]
            c.close()
            time.sleep(0.3)                          # the dangerous pause
            if use_lease:
                ok = lease_set(keys=[key, lease], args=[token, str(price), 300])
                return f"reader set {'ACCEPTED' if ok else 'REJECTED (lease invalidated)'}"
            R.set(key, str(price), ex=300)
            return "reader set ACCEPTED"

        def writer():
            time.sleep(0.1)
            c = psycopg.connect(PGURL, autocommit=True)
            c.execute("UPDATE products SET price = 20.00 WHERE id = %s", (pid,))
            c.close()
            R.delete(key, lease)                     # invalidation also kills any outstanding lease
            return "writer: DB price=20.00, cache key deleted"

        with ThreadPoolExecutor(2) as ex:
            fr, fw = ex.submit(reader), ex.submit(writer)
            msgs = [fw.result(), fr.result()]
        db_price = conn.execute("SELECT price FROM products WHERE id = %s", (pid,)).fetchone()[0]
        cached = R.get(key)
        verdict = "STALE until TTL" if cached is not None and cached != str(db_price) else "consistent"
        print(f"[{'lease' if use_lease else 'plain cache-aside'}] {msgs[0]}; {msgs[1]}; "
              f"DB={db_price} cache={cached} ttl={R.ttl(key)}s -> {verdict}")
        conn.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment", choices=["aside", "policy", "stampede", "race", "all"])
    ap.add_argument("--zipf", type=float, default=0.99, help="Zipf exponent (YCSB-style default 0.99)")
    ap.add_argument("--requests", type=int, default=20_000)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--policy-requests", type=int, default=40_000)
    ap.add_argument("--policy-keys", type=int, default=20_000)
    ap.add_argument("--policy-mem", default="3mb", help="comma-separated maxmemory values")
    ap.add_argument("--stampede-threads", type=int, default=50)
    ap.add_argument("--duration", type=float, default=20.0)
    ap.add_argument("--ttl", type=float, default=2.0)
    ap.add_argument("--cost", type=float, default=0.1, help="recompute cost in seconds")
    ap.add_argument("--beta", type=float, default=1.0, help="XFetch beta (>1 recomputes earlier)")
    ap.add_argument("--think", type=float, default=0.02, help="client pause between requests (s)")
    a = ap.parse_args()
    exps = {"aside": exp_aside, "policy": exp_policy, "stampede": exp_stampede, "race": exp_race}
    names = list(exps) if a.experiment == "all" else [a.experiment]
    for i, n in enumerate(names):
        if i:
            print()
        exps[n](a)


if __name__ == "__main__":
    main()
