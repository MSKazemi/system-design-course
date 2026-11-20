"""L26 — experiments against the LiteLLM gateway. Standard library only (python3 gateway_lab.py <experiment>).

  balance   10 requests to alias lumen-chat; which replica served each one
  failover  same, while you stop one replica (docker compose -p sd-26 stop llm-b)
  fallback  request alias lumen-premium (dead backend) -> served by lumen-chat
  ratelimit create a team key with a tiny tokens-per-minute limit and exceed it
  stream    stream through the gateway; time to first token vs total; usage at the end
  spend     per-key spend recorded by the gateway (cost attribution)
"""
from __future__ import annotations

import collections
import json
import os
import sys
import time
import urllib.error
import urllib.request

GW = os.environ.get("GATEWAY", "http://localhost:12600")
MASTER = os.environ.get("LITELLM_MASTER_KEY", "sk-lab-master-0000")
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".team-key")


def http(method: str, path: str, key: str, body: dict | None = None, timeout: float = 120):
    req = urllib.request.Request(GW + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), json.loads(e.read() or b"{}")


def chat(key: str, model: str, prompt: str, max_tokens: int = 16):
    return http("POST", "/v1/chat/completions", key,
                {"model": model, "max_tokens": max_tokens, "temperature": 0,
                 "messages": [{"role": "user", "content": prompt}]})


def served_by(headers: dict) -> str:
    h = {k.lower(): v for k, v in headers.items()}
    return h.get("x-litellm-model-api-base", "?")


def balance(n: int = 10):
    counts = collections.Counter()
    for i in range(n):
        t0 = time.monotonic()
        status, h, body = chat(MASTER, "lumen-chat", f"Say the number {i}.")
        counts[(status, served_by(h))] += 1
        print(f"  req {i:2d}: HTTP {status}  served by {served_by(h):<22} {1000 * (time.monotonic() - t0):6.0f} ms")
    print("  summary:", dict(counts))


def fallback():
    status, h, body = chat(MASTER, "lumen-premium", "Reply with OK.")
    hl = {k.lower(): v for k, v in h.items()}
    print(f"  HTTP {status}; asked for lumen-premium; served by {served_by(h)}; "
          f"model={body.get('model')}; attempted_fallbacks={hl.get('x-litellm-attempted-fallbacks')}; "
          f"attempted_retries={hl.get('x-litellm-attempted-retries')}")


def ratelimit():
    status, _, body = http("POST", "/key/generate", MASTER,
                           {"key_alias": f"team-docs-{int(time.time())}", "models": ["lumen-chat"],
                            "tpm_limit": 200, "rpm_limit": 100, "max_budget": 1.0,
                            "metadata": {"team": "docs"}})
    if status != 200:
        print("  key generation failed:", status, body)
        return
    key = body["key"]
    open(STATE, "w").write(key)
    print(f"  created team key (tpm_limit=200, rpm_limit=100) -> saved to {STATE}")
    for i in range(12):
        status, h, body = chat(key, "lumen-chat", "Write one sentence about rate limits.", max_tokens=40)
        hl = {k.lower(): v for k, v in h.items()}
        used = (body.get("usage") or {}).get("total_tokens")
        extra = body.get("error", {}).get("message", "")[:90] if status != 200 else ""
        print(f"  req {i:2d}: HTTP {status} tokens={used} remaining-tokens={hl.get('x-ratelimit-remaining-tokens')} {extra}")
        if status == 429:
            break


def stream():
    body = {"model": "lumen-chat", "stream": True, "max_tokens": 80, "temperature": 0,
            "stream_options": {"include_usage": True},
            "messages": [{"role": "user", "content": "Explain what an LLM gateway does in three sentences."}]}
    req = urllib.request.Request(GW + "/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {MASTER}", "Content-Type": "application/json"})
    t0 = time.monotonic()
    ttft, chunks, usage, text = None, 0, None, []
    with urllib.request.urlopen(req, timeout=300) as r:
        for raw in r:
            line = raw.decode().strip()
            if not line.startswith("data:") or line == "data: [DONE]":
                continue
            ev = json.loads(line[5:])
            if ev.get("usage"):
                usage = ev["usage"]
            for ch in ev.get("choices", []):
                delta = (ch.get("delta") or {}).get("content")
                if delta:
                    chunks += 1
                    text.append(delta)
                    if ttft is None:
                        ttft = time.monotonic() - t0
    total = time.monotonic() - t0
    print(f"  text: {''.join(text)[:160]!r}…")
    print(f"  time to first token {ttft * 1000:.0f} ms, total {total * 1000:.0f} ms, content chunks {chunks}")
    print(f"  usage reported at end of stream: {usage}")


def spend():
    if not os.path.exists(STATE):
        print("  run the ratelimit experiment first (it creates the team key)")
        return
    key = open(STATE).read().strip()
    status, _, body = http("GET", f"/key/info?key={key}", MASTER)
    info = body.get("info", body)
    print(f"  HTTP {status}: key_alias={info.get('key_alias')} spend=${info.get('spend')} "
          f"max_budget={info.get('max_budget')} tpm_limit={info.get('tpm_limit')} metadata={info.get('metadata')}")


if __name__ == "__main__":
    exp = sys.argv[1] if len(sys.argv) > 1 else "balance"
    {"balance": balance, "failover": balance, "fallback": fallback, "ratelimit": ratelimit,
     "stream": stream, "spend": spend}[exp]()
