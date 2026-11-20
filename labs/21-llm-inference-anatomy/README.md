# Lab L21 — Measuring the anatomy of LLM inference

Lesson: [SYSDESIGN-21 — Anatomy of LLM inference](../../course/03-ai-systems/21-llm-inference-anatomy.md).

## Goal

Serve a tiny open model on your laptop CPU through an OpenAI-compatible server, then measure — from the client side —
the quantities the lesson defines: **TTFT, TPOT, ITL, end-to-end latency, throughput and goodput**. Change one variable
at a time (prompt length, output length, concurrency) and check each result against the lesson's model:
prefill cost grows with prompt length; decode cost per token barely does; batching raises aggregate throughput while
each user slows down.

## What you will observe

- TTFT grows with prompt length (prefill work); TPOT changes much less.
- E2E latency grows roughly linearly with output length (one decode step per token).
- Raising concurrency raises aggregate output tokens/s but also per-request TPOT (continuous batching).
- The server's own KV-cache sizing log line matches the lesson's KV formula.
- vLLM's Prometheus metrics (`/metrics`) and tokenizer endpoint (`/tokenize`).

## Prerequisites

- x86-64 Linux or macOS/Windows with Docker Desktop; **Docker Engine 29 + Compose v5** (tested with Docker 29.10.0,
  Compose v5.8.0). Apple-silicon/ARM: use the `v0.34.0-arm64` tag (not tested here).
- ≈ 10 GB free disk (the vLLM CPU image is 1.8 GB compressed / ≈ 7.7 GB on disk; model ≈ 1 GB) and ≥ 8 GB free RAM.
- Python ≥ 3.10 on the host (the benchmark client uses the standard library only).
- Internet access on first run to download the model from Hugging Face (no token needed for this model).

Images and model (pinned):

| Component | Version |
|---|---|
| vLLM CPU server | `vllm/vllm-openai-cpu:v0.34.0-x86_64` (vLLM v0.34.0, released 2026-11-16) |
| Model | `Qwen/Qwen2.5-0.5B-Instruct` (0.49 B parameters, Apache-2.0) |
| Fallback server | `ghcr.io/ggml-org/llama.cpp:server-b12464` with `Qwen/Qwen2.5-0.5B-Instruct-GGUF` (Q8_0) |

**Why vLLM's CPU image?** It is the same engine the course teaches (scheduler, KV cache, prefix caching, metrics),
so the numbers you read and the metrics you scrape are the real thing, just slower. **Why a fallback?** The vLLM CPU
build prefers AVX-512; on AVX2-only CPUs it works with "limited features" (vLLM docs) and BF16 is slow, so this lab runs
it in FP32 and eager mode. If start-up is impractical on your machine, the llama.cpp server is small, fast to start and
also OpenAI-compatible (it also implements continuous batching), but it is a different engine, so its internals differ.

## Run

```bash
cd labs/21-llm-inference-anatomy
docker compose -p sd-21 up -d                         # first start downloads the model (minutes)
docker compose -p sd-21 logs -f vllm                  # wait for "Application startup complete"
curl -s localhost:12101/health && echo ready
curl -s localhost:12101/v1/models | python3 -m json.tool
```

One streamed request by hand (watch the SSE events arrive):

```bash
curl -N localhost:12101/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "Qwen/Qwen2.5-0.5B-Instruct",
  "messages": [{"role": "user", "content": "Explain a KV cache in two sentences."}],
  "max_tokens": 60, "stream": true, "stream_options": {"include_usage": true}}'
```

Baseline benchmark (1 request at a time, 4 requests):

```bash
python3 bench.py --url http://localhost:12101 --model Qwen/Qwen2.5-0.5B-Instruct \
  --concurrency 1 --requests 4 --prompt-words 100 --max-tokens 64
```

`bench.py` streams from `/v1/completions`, timestamps every SSE chunk, takes exact token counts from the final
`usage` chunk, and forces a fixed output length with vLLM's `ignore_eos` extension (disable with `--no-ignore-eos`).

## Experiments

1. **Tokens are not words.** Count tokens for a sentence of your own:
   `curl -s localhost:12101/tokenize -H 'Content-Type: application/json' -d '{"model":"Qwen/Qwen2.5-0.5B-Instruct","prompt":"Lumen answers questions about your documents."}'`
   Compute words per token. Try another language or some code.
2. **KV formula check.** In the server log, find `CPU KV cache size: N tokens`. The lab gives the engine 2 GiB of KV.
   Compute the expected value with the lesson's formula (24 layers × 2 × 2 KV heads × 64 × *bytes*), where *bytes* is
   4 for the FP32 dtype used here. Compare with N.
3. **Prompt length → TTFT.** Run `bench.py` with `--prompt-words 50`, `400`, `1500` (concurrency 1, `--max-tokens 32`).
   Record TTFT p50 and TPOT p50 for each.
4. **Output length → E2E.** Fix `--prompt-words 100` and vary `--max-tokens 16`, `64`, `256`. Plot E2E vs output tokens;
   the slope is your TPOT.
5. **Concurrency → batching.** Fix prompt and output, vary `--concurrency 1`, `2`, `4`, `8` with `--requests` = 2 ×
   concurrency. Record aggregate `output_tok_per_s` and `tpot_ms_p50`.
6. **Bandwidth bound.** FP32 weights are ≈ 0.49 × 10⁹ × 4 B ≈ 2 GB. Look up your RAM's theoretical bandwidth
   (channels × MT/s × 8 bytes). Divide by 2 GB: that is an upper bound on single-stream decode tokens/s. How close is
   your measured 1 ÷ TPOT?
7. **Server-side view.** `curl -s localhost:12101/metrics | grep -E "^vllm:(time_to_first_token|inter_token|num_requests|kv_cache_usage)"`
   and compare the server's TTFT histogram with what the client measured. Where does the difference come from?

## Expected results

Directions, not numbers — your CPU, memory and background load decide the values:

- Exp. 2: N should match the formula within a block (the engine rounds to whole KV blocks).
- Exp. 3: TTFT rises clearly with prompt length; TPOT rises a little (more KV to read per step).
- Exp. 4: E2E ≈ TTFT + TPOT × (n − 1) — a straight line.
- Exp. 5: aggregate tokens/s rises with concurrency but less than linearly; TPOT rises. On a CPU, compute saturates
  much earlier than on a GPU, so the gain flattens sooner.
- Exp. 6: measured single-stream speed is below the bandwidth bound (the bound ignores compute, attention, framework
  overhead and the fact that a laptop rarely reaches peak bandwidth).
- Exp. 7: client TTFT ≥ server TTFT (network, HTTP, detokenisation and streaming are outside the engine's timer).

## Clean up

```bash
docker compose -p sd-21 down -v          # removes containers and the model/compile cache volumes
docker image rm vllm/vllm-openai-cpu:v0.34.0-x86_64   # optional: frees ≈ 7.7 GB (lab L22 uses the same image)
```

## Cost

€0 — everything runs locally. The first run downloads ≈ 1.8 GB (image) + ≈ 1 GB (model).

## Test status

**runtime-tested** on 2026-11-20 — both the vLLM path and the llama.cpp fallback. See "Test record" at the end of
this file.

## Troubleshooting

- **Start-up takes many minutes, log shows "No available shared memory broadcast block found in 60 seconds".** The
  engine is busy warming up; on a loaded laptop this can be slow. This lab already uses `--enforce-eager` (no
  `torch.compile`) and FP32 to keep start-up short. Close other heavy processes.
- **The very first request takes several minutes.** vLLM's CPU path compiles Triton-CPU kernels on first use (one-off;
  ≈ 6 minutes on the test laptop). They are cached in the `triton-cache` volume, so later restarts answer in seconds —
  unless you ran `down -v`. `bench.py` sends one untimed warm-up request first; for the very first run, send a manual
  request and wait for it before benchmarking.
- **`get_mempolicy: Operation not permitted`.** The compose file adds `cap_add: [SYS_NICE]` and
  `seccomp=unconfined`, as the vLLM CPU docs recommend.
- **Thread binding.** vLLM binds OpenMP threads automatically (`VLLM_CPU_OMP_THREADS_BIND=auto`). To override:
  `OMP_BIND=0-5 docker compose -p sd-21 up -d --force-recreate`. Use one logical CPU per physical core
  (`lscpu -e` shows the mapping) for best results.
- **AVX-512 machine?** Set `DTYPE=bfloat16` for half the memory traffic.
- **Fallback: llama.cpp server.**
  `docker compose -p sd-21 --profile llamacpp up -d llamacpp` then run `bench.py --url http://localhost:12102 --model any`.
  (llama.cpp ignores the model name; it serves the one GGUF it loaded.) Its `/metrics` and `/tokenize` endpoints differ
  from vLLM's.
- **Port clash.** Host ports 12101 (vLLM) and 12102 (llama.cpp) are bound to 127.0.0.1 only; change them in
  `compose.yaml` if needed.

## Test record

**Status: runtime-tested, 2026-11-20 (vLLM path).** Host: Ubuntu 24.04.5 LTS, kernel 7.0.0-43, AMD Ryzen 5 PRO 4650U
(6 cores / 12 threads, AVX2, **no AVX-512**), 30 GiB RAM, Docker 29.10.0, Compose v5.8.0, Python 3.12.3. Image
`vllm/vllm-openai-cpu:v0.34.0-x86_64`, model `Qwen/Qwen2.5-0.5B-Instruct`, `--dtype float32 --enforce-eager`, 2 GiB
KV. The laptop was shared with other heavy jobs during the run (load average 12–20), so absolute numbers are noisy;
the trends are the result. All numbers below were observed, not estimated.

What happened while making the lab work (kept in the compose file as fixes):

- With `--dtype bfloat16` the log showed `Failed to create oneDNN linear, fallback to torch linear` (no fast BF16 on
  AVX2) and warm-up took minutes → switched the default to FP32.
- The first request after start-up compiled 39–40 Triton-CPU kernels (seen with `py-spy dump`: `triton/backends/cpu/build.py`)
  and took ≈ 6 minutes; with the `triton-cache` volume a restarted server answered its first request in ≈ 2 s.
- With `torch.compile` (default) start-up exceeded 10 minutes on this loaded laptop; `--enforce-eager` brought engine
  start-up to ≈ 50 s after the model was cached. First model download: ≈ 5.5 minutes for ≈ 1 GB.

Observed results (client-side, `bench.py`):

| Exp. | Setting | Result |
|---|---|---|
| 1 | `/tokenize` on "Lumen answers questions about your documents." | 7 words → **8 tokens** |
| 2 | engine log, 2 GiB KV, FP32 | `CPU KV cache size: 87,296 tokens`. Formula: 24 × 2 × 2 × 64 × 4 B = 24,576 B/token → 87,381 tokens → 1,364 whole 64-token blocks = **87,296** (exact match). An earlier BF16 start reported 174,720 tokens = 2 × as many (12,288 B/token), also exact. |
| 3 | prompt 66 / 429 / 1,564 tokens, 32 output tokens | TTFT p50 **353 / 2,025 / 7,985 ms**; TPOT p50 **102 / 108 / 109 ms** |
| 4 | output 16 / 64 / 256 tokens, ≈ 118-token prompt | E2E p50 **2,054 / 7,137 / 28,487 ms** (≈ linear); TPOT p50 99 / 104 / 109 ms |
| 5 | concurrency 1 / 2 / 4 / 8 (32 output tokens) | output tokens/s **8.2 / 13.1 / 21.2 / 29.5** (3.6× at 8); TPOT p50 **103 / 114 / 130 / 148 ms**; TTFT p50 615 / 807 / 2,181 / 4,240 ms; goodput at the default SLOs (TTFT ≤ 2 s, TPOT ≤ 200 ms) 0.26 / 0.41 / 0.17 / **0.0** req/s |
| 7 | `/metrics` | present and populated: `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:request_time_per_output_token_seconds`, `vllm:e2e_request_latency_seconds`, `vllm:request_queue_time_seconds`, `vllm:num_requests_running`, `vllm:num_requests_waiting`, `vllm:kv_cache_usage_perc`, `vllm:prefix_cache_queries_total`, `vllm:prefix_cache_hits_total`, `vllm:num_preemptions_total` |

Reading the numbers: prefill on this CPU ran at roughly 200 prompt tokens/s, so TTFT is dominated by prompt length;
decode stayed near 100–110 ms/token regardless of prompt length; batching 8 requests multiplied aggregate throughput
by 3.6× while each request's TPOT rose by ≈ 44 % — and TTFT, which includes waiting behind other prefills, is what
broke the SLO first (goodput fell to zero at concurrency 8 although throughput was highest). Exp. 6 was not run on
this host (its RAM bandwidth was not measured). An early run without per-request nonces got prefix-cache hits across
runs (3,456 hit tokens) that flattered TTFT; `bench.py` now makes every unique prompt part unique per run, and the
rerun above recorded **0** hits.

**llama.cpp fallback** (`ghcr.io/ggml-org/llama.cpp:server-b12464`, `Qwen2.5-0.5B-Instruct-GGUF` Q8_0, 4 slots), same
host, same day: first start downloaded the GGUF and was ready in ≈ 4 minutes; `ignore_eos` was honoured.
Concurrency 1: TTFT p50 644 ms, TPOT p50 **24.1 ms**, 21.8 output tokens/s. Concurrency 4: 30.3 tokens/s, TPOT p50
52.7 ms. 1,559-token prompt: TTFT p50 10.7 s. Note the decode speed: Q8_0 weights are ≈ 4× fewer bytes than the FP32
weights vLLM ran with here, and TPOT was ≈ 4× lower — the bandwidth-bound decode of the lesson, seen across two engines
(other differences between the engines also contribute, so treat this as illustrative, not a controlled comparison).

Clean-up verified: `docker compose -p sd-21 --profile llamacpp down -v` removed containers, network and volumes; the
two images were removed afterwards to free ≈ 9 GB.
