# Lab L25 — A budgeted agent runtime with MCP tools and a container sandbox (SYSDESIGN-25)

## Goal

Build and break the *runtime* around an agent, the part that system design is about:

- an agent loop against a local OpenAI-compatible model with tool calling;
- tools discovered from an **MCP server** (official Python SDK `mcp==2.3.0`, stdio transport);
- model-written code executed in a **locked-down container** (no network, read-only root, non-root, CPU, memory,
  PID and wall-clock limits);
- **budgets** (steps, tokens, deadline, per-tool timeout), **loop detection**, a **human-approval** gate for a
  side-effecting tool, and **idempotent side effects across a simulated crash**;
- a JSONL **trace** of every model call, proposed call, approval and tool call.

Lesson: [SYSDESIGN-25](../../course/03-ai-systems/25-agentic-systems.md). Companion course for building agents in
depth: [AI Agent Systems](https://github.com/MSKazemi/ai-agent-systems-course).

## What you will observe

- The runtime, not the model, decides whether each proposed call is allowed, needs approval, or is denied.
- Sandbox code cannot open a network connection or write to `/`, runs as uid 65534, and is killed at 10 s.
- A repeated identical call trips the loop detector. A token budget stops a long run with a partial result.
- After a crash *between* "tool executed" and "checkpoint written", the resumed task re-sends the call with the same
  runtime-generated idempotency key, and the tool suppresses the duplicate email.
- A small model sometimes emits truncated, invalid tool-call JSON. The runtime records it, keeps it out of the
  history, and asks again.

## Prerequisites

- Docker Engine 29.x and Compose v5 (tested: 29.10.0 / v5.8.0). The sandbox uses the host's Docker CLI.
- Python 3.11+ and [uv](https://docs.astral.sh/uv/) on the host (tested: Python 3.12.3; uv fetches `mcp==2.3.0`).
- Images: `ghcr.io/ggml-org/llama.cpp:server-b12464` (model server), `python:3.12-slim` (sandbox).
- ~1.5 GB RAM for the model server. Internet on first run (~430 MB GGUF from Hugging Face).
- Host port: `127.0.0.1:12501`.
- Optional stronger isolation: gVisor installed as Docker runtime `runsc`, then `export SANDBOX_RUNTIME=runsc`.

## Run

```bash
cd labs/25-agentic-systems
docker pull python:3.12-slim                         # sandbox image
alias agent='uv run -q --python 3.12 --with mcp==2.3.0 python agent.py'

# 1) Runtime only, deterministic fake model (no LLM needed)
agent --scripted happy        # search -> run_python in the sandbox -> final answer
agent --scripted escape       # sandbox: network blocked, read-only FS, non-root, 10 s kill
agent --scripted loop         # same call repeated -> loop detector stops the task (exit code 3)
agent --scripted tokens --max-tokens 1500 --loop-limit 5   # token budget exhausted (exit code 2)
agent --scripted email --approve never                     # approval denied, no email sent
agent --scripted email --approve always --task-id t1 --crash-after-tool   # crash after send, before checkpoint
agent --scripted email --approve always --task-id t1                      # resume: duplicate suppressed
cat outbox.jsonl              # exactly one email

# 2) With a real local model
docker compose -p sd-25 up -d                        # waits for the GGUF download on first start
agent                                                # default task
agent --task "Find the chat history retention range, then email it to ops@example.com with send_email."
cat trace.jsonl | head
```

`--approve ask` (the default) prompts on the terminal. Non-interactive runs deny.

## Experiments

1. **Policy.** Change `POLICY["run_python"]` to `"approve"`, then to `"deny"`. Where should this policy live in
   production, and who may change it?
2. **Budgets.** Run the real model with `--max-steps 2` and `--deadline 5`. What does the user get back?
3. **Sandbox.** Give the sandbox a network (`--network bridge`) and rerun `--scripted escape`. Then restore it.
   Which leg of the "lethal trifecta" did you just re-open?
4. **Idempotency.** Remove `targs["idempotency_key"] = …` from `agent.py` and repeat the crash/resume pair. Count
   the emails.
5. **Model size.** Point `--hf-file` in `compose.yaml` at a larger instruct model (for example Qwen2.5-1.5B-Instruct
   GGUF) and compare how often the agent completes the multi-step email task. Count steps and tokens from
   `trace.jsonl`.
6. **pass^k.** Run the same real-model task 5 times. How many succeed? (See τ-bench's pass^k in the lesson.)

## Expected results

- Scripted runs are deterministic: `happy` ends with the 209715200-bytes answer. `escape` prints
  `network blocked`, `fs blocked`, `uid 65534`, then `killed: wall-clock limit 10s exceeded`. `loop` stops with
  `loop detected`. `tokens` stops with `token budget exhausted`. The crash/resume pair leaves exactly one line in
  `outbox.jsonl` and logs `duplicate suppressed`.
- Real model: behaviour varies by model and seed. A 0.5B model usually calls `search_docs` and answers. It often
  skips later steps (arithmetic, email) or produces malformed calls. That is a realistic reason to evaluate agents
  over many trials and to keep budgets tight.

## Clean up

```bash
docker compose -p sd-25 down -v
rm -f trace.jsonl outbox.jsonl journal-*.json
```

## Cost

€0. Local CPU only. No API keys. (To try a hosted model, set `--model-url`, `--model` and `OPENAI_API_KEY`. That
is optional and may cost money.)

## Test status

**runtime-tested** on 2026-11-20. Host: Ubuntu 24.04.5 LTS, kernel 7.0.0-43-generic, Docker 29.10.0, Compose
v5.8.0, Python 3.12.3, uv, `mcp==2.3.0`, llama.cpp `server-b12464`, Qwen2.5-0.5B-Instruct Q4_0 GGUF.

Observed:
- `--scripted happy`: 3 model turns, `search_docs` returned `[nw-02]…`, `run_python` returned `exit=0 | 209715200`
  (≈1.7 s including container start). Final answer printed.
- `--scripted escape`: `network blocked: gaierror | fs blocked: OSError | uid 65534`. The infinite loop was
  `killed: wall-clock limit 10s exceeded` (10.2 s).
- `--scripted loop`: stopped at the 3rd identical call (`loop_detected`, repeats=3).
- `--scripted tokens --max-tokens 1500`: stopped with `token budget exhausted (1544/1500)` (exit code 2). The check
  runs *before* each model call, so a budget can be overshot by one call.
- `--scripted email --approve never`: approval denied, no outbox entry. The crash run exited with code 9 after the
  send. The resumed run logged `duplicate suppressed (idempotency_key=t1:0:send_email)`, and the outbox
  contained exactly one email. The scripted suite was re-run on the final `agent.py` with the same results (exit codes:
  happy 0, loop 3, tokens 2, crash 9, resume 0).
- Real model, default task (3 runs): each run called `search_docs("upload size limit")` and answered "200 MB" in 2
  model calls (1,146 tokens). It did not perform the bytes conversion. In an earlier run before the runtime handled
  it, the model emitted a truncated `run_python` call. llama.cpp returned HTTP 500 on every later turn because the
  malformed call was in the history. The current runtime drops such calls (`malformed_tool_call`).
- Real model, email task (`--approve never` and `always`): the model searched and answered but never called
  `send_email`, so the approval path was exercised only in scripted mode.
- Not tested: gVisor (`SANDBOX_RUNTIME=runsc`), larger models, interactive `--approve ask`.

## Troubleshooting

- `permission denied … docker.sock`: the user running the agent must be able to run `docker` (the MCP server
  starts sandbox containers).
- First sandbox call is slow: Docker is pulling `python:3.12-slim`. Pre-pull it.
- HTTP 500 `Failed to parse tool call arguments`: the model produced invalid JSON. The runtime records
  `malformed_tool_call` and retries. If it repeats, use a larger model.
- No tool calls at all: the server must run with `--jinja` (already set) so the chat template's tool format is
  used.
