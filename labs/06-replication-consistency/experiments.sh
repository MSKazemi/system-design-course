#!/usr/bin/env bash
# Lab L06 experiments. Usage: ./experiments.sh {status|ryw|load|sync|failover|splitbrain|all}
# Requires the stack to be up:  docker compose -p sd-06 up -d --wait
set -euo pipefail
cd "$(dirname "$0")"
DC=(docker compose -p sd-06)

P() { "${DC[@]}" exec -T primary psql -X -U postgres -d lumen -Atq -c "$1"; }
R() { "${DC[@]}" exec -T replica psql -X -U postgres -d lumen -Atq -c "$1"; }
now_ms() { date +%s%3N; }
hr() { printf '\n== %s\n' "$*"; }

status() {
  hr "1. Replication status (on the primary: pg_stat_replication)"
  P "SELECT application_name, state, sync_state, coalesce(replay_lag::text,'(idle)') AS replay_lag
     FROM pg_stat_replication;"
  echo "replica in recovery (read-only standby)? $(R 'SELECT pg_is_in_recovery();')"
  echo -n "write to replica: "
  R "INSERT INTO events(note) VALUES ('should fail');" 2>&1 | tail -1 || true
}

ryw() {
  hr "2. Read-your-writes violation: replica applies WAL 2 s late (recovery_min_apply_delay)"
  R "ALTER SYSTEM SET recovery_min_apply_delay = '2s';" ; R "SELECT pg_reload_conf();" >/dev/null
  sleep 1
  local id t0 seen
  id=$(P "INSERT INTO events(note) VALUES ('profile updated') RETURNING id;")
  t0=$(now_ms)
  echo "wrote id=$id on primary; primary sees it: $(P "SELECT count(*) FROM events WHERE id=$id;")"
  echo "replica sees it immediately: $(R "SELECT count(*) FROM events WHERE id=$id;")"
  until [ "$(R "SELECT count(*) FROM events WHERE id=$id;")" = "1" ]; do sleep 0.1; done
  seen=$(( $(now_ms) - t0 ))
  echo "replica first saw the row after ${seen} ms"
  echo "replay_lag reported by primary: $(P "SELECT coalesce(replay_lag::text,'(idle)') FROM pg_stat_replication;")"
  R "ALTER SYSTEM RESET recovery_min_apply_delay;" ; R "SELECT pg_reload_conf();" >/dev/null
}

load() {
  hr "3. Natural lag under write load (no artificial delay): pgbench on the primary, sampled every 0.5 s"
  P "SET client_min_messages = warning; DROP TABLE IF EXISTS pgbench_accounts, pgbench_branches, pgbench_history, pgbench_tellers;"
  "${DC[@]}" exec -T primary pgbench -U postgres -i -s 10 -q lumen >/dev/null 2>&1
  "${DC[@]}" exec -T primary pgbench -U postgres -c 8 -j 4 -T 8 -N lumen >/tmp/sd06-pgbench.$$ 2>&1 &
  local pid=$!
  for _ in $(seq 1 12); do
    P "SELECT 'bytes behind=' || pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)
              || '  replay_lag=' || coalesce(replay_lag::text, '(idle)') FROM pg_stat_replication;"
    sleep 0.5
  done
  wait $pid || true
  grep -E "^tps|latency average" /tmp/sd06-pgbench.$$ || true
  rm -f /tmp/sd06-pgbench.$$
}

bench_tps() { # $1 = synchronous_commit value
  "${DC[@]}" exec -T primary env PGOPTIONS="-c synchronous_commit=$1" \
    pgbench -U postgres -c 8 -j 4 -T 8 -N lumen 2>/dev/null | grep -E "^tps|latency average" | tr '\n' ' '
  echo
}

sync() {
  hr "4. Synchronous replication: latency cost and availability cost"
  P "SELECT 1 FROM pgbench_branches LIMIT 1;" >/dev/null 2>&1 || \
    "${DC[@]}" exec -T primary pgbench -U postgres -i -s 10 -q lumen >/dev/null 2>&1
  P "ALTER SYSTEM SET synchronous_standby_names = 'replica1';" ; P "SELECT pg_reload_conf();" >/dev/null
  sleep 1
  echo "sync_state now: $(P "SELECT sync_state FROM pg_stat_replication;")"
  for mode in local remote_write on remote_apply; do
    printf '%-13s ' "$mode"; bench_tps "$mode"
  done
  echo "-- stop the replica, then try one synchronous commit with a 5 s client timeout:"
  "${DC[@]}" stop replica >/dev/null 2>&1
  local t0; t0=$(now_ms)
  if timeout 5 "${DC[@]}" exec -T primary psql -X -U postgres -d lumen -Atq \
       -c "INSERT INTO events(note) VALUES ('sync write, no standby');" >/dev/null 2>&1; then
    echo "commit returned after $(( $(now_ms) - t0 )) ms"
  else
    echo "commit did NOT return within $(( $(now_ms) - t0 )) ms: the primary waits for a standby that is gone"
  fi
  P "ALTER SYSTEM RESET synchronous_standby_names;" ; P "SELECT pg_reload_conf();" >/dev/null
  "${DC[@]}" start replica >/dev/null 2>&1
  "${DC[@]}" up -d --wait replica >/dev/null 2>&1
  echo "synchronous_standby_names reset; replica restarted."
  echo "rows with the 'timed-out' note on the primary now: $(P "SELECT count(*) FROM events WHERE note = 'sync write, no standby';")"
  echo "note: the client gave up, but the INSERT was already in the primary's WAL and committed as soon as"
  echo "      the wait was released: a 'timed-out' write is not necessarily a 'failed' write (make writes idempotent)."
}

failover() {
  hr "5. Failover: stop the primary, promote the replica"
  P "INSERT INTO events(note) VALUES ('last write before failover');" >/dev/null
  sleep 1
  "${DC[@]}" stop primary >/dev/null 2>&1
  echo "primary stopped. replica in recovery? $(R 'SELECT pg_is_in_recovery();')"
  echo "promote: $(R 'SELECT pg_promote(wait => true, wait_seconds => 30);')"
  echo "replica in recovery? $(R 'SELECT pg_is_in_recovery();')"
  echo "write on new primary: id=$(R "INSERT INTO events(note) VALUES ('written on new primary') RETURNING id;")"
}

splitbrain() {
  hr "6. Split brain: the old primary comes back and nobody fenced it"
  "${DC[@]}" start primary >/dev/null 2>&1
  until P "SELECT 1;" >/dev/null 2>&1; do sleep 1; done
  echo "old primary in recovery? $(P 'SELECT pg_is_in_recovery();')   (false = it thinks it is primary)"
  local a b
  a=$(P "INSERT INTO events(note) VALUES ('order 42 paid (old primary)') RETURNING id;")
  b=$(R "INSERT INTO events(note) VALUES ('order 42 refunded (new primary)') RETURNING id;")
  echo "old primary accepted id=$a; new primary accepted id=$b"
  echo "old primary latest rows:"; P "SELECT id, note FROM events ORDER BY id DESC LIMIT 3;"
  echo "new primary latest rows:"; R "SELECT id, note FROM events ORDER BY id DESC LIMIT 3;"
  echo "two writable copies with divergent histories (and possibly the same ids): this is split brain."
  echo "fix in production: fence the old primary (STONITH / revoke its lease) BEFORE promoting, then"
  echo "rejoin it with pg_rewind or a fresh pg_basebackup. Reset this lab with: docker compose -p sd-06 down -v"
}

case "${1:-all}" in
  status) status ;;
  ryw) ryw ;;
  load) load ;;
  sync) sync ;;
  failover) failover ;;
  splitbrain) splitbrain ;;
  all) status; ryw; load; sync; failover; splitbrain ;;
  *) echo "usage: $0 {status|ryw|load|sync|failover|splitbrain|all}"; exit 2 ;;
esac
