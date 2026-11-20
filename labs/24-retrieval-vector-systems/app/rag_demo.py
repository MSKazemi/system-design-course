"""L24 — a tiny, honest RAG retrieval stage: dense vs lexical vs hybrid (RRF), ACL-aware.

Steps: embed corpus with a local embedding model (any OpenAI-compatible /v1/embeddings server) -> store in pgvector with tenant/ACL metadata
-> answer labelled queries with three retrievers -> report recall@k, MRR and nDCG@k
-> show what an un-filtered retriever would leak -> optionally generate a cited answer.

Postgres full-text ranking (ts_rank_cd) is used as the lexical retriever. It is NOT BM25 (no IDF
saturation model); it stands in for "keyword search" in this lab only.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import urllib.request

import psycopg

from corpus import DOCS, QUERIES

PGURL = os.environ.get("PGURL", "postgresql://lumen:lumen-lab-only@localhost:12401/lumen")
EMBED_URL = os.environ.get("EMBED_URL", "http://localhost:12411/v1")
CHAT_URL = os.environ.get("CHAT_URL", "http://localhost:12412/v1")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")   # name is informational for llama.cpp
GEN_MODEL = os.environ.get("GEN_MODEL", "qwen2.5-0.5b-instruct")


def post(url: str, body: dict, timeout: float = 600) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def embed(texts: list[str]) -> list[list[float]]:
    out = post(EMBED_URL + "/embeddings", {"model": EMBED_MODEL, "input": texts})
    vecs = [d["embedding"] for d in sorted(out["data"], key=lambda d: d["index"])]
    # normalise so that cosine distance, inner product and L2 rank identically
    return [[a / (sum(b * b for b in v) ** 0.5) for a in v] for v in vecs]


def lit(v) -> str:
    return "[" + ",".join(f"{a:.6f}" for a in v) + "]"


def dense(cur, qv, tenant, groups, k):
    cur.execute("""SELECT id FROM docs WHERE tenant = %s AND acl = ANY(%s)
                   ORDER BY embedding <=> %s::vector LIMIT %s""", (tenant, list(groups), lit(qv), k))
    return [r[0] for r in cur.fetchall()]


def lexical(cur, q, tenant, groups, k):
    # OR the query terms together so that natural-language questions still match (plainto_tsquery ANDs them)
    terms = [t for t in re.findall(r"[A-Za-z0-9-]+", q) if len(t) > 1]
    tsq = " | ".join(f"'{t}'" for t in terms) or "''"
    cur.execute("""SELECT id FROM docs, to_tsquery('english', %s) query
                   WHERE tenant = %s AND acl = ANY(%s) AND tsv @@ query
                   ORDER BY ts_rank_cd(tsv, query) DESC LIMIT %s""", (tsq, tenant, list(groups), k))
    return [r[0] for r in cur.fetchall()]


def rrf(lists: list[list[str]], k: int, c: int = 60) -> list[str]:
    """Reciprocal rank fusion (Cormack, Clarke & Buettcher, SIGIR 2009): score = sum 1/(c + rank)."""
    score: dict[str, float] = {}
    for lst in lists:
        for rank, doc in enumerate(lst, start=1):
            score[doc] = score.get(doc, 0.0) + 1.0 / (c + rank)
    return [d for d, _ in sorted(score.items(), key=lambda kv: -kv[1])][:k]


def metrics(ranked: list[str], rel: set[str], k: int) -> tuple[float, float, float]:
    top = ranked[:k]
    rec = len(set(top) & rel) / len(rel)
    mrr = next((1 / i for i, d in enumerate(ranked, 1) if d in rel), 0.0)
    dcg = sum(1 / math.log2(i + 1) for i, d in enumerate(top, 1) if d in rel)
    idcg = sum(1 / math.log2(i + 1) for i in range(1, min(len(rel), k) + 1))
    return rec, mrr, dcg / idcg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--generate", action="store_true", help="also generate one cited answer with GEN_MODEL")
    args = ap.parse_args()
    k = args.k

    vecs = embed([f"{d[3]}. {d[4]}" for d in DOCS])
    dim = len(vecs[0])
    print(f"embedded {len(DOCS)} chunks, dimension {dim}")

    with psycopg.connect(PGURL, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute("DROP TABLE IF EXISTS docs")
        cur.execute(f"""CREATE TABLE docs (
            id text PRIMARY KEY, tenant text NOT NULL, acl text NOT NULL,
            title text NOT NULL, body text NOT NULL, embedding vector({dim}) NOT NULL,
            tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', title || ' ' || body)) STORED)""")
        for d, v in zip(DOCS, vecs):
            cur.execute("INSERT INTO docs VALUES (%s,%s,%s,%s,%s,%s::vector)", (*d, lit(v)))
        cur.execute("CREATE INDEX ON docs USING gin (tsv)")
        cur.execute("CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops)")
        cur.execute("CREATE INDEX ON docs (tenant, acl)")

        qvecs = embed([q[0] for q in QUERIES])
        scores = {"dense": [], "lexical": [], "hybrid-rrf": []}
        print(f"\n{'query':<48} {'dense':<18} {'lexical':<18} {'hybrid':<18} relevant")
        for (q, tenant, groups, rel), qv in zip(QUERIES, qvecs):
            dn = dense(cur, qv, tenant, groups, 10)
            lx = lexical(cur, q, tenant, groups, 10)
            hy = rrf([dn, lx], 10)
            for name, ranked in (("dense", dn), ("lexical", lx), ("hybrid-rrf", hy)):
                scores[name].append(metrics(ranked, rel, k))
            print(f"{q[:47]:<48} {','.join(dn[:2]):<18} {','.join(lx[:2]) or '-':<18} {','.join(hy[:2]):<18} {','.join(sorted(rel))}")

        print(f"\n{'retriever':<12} recall@{k}  MRR    nDCG@{k}   (n={len(QUERIES)} hand-labelled queries)")
        for name, rows in scores.items():
            r, m, n = (statistics.mean(c) for c in zip(*rows))
            print(f"{name:<12} {r:8.3f} {m:6.3f} {n:8.3f}")

        # ACL demonstration: the same question, with and without the ACL predicate
        q = "salary bands"
        qv = embed([q])[0]
        cur.execute("SELECT id, acl FROM docs WHERE tenant='fabrikam' ORDER BY embedding <=> %s::vector LIMIT 3", (lit(qv),))
        unfiltered = cur.fetchall()
        allowed = dense(cur, qv, "fabrikam", {"all"}, 3)
        print(f"\n[ACL] '{q}' for a fabrikam user in group 'all'")
        print(f"  without ACL filter: {unfiltered}   <- an 'hr' document would reach the prompt")
        print(f"  with ACL filter   : {allowed}")

        if args.generate:
            q, tenant, groups, _ = QUERIES[2]
            qv = embed([q])[0]
            ids = rrf([dense(cur, qv, tenant, groups, 10), lexical(cur, q, tenant, groups, 10)], 3)
            cur.execute("SELECT id, body FROM docs WHERE id = ANY(%s)", (ids,))
            ctx = "\n".join(f"[{i}] {b}" for i, b in cur.fetchall())
            prompt = (f"Answer using only the sources below and cite them like [nw-01].\n"
                      f"Sources:\n{ctx}\n\nQuestion: {q}\nAnswer:")
            out = post(CHAT_URL + "/chat/completions",
                       {"model": GEN_MODEL, "temperature": 0, "max_tokens": 120,
                        "messages": [{"role": "user", "content": prompt}]})["choices"][0]["message"]["content"]
            cited = set(re.findall(r"\[([a-z]{2}-\d{2})\]", out))
            print(f"\n[generate] {q}\n{out.strip()}")
            print(f"  cited={sorted(cited)}  retrieved={sorted(ids)}  "
                  f"citations outside retrieved set={sorted(cited - set(ids)) or 'none'}")


if __name__ == "__main__":
    main()
