# L06 — Replication lag, synchronous commit and failover

Lab for [SYSDESIGN-06 Replication & consistency](../../course/01-foundations/06-replication-consistency.md).

## Goal

Run a PostgreSQL primary with a streaming hot-standby replica and make the chapter's failure modes visible: a
read-your-writes violation, replication lag under load, the availability price of synchronous replication, a manual
failover, and a split brain caused by bringing back an unfenced old primary.

## What you will observe

- A row written on the primary that the replica does not return for ~2 s (with an injected apply delay), and
  `pg_stat_replication.replay_lag` reporting the same delay.
- Natural lag on a laptop: a few KB of WAL and about a millisecond, even under `pgbench` load.
- With a synchronous standby configured, a commit that **does not return** once the standby is stopped, and that
  commits later when the wait is released.
- `pg_promote()` turning the replica into a writable primary.
- Two writable primaries with divergent histories after the old primary restarts.

## Prerequisites

- Docker Engine with Compose v2+ (tested: Docker 29.10.0, Compose v5.8.0), Bash, GNU `date`/`timeout` (Linux; on macOS
  install coreutils).
- Image `postgres:18.7-alpine` (~430 MB on disk). `pgbench` ships in the image.
- Free localhost ports **10632** (primary) and **10633** (replica).

## Run

```bash
cd labs/06-replication-consistency
docker compose -p sd-06 up -d --wait     # primary initialises; replica clones it with pg_basebackup and streams
./experiments.sh all                     # all six experiments, ~1 minute
```

Or one at a time, in this order: `status`, `ryw`, `load`, `sync`, `failover`, `splitbrain`. The last two change the
topology; reset with `docker compose -p sd-06 down -v && docker compose -p sd-06 up -d --wait`.

How the replica is built (`replica-entrypoint.sh`): `pg_basebackup -R -X stream -C -S replica1` clones the primary,
writes `standby.signal` and `primary_conninfo` (with `application_name=replica1`), and creates a physical replication
slot so the primary keeps the WAL the replica still needs.

## Experiments

1. **`status`** — `pg_stat_replication` on the primary (state, sync state, replay lag); a write attempted on the replica
   fails because it is a read-only standby.
2. **`ryw`** — sets `recovery_min_apply_delay = '2s'` on the replica, writes on the primary, reads immediately from the
   replica (missing), polls until visible, then resets the delay.
3. **`load`** — `pgbench -c 8 -j 4 -T 8 -N` on the primary while sampling WAL bytes behind and `replay_lag` every 0.5 s.
4. **`sync`** — sets `synchronous_standby_names = 'replica1'`, runs `pgbench` under `synchronous_commit` = `local`,
   `remote_write`, `on` and `remote_apply`, then stops the replica and attempts one commit with a 5 s client timeout.
5. **`failover`** — stops the primary and calls `pg_promote(wait => true)` on the replica, then writes to it.
6. **`splitbrain`** — restarts the old primary (nothing fenced it, so it starts as a primary) and writes to both nodes.

Extension (not scripted): on a laptop the replica is microseconds away, so synchronous replication's *latency* cost is
invisible. Add delay between the containers (for example with Toxiproxy, used in lab L11, or `tc netem` in a container
with `NET_ADMIN`) and rerun `sync` to see each mode's round-trip cost appear.

## Expected results

- `ryw`: replica count `0` immediately after the write, row visible after ≈ the configured delay; `replay_lag` ≈ delay.
- `load`: bytes behind in the hundreds to low thousands, lag around a millisecond; no growth over the run.
- `sync`: on one host, TPS for the four modes within run-to-run noise of each other; the commit with the replica stopped
  does **not** return within 5 s; after the reset its row is present.
- `failover`: `pg_is_in_recovery()` goes from `t` to `f`; writes succeed on the promoted node.
- `splitbrain`: the old primary reports `pg_is_in_recovery() = f` and accepts a write; both nodes show different latest
  rows.

## Clean up

```bash
docker compose -p sd-06 down -v
```

## Cost

€0: everything runs locally.

## Test status

**runtime-tested** — 2026-11-19 (UTC), Ubuntu Linux (kernel 7.0.0-43-generic, x86_64, 12 cores, heavily loaded by
unrelated workloads), Docker 29.10.0, Compose v5.8.0, PostgreSQL 18.7 (`postgres:18.7-alpine`). The full
`./experiments.sh all` run took 1 min 6 s. Observed output (abridged):

```text
== 1. replica1|streaming|async|00:00:00.001037 ; write to replica: ERROR: cannot execute INSERT in a read-only transaction
== 2. replica sees it immediately: 0 ; replica first saw the row after 2164 ms ; replay_lag 00:00:01.99605
== 3. bytes behind 40-2144, replay_lag 0.2-2.8 ms ; pgbench: latency average 2.972 ms, tps 2692
== 4. sync_state: sync
      local         latency average = 3.048 ms tps = 2624
      remote_write  latency average = 2.857 ms tps = 2800
      on            latency average = 2.766 ms tps = 2893
      remote_apply  latency average = 2.822 ms tps = 2835
      commit did NOT return within 5017 ms: the primary waits for a standby that is gone
      rows with the 'timed-out' note on the primary now: 1
== 5. replica in recovery? t -> promote: t -> in recovery? f ; write on new primary: id=34
== 6. old primary in recovery? f ; old primary accepted id=4 ; new primary accepted id=35
```

Two observations worth discussing:

- The four `synchronous_commit` modes did not differ beyond noise in this run (an earlier development run on the same
  host showed `local` 2.5 ms vs `on` 3.9 ms average latency). With both containers on one host there is no real network
  round trip to pay; the experiment demonstrates the availability cost, not the latency cost.
- After promotion the new primary's ids jumped to 34 while the old primary continued at 4. PostgreSQL WAL-logs sequence
  values ahead in batches (`SEQ_LOG_VALS = 32` in `src/backend/commands/sequence.c`), so the replica inherited a value
  32 ahead. The two nodes' id ranges therefore do not collide *immediately* in this run, but they would after about 30
  more inserts on the old primary: the divergence is real either way.

## Troubleshooting

- **Replica never becomes healthy**: `docker compose -p sd-06 logs replica`. If the clone failed half-way, `down -v`
  and start again (the entrypoint only clones into an empty data directory).
- **`pg_hba.conf` rejection for `replicator`**: the init script runs only on the primary's *first* start; `down -v` to
  re-initialise.
- **`sync` leaves the primary blocking**: run `docker compose -p sd-06 exec primary psql -U postgres -c "ALTER SYSTEM
  RESET synchronous_standby_names" -c "SELECT pg_reload_conf()"`.
- **`timeout` or `date +%s%3N` not found** (macOS): install GNU coreutils and use `gtimeout`/`gdate`, or run in a Linux
  VM.
