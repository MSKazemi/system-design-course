# 09 — Coordination & consensus (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/01-foundations/09-coordination-consensus.md](../course/01-foundations/09-coordination-consensus.md).

## Slide 1 — The requirement

- Lumen: exactly one active job scheduler and one ledger writer, three replicas across three zones
- Fail over in under 5 s; never two writers at once; never lose an acknowledged config change
- Hard because nodes can't tell dead from slow, clocks disagree, and processes pause

**Visual:** three zones, a scheduler replica in each, one highlighted as "active"; a question mark over the others.
Icons: `arch-region`, `arch-server`, `pattern-leader-election`.

**Speaker notes:** Coordination is about agreement: who leads, what the config is, what came first. One machine makes it
trivial. Three machines and a network make it one of the hardest problems in the field.

## Slide 2 — Which coordination problem do you have?

- Exactly one active instance → leader election (lease in a consensus store)
- Mutual exclusion → lock **plus fencing token**
- Agreed config → linearizable KV with watches
- Ordering, unique IDs and liveness → usually solvable *without* consensus

**Visual:** two-column table, "needs consensus" vs "avoid consensus". Icons: `pattern-consensus`, `pattern-idempotency`.

**Speaker notes:** Only the first three need consensus. Avoiding consensus where possible is a design skill, because
consensus costs latency and availability.

## Slide 3 — System models and FLP

- Asynchronous, synchronous, partially synchronous; crash-stop, crash-recovery, Byzantine
- Safety (nothing bad) vs liveness (something good eventually)
- FLP (1985): no deterministic protocol is guaranteed to terminate in a fully asynchronous system with even one crash
- Escape: always safe, live once the network behaves (partial synchrony)

**Visual:** triangle "safety / liveness / full asynchrony: pick two"; FLP citation on screen.

**Speaker notes:** FLP doesn't say consensus doesn't work. It says we can't guarantee termination under arbitrary
delays. Raft keeps safety unconditionally and gets liveness when timing cooperates.

## Slide 4 — Quorums: why majorities and odd numbers

- Any two majorities overlap; that is how a new leader learns old decisions
- *n* = 2*f* + 1 tolerates *f* failures: 3 → 1, 5 → 2, 7 → 3
- 4 members tolerate 1 failure, same as 3, and are slower
- etcd FAQ: no more than seven members; Kubernetes recommends five in production

**Visual:** two overlapping circles of three out of five nodes; table of cluster size vs failures tolerated.
Icons: `nosql-etcd`, `pattern-replication`.

**Speaker notes:** The overlap argument is the single most important idea in this chapter. Everything else is
mechanism to exploit it safely.

## Slide 5 — Paxos in two phases

- Prepare(n) → acceptors promise to ignore lower numbers and report accepted values
- Accept(n, v): v must be the highest previously accepted value, if any
- A value is chosen when a majority accepts it
- Multi-Paxos: stable leader, skip phase 1 for consecutive slots

**Visual:** sequence diagram, proposer and three acceptors, one reporting an earlier value "X".

**Speaker notes:** The "carry forward the highest accepted value" rule is what makes Paxos safe. Duelling proposers
can live-lock; electing a distinguished proposer fixes progress.

## Slide 6 — Raft: terms and elections

- Follower → candidate → leader; terms are a logical clock
- Randomized election timeouts (paper: 150–300 ms) avoid split votes
- Vote only for candidates whose log is at least as up to date (last term, then length)
- etcd defaults: 100 ms heartbeat, 1000 ms election timeout

**Visual:** state diagram (follower/candidate/leader) with timeouts; timeline of term numbers.
Icons: `pattern-leader-election`, `ops-clock`.

**Speaker notes:** In the Raft paper, no randomization meant elections over 10 s because of split votes. Just 5 ms of
randomness brought median downtime to 287 ms.

## Slide 7 — Raft: replication and the commit rule

- AppendEntries carries (prevLogIndex, prevLogTerm); mismatch → leader backs up
- Committed = current-term entry on a majority; older entries commit indirectly
- "On a majority" ≠ "committed" for old-term entries (paper Figure 8)
- Five safety properties: election safety, append-only, log matching, leader completeness, state machine safety

**Visual:** five log rows S1–S5 with colored-and-labeled terms; one old-term entry on a majority marked "not yet
committed".

**Speaker notes:** This is the interview favorite. Walk the Figure 8 trace: an old-term entry on a majority can still
be overwritten unless a current-term entry commits after it.

## Slide 8 — Membership changes and disruptive servers

- Never switch all servers at once: two majorities could form
- Joint consensus (C_old,new) or one server at a time
- Remove the dead member before adding a replacement
- Pre-Vote stops a rejoining node from inflating terms (default on in current etcd)

**Visual:** before/after cluster diagrams with the overlapping majority highlighted.

**Speaker notes:** Most real outages in coordination clusters are operational, not algorithmic. Membership changes
during degradation are a classic way to lose quorum.

## Slide 9 — Leases and fencing tokens

- Leader election = create-if-absent key bound to a lease; others watch
- A paused holder doesn't know its lease expired (GC pause, VM stall)
- Fencing token: monotonic number per grant; **the resource** rejects lower tokens
- etcd: use the lock key's revision (Jepsen 2020); Chubby called it a sequencer

**Visual:** sequence diagram, A token 33 pauses, B token 34 writes, A's write rejected.
Icons: `security-lock`, `security-token`, `arch-database`.

**Speaker notes:** Checking the TTL before writing does not help, because the pause can come after the check. If the
resource cannot check tokens, make the operation idempotent instead.

## Slide 10 — Clocks: pick the weakest one that works

- Wall clock (NTP): a few hundred µs on a fast LAN; can step; never for cross-node ordering
- Lamport: a → b ⇒ C(a) < C(b), not the converse
- Vector: detects concurrency (Dynamo); grows with writers
- HLC: causality plus near-wall-time in 64 bits (CockroachDB)
- TrueTime: interval [earliest, latest]; commit wait ≈ 2ε (ε̄ ≈ 4 ms in the 2012 paper)

**Visual:** decision flowchart "what must you order?" → five clock types. Icons: `ops-clock`.

**Speaker notes:** Every step up this ladder costs something: size for vector clocks, latency for TrueTime. Choose by
the ordering guarantee you actually need.

## Slide 11 — Unique IDs without coordination

- UUIDv7 (RFC 9562, 2024): 48-bit ms timestamp + 74 random bits, index friendly
- ULID: 48-bit time + 80 random bits, 26 base32 chars
- Snowflake: 41-bit ms | 10-bit worker | 12-bit sequence = 4,096 IDs/ms/worker, about 69 years
- Worker IDs need a lease; clocks going backwards must stop generation

**Visual:** three bit-layout bars side by side with field widths labeled.

**Speaker notes:** Ask the clarifying questions first: 64 or 128 bits, sortable, guessable, IDs per second. PostgreSQL
18 now ships `uuidv7()` built in.

## Slide 12 — Gossip and failure detection

- All-to-all heartbeats: O(n²) messages
- SWIM: ping one random peer, `ping-req` via k others, suspect before declaring dead, piggyback updates
- Phi accrual: φ = −log₁₀ P_later; Cassandra convicts at φ = 8 by default
- Detectors decide routing; consensus plus fencing decides safety

**Visual:** ring of nodes; one ping fails, two indirect probes; a "suspected" badge.
Icons: `pattern-health-check`, `arch-servers-cluster`.

**Speaker notes:** A failure detector can only ever say "suspected". That is FLP in operational form.

## Slide 13 — Operating it

- Election storms: watch `etcd_server_leader_changes_seen_total`; fix disk latency (WAL fsync p99 < 10 ms)
- Quorum loss: `etcd_server_has_leader` = 0; spread members over failure domains
- Back up and rehearse restore; test leader kills and client pauses
- Cross-region quorums cost every write a cross-region round trip

**Visual:** small dashboard mock with three panels (leader changes, fsync p99, has_leader).
Icons: `ops-metrics`, `ops-alert`, `ops-latency`.

**Speaker notes:** Most etcd instability is a slow disk. Coordination clusters are cheap to run and expensive to lose.

## Slide 14 — Interview angle

- CLARIFY: correctness or efficiency lock? can the resource check tokens? failover target?
- QUANTIFY: 2f + 1 members; RTT + fsync = write latency; TTL + election = failover
- SKETCH → DEEPEN → STRESS: etcd across zones, leases + watches, fencing; partitioned leader, paused client
- WRAP: safe under any timing, live with a connected majority
- Red flags: SETNX + TTL as "a lock", two-node HA, comparing server timestamps

**Visual:** the six-step framework strip with this chapter's keywords under each step.

**Speaker notes:** The strongest signal in these interviews is naming the paused-client problem and the fencing token
without being prompted.
