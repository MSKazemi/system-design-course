# L07 — Consistent hashing and rebalancing, simulated

Lab for [SYSDESIGN-07 Partitioning & sharding](../../course/01-foundations/07-partitioning-sharding.md).

## Goal

Measure, instead of memorising, how four key-to-node mappings behave when the cluster grows, how virtual nodes change
balance, what key salting does to a hot key under a skewed workload, and why monotonically increasing keys break range
partitioning.

## What you will observe

- `hash % n` moving ~91 % of keys when 10 nodes become 11; ring, rendezvous and jump hash moving ~9 % (the minimum,
  1/11).
- A consistent-hash ring with one token per node putting ~3× the average load on its busiest node, and that factor
  shrinking as virtual nodes increase.
- The hottest key of a Zipf(1.1) workload carrying more traffic than a whole node's fair share, and salting the top keys
  bringing the busiest node close to the mean.
- Range partitioning with fixed boundaries sending every new timestamp-keyed write to one partition.

## Prerequisites

- Python **3.10 or newer**, standard library only (tested with 3.12.3 on the host and 3.14.10 in `python:3.14-slim`).
  No Docker, no packages, no network.

## Run

```bash
cd labs/07-partitioning-sharding
python3 -m unittest -v test_shardsim      # 7 property tests (monotonicity, minimal movement, balance)
python3 shardsim.py all                    # all five experiments, a few seconds
python3 shardsim.py --help
```

Individual experiments: `movement`, `balance`, `hotkey`, `range`, `lookup`. Useful knobs: `--nodes`, `--keys`,
`--vnodes`, `--zipf`, `--hot`.

## Experiments

1. **`movement`** — fraction of keys whose node changes when growing from `--nodes` to `--nodes + 1`, per scheme.
2. **`balance`** — max/mean, min/mean and coefficient of variation of keys per node for a ring with 1, 8, 64 and 256
   virtual nodes, and for modulo, rendezvous and jump.
3. **`hotkey`** — request weights follow Zipf(`--zipf`) over the keys; the `--hot` most popular keys are salted into
   1, 4, 16 or 64 sub-keys; reports the busiest node's share of all requests.
4. **`range`** — 100,000 writes with increasing timestamp keys against fixed range boundaries vs a hash ring.
5. **`lookup`** — relative per-lookup cost of each scheme in pure Python (rendezvous is O(n) per lookup).

Try next: `python3 shardsim.py movement --nodes 4`; `python3 shardsim.py balance --nodes 50`;
`python3 shardsim.py hotkey --zipf 0.8` (less skew: does salting still matter?); `--vnodes 256` for the hot-key run.
Then extend `shardsim.py`: add consistent hashing with bounded loads (Mirrokni et al., 2018: forward a key to the next
node clockwise when its owner already holds ⌈c·m/n⌉ keys) and measure max/mean and movement for c = 1.25.

## Expected results

- `movement`: modulo ≈ n/(n+1); the three consistent schemes ≈ 1/(n+1), within a fraction of a percent at 100,000 keys.
- `balance`: ring max/mean falling steeply from v = 1 to v = 64, slowly after; modulo, rendezvous and jump all near 1.0
  for uniform keys.
- `hotkey`: busiest-node share falling as the salt count rises, until the ring's own placement variance dominates.
- `range`: one range partition receives 100 % of new writes; the hash ring spreads them over all nodes.
- `lookup`: rendezvous several times slower per lookup than the others at 10 nodes, and growing linearly with nodes.

## Clean up

Nothing to clean up (the script writes no files; remove `__pycache__/` if your Python created one).

## Cost

€0.

## Test status

**runtime-tested** — 2026-11-19, Ubuntu Linux (kernel 7.0.0-43-generic, x86_64), Python 3.12.3 (host) and Python 3.14.10
(`python:3.14-slim` container). `python3 -m unittest -v test_shardsim`: **7 tests, OK** on both. Observed output of
`python3 shardsim.py all` (100,000 keys, 10 nodes; deterministic, so your numbers should match except `lookup`):

```text
# Experiment 1 - keys moved when growing 10 -> 11 nodes (ideal minimum 9.091%)
modulo           90.890%
ring(v=64)        9.134%
rendezvous        9.115%
jump              9.079%

# Experiment 2 - load balance across 10 nodes
scheme            max/mean  min/mean      CV
ring(v=1)            2.939     0.060   0.925
ring(v=8)            1.438     0.714   0.248
ring(v=64)           1.147     0.848   0.084
ring(v=256)          1.119     0.906   0.057
modulo               1.009     0.988   0.006
rendezvous           1.009     0.986   0.007
jump                 1.014     0.989   0.007

# Experiment 3 - hot keys: Zipf s=1.1, hottest key = 13.47% of requests (even node share 10.00%)
salt buckets   hot keys salted  max/mean  busiest node share
1                            0     1.925              19.25%
4                           10     1.565              15.65%
16                          10     1.189              11.89%
64                          10     1.246              12.46%

# Experiment 4 - increasing timestamp keys
range (fixed bounds)               100.00% busiest node share, 1 node receiving writes
hash ring                           11.20% busiest node share, 10 nodes receiving writes

# Experiment 5 - lookup cost (pure Python, relative only; this host)
modulo 1.13 us, ring(v=64) 1.50 us, rendezvous 12.14 us, jump 2.73 us per lookup
```

Note the 64-bucket row in experiment 3: once the hot keys are spread thin, the remaining imbalance comes from the ring's
placement variance at 64 virtual nodes, not from key frequency.

## Troubleshooting

- **`ModuleNotFoundError: test_shardsim`**: run from inside `labs/07-partitioning-sharding/`, and do not pass `-I` to
  `python3 -m unittest` (isolated mode drops the current directory from the import path).
- **Different numbers**: everything except `lookup` is deterministic (BLAKE2b hashing, fixed seeds). If results differ,
  check that you have not changed `--keys`, `--nodes` or `--vnodes`.
