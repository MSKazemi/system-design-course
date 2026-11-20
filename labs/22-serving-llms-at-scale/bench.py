#!/usr/bin/env python3
"""Tiny, dependency-free streaming benchmark for OpenAI-compatible LLM servers.

Measures, per request: TTFT (time to first token), TPOT (time per output token
after the first), ITL (gaps between streamed chunks) and end-to-end latency;
and, per run: output tokens/s, total tokens/s, requests/s and goodput.

Standard library only (Python >= 3.10). Works against vLLM, llama.cpp
`llama-server` and Ollama's OpenAI-compatible endpoint.

Examples
  python3 bench.py --url http://localhost:12101 --model Qwen/Qwen2.5-0.5B-Instruct \
      --concurrency 1 --requests 4 --prompt-words 200 --max-tokens 64
  python3 bench.py ... --shared-prefix-words 600   # every request shares a long prefix
  python3 bench.py ... --json                       # machine-readable summary
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

WORDS = (
    "system design capacity latency throughput cache queue replica shard token "
    "gateway budget memory bandwidth scheduler batch prefill decode request user "
    "region failure retry timeout metric trace alert window storage index model"
).split()


def make_text(n_words: int, rng: random.Random) -> str:
    return " ".join(rng.choice(WORDS) for _ in range(n_words))


def pct(values: list[float], p: float) -> float:
    """Nearest-rank percentile; returns nan for empty input."""
    if not values:
        return float("nan")
    s = sorted(values)
    k = max(0, min(len(s) - 1, math.ceil(p / 100.0 * len(s)) - 1))
    return s[k]


def one_request(args, idx: int, shared_prefix: str) -> dict:
    rng = random.Random(args.seed * 1000 + idx)
    # A per-run, per-request nonce keeps the *unique* part of each prompt unique, so results are not
    # flattered by prefix-cache hits from earlier runs. Only --shared-prefix-words is meant to be shared.
    body_text = f"[req {args.seed}-{idx}] " + make_text(args.prompt_words, rng)
    prompt = (shared_prefix + "\n\n" if shared_prefix else "") + body_text
    payload = {
        "model": args.model,
        "prompt": prompt,
        "max_tokens": args.max_tokens,
        "temperature": 0.0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if args.ignore_eos:
        payload["ignore_eos"] = True  # vLLM / llama.cpp extension: force exactly max_tokens
    req = urllib.request.Request(
        args.url.rstrip("/") + "/v1/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    first = None
    last = None
    gaps: list[float] = []
    chunks = 0
    usage = None
    error = None
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            for raw in resp:  # SSE: lines of "data: {...}" separated by blank lines
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                obj = json.loads(data)
                if obj.get("usage"):
                    usage = obj["usage"]
                choices = obj.get("choices") or []
                if choices and choices[0].get("text"):
                    now = time.perf_counter()
                    if first is None:
                        first = now
                    else:
                        gaps.append(now - last)
                    last = now
                    chunks += 1
    except (urllib.error.URLError, OSError, ValueError) as exc:  # network, timeout, bad JSON
        error = repr(exc)
    t_end = time.perf_counter()
    out_tokens = (usage or {}).get("completion_tokens", chunks)
    in_tokens = (usage or {}).get("prompt_tokens", 0)
    ttft = (first - t0) if first is not None else float("nan")
    e2e = t_end - t0
    tpot = (e2e - ttft) / (out_tokens - 1) if out_tokens and out_tokens > 1 and first else float("nan")
    return {
        "idx": idx, "error": error, "ttft": ttft, "tpot": tpot, "e2e": e2e,
        "itl": gaps, "out_tokens": out_tokens, "in_tokens": in_tokens,
        "start": t0, "end": t_end,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default="http://localhost:12101")
    ap.add_argument("--model", required=True)
    ap.add_argument("--requests", type=int, default=8, help="total requests to send")
    ap.add_argument("--concurrency", type=int, default=1, help="requests in flight at once")
    ap.add_argument("--prompt-words", type=int, default=100, help="random words per prompt (unique part)")
    ap.add_argument("--shared-prefix-words", type=int, default=0, help="identical prefix prepended to every prompt")
    ap.add_argument("--max-tokens", type=int, default=64)
    ap.add_argument("--ignore-eos", action="store_true", default=True)
    ap.add_argument("--no-ignore-eos", dest="ignore_eos", action="store_false")
    ap.add_argument("--slo-ttft-ms", type=float, default=2000.0, help="TTFT SLO used for goodput")
    ap.add_argument("--slo-tpot-ms", type=float, default=200.0, help="TPOT SLO used for goodput")
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument("--seed", type=int, default=None, help="default: random per run (avoids cross-run cache hits)")
    ap.add_argument("--warmup", type=int, default=1, help="untimed warm-up requests")
    ap.add_argument("--json", action="store_true", help="print one JSON summary line")
    args = ap.parse_args()
    if args.seed is None:
        args.seed = random.SystemRandom().randrange(1, 10**9)

    shared = make_text(args.shared_prefix_words, random.Random(424242)) if args.shared_prefix_words else ""
    for w in range(args.warmup):
        one_request(args, -1 - w, "")

    results: list[dict] = []
    lock = threading.Lock()
    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        for r in pool.map(lambda i: one_request(args, i, shared), range(args.requests)):
            with lock:
                results.append(r)
    wall = time.perf_counter() - t_start

    ok = [r for r in results if not r["error"]]
    errs = [r for r in results if r["error"]]
    ttfts = [r["ttft"] * 1000 for r in ok if r["ttft"] == r["ttft"]]
    tpots = [r["tpot"] * 1000 for r in ok if r["tpot"] == r["tpot"]]
    itls = [g * 1000 for r in ok for g in r["itl"]]
    e2es = [r["e2e"] * 1000 for r in ok]
    out_tok = sum(r["out_tokens"] for r in ok)
    in_tok = sum(r["in_tokens"] for r in ok)
    good = [r for r in ok if r["ttft"] * 1000 <= args.slo_ttft_ms and (r["tpot"] != r["tpot"] or r["tpot"] * 1000 <= args.slo_tpot_ms)]

    summary = {
        "concurrency": args.concurrency, "requests": len(results), "errors": len(errs),
        "prompt_tokens_mean": round(in_tok / len(ok), 1) if ok else None,
        "output_tokens_mean": round(out_tok / len(ok), 1) if ok else None,
        "wall_s": round(wall, 2),
        "ttft_ms_p50": round(pct(ttfts, 50), 1), "ttft_ms_p99": round(pct(ttfts, 99), 1),
        "tpot_ms_p50": round(pct(tpots, 50), 1), "tpot_ms_p99": round(pct(tpots, 99), 1),
        "itl_ms_p50": round(pct(itls, 50), 1), "itl_ms_p99": round(pct(itls, 99), 1),
        "e2e_ms_p50": round(pct(e2es, 50), 1), "e2e_ms_p99": round(pct(e2es, 99), 1),
        "output_tok_per_s": round(out_tok / wall, 2) if wall else None,
        "total_tok_per_s": round((out_tok + in_tok) / wall, 2) if wall else None,
        "req_per_s": round(len(ok) / wall, 3) if wall else None,
        "goodput_req_per_s": round(len(good) / wall, 3) if wall else None,
        "mean_tpot_ms": round(statistics.fmean(tpots), 1) if tpots else None,
    }
    if args.json:
        print(json.dumps(summary))
    else:
        for k, v in summary.items():
            print(f"{k:>20}: {v}")
        if errs:
            print("first error:", errs[0]["error"], file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
