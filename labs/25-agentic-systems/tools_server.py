"""L25 — MCP tool server (official Python SDK, stdio transport).

Tools:
  search_docs(query)                      read-only, in-memory fictional Lumen docs
  run_python(code)                        executes model-written code in a locked-down container
  send_email(to, subject, body, idem_key) side effect (writes to an outbox file), idempotent by key

The *agent runtime* decides which of these need approval; the server never trusts the caller either:
arguments are validated, outputs are truncated, the sandbox has no network and no credentials.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import uuid

from mcp.server import MCPServer

SANDBOX_IMAGE = os.environ.get("SANDBOX_IMAGE", "python:3.12-slim")
SANDBOX_RUNTIME = os.environ.get("SANDBOX_RUNTIME", "")          # e.g. "runsc" if gVisor is installed
SANDBOX_TIMEOUT_S = float(os.environ.get("SANDBOX_TIMEOUT_S", "10"))
OUTBOX = pathlib.Path(os.environ.get("OUTBOX", "outbox.jsonl"))
MAX_OUTPUT = 2_000  # characters returned to the model, never megabytes

DOCS = {
    "nw-02": "Error LUM-4031: upload larger than the workspace limit of 200 MB (Northwind).",
    "nw-10": "Admins can set chat history retention between 7 and 730 days (Northwind).",
    "fb-02": "Fabrikam workspace: LUM-4031 appears when a file exceeds 50 MB.",
    "nw-05": "Workspace owners rotate the API key under Settings > Security; old key valid 24 h.",
}

mcp = MCPServer("lumen-tools")


@mcp.tool()
def search_docs(query: str) -> str:
    """Search the Lumen help centre. Returns up to 3 matching passages with their ids."""
    terms = {t.lower().strip("?.,") for t in query.split() if len(t) > 2}
    scored = sorted(((sum(t in text.lower() for t in terms), did, text) for did, text in DOCS.items()),
                    reverse=True)
    hits = [f"[{did}] {text}" for score, did, text in scored if score > 0][:3]
    return "\n".join(hits) or "no results"


@mcp.tool()
def run_python(code: str) -> str:
    """Run a short Python 3 program in an isolated sandbox (no network, read-only FS, 128 MB RAM,
    0.5 CPU, 64 processes, 10 s). Returns stdout/stderr (truncated). Print the values you need."""
    if len(code) > 10_000:
        return "error: code too long"
    name = f"sd25-sbx-{uuid.uuid4().hex[:10]}"
    cmd = ["docker", "run", "--rm", "-i", "--name", name,
           "--network", "none",                 # no egress: exfiltration and downloads fail
           "--read-only", "--tmpfs", "/tmp:rw,size=16m",
           "--memory", "128m", "--memory-swap", "128m", "--cpus", "0.5", "--pids-limit", "64",
           "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
           "--user", "65534:65534",            # nobody
           "--env", "HOME=/tmp"]
    if SANDBOX_RUNTIME:
        cmd += ["--runtime", SANDBOX_RUNTIME]
    cmd += [SANDBOX_IMAGE, "python", "-I", "-"]
    try:
        p = subprocess.run(cmd, input=code, capture_output=True, text=True, timeout=SANDBOX_TIMEOUT_S)
        out = (p.stdout + ("\n[stderr]\n" + p.stderr if p.stderr else ""))
        status = f"exit={p.returncode}"
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "kill", name], capture_output=True)
        out, status = "", f"killed: wall-clock limit {SANDBOX_TIMEOUT_S:.0f}s exceeded"
    return f"{status}\n{out[:MAX_OUTPUT]}"


@mcp.tool()
def send_email(to: str, subject: str, body: str, idempotency_key: str) -> str:
    """Send an email (simulated: appended to an outbox file). Duplicate idempotency keys are ignored."""
    if "@" not in to or not to.endswith(("example.com", "example.org")):
        return "error: recipient must be an example.com / example.org address in this lab"
    seen = set()
    if OUTBOX.exists():
        seen = {json.loads(line)["idempotency_key"] for line in OUTBOX.read_text().splitlines() if line}
    if idempotency_key in seen:
        return f"duplicate suppressed (idempotency_key={idempotency_key})"
    with OUTBOX.open("a") as f:
        f.write(json.dumps({"to": to, "subject": subject, "body": body[:500],
                            "idempotency_key": idempotency_key}) + "\n")
    return f"sent to {to}"


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
