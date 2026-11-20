"""Driver for lab L10: fires bursts at five Redis-backed rate limiters and prints allowed/denied counts.

Usage (inside the compose network):
    python run_experiments.py --all
    python run_experiments.py --exp boundary --limit 10 --window-ms 10000
"""

from __future__ import annotations

import argparse
import os
import threading
import time
import uuid

import redis

from limiters import Limiters, naive_token_bucket

ALGOS = ["fixed_window", "sliding_log", "sliding_counter", "token_bucket", "gcra"]


def fresh_key(name: str) -> str:
    return f"{name}-{uuid.uuid4().hex[:8]}"


def table(title: str, rows: list[tuple], header: tuple) -> None:
    print(f"\n=== {title} ===")
    widths = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*header))
    print(fmt.format(*["-" * w for w in widths]))
    for row in rows:
        print(fmt.format(*row))


def fire(lim: Limiters, algo: str, key: str, times_ms: list[int]) -> tuple[int, int]:
    fn = lim.all()[algo]
    allowed = sum(1 for t in times_ms if fn(key, t).allowed)
    return allowed, len(times_ms) - allowed


def exp_boundary(lim: Limiters) -> None:
    """N requests just before a window boundary, N more just after: the fixed-window double burst."""
    n, w = lim.limit, lim.window_ms
    start = 100 * w                                  # virtual time aligned to a window boundary
    before = [start + w - 100 + i for i in range(n)]  # t = 9.900 s .. 9.909 s (for w = 10 s)
    after = [start + w + i for i in range(n)]         # t = 10.000 s .. 10.009 s
    rows = []
    for algo in ALGOS:
        key = fresh_key("boundary")
        a1, d1 = fire(lim, algo, key, before)
        a2, d2 = fire(lim, algo, key, after)
        rows.append((algo, f"{a1}/{n}", f"{a2}/{n}", a1 + a2, "<-- 2x the limit in ~0.1 s" if a1 + a2 > n else ""))
    table(f"Exp 1 boundary burst: limit={n} per {w} ms; {n} reqs at window_end-100ms, {n} at window_start",
          rows, ("algorithm", "allowed_before", "allowed_after", "total_in_~110ms", "note"))


def exp_sustained(lim: Limiters, seconds: int = 60, offered_factor: float = 2.0) -> None:
    """Offer `offered_factor` x the allowed rate, evenly spaced, after the burst allowance is used up."""
    w = lim.window_ms
    rate = lim.rate_per_s * offered_factor
    gap = 1000.0 / rate
    start = 200 * w
    times = [int(start + i * gap) for i in range(int(seconds * rate))]
    expected = lim.rate_per_s * seconds
    rows = []
    for algo in ALGOS:
        a, d = fire(lim, algo, fresh_key("sustained"), times)
        rows.append((algo, len(times), a, d, f"{a / seconds:.2f}"))
    table(f"Exp 2 sustained overload: offered {rate:.1f} req/s for {seconds} s (limit {lim.rate_per_s:.1f} req/s, "
          f"long-run ideal ~{expected:.0f} + burst)", rows, ("algorithm", "offered", "allowed", "denied", "allowed_per_s"))


def exp_idle_then_burst(lim: Limiters) -> None:
    """After idle: an instant burst of 3x the limit, then a second burst of 1x the limit half a window later."""
    n, w = lim.limit, lim.window_ms
    t1 = 300 * w + w // 2                            # mid-window
    t2 = t1 + w // 2                                 # exactly the next window boundary
    rows = []
    for algo in ALGOS:
        key = fresh_key("burst")
        a1, d1 = fire(lim, algo, key, [t1] * (3 * n))
        a2, d2 = fire(lim, algo, key, [t2] * n)
        rows.append((algo, f"{a1}/{3 * n}", f"{a2}/{n}"))
    table(f"Exp 3 bursts after idle: {3 * n} at t, then {n} at t+W/2 (limit={n}/window, W={w} ms)", rows,
          ("algorithm", "burst1_allowed", "burst2_allowed"))


def exp_race(r: redis.Redis, lim: Limiters, threads: int = 50) -> None:
    """Concurrent clients hit one key at the same real instant: naive read-modify-write vs atomic Lua."""
    rows = []
    for name in ("naive_get_then_set", "lua_token_bucket"):
        for trial in range(3):
            key = fresh_key("race")
            barrier = threading.Barrier(threads)
            results: list[bool] = []
            lock = threading.Lock()

            def worker() -> None:
                c = redis.Redis.from_url(os.environ["REDIS_URL"])
                lim_local = Limiters(c, lim.limit, lim.window_ms)
                barrier.wait()
                now = int(time.time() * 1000)
                if name == "naive_get_then_set":
                    ok = naive_token_bucket(c, key, now, lim.rate_per_s, lim.limit)
                else:
                    ok = lim_local.token_bucket(key, now).allowed
                with lock:
                    results.append(ok)

            ts = [threading.Thread(target=worker) for _ in range(threads)]
            for th in ts:
                th.start()
            for th in ts:
                th.join()
            allowed = sum(results)
            rows.append((name, trial + 1, threads, lim.limit, allowed,
                         "OVER-ADMITTED" if allowed > lim.limit else "ok"))
    table(f"Exp 4 race: {threads} concurrent clients, bucket capacity {lim.limit}", rows,
          ("implementation", "trial", "clients", "capacity", "allowed", "verdict"))


def exp_memory(r: redis.Redis, lim: Limiters) -> None:
    """State per client key after `limit` admitted requests."""
    n, w = lim.limit, lim.window_ms
    t0 = 400 * w
    rows = []
    for algo, prefix in (("fixed_window", "fw"), ("sliding_log", "sl"), ("sliding_counter", "sc"),
                         ("token_bucket", "tb"), ("gcra", "gc")):
        key = fresh_key("mem")
        fn = lim.all()[algo]
        for i in range(n):
            fn(key, t0 + i)
        total = 0
        for k in r.scan_iter(match=f"{prefix}:{key}*"):
            total += r.memory_usage(k) or 0
        rows.append((algo, n, total))
    table(f"Exp 5 Redis memory per client after {n} requests (MEMORY USAGE, bytes)", rows,
          ("algorithm", "requests", "bytes"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--exp", choices=["boundary", "sustained", "burst", "race", "memory"], action="append")
    p.add_argument("--all", action="store_true")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--window-ms", type=int, default=10_000)
    p.add_argument("--threads", type=int, default=50)
    args = p.parse_args()

    r = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:11079/0"))
    info = r.info("server")
    print(f"Redis {info['redis_version']} | redis-py {redis.__version__} | limit={args.limit} "
          f"window_ms={args.window_ms}")
    lim = Limiters(r, args.limit, args.window_ms)
    exps = ["boundary", "sustained", "burst", "race", "memory"] if args.all or not args.exp else args.exp
    for e in exps:
        if e == "boundary":
            exp_boundary(lim)
        elif e == "sustained":
            exp_sustained(lim)
        elif e == "burst":
            exp_idle_then_burst(lim)
        elif e == "race":
            exp_race(r, lim, args.threads)
        elif e == "memory":
            # a larger limit makes the log-vs-counter difference visible
            exp_memory(r, Limiters(r, max(args.limit, 1000), args.window_ms))
    print("\nDone.")


if __name__ == "__main__":
    main()
