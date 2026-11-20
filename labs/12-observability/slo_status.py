#!/usr/bin/env python3
"""Print the lab's SLO view from the Prometheus HTTP API (stdlib only).

Usage:  python3 slo_status.py            # one snapshot
        python3 slo_status.py --watch    # refresh every 5 s (Ctrl-C to stop)
"""
import json
import sys
import time
import urllib.parse
import urllib.request

PROM = "http://127.0.0.1:11290"
QUERIES = {
    "requests/s": 'sum(rate(http_server_request_duration_seconds_count{job="lumen-api"}[1m]))',
    "error ratio 25s": "lumen:sli_error:ratio_rate25s",
    "error ratio 5m": "lumen:sli_error:ratio_rate5m",
    "burn rate 25s": "lumen:slo_burn_rate:25s",
    "burn rate 5m": "lumen:slo_burn_rate:5m",
    "p99 latency (s)": 'histogram_quantile(0.99, sum by (le) (rate(http_server_request_duration_seconds_bucket{job="lumen-api"}[1m])))',
    "series for metric": 'count(http_server_request_duration_seconds_bucket{job="lumen-api"})',
}


def query(expr: str):
    url = f"{PROM}/api/v1/query?" + urllib.parse.urlencode({"query": expr})
    with urllib.request.urlopen(url, timeout=5) as r:
        res = json.load(r)["data"]["result"]
    return float(res[0]["value"][1]) if res else None


def alerts():
    with urllib.request.urlopen(f"{PROM}/api/v1/alerts", timeout=5) as r:
        return [(a["labels"]["alertname"], a["state"]) for a in json.load(r)["data"]["alerts"]]


def snapshot() -> None:
    print(time.strftime("%H:%M:%S"))
    for name, expr in QUERIES.items():
        v = query(expr)
        print(f"  {name:18s} {'-' if v is None else f'{v:.4f}'}")
    print("  alerts            ", alerts() or "none")


if __name__ == "__main__":
    if "--watch" in sys.argv:
        while True:
            snapshot()
            time.sleep(5)
    else:
        snapshot()
