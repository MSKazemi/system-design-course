# L09 — Kill the leader: Raft elections, quorum loss and fencing tokens with etcd

Lab for [SYSDESIGN-09 Coordination & consensus](../../course/01-foundations/09-coordination-consensus.md).

## Goal

Run a three-member etcd (Raft) cluster on your laptop. Watch a leader election happen when you kill the leader, see
what losing a majority does to reads and writes, and demonstrate why a lease-based lock needs a **fencing token**.

## What you will observe

1. Exactly one member reports itself `LEADER`, and all members agree on the Raft term.
2. After you SIGKILL the leader, the two survivors elect a new leader in a **higher term**. The script measures how
   long that took and when the first write succeeded again.
3. With two of three members stopped, **linearizable writes and reads fail**, while a `serializable` read still answers
   from the remaining member's local (possibly stale) state.
4. Client A takes a lease-based lock, "pauses" past its lease TTL, and writes after client B has taken the lock.
   Without fencing, A's stale write **overwrites** B's. With the etcd revision used as a fencing token, the store
   **rejects** it.

## Prerequisites

- Docker Engine with Compose v2+ (tested with Docker 29.10.0 and Docker Compose v5.8.0)
- Python 3.10+ on the host (standard library only; tested with Python 3.12.3)
- Free host ports 10901–10903 (bound to 127.0.0.1 only)
- Image: `gcr.io/etcd-development/etcd:v3.7.4` (about 87 MB unpacked; etcd v3.7.4 is the current patch release as of
  2026-11, see https://github.com/etcd-io/etcd/releases)

## Run

```bash
cd labs/09-coordination-consensus
docker compose -p sd-09 up -d --wait     # starts etcd1..3 and waits for health checks
python3 -I lab.py status                 # who leads, in which term
```

You can also use the bundled `etcdctl` inside any member:

```bash
docker compose -p sd-09 exec etcd1 etcdctl \
  --endpoints=http://etcd1:2379,http://etcd2:2379,http://etcd3:2379 endpoint status -w table
```

## Experiments

1. **Baseline.** Run `python3 -I lab.py status` a few times. Note the leader, the `raftTerm` (identical on all
   members) and `raftIndex`.
2. **Kill the leader.** `python3 -I lab.py kill-leader` sends SIGKILL to the current leader with `docker kill`. It
   then polls the survivors every 50 ms until one reports a different leader in a higher term, and attempts a write
   (0.5 s client timeout) until one succeeds. Times are measured from just *before* the kill command, so they include
   the time Docker takes to deliver the signal. The script prints that time separately. Run `python3 -I lab.py status`: the killed member shows `DOWN`.
3. **Rejoin.** `python3 -I lab.py restart-all`. The old leader returns as a **follower** in the new term. It does not
   take back leadership, because its term is stale. Repeat experiments 2–3 three to five times and record the spread
   of election times.
4. **Quorum loss.** `python3 -I lab.py quorum-loss` stops etcd2 and etcd3. It then tries a write, a default
   (linearizable) read and a `serializable` read against etcd1. Restore with `python3 -I lab.py restart-all`.
5. **Fencing tokens.** `python3 -I lab.py fencing` runs the paused-client scenario twice, first against a store that
   does not check tokens and then against one that does. The token is the etcd revision at which the lock key was
   created; Jepsen's etcd analysis recommends exactly this.
6. **Tune timing (optional).** In `compose.yaml`, change `--election-timeout=1000` to `5000` on all three members.
   Recreate with `docker compose -p sd-09 down -v && docker compose -p sd-09 up -d --wait`, then repeat experiment 2.
   etcd's tuning guide says the election timeout should be at least 10× the RTT between members.
7. **Watch an election with etcdctl (optional).** In one terminal run
   `docker compose -p sd-09 exec etcd2 etcdctl elect lumen-scheduler sched-B`. In another run
   `docker compose -p sd-09 exec etcd1 etcdctl elect -l lumen-scheduler` to see who leads. Stop the first with Ctrl-C
   and watch leadership disappear.

## Expected results

Describe what you see; do not compare against someone else's numbers.

- Experiment 2: a new leader in a term greater than the old one. Subtract the printed `docker kill` time, and the rest
  is on the order of the election timeout (1000 ms by default) plus randomization and a vote round trip. It should be
  neither milliseconds nor tens of seconds. The
  first successful write comes at or shortly after the new leader appears.
- Experiment 3: the restarted member is a follower; the term does not go back.
- Experiment 4: the write and the linearizable read fail with a timeout or error. The serializable read succeeds.
- Experiment 5: final value `'A-2 (stale)'` without fencing, and `'B-1'` with fencing and a `REJECT` line for A.
- Experiment 6: the election takes noticeably longer.

## Clean up

```bash
docker compose -p sd-09 down -v
# optional: docker image rm gcr.io/etcd-development/etcd:v3.7.4
```

## Cost

€0. Everything runs locally; no cloud resources.

## Test status

**runtime-tested**, 2026-11-19/20. Host: Ubuntu 24.04 (Linux kernel 7.0.0), x86_64; Docker 29.10.0; Docker Compose
v5.8.0; Python 3.12.3; image `gcr.io/etcd-development/etcd:v3.7.4`. The laptop was also running other labs at the
time, so expect your timings to differ.

Observed (summary of real output):

- `docker compose -p sd-09 up -d --wait`: all three members healthy. `lab.py status` showed one `LEADER` and two
  followers, all at raftTerm 2. `etcd --help` in this image shows `--heartbeat-interval '100'`,
  `--election-timeout '1000'` and `--pre-vote 'true'` as defaults.
- `kill-leader`, final script version, 5 runs. Measured from *before* `docker kill`, which itself took about 0.5–0.65 s,
  a new leader in term N+1 was observed after about 1.6, 1.6, 1.7, 1.8 and 2.2 s. The first successful write came
  5–15 ms after the new leader was observed. Earlier runs that started the timer after a slower `docker compose kill`
  saw 0.57–1.14 s, which shows how much of the number is measurement overhead.
- After `restart-all`, the old leader rejoined as a follower in the new term; the term never went back.
- `quorum-loss`: `linearizable write: FAILED (TimeoutError)`, `range serializable=False: FAILED (TimeoutError)`,
  `range serializable=True: SUCCEEDED`.
- `fencing`: without the token check the final value was `'A-2 (stale)'`; with it, `REJECT A write 'A-2 (stale)'
  (token 20 < highest seen 22)` and final value `'B-1'`. B acquired the lock about 2.3–2.6 s after A stopped renewing,
  with a 2 s TTL.
- Experiment 7: `etcdctl elect lumen-scheduler sched-B` in etcd2 and `etcdctl elect -l lumen-scheduler` in etcd1
  printed `lumen-scheduler/<id>` and `sched-B`. The `endpoint status -w table` command also worked.
- Smoke re-run after a final code tidy: new leader in term 3 after ~1.7 s (docker kill ~0.58 s).
- **Not run:** experiment 6 (5000 ms election timeout).
- Cleaned up with `docker compose -p sd-09 down -v`. No containers or volumes remained.

## Troubleshooting

- **`No etcd member reachable`**: the cluster is not up or the ports are taken. Check `docker compose -p sd-09 ps` and
  `ss -ltnp | grep 1090`.
- **`--wait` times out on first start**: the members need each other to form a cluster. Check
  `docker compose -p sd-09 logs etcd1`; restarting all three together usually fixes a half-started cluster.
- **The election seems very slow or flaps**: etcd is sensitive to disk latency. On a busy laptop, WAL fsync can be
  slow; see the etcd FAQ on "failed to send out heartbeat on time".
- **The image has no shell**: the etcd image is minimal, so run `etcdctl` directly with `docker compose exec`, not
  through `sh -c`.
- **Leftover state between runs**: `docker compose -p sd-09 down -v` removes the data volumes; without `-v` the old
  cluster ID and terms persist.
