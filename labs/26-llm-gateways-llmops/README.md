# Lab L26 — An LLM gateway: aliases, load balancing, failover, fallback, token limits, streaming, spend (SYSDESIGN-26)

## Goal

Put a real LLM gateway (LiteLLM proxy, pinned `v1.108.12-lts`) in front of two local model replicas and observe the
gateway behaviours from the lesson:

1. one **model alias** (`lumen-chat`) load-balanced over two deployments;
2. **failover** when a replica dies (retries + cooldown);
3. a **fallback chain** from a dead "premium provider" alias to `lumen-chat`;
4. a per-team **virtual key** with a tokens-per-minute limit → `429`;
5. **streaming** through the proxy: time to first token vs total, usage at the end of the stream;
6. **cost attribution**: per-key spend recorded by the gateway.

Lesson: [SYSDESIGN-26](../../course/03-ai-systems/26-llm-gateways-llmops.md).

## What you will observe

- Response headers that say which deployment served each request, and whether fallbacks or retries happened.
- The cost of failure detection: the first requests after a replica dies can be slow (retries and timeouts) until
  the deployment is cooled down.
- Token limits enforced *after* the fact: a key can overshoot its TPM limit by the tokens of in-flight requests,
  because output length is unknown at admission.
- Spend appearing on the key only after the gateway's asynchronous spend writer flushes.

## Prerequisites

- Docker Engine 29.x and Compose v5 (tested: 29.10.0 / v5.8.0). Python 3.9+ on the host (standard library only).
- Images (pinned): `docker.litellm.ai/berriai/litellm:v1.108.12-lts` (~1.8 GB unpacked),
  `ghcr.io/ggml-org/llama.cpp:server-b12464`, `postgres:18.6-alpine` (18.6 is the tested tag; 18.7 was published
  on 2026-11-18 and has not been run with this lab yet).
- ~3 GB RAM (two model replicas + gateway + Postgres). Internet on first run (~430 MB GGUF from Hugging Face).
- Host ports: `127.0.0.1:12600` (gateway), `12611` / `12612` (replicas, debug only).
- No provider API keys. The master key in `compose.yaml` is a lab-only value.

## Run

```bash
cd labs/26-llm-gateways-llmops
docker compose -p sd-26 up -d          # llm-a downloads the model first; gateway starts when both replicas are healthy
docker compose -p sd-26 ps             # wait until gateway is "healthy"

python3 gateway_lab.py balance         # 10 requests, which replica served each
docker compose -p sd-26 stop llm-b
python3 gateway_lab.py failover        # same, with one replica down
docker compose -p sd-26 start llm-b
python3 gateway_lab.py fallback        # dead "premium" alias -> served by lumen-chat
python3 gateway_lab.py ratelimit       # team key with tpm_limit=200 -> 429
python3 gateway_lab.py stream          # SSE through the gateway, TTFT vs total
sleep 60; python3 gateway_lab.py spend # per-key spend (written asynchronously)
```

Raw curl, if you prefer:

```bash
curl -s localhost:12600/v1/chat/completions -H "Authorization: Bearer sk-lab-master-0000" \
  -H "Content-Type: application/json" \
  -d '{"model":"lumen-chat","messages":[{"role":"user","content":"Hello"}],"max_tokens":20}' -D - | grep -i x-litellm
```

## Experiments

1. **Routing strategy.** Set `routing_strategy: least-busy` (or `latency-based-routing`) in `config.yaml`, restart
   the gateway (`docker compose -p sd-26 restart gateway`), and fire concurrent requests (for example 8 parallel
   `balance` runs). Does the distribution change?
2. **Failure detection cost.** With `llm-b` stopped, time the first three requests. Add `timeout: 5` to the
   `llm-b` deployment's `litellm_params` and repeat. What is the trade-off for long generations?
3. **Fallback order.** Add a second fallback target and stop *both* replicas. What error reaches the client, and
   after how long?
4. **Reservation.** Rerun `ratelimit` with `max_tokens` 40 vs 400. How many requests pass before the `429`? Relate
   it to the lesson's reserve-and-refund design.
5. **Buffering.** Put an nginx with default `proxy_buffering on` in front of the gateway and rerun `stream`. Compare
   time to first token. Then add `proxy_buffering off`.
6. **Cost attribution.** Create two team keys with different `metadata.team`, send traffic with both, and compare
   `spend`. How would you add self-hosted GPU cost to the same report?

## Expected results

- `balance`: all HTTP 200, requests split across `llm-a` and `llm-b` (shuffle, so not exactly 50/50).
- `failover`: all HTTP 200, served by `llm-a`. One or more early requests are much slower than the rest.
- `fallback`: HTTP 200, `attempted_fallbacks=1`, served by a `lumen-chat` replica.
- `ratelimit`: a few HTTP 200s, then `429 Rate limit exceeded`. Total tokens used before the 429 can exceed
  `tpm_limit`.
- `stream`: TTFT far below total time. A `usage` object (including the configured illustrative `cost`) in the last
  chunk.
- `spend`: a small non-zero spend on the team key after the flush interval.

## Clean up

```bash
docker compose -p sd-26 down -v
rm -f .team-key
docker rmi docker.litellm.ai/berriai/litellm:v1.108.12-lts   # optional, ~1.8 GB
```

## Cost

€0. All local. Prices in `config.yaml` are fictional transfer prices used only to demonstrate cost attribution.

## Test status

**runtime-tested** on 2026-11-20. Host: Ubuntu 24.04.5 LTS, kernel 7.0.0-43-generic, Docker 29.10.0, Compose
v5.8.0. LiteLLM `v1.108.12-lts`, llama.cpp `server-b12464`, Qwen2.5-0.5B-Instruct Q4_0, Postgres 18.6.

Observed (single runs):
- `balance`: 10/10 HTTP 200. 7 served by `llm-a`, 3 by `llm-b`. Latency 143–1,396 ms (first requests slower).
- `failover` (llm-b stopped): 10/10 HTTP 200, all by `llm-a`. The **first request took 63.8 s** in one run. In a
  second run a later request took 14.7 s. The rest took 0.1–3.5 s. The gateway's container resolved `llm-b` to
  "name resolution failure" in 0.01 s, so the delay is in the gateway's retry and backoff handling of the failed
  deployment, not DNS. We did not investigate further. Treat failure-detection latency as something to measure in
  your own gateway.
- `fallback`: HTTP 200, `attempted_fallbacks=1`, `attempted_retries=0`, served by `llm-a`.
- `ratelimit` (`tpm_limit=200`, `max_tokens=40`): four HTTP 200s at 76 tokens each (304 tokens), then HTTP 429
  `Rate limit exceeded … Limit type: tokens. Current limit: 200`. That is an overshoot of the TPM limit, as
  predicted. `x-ratelimit-remaining-tokens` was not returned on these responses.
- `stream`: TTFT 187 ms, total 1,637 ms, 80 content chunks. Final usage `prompt_tokens=41`,
  `completion_tokens=80`, `cached_tokens=24`, `cost=7.22e-05` (= 41 × 2e-7 + 80 × 8e-7).
- `spend`: `$0.0` immediately after the requests. `$0.0001568` about 60 s later (asynchronous spend writes).

## Troubleshooting

- Gateway restarts or is unhealthy: check `docker logs sd-26-gateway-1`. On first start it applies database
  migrations, which takes a little while.
- `No connected db.` when creating keys: virtual keys need Postgres (`DATABASE_URL`). Check that `db` is healthy.
- `llm-b` never healthy: it waits for `llm-a` to finish the model download into the shared volume.
- Port conflicts: change the left-hand port numbers (stay within 12600–12699).
- Using Ollama instead of llama.cpp: point `api_base` at Ollama's OpenAI-compatible endpoint (`http://ollama:11434/v1`)
  and set `model: openai/<ollama-model-name>`.
