#!/usr/bin/env bash
# Step the arrival rate and print one RESULT line (client view) and one SERVER line
# (server view, for Little's law) per step.
#
# Usage: ./sweep.sh [DURATION] [rate ...]       e.g. ./sweep.sh 30s 20 40 60 80 90 95
# By default k6 runs as the grafana/k6 container on the compose network.
# If you have the k6 binary installed, K6_BIN=k6 ./sweep.sh runs it on the host instead
# (it then targets the published port 127.0.0.1:10101).
# K6_OUT=experimental-prometheus-rw streams k6 metrics to the optional Prometheus.
set -euo pipefail
cd "$(dirname "$0")"
DURATION="${1:-30s}"; shift || true
RATES=("$@"); [ ${#RATES[@]} -eq 0 ] && RATES=(20 40 60 70 80 90 95 98 110)
for r in "${RATES[@]}"; do
  args=(run --quiet -e RATE="$r" -e DURATION="$DURATION")
  [ -n "${K6_OUT:-}" ] && args+=(-o "$K6_OUT")
  if [ -n "${K6_BIN:-}" ]; then
    "$K6_BIN" "${args[@]}" -e TARGET=http://127.0.0.1:10101 k6/load.js 2>&1
  else
    docker compose -p sd-01 run --rm k6 "${args[@]}" /scripts/load.js 2>&1
  fi | grep --line-buffered -E 'RESULT|SERVER' | sed -E 's/.*(RESULT|SERVER)/\1/; s/" source=console//'
done
