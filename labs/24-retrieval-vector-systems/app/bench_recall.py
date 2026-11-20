"""L24 — exact vs approximate nearest-neighbour search in pgvector.

Measures, on synthetic clustered unit vectors:
  * storage: table and index sizes vs the 4*d+8 bytes/vector estimate
  * HNSW recall@k and latency as hnsw.ef_search varies
  * IVFFlat recall@k and latency as ivfflat.probes varies
  * filtered search: post-filtering shortfall and pgvector iterative index scans

Synthetic vectors are NOT real embeddings: they isolate the index behaviour from model quality.
Real embedding distributions are usually easier for graph indexes than this data; treat the
numbers you get as a property of *this* dataset on *your* machine, not as a benchmark.
"""
from __future__ import annotations

import argparse
import os
import statistics
import time

import numpy as np
import psycopg

PGURL = os.environ.get("PGURL", "postgresql://lumen:lumen-lab-only@localhost:12401/lumen")


def make_data(n: int, centers: np.ndarray, rng: np.random.Generator, spread: float) -> np.ndarray:
    """Points = random cluster centre + isotropic noise, then L2-normalised (cosine == inner product)."""
    assign = rng.integers(0, len(centers), size=n)
    x = centers[assign] + spread * rng.normal(size=(n, centers.shape[1])).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    return x.astype(np.float32)


def vec_literal(v: np.ndarray) -> str:
    return "[" + ",".join(f"{a:.6f}" for a in v) + "]"


def exact_topk(x: np.ndarray, q: np.ndarray, k: int, mask: np.ndarray | None = None) -> list[list[int]]:
    sims = q @ x.T  # unit vectors: cosine similarity == inner product
    if mask is not None:
        sims[:, ~mask] = -np.inf
    idx = np.argpartition(-sims, kth=k, axis=1)[:, :k]
    out = []
    for row, cand in zip(sims, idx):
        out.append([int(c) for c in cand[np.argsort(-row[cand])]])
    return out


def run_queries(cur, queries: np.ndarray, k: int, where: str = "") -> tuple[list[list[int]], list[float]]:
    results, lat = [], []
    sql = f"SELECT id FROM items {where} ORDER BY embedding <=> %s::vector LIMIT {k}"
    for qv in queries:
        lit = vec_literal(qv)
        t0 = time.perf_counter()
        cur.execute(sql, (lit,))
        rows = cur.fetchall()
        lat.append((time.perf_counter() - t0) * 1000)
        results.append([r[0] for r in rows])
    return results, lat


def recall(approx: list[list[int]], exact: list[list[int]], k: int) -> float:
    return statistics.mean(len(set(a[:k]) & set(e[:k])) / k for a, e in zip(approx, exact))


def pct(xs: list[float], p: float) -> float:
    s = sorted(xs)
    return s[min(len(s) - 1, int(round(p / 100 * (len(s) - 1))))]


def report(label: str, approx, lat, exact, k):
    print(f"  {label:<22} recall@{k}={recall(approx, exact, k):.3f}  "
          f"p50={pct(lat, 50):6.2f} ms  p95={pct(lat, 95):6.2f} ms")


def size(cur, rel: str) -> int:
    cur.execute("SELECT pg_total_relation_size(%s)", (rel,))
    return cur.fetchone()[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50_000)
    ap.add_argument("--dim", type=int, default=384)
    ap.add_argument("--clusters", type=int, default=200)
    ap.add_argument("--queries", type=int, default=200)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--tenants", type=int, default=100, help="filter column cardinality (1/tenants selectivity)")
    ap.add_argument("--spread", type=float, default=1.8, help="noise / centre scale; larger = overlapping clusters = harder")
    ap.add_argument("--seed", type=int, default=24)
    args = ap.parse_args()
    k = args.k

    rng = np.random.default_rng(args.seed)
    centers = rng.normal(size=(args.clusters, args.dim)).astype(np.float32)
    x = make_data(args.n, centers, rng, args.spread)
    q = make_data(args.queries, centers, rng, args.spread)  # same cluster centres, independent points
    tenant = (np.arange(args.n) % args.tenants).astype(np.int32)

    with psycopg.connect(PGURL, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute("DROP TABLE IF EXISTS items")
        cur.execute(f"CREATE TABLE items (id int PRIMARY KEY, tenant int NOT NULL, embedding vector({args.dim}) NOT NULL)")
        t0 = time.perf_counter()
        with cur.copy("COPY items (id, tenant, embedding) FROM STDIN") as cp:
            for i in range(args.n):
                cp.write_row((i, int(tenant[i]), vec_literal(x[i])))
        print(f"loaded {args.n} x {args.dim}-d vectors in {time.perf_counter() - t0:.1f} s")
        cur.execute("VACUUM ANALYZE items")

        est = args.n * (4 * args.dim + 8)
        print("\n[storage]")
        print(f"  estimate n*(4d+8)       = {est / 2**20:8.1f} MiB (raw vectors only)")
        print(f"  table (heap+toast+pkey) = {size(cur, 'items') / 2**20:8.1f} MiB")

        exact = exact_topk(x, q, k)

        print("\n[exact scan: no ANN index]")
        res, lat = run_queries(cur, q[:50], k)
        report("sequential scan", res, lat, exact[:50], k)

        print("\n[HNSW m=16 ef_construction=64]")
        t0 = time.perf_counter()
        cur.execute("CREATE INDEX items_hnsw ON items USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)")
        print(f"  build time {time.perf_counter() - t0:.1f} s, index size {size(cur, 'items_hnsw') / 2**20:.1f} MiB")
        for ef in (10, 20, 40, 80, 160, 320):
            cur.execute(f"SET hnsw.ef_search = {ef}")
            res, lat = run_queries(cur, q, k)
            report(f"ef_search={ef}", res, lat, exact, k)

        print("\n[filtered: WHERE tenant = t, selectivity 1/%d]" % args.tenants)
        mask_exact = []
        fq = q[:50]
        tq = [int(i % args.tenants) for i in range(len(fq))]
        for qi, t in zip(fq, tq):
            mask_exact.append(exact_topk(x, qi[None, :], k, mask=(tenant == t))[0])
        cur.execute("SET hnsw.ef_search = 40")
        for mode in ("off", "relaxed_order"):
            cur.execute(f"SET hnsw.iterative_scan = {mode}")
            got, lat = [], []
            for qi, t in zip(fq, tq):
                t0 = time.perf_counter()
                cur.execute(f"SELECT id FROM items WHERE tenant = %s ORDER BY embedding <=> %s::vector LIMIT {k}",
                            (t, vec_literal(qi)))
                got.append([r[0] for r in cur.fetchall()])
                lat.append((time.perf_counter() - t0) * 1000)
            avg_rows = statistics.mean(len(g) for g in got)
            print(f"  iterative_scan={mode:<13} avg rows returned={avg_rows:5.1f}/{k}  "
                  f"recall@{k}={recall(got, mask_exact, k):.3f}  p50={pct(lat, 50):.2f} ms")
        cur.execute("SET hnsw.iterative_scan = off")
        cur.execute("CREATE INDEX items_tenant ON items (tenant)")
        cur.execute("ANALYZE items")
        cur.execute("EXPLAIN SELECT id FROM items WHERE tenant = 7 ORDER BY embedding <=> %s::vector LIMIT 10",
                    (vec_literal(fq[0]),))
        plan = " -> ".join(r[0].strip().lstrip("-> ").split("  ")[0] for r in cur.fetchall()
                           if "Sort Key" not in r[0] and "Cond" not in r[0])
        print(f"  with a B-tree on tenant the planner chooses: {plan}")
        cur.execute("DROP INDEX items_tenant")
        cur.execute("DROP INDEX items_hnsw")

        lists = max(1, args.n // 1000)
        print(f"\n[IVFFlat lists={lists}]")
        t0 = time.perf_counter()
        cur.execute(f"CREATE INDEX items_ivf ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = {lists})")
        print(f"  build time {time.perf_counter() - t0:.1f} s, index size {size(cur, 'items_ivf') / 2**20:.1f} MiB")
        for probes in (1, 2, 4, 8, 16):
            cur.execute(f"SET ivfflat.probes = {probes}")
            res, lat = run_queries(cur, q, k)
            report(f"probes={probes}", res, lat, exact, k)


if __name__ == "__main__":
    main()
