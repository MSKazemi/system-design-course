#!/usr/bin/env python3
"""L09 helper: observe Raft leader election and fencing tokens on a 3-member etcd cluster.

Standard library only. Talks to etcd's v3 JSON/HTTP gateway on localhost:10901-10903 and
uses `docker compose -p sd-09` to stop/start members.

Usage:
  python3 -I lab.py status          # who is leader, raft term, raft index per member
  python3 -I lab.py kill-leader     # SIGKILL the leader, time the election and first write
  python3 -I lab.py restart-all     # start any stopped member again
  python3 -I lab.py quorum-loss     # stop 2 of 3 members; show writes fail, stale reads work
  python3 -I lab.py fencing         # lease-based lock + revision as fencing token
"""
from __future__ import annotations

import base64
import json
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

PROJECT = "sd-09"
HERE = pathlib.Path(__file__).resolve().parent
MEMBERS = {"etcd1": 10901, "etcd2": 10902, "etcd3": 10903}


# ---------------------------------------------------------------- etcd HTTP gateway
def b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def unb64(s: str) -> str:
    return base64.b64decode(s).decode()


def call(port: int, path: str, body: dict, timeout: float = 2.0) -> dict:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        out = json.loads(resp.read() or b"{}")
    if "error" in out:  # gateway reports gRPC errors in the body
        raise RuntimeError(out.get("message") or out["error"])
    return out


def status(port: int, timeout: float = 0.5) -> dict | None:
    try:
        return call(port, "/v3/maintenance/status", {}, timeout=timeout)
    except (urllib.error.URLError, OSError, RuntimeError, TimeoutError):
        return None


def member_names(port: int) -> dict[str, str]:
    out = call(port, "/v3/cluster/member/list", {})
    return {m["ID"]: m.get("name", "?") for m in out["members"]}


def any_port() -> int:
    for port in MEMBERS.values():
        if status(port):
            return port
    sys.exit("No etcd member reachable on 10901-10903. Did you run `docker compose -p sd-09 up -d`?")


def compose(*args: str) -> None:
    subprocess.run(["docker", "compose", "-p", PROJECT, "-f", str(HERE / "compose.yaml"), *args],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def put(port: int, key: str, value: str, lease: str | None = None, timeout: float = 2.0) -> dict:
    body = {"key": b64(key), "value": b64(value)}
    if lease:
        body["lease"] = lease
    return call(port, "/v3/kv/put", body, timeout=timeout)


# ---------------------------------------------------------------- commands
def cmd_status() -> None:
    names = member_names(any_port())
    print(f"{'member':7} {'port':5} {'role':8} {'raftTerm':>8} {'raftIndex':>9} version")
    for name, port in MEMBERS.items():
        st = status(port)
        if not st:
            print(f"{name:7} {port:5} {'DOWN':8}")
            continue
        me = st["header"]["member_id"]
        role = "LEADER" if st.get("leader") == me else "follower"
        print(f"{name:7} {port:5} {role:8} {st.get('raftTerm', '?'):>8} {st.get('raftIndex', '?'):>9} "
              f"{st.get('version', '?')}  (leader={names.get(st.get('leader'), st.get('leader'))})")


def find_leader() -> tuple[str, int, int]:
    for name, port in MEMBERS.items():
        st = status(port)
        if st and st.get("leader") == st["header"]["member_id"]:
            return name, int(st["raftTerm"]), port
    sys.exit("No leader found (is the cluster healthy?)")


def cmd_kill_leader() -> None:
    old, old_term, _ = find_leader()
    survivors = {n: p for n, p in MEMBERS.items() if n != old}
    print(f"leader before: {old} (term {old_term}); killing it with SIGKILL ...")
    t0 = time.monotonic()  # started BEFORE the kill: the result is an upper bound that includes docker CLI time
    # plain `docker kill` is faster than `docker compose kill`, which keeps the measurement tighter
    subprocess.run(["docker", "kill", "--signal", "SIGKILL", f"{PROJECT}-{old}-1"], check=True,
                   stdout=subprocess.DEVNULL)
    kill_ms = (time.monotonic() - t0) * 1000
    new_leader_ms = first_write_ms = None
    new_name, new_term = None, None
    names = member_names(next(iter(survivors.values())))
    attempts = failures = 0
    while time.monotonic() - t0 < 30 and (new_leader_ms is None or first_write_ms is None):
        if new_leader_ms is None:
            for n, p in survivors.items():
                st = status(p, timeout=0.3)
                if st and st.get("leader") not in (None, "0") and int(st["raftTerm"]) > old_term \
                        and names.get(st["leader"]) != old:
                    new_leader_ms = (time.monotonic() - t0) * 1000
                    new_name, new_term = names.get(st["leader"], st["leader"]), int(st["raftTerm"])
                    break
        if first_write_ms is None:
            attempts += 1
            try:
                put(next(iter(survivors.values())), "/lab/probe", str(time.time()), timeout=0.5)
                first_write_ms = (time.monotonic() - t0) * 1000
            except Exception:
                failures += 1
        time.sleep(0.05)
    if new_leader_ms is None:
        print("no new leader within 30 s")
        return
    print(f"(docker kill itself took ~{kill_ms:.0f} ms; all times are measured from before the kill)")
    print(f"new leader:   {new_name} (term {new_term}) observed after ~{new_leader_ms:.0f} ms")
    if first_write_ms is not None:
        print(f"first successful write via a survivor after ~{first_write_ms:.0f} ms "
              f"({failures} failed write attempts out of {attempts})")
    print(f"restart the old leader with:  python3 -I lab.py restart-all   (it rejoins as a follower)")


def cmd_restart_all() -> None:
    compose("start")
    for _ in range(60):
        if all(status(p) for p in MEMBERS.values()):
            break
        time.sleep(0.5)
    cmd_status()


def cmd_quorum_loss() -> None:
    victims = ["etcd2", "etcd3"]
    print(f"stopping {victims}: 1 of 3 members left, majority (2) lost")
    compose("stop", "-t", "0", *victims)
    time.sleep(2)
    try:
        put(10901, "/lab/q", "x", timeout=3)
        print("linearizable write: SUCCEEDED (unexpected)")
    except Exception as exc:
        print(f"linearizable write: FAILED as expected ({type(exc).__name__}: {str(exc)[:70]})")
    for serializable in (False, True):
        try:
            call(10901, "/v3/kv/range", {"key": b64("/lab/probe"), "serializable": serializable}, timeout=3)
            print(f"range serializable={serializable}: SUCCEEDED"
                  + ("  <- answered from local, possibly stale state" if serializable else ""))
        except Exception as exc:
            print(f"range serializable={serializable}: FAILED ({type(exc).__name__})")
    print("restore with:  python3 -I lab.py restart-all")


class FencedStore:
    """The protected resource. It remembers the highest token and rejects older ones."""

    def __init__(self, fenced: bool) -> None:
        self.fenced, self.max_token, self.value = fenced, 0, None

    def write(self, who: str, token: int, value: str) -> None:
        if self.fenced and token < self.max_token:
            print(f"   store: REJECT {who} write {value!r} (token {token} < highest seen {self.max_token})")
            return
        self.max_token = max(self.max_token, token)
        self.value = value
        print(f"   store: accept {who} write {value!r} (token {token}); value now {self.value!r}")


def acquire(port: int, who: str, ttl: int) -> tuple[str, int]:
    """Lease-backed lock: create /lab/lock only if it does not exist. Token = revision of the create."""
    lease = call(port, "/v3/lease/grant", {"TTL": ttl})["ID"]
    key = b64("/lab/lock")
    while True:
        out = call(port, "/v3/kv/txn", {
            "compare": [{"target": "CREATE", "key": key, "result": "EQUAL", "create_revision": "0"}],
            "success": [{"request_put": {"key": key, "value": b64(who), "lease": lease}}],
            "failure": [{"request_range": {"key": key}}],
        })
        if out.get("succeeded"):
            return lease, int(out["header"]["revision"])
        time.sleep(0.2)  # someone else holds it; wait for their lease to expire


def cmd_fencing() -> None:
    port = any_port()
    for fenced in (False, True):
        call(port, "/v3/kv/deleterange", {"key": b64("/lab/lock")})
        print(f"\n=== storage {'WITH' if fenced else 'WITHOUT'} fencing-token check ===")
        store = FencedStore(fenced)
        lease_a, tok_a = acquire(port, "A", ttl=2)
        print(f"A acquires lock: lease {lease_a}, fencing token (etcd revision) {tok_a}")
        store.write("A", tok_a, "A-1")
        print("A pauses (think: 5 s GC pause) and stops refreshing its lease ...")
        t0 = time.monotonic()
        lease_b, tok_b = acquire(port, "B", ttl=10)
        print(f"B acquires lock after ~{time.monotonic() - t0:.1f} s (A's lease expired): token {tok_b}")
        store.write("B", tok_b, "B-1")
        print("A wakes up, still believes it holds the lock, writes with its old token:")
        store.write("A", tok_a, "A-2 (stale)")
        print(f"final value: {store.value!r}")
        call(port, "/v3/lease/revoke", {"ID": lease_b})


def main() -> None:
    cmds = {"status": cmd_status, "kill-leader": cmd_kill_leader, "restart-all": cmd_restart_all,
            "quorum-loss": cmd_quorum_loss, "fencing": cmd_fencing}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]]()


if __name__ == "__main__":
    main()
