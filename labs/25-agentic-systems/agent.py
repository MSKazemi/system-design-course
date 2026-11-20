"""L25 — a minimal, budgeted agent runtime.

  model  : any OpenAI-compatible /v1/chat/completions endpoint with tool calling (llama.cpp --jinja,
           vLLM, Ollama ...), or --scripted for a deterministic fake model (no LLM needed)
  tools  : discovered from an MCP server over stdio (tools_server.py)
  runtime: policy (allow / approve / deny), budgets (steps, tokens, wall clock, per-tool timeout),
           loop detection, intent/result journal for idempotent side effects, JSONL trace

The model proposes; the runtime disposes. Nothing in the prompt is a security control.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from mcp import Client
from mcp.client.stdio import StdioServerParameters

HERE = os.path.dirname(os.path.abspath(__file__))

# Runtime policy. Decided by the operator, not by the tool server's self-description.
POLICY = {"search_docs": "allow", "run_python": "allow", "send_email": "approve"}

SYSTEM = ("You are Lumen's task agent. First use search_docs to find facts. Use run_python only for arithmetic: "
          "send a one- or two-line program that prints the result. When you have the answer, reply with a short "
          "final answer and cite doc ids like [nw-02].")


@dataclass
class Budget:
    max_steps: int = 8
    max_tokens: int = 20_000
    deadline_s: float = 120.0
    tool_timeout_s: float = 20.0
    used_tokens: int = 0
    started: float = field(default_factory=time.monotonic)

    def check(self, step: int) -> str | None:
        if step >= self.max_steps:
            return f"step budget exhausted ({self.max_steps})"
        if self.used_tokens >= self.max_tokens:
            return f"token budget exhausted ({self.used_tokens}/{self.max_tokens})"
        if time.monotonic() - self.started >= self.deadline_s:
            return f"deadline exceeded ({self.deadline_s:.0f}s)"
        return None


class Trace:
    def __init__(self, path: str, task_id: str):
        self.f = open(path, "a")
        self.task_id = task_id

    def span(self, kind: str, **attrs):
        rec = {"task_id": self.task_id, "kind": kind, "ts": round(time.time(), 3), **attrs}
        self.f.write(json.dumps(rec) + "\n")
        self.f.flush()
        short = {k: (str(v)[:70] + "…" if len(str(v)) > 70 else v) for k, v in attrs.items()}
        print(f"  [{kind}] {short}", flush=True)


def _valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False


# ---------------------------------------------------------------- models
def openai_chat(url: str, model: str, messages: list, tools: list) -> tuple[dict, int]:
    body = {"model": model, "messages": messages, "tools": tools, "temperature": 0, "max_tokens": 400}
    req = urllib.request.Request(url.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "none")})
    with urllib.request.urlopen(req, timeout=300) as r:
        out = json.loads(r.read())
    usage = out.get("usage") or {}
    return out["choices"][0]["message"], int(usage.get("total_tokens", 0))


def call(name: str, **args) -> dict:
    return {"role": "assistant", "content": None, "tool_calls": [
        {"id": f"call_{name}_{len(json.dumps(args))}", "type": "function",
         "function": {"name": name, "arguments": json.dumps(args)}}]}


SCRIPTS = {  # deterministic fake model: a fixed list of assistant turns per scenario
    "happy": [call("search_docs", query="LUM-4031 upload limit Northwind"),
              call("run_python", code="print(200 * 1024 * 1024)"),
              {"role": "assistant", "content": "Northwind's upload limit is 200 MB = 209715200 bytes [nw-02]."}],
    "loop": [call("search_docs", query="retention")] * 10,
    "escape": [call("run_python", code=(
        "import socket, os\n"
        "try:\n    socket.create_connection(('example.com', 80), timeout=3); print('NETWORK OPEN')\n"
        "except Exception as e:\n    print('network blocked:', type(e).__name__)\n"
        "try:\n    open('/etc/pwned', 'w'); print('ROOT FS WRITABLE')\n"
        "except Exception as e:\n    print('fs blocked:', type(e).__name__)\n"
        "print('uid', os.getuid())\n")),
        call("run_python", code="while True: pass"),
        {"role": "assistant", "content": "Sandbox checks done."}],
    "email": [call("send_email", to="ops@example.com", subject="Retention report",
                   body="Retention is configurable between 7 and 730 days [nw-10].", idempotency_key="IGNORED"),
              {"role": "assistant", "content": "Email step finished."}],
    "tokens": [call("search_docs", query=f"query {i}") for i in range(10)],
}


def scripted(scenario: str):
    turns = iter(SCRIPTS[scenario])

    def model(messages, tools):
        msg = next(turns, {"role": "assistant", "content": "(script exhausted)"})
        est = sum(len(json.dumps(m)) for m in messages) // 4  # ~4 chars/token estimate for the fake model
        return msg, est
    return model


# ---------------------------------------------------------------- runtime
def approve(tool: str, args: dict, mode: str) -> bool:
    print(f"\n  >>> APPROVAL REQUIRED: {tool}({json.dumps(args)})")
    if mode == "always":
        print("  >>> auto-approved (--approve always)")
        return True
    if mode == "never" or not sys.stdin.isatty():
        print("  >>> denied (--approve never or non-interactive)")
        return False
    return input("  >>> approve? [y/N] ").strip().lower() == "y"


async def run(args) -> int:
    task_id = args.task_id
    trace = Trace(args.trace, task_id)
    budget = Budget(args.max_steps, args.max_tokens, args.deadline, args.tool_timeout)
    model = scripted(args.scripted) if args.scripted else (
        lambda m, t: openai_chat(args.model_url, args.model, m, t))
    # step-intent -> result. A JSON file stands in for a durable checkpoint store (Postgres, Temporal history...)
    jpath = args.journal or f"journal-{task_id}.json"
    journal: dict[str, str] = json.load(open(jpath)) if os.path.exists(jpath) else {}
    if journal:
        trace.span("resumed", recorded_steps=len(journal))
    seen_calls: dict[str, int] = {}

    server = StdioServerParameters(command=sys.executable, args=[os.path.join(HERE, "tools_server.py")],
                                   env={**os.environ})
    async with Client(server) as mcp:
        listed = await mcp.list_tools()
        tools = [{"type": "function", "function": {"name": t.name, "description": t.description,
                                                   "parameters": t.input_schema}} for t in listed.tools]
        trace.span("tools_discovered", tools=[t.name for t in listed.tools])
        messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": args.task}]

        for step in range(10_000):
            reason = budget.check(step)
            if reason:
                trace.span("stopped", reason=reason, step=step)
                print(f"\nRESULT: stopped early: {reason}")
                return 2
            t0 = time.monotonic()
            try:
                msg, tokens = model(messages, tools)
            except urllib.error.HTTPError as e:
                # e.g. a small model emits a truncated / malformed tool call and the server cannot parse it.
                # Treat it as a failed step (it still consumed budget) and tell the model what went wrong.
                detail = e.read().decode(errors="replace")[:160]
                trace.span("llm_error", step=step, status=e.code, detail=detail)
                messages.append({"role": "user", "content": "Your last tool call could not be parsed. "
                                 "Call one tool with short, valid JSON arguments."})
                continue
            budget.used_tokens += tokens
            trace.span("llm_call", step=step, tokens=tokens, total_tokens=budget.used_tokens,
                       ms=round((time.monotonic() - t0) * 1000))
            calls = msg.get("tool_calls") or []
            bad = [tc for tc in calls if not _valid_json(tc["function"].get("arguments") or "{}")]
            if bad:
                # Never put a malformed call into the history: the server would fail to re-parse it on every
                # later turn. Record it, drop it, and ask the model to try again (the step still counts).
                trace.span("malformed_tool_call", step=step, tool=bad[0]["function"]["name"],
                           args=bad[0]["function"].get("arguments", "")[:120])
                messages.append({"role": "user", "content": "Your last tool call had invalid or truncated JSON "
                                 "arguments. Call one tool again with short, valid arguments."})
                continue
            messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
            if not calls:
                print(f"\nRESULT: {msg.get('content')}")
                trace.span("final", step=step, tokens=budget.used_tokens)
                return 0
            for tc in calls:
                name = tc["function"]["name"]
                try:
                    targs = json.loads(tc["function"]["arguments"] or "{}")
                except json.JSONDecodeError:
                    targs = None
                key = hashlib.sha256(f"{name}:{json.dumps(targs, sort_keys=True)}".encode()).hexdigest()[:12]
                seen_calls[key] = seen_calls.get(key, 0) + 1
                verdict = POLICY.get(name, "deny")
                trace.span("proposed", step=step, tool=name, verdict=verdict, args=tc["function"]["arguments"])
                if targs is None:
                    result = "error: arguments were not valid JSON"
                elif seen_calls[key] > args.loop_limit:
                    trace.span("loop_detected", tool=name, repeats=seen_calls[key])
                    print("\nRESULT: stopped early: loop detected (same tool call repeated)")
                    return 3
                elif verdict == "deny":
                    result = f"error: tool '{name}' is not permitted for this task"
                elif verdict == "approve" and not approve(name, targs, args.approve):
                    result = "error: a human reviewer rejected this action"
                    trace.span("approval", tool=name, approved=False)
                else:
                    if verdict == "approve":
                        trace.span("approval", tool=name, approved=True)
                        # idempotency key derived by the runtime, never chosen by the model
                        targs["idempotency_key"] = f"{task_id}:{step}:{name}"
                    intent = f"{step}:{key}"
                    if intent in journal:                      # resume path: reuse the recorded result
                        result = journal[intent]
                    else:
                        t1 = time.monotonic()
                        try:
                            r = await asyncio.wait_for(mcp.call_tool(name, targs), timeout=budget.tool_timeout_s)
                            result = "\n".join(getattr(c, "text", "") for c in r.content) or str(r.structured_content)
                        except asyncio.TimeoutError:
                            result = f"error: tool timeout after {budget.tool_timeout_s:.0f}s"
                        if args.crash_after_tool:
                            print("\n  !!! simulated crash: tool returned, journal NOT yet written", flush=True)
                            os._exit(9)
                        journal[intent] = result
                        json.dump(journal, open(jpath, "w"))
                        trace.span("tool_call", step=step, tool=name, ms=round((time.monotonic() - t1) * 1000),
                                   result=result.replace("\n", " | "))
                messages.append({"role": "tool", "tool_call_id": tc.get("id", name), "content": result[:2000]})
    return 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", default="What is the Northwind upload size limit in bytes? Use the tools.")
    ap.add_argument("--scripted", choices=sorted(SCRIPTS), help="use a deterministic fake model")
    ap.add_argument("--model-url", default=os.environ.get("MODEL_URL", "http://localhost:12501/v1"))
    ap.add_argument("--model", default=os.environ.get("MODEL", "qwen2.5-0.5b-instruct"))
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=20_000)
    ap.add_argument("--deadline", type=float, default=180.0)
    ap.add_argument("--tool-timeout", type=float, default=20.0)
    ap.add_argument("--loop-limit", type=int, default=2, help="max identical calls before stopping")
    ap.add_argument("--approve", choices=["ask", "always", "never"], default="ask")
    ap.add_argument("--trace", default="trace.jsonl")
    ap.add_argument("--task-id", default=f"task-{int(time.time())}")
    ap.add_argument("--journal", help="checkpoint file (default journal-<task-id>.json)")
    ap.add_argument("--crash-after-tool", action="store_true",
                    help="exit right after the first tool call returns, before the journal is written")
    args = ap.parse_args()
    sys.exit(asyncio.run(run(args)))


if __name__ == "__main__":
    main()
