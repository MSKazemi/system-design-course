"""Tiny HTTP clients for lab L14, shipped in the same image as the server (no extra pulls).

  python client.py load  <url> <seconds>   hammer <url> in a loop for <seconds>
  python client.py probe <url>             5 calls/s forever, one line per call: "<unix-ts> <version|ERR>"
"""
import json
import sys
import time
import urllib.request


def call(url: str, timeout: float) -> str:
    # A fresh connection per call, so kube-proxy spreads calls across all ready endpoints.
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.load(r).get("version", "?")


def load(url: str, seconds: float) -> None:
    end = time.time() + seconds
    ok = err = 0
    while time.time() < end:
        try:
            call(url, 5)
            ok += 1
        except Exception:
            err += 1
    print(f"load done: ok={ok} err={err}", flush=True)


def probe(url: str) -> None:
    while True:
        try:
            v = call(url, 2)
        except Exception:
            v = "ERR"
        print(f"{int(time.time())} {v}", flush=True)
        time.sleep(0.2)


if __name__ == "__main__":
    mode, url = sys.argv[1], sys.argv[2]
    if mode == "load":
        load(url, float(sys.argv[3]))
    else:
        probe(url)
