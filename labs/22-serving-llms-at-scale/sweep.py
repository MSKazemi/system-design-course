#!/usr/bin/env python3
"""Lab L22 driver: concurrency sweep and prefix-cache experiment against a vLLM server.

Standard library only. Uses bench.py (same directory) as a subprocess so each run is isolated.

  python3 sweep.py concurrency --model Qwen/Qwen2.5-0.5B-Instruct --levels 1 2 4 8 16
  python3 sweep.py prefix      --model Qwen/Qwen2.5-0.5B-Instruct --shared-prefix-words 800
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def run_bench(url: str, model: str, *extra: str) -> dict:
    cmd = [sys.executable, os.path.join(HERE, "bench.py"), "--url", url, "--model", model, "--json", *extra]
    out = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if out.returncode != 0 and not out.stdout.strip():
        raise SystemExit(f"bench failed: {out.stderr.strip()}")
    return json.loads(out.stdout.strip().splitlines()[-1])


def scrape(url: str, names: tuple[str, ...]) -> dict[str, float]:
    """Sum Prometheus samples whose metric name matches one of `names` (labels ignored)."""
    text = urllib.request.urlopen(url.rstrip("/") + "/metrics", timeout=10).read().decode()
    vals: dict[str, float] = {n: 0.0 for n in names}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+([0-9.eE+-]+)$", line)
        if m and m.group(1) in vals:
            vals[m.group(1)] += float(m.group(3))
    return vals


def table(rows: list[dict], cols: list[str]) -> None:
    widths = [max(len(c), *(len(str(r.get(c))) for r in rows)) for c in cols]
    print("  ".join(c.rjust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(str(r.get(c)).rjust(w) for c, w in zip(cols, widths)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["concurrency", "prefix"])
    ap.add_argument("--url", default="http://localhost:12201")
    ap.add_argument("--model", required=True)
    ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    ap.add_argument("--requests-per-level", type=int, default=0, help="default: 2 × concurrency (min 4)")
    ap.add_argument("--prompt-words", type=int, default=64)
    ap.add_argument("--max-tokens", type=int, default=64)
    ap.add_argument("--shared-prefix-words", type=int, default=800)
    ap.add_argument("--prefix-requests", type=int, default=8)
    args = ap.parse_args()

    if args.mode == "concurrency":
        rows = []
        for c in args.levels:
            n = args.requests_per_level or max(4, 2 * c)
            r = run_bench(args.url, args.model, "--concurrency", str(c), "--requests", str(n),
                          "--prompt-words", str(args.prompt_words), "--max-tokens", str(args.max_tokens))
            rows.append(r)
            print(f"concurrency {c}: {r['output_tok_per_s']} out tok/s, TPOT p50 {r['tpot_ms_p50']} ms", file=sys.stderr)
        table(rows, ["concurrency", "requests", "errors", "ttft_ms_p50", "ttft_ms_p99", "tpot_ms_p50",
                     "itl_ms_p99", "output_tok_per_s", "req_per_s"])
        base = rows[0]["output_tok_per_s"] or 1
        print("\nthroughput gain vs first level:", ", ".join(f"c={r['concurrency']}: {r['output_tok_per_s'] / base:.2f}x" for r in rows))
        return 0

    names = ("vllm:prefix_cache_queries_total", "vllm:prefix_cache_hits_total",
             "vllm:prefix_cache_queries", "vllm:prefix_cache_hits")
    before = scrape(args.url, names)
    r = run_bench(args.url, args.model, "--concurrency", "1", "--requests", str(args.prefix_requests),
                  "--prompt-words", "16", "--shared-prefix-words", str(args.shared_prefix_words),
                  "--max-tokens", "16", "--warmup", "0")
    after = scrape(args.url, names)
    delta = {k: after[k] - before[k] for k in names if after[k] or before[k]}
    print(json.dumps({"bench": r, "prefix_cache_metric_deltas": delta}, indent=2))
    q = delta.get("vllm:prefix_cache_queries_total", delta.get("vllm:prefix_cache_queries", 0))
    h = delta.get("vllm:prefix_cache_hits_total", delta.get("vllm:prefix_cache_hits", 0))
    if q:
        print(f"\nprefix-cache hit rate during run: {h / q:.1%} ({h:.0f} of {q:.0f} prompt tokens)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
