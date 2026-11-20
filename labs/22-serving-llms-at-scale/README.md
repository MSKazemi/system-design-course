# Lab L22 — Batching and prefix caching, measured

Lesson: [SYSDESIGN-22 — Serving LLMs at scale](../../course/03-ai-systems/22-serving-llms-at-scale.md).
Builds on [Lab L21](../21-llm-inference-anatomy/README.md) (same image, model and benchmark client).

## Goal

Make two of vLLM's core mechanisms visible with numbers you measure yourself:

1. **Continuous batching** — a concurrency sweep (1 → 16 requests in flight) showing aggregate throughput rising while
   per-request TPOT degrades.
2. **Automatic prefix caching (APC)** — the same shared-prefix workload with `--enable-prefix-caching` and
   `--no-enable-prefix-caching`, compared on TTFT and on vLLM's `vllm:prefix_cache_*` counters.

## What you will observe

- The throughput/latency trade-off of batching as a table you produced.
- TTFT for requests that share a long prefix dropping sharply after the first request when APC is on, and not when it is off.
- Prefix-cache hit counters in `/metrics`.
- Engine metrics an autoscaler would use: `vllm:num_requests_running`, `vllm:num_requests_waiting`,
  `vllm:kv_cache_usage_perc`.

## Prerequisites

Same as L21: Docker Engine 29 + Compose v5, Python ≥ 3.10, ≈ 10 GB disk, ≥ 8 GB free RAM, internet for the first
model download.

| Component | Version |
|---|---|
| vLLM CPU server | `vllm/vllm-openai-cpu:v0.34.0-x86_64` (vLLM v0.34.0) |
| Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Clients | `bench.py` (copy of L21's) and `sweep.py` — Python standard library only |

**GPU (optional).** With an NVIDIA GPU and the NVIDIA Container Toolkit, replace the image with the GPU build
`vllm/vllm-openai:v0.34.0`, drop the CPU-only flags (`--dtype=float32`, `--kv-cache-memory-bytes`, `--enforce-eager`,
the `cap_add`/`security_opt` lines) and add `gpus: all` to the service. Not tested in this course's environment (no GPU
available); GPU numbers will be far higher, but the curve shapes are the point.

## Run

```bash
cd labs/22-serving-llms-at-scale
docker compose -p sd-22 up -d                    # prefix caching ON (the vLLM V1 default)
until curl -sf localhost:12201/health; do sleep 5; done; echo ready
```

## Experiments

1. **Concurrency sweep (APC on).**
   `python3 sweep.py concurrency --model Qwen/Qwen2.5-0.5B-Instruct --levels 1 2 4 8 16`
   While it runs, in a second terminal:
   `watch -n1 "curl -s localhost:12201/metrics | grep -E '^vllm:num_requests_(running|waiting)|^vllm:kv_cache_usage_perc'"`.
   Note where `num_requests_waiting` becomes non-zero: the lab caps the engine at `--max-num-seqs=16`.
2. **Prefix caching ON.**
   `python3 sweep.py prefix --model Qwen/Qwen2.5-0.5B-Instruct --shared-prefix-words 800 --prefix-requests 8`
   Eight sequential requests share an ≈ 800-word prefix and differ in a 16-word suffix. Record TTFT p50 (warm requests),
   TTFT p99 (≈ the cold first request) and the printed hit rate.
3. **Prefix caching OFF.**
   `APC_FLAG=--no-enable-prefix-caching docker compose -p sd-22 up -d --force-recreate`, wait for health, then repeat
   experiment 2. Every request now pays the full prefill.
4. **Break the cache on purpose.** With APC on, change `bench.py` to put the random part *before* the shared prefix
   (swap the order in `one_request`) and rerun experiment 2. Explain the result using the block-hash chain from the
   lesson.
5. **(Optional) Batch cap.** Restart with `MAX_NUM_SEQS=4` and rerun the sweep: past concurrency 4, extra requests
   queue (`num_requests_waiting`) and TTFT, not TPOT, absorbs the load.

## Expected results

Directions, not numbers — a laptop CPU is not a GPU:

- Exp. 1: aggregate `output_tok_per_s` grows with concurrency, sub-linearly, and flattens once the CPU's compute
  saturates; `tpot_ms_p50` rises. The knee comes at much lower concurrency than on a GPU.
- Exp. 2 vs 3: with APC on, warm-request TTFT is a fraction of the cold TTFT and the hit rate is high; with APC off,
  all requests have similar (high) TTFT and the hit counters stay at zero.
- Exp. 4: hit rate collapses to ≈ 0 — a changed first block changes every downstream block hash.
- Exp. 5: TTFT p99 rises sharply above the cap while TPOT stays roughly flat.

## Clean up

```bash
docker compose -p sd-22 down -v
docker image rm vllm/vllm-openai-cpu:v0.34.0-x86_64   # optional, ≈ 7.7 GB, shared with L21
```

## Cost

€0 locally. A GPU run in a cloud would be billed by the provider; none is required.

## Test status

**runtime-tested** on 2026-11-20 (CPU path; experiments 1–4). Experiment 5 and the GPU variant were **not run**. See
"Test record" below.

## Troubleshooting

- Slow start-up or "No available shared memory broadcast block" warnings: see L21's troubleshooting; this lab already
  uses `--enforce-eager` and FP32 for AVX2 laptops.
- The very first request after a fresh `up` compiles Triton-CPU kernels (≈ 6 minutes on the test laptop, once; cached
  in the `triton-cache` volume). Send one manual request and wait for it before running `sweep.py`.
- Metric names: this lab's parser accepts both `vllm:prefix_cache_hits` and `vllm:prefix_cache_hits_total` styles.
- Port 12201 is bound to 127.0.0.1 only.

## Test record

**Status: runtime-tested, 2026-11-20 (CPU).** Host: Ubuntu 24.04.5 LTS, kernel 7.0.0-43, AMD Ryzen 5 PRO 4650U
(6C/12T, AVX2, no AVX-512), 30 GiB RAM, Docker 29.10.0, Compose v5.8.0, Python 3.12.3; image
`vllm/vllm-openai-cpu:v0.34.0-x86_64`; `Qwen/Qwen2.5-0.5B-Instruct`, FP32, `--enforce-eager`, `--max-num-seqs 16`,
`--max-num-batched-tokens 2048`, 2 GiB KV. The laptop was shared with other heavy jobs (load average 13–20), so
treat absolute values as noisy. Observed, not estimated:

**Experiment 1 — concurrency sweep** (`--max-tokens 32`, ≈ 118-token prompts, APC on, 2 × concurrency requests per level):

| Concurrency | TTFT p50 (ms) | TTFT p99 (ms) | TPOT p50 (ms) | ITL p99 (ms) | Output tokens/s | Gain vs 1 |
|---|---|---|---|---|---|---|
| 1 | 398 | 504 | 111.5 | 140 | 8.1 | 1.00× |
| 2 | 625 | 1,095 | 149.1 | 501 | 11.1 | 1.37× |
| 4 | 1,598 | 1,711 | 174.3 | 244 | 19.0 | 2.35× |
| 8 | 3,131 | 3,469 | 174.0 | 218 | 30.0 | 3.71× |
| 16 | 5,793 | 6,149 | 216.8 | 311 | 41.0 | 5.06× |

Aggregate throughput rose 5× from 1 to 16 concurrent requests while TPOT roughly doubled; TTFT grew fastest, because
new requests' prefills queue behind each other and share steps with running decodes.

**Experiments 2–4 — prefix caching** (8 sequential requests, ≈ 870 prompt tokens each, of which the first ≈ 770–830
tokens — the 800-word generated prefix — are shared; 16 output tokens):

| Run | TTFT p50 (ms) | TTFT p99 (ms) | `prefix_cache_hits_total` Δ / `queries_total` Δ |
|---|---|---|---|
| APC on (default) | **594** | 4,016 (the cold first request) | 5,376 / 6,957 tokens = **77.3 %** |
| APC off (`--no-enable-prefix-caching`) | **3,886** | 4,502 | counters did not move |
| APC on, unique text placed *before* the shared prefix (exp. 4) | **4,186** | 4,720 | 0 / 6,957 = **0 %** |

The hit count is exactly 7 requests × 12 full 64-token blocks (768 tokens) — the first request misses and the partial
last block of the prefix is never cached, as the lesson's description of vLLM's full-block hashing predicts. With APC
on, warm requests reached their first token ≈ 6.5× sooner than with APC off. Moving the unique text to the front made
every block hash differ and removed all hits.

Not run: experiment 5 (batch cap) and the GPU variant. Test convenience: model and Triton caches were copied from the
L21 run into this project's volumes before the first start, so the ≈ 5.5-minute download and ≈ 6-minute first-request
compile were not repeated here. Clean-up verified: `docker compose -p sd-22 down -v`, then those pre-created volumes
were removed by hand (Compose only removes volumes it created itself).
