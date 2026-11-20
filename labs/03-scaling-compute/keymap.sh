#!/usr/bin/env bash
# Experiment 5: how many keys move to a different replica when one replica disappears?
# Usage: ./keymap.sh consistent|mapbased [N_KEYS]
set -euo pipefail
cd "$(dirname "$0")"
MODE="${1:-consistent}"; N="${2:-300}"
PORT=10383; BACKEND=be_hash_consistent
if [ "$MODE" = "mapbased" ]; then PORT=10384; BACKEND=be_hash_mapbased; fi

# Wait until HAProxy reports server $1 in $BACKEND with status $2 (UP or DOWN).
wait_for() {
  for _ in $(seq 1 60); do
    s=$(curl -s 'http://127.0.0.1:10390/;csv' | awk -F, -v b="$BACKEND" -v sv="$1" '$1==b && $2==sv {print $18}')
    case "$s" in "$2"*) return 0;; esac
    sleep 1
  done
  echo "timed out waiting for $1 to be $2 (last status: ${s:-none})" >&2; exit 1
}
# One line per key: the name of the replica that answered.
map() { for k in $(seq 1 "$N"); do
  curl -s "http://127.0.0.1:${PORT}/work?key=user-$k" | sed -E 's/.*"name": "([^"]+)".*/\1/'; echo; done; }

B=$(mktemp); A=$(mktemp); trap 'rm -f "$B" "$A"' EXIT
for s in app1 app2 app3; do wait_for "$s" UP; done
echo "mapping $N keys with all three replicas up ($MODE)..."
map > "$B"
echo "stopping app3 and waiting for HAProxy to mark it DOWN..."
docker compose -p sd-03 stop app3 >/dev/null 2>&1
wait_for app3 DOWN
map > "$A"
moved=$(paste -d" " "$B" "$A" | awk '$1!=$2' | wc -l)
on3=$(grep -c "^app3$" "$B" || true)
echo "keys that were on app3: $on3 / $N"
echo "keys that moved:        $moved / $N"
echo "restarting app3..."
docker compose -p sd-03 start app3 >/dev/null 2>&1
wait_for app3 UP
