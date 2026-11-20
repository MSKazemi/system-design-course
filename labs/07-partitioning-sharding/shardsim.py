#!/usr/bin/env python3
"""shardsim — a dependency-free partitioning simulator for SYSDESIGN-07 (lab L07).

Compares four ways to map keys to nodes:
  modulo      hash(key) % n
  ring        consistent hashing (Karger et al., 1997) with V virtual nodes per node
  rendezvous  highest-random-weight hashing (Thaler & Ravishankar, 1998)
  jump        jump consistent hash (Lamping & Veach, 2014)

and runs four experiments: key movement on resize, load balance vs virtual nodes,
hot keys with and without key salting, and range vs hash partitioning of sequential keys.

Standard library only. Deterministic: all hashing uses BLAKE2b, all randomness uses a seed.
Run `python3 shardsim.py --help`.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import random
import statistics
from collections import Counter
from typing import Callable, Dict, List, Sequence


def h64(data: str) -> int:
    """Stable 64-bit hash (Python's built-in hash() is salted per process, so never use it here)."""
    return int.from_bytes(hashlib.blake2b(data.encode(), digest_size=8).digest(), "big")


# ---------------------------------------------------------------------------------------------
# Partitioners. Each exposes .name and .locate(key) -> node name.
# ---------------------------------------------------------------------------------------------
class Modulo:
    name = "modulo"

    def __init__(self, nodes: Sequence[str]):
        self.nodes = list(nodes)

    def locate(self, key: str) -> str:
        return self.nodes[h64(key) % len(self.nodes)]


class Ring:
    """Consistent hashing ring. Each node owns `vnodes` points (tokens) on a 2^64 circle;
    a key belongs to the first token clockwise from hash(key)."""

    name = "ring"

    def __init__(self, nodes: Sequence[str], vnodes: int = 64):
        self.vnodes = vnodes
        self.name = f"ring(v={vnodes})"
        pts = []
        for n in nodes:
            for i in range(vnodes):
                pts.append((h64(f"{n}#vn{i}"), n))
        pts.sort()
        self._tokens = [t for t, _ in pts]
        self._owners = [o for _, o in pts]

    def locate(self, key: str) -> str:
        i = bisect.bisect_right(self._tokens, h64(key))
        return self._owners[i % len(self._owners)]


class Rendezvous:
    """Highest random weight: every node scores the key; the highest score wins. O(n) per lookup."""

    name = "rendezvous"

    def __init__(self, nodes: Sequence[str]):
        self.nodes = list(nodes)

    def locate(self, key: str) -> str:
        return max(self.nodes, key=lambda n: h64(f"{n}|{key}"))


def jump_hash(key: int, num_buckets: int) -> int:
    """Jump consistent hash, transcribed from the algorithm in Lamping & Veach (2014), Figure 1."""
    b, j = -1, 0
    key &= 0xFFFFFFFFFFFFFFFF
    while j < num_buckets:
        b = j
        key = (key * 2862933555777941757 + 1) & 0xFFFFFFFFFFFFFFFF
        j = int((b + 1) * (float(1 << 31) / float((key >> 33) + 1)))
    return b


class Jump:
    """Jump hash maps to bucket numbers 0..n-1, so nodes can only be added or removed at the end."""

    name = "jump"

    def __init__(self, nodes: Sequence[str]):
        self.nodes = list(nodes)

    def locate(self, key: str) -> str:
        return self.nodes[jump_hash(h64(key), len(self.nodes))]


def make(scheme: str, nodes: Sequence[str], vnodes: int = 64):
    if scheme == "modulo":
        return Modulo(nodes)
    if scheme == "ring":
        return Ring(nodes, vnodes)
    if scheme == "rendezvous":
        return Rendezvous(nodes)
    if scheme == "jump":
        return Jump(nodes)
    raise ValueError(scheme)


def node_names(n: int) -> List[str]:
    return [f"node-{i:02d}" for i in range(n)]


def keys(count: int, prefix: str = "user") -> List[str]:
    return [f"{prefix}:{i}" for i in range(count)]


# ---------------------------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------------------------
def moved_fraction(scheme: str, ks: Sequence[str], n_before: int, n_after: int, vnodes: int = 64) -> float:
    a = make(scheme, node_names(n_before), vnodes)
    b = make(scheme, node_names(n_after), vnodes)
    moved = sum(1 for k in ks if a.locate(k) != b.locate(k))
    return moved / len(ks)


def load_stats(part, ks: Sequence[str], weights: Sequence[float] | None = None) -> Dict[str, float]:
    c: Counter = Counter()
    if weights is None:
        for k in ks:
            c[part.locate(k)] += 1
    else:
        for k, w in zip(ks, weights):
            c[part.locate(k)] += w
    loads = list(c.values())
    mean = sum(loads) / len(loads)
    return {
        "max_over_mean": max(loads) / mean,
        "min_over_mean": min(loads) / mean,
        "cv": statistics.pstdev(loads) / mean,  # coefficient of variation
    }


def zipf_weights(n: int, s: float) -> List[float]:
    raw = [1.0 / (r ** s) for r in range(1, n + 1)]
    tot = sum(raw)
    return [x / tot for x in raw]


# ---------------------------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------------------------
def exp_movement(args) -> None:
    ks = keys(args.keys)
    print(f"# Experiment 1 - keys moved when growing {args.nodes} -> {args.nodes + 1} nodes "
          f"({args.keys} keys)")
    print(f"# ideal minimum = 1/{args.nodes + 1} = {1 / (args.nodes + 1):.3%}")
    print(f"{'scheme':<14}{'moved':>10}")
    for s in ("modulo", "ring", "rendezvous", "jump"):
        f = moved_fraction(s, ks, args.nodes, args.nodes + 1, args.vnodes)
        label = f"ring(v={args.vnodes})" if s == "ring" else s
        print(f"{label:<14}{f:>10.3%}")


def exp_balance(args) -> None:
    ks = keys(args.keys)
    nodes = node_names(args.nodes)
    print(f"# Experiment 2 - load balance across {args.nodes} nodes, {args.keys} uniform keys")
    print(f"{'scheme':<16}{'max/mean':>10}{'min/mean':>10}{'CV':>8}")
    for v in (1, 8, 64, 256):
        st = load_stats(Ring(nodes, v), ks)
        print(f"{'ring(v=' + str(v) + ')':<16}{st['max_over_mean']:>10.3f}{st['min_over_mean']:>10.3f}{st['cv']:>8.3f}")
    for s in ("modulo", "rendezvous", "jump"):
        st = load_stats(make(s, nodes), ks)
        print(f"{s:<16}{st['max_over_mean']:>10.3f}{st['min_over_mean']:>10.3f}{st['cv']:>8.3f}")


def exp_hotkey(args) -> None:
    """Zipf-distributed request weights over keys; the top key is very hot.
    Salting appends a suffix 0..S-1 to the hottest keys so their traffic spreads over S sub-keys."""
    nodes = node_names(args.nodes)
    ring = Ring(nodes, args.vnodes)
    ks = keys(args.keys, "item")
    w = zipf_weights(len(ks), args.zipf)
    print(f"# Experiment 3 - hot keys: Zipf s={args.zipf} over {args.keys} keys, {args.nodes} nodes")
    print(f"# hottest key alone carries {w[0]:.2%} of all requests "
          f"(a perfectly even node share is {1 / args.nodes:.2%})")
    print(f"{'salt buckets':<14}{'hot keys salted':>16}{'max/mean':>10}{'busiest node share':>20}")
    for salt in (1, 4, 16, 64):
        salted_k: List[str] = []
        salted_w: List[float] = []
        for rank, (k, wt) in enumerate(zip(ks, w)):
            if salt > 1 and rank < args.hot:
                for i in range(salt):
                    salted_k.append(f"{k}#{i}")
                    salted_w.append(wt / salt)
            else:
                salted_k.append(k)
                salted_w.append(wt)
        st = load_stats(ring, salted_k, salted_w)
        share = st["max_over_mean"] / args.nodes
        print(f"{salt:<14}{(args.hot if salt > 1 else 0):>16}{st['max_over_mean']:>10.3f}{share:>20.2%}")
    print("# cost of salting: a read of a salted key must fan out to all S sub-keys (or pick one at random\n"
          "# for idempotent counters and merge later).")


def exp_range(args) -> None:
    """Writes with monotonically increasing keys (timestamps / auto-increment ids)."""
    nodes = node_names(args.nodes)
    n_writes = args.keys
    start = 1_700_000_000_000
    # Range partitioning: split the key space observed so far into equal-width ranges, as if
    # boundaries were set from yesterday's data. All new keys are larger than every boundary.
    boundaries = [start + (i + 1) * (n_writes // args.nodes) for i in range(args.nodes - 1)]
    rng = random.Random(7)
    new_keys = sorted(start + n_writes + rng.randrange(0, 10 * n_writes) for _ in range(n_writes))
    rc: Counter = Counter(nodes[bisect.bisect_right(boundaries, k)] for k in new_keys)
    ring = Ring(nodes, args.vnodes)
    hc: Counter = Counter(ring.locate(str(k)) for k in new_keys)
    print(f"# Experiment 4 - {n_writes} new writes with increasing timestamp keys, {args.nodes} nodes")
    print(f"{'scheme':<22}{'busiest node share':>20}{'nodes receiving writes':>24}")
    print(f"{'range (fixed bounds)':<22}{max(rc.values()) / n_writes:>20.2%}{len(rc):>24}")
    print(f"{'hash ring':<22}{max(hc.values()) / n_writes:>20.2%}{len(hc):>24}")
    print("# range keeps scans cheap but sends every new key to the last range; hash spreads writes but\n"
          "# turns a time-range scan into a scatter-gather over every node.")


def exp_lookup_cost(args) -> None:
    import time
    nodes = node_names(args.nodes)
    ks = keys(20_000)
    print(f"# Experiment 5 - lookup cost, {args.nodes} nodes, 20000 lookups (pure Python, relative only)")
    for s in ("modulo", "ring", "rendezvous", "jump"):
        p = make(s, nodes, args.vnodes)
        t0 = time.perf_counter()
        for k in ks:
            p.locate(k)
        dt = time.perf_counter() - t0
        label = f"ring(v={args.vnodes})" if s == "ring" else s
        print(f"{label:<14}{dt * 1e6 / len(ks):>8.2f} us/lookup")


EXPERIMENTS: Dict[str, Callable] = {
    "movement": exp_movement,
    "balance": exp_balance,
    "hotkey": exp_hotkey,
    "range": exp_range,
    "lookup": exp_lookup_cost,
}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("experiment", choices=[*EXPERIMENTS, "all"])
    ap.add_argument("--keys", type=int, default=100_000, help="number of keys (default 100000)")
    ap.add_argument("--nodes", type=int, default=10, help="number of nodes (default 10)")
    ap.add_argument("--vnodes", type=int, default=64, help="virtual nodes per node for the ring (default 64)")
    ap.add_argument("--zipf", type=float, default=1.1, help="Zipf exponent for the hot-key experiment")
    ap.add_argument("--hot", type=int, default=10, help="how many of the hottest keys to salt")
    args = ap.parse_args(argv)
    names = list(EXPERIMENTS) if args.experiment == "all" else [args.experiment]
    for i, n in enumerate(names):
        if i:
            print()
        EXPERIMENTS[n](args)


if __name__ == "__main__":
    main()
