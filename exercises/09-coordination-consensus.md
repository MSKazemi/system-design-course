# 09 — Exercises

Exercises for [SYSDESIGN-09 Coordination & consensus](../course/01-foundations/09-coordination-consensus.md).
Numbers in brackets refer to that lesson's reference list.

---

### 1. [Core] Sizing a consensus group

Lumen wants its coordination cluster to survive (a) the loss of any one availability zone, and separately (b) the loss
of any one zone *while* another member elsewhere is down for an upgrade. The region has three zones. How many members
do you need for (a) and (b), and how do you place them?

<details><summary>Answer</summary>

A majority quorum with *n* = 2*f* + 1 members tolerates *f* failures [8].

- **(a)** Three members, one per zone. Losing a zone removes one member; 2 of 3 is still a majority.
- **(b)** Count the worst case: the largest zone fails *and* one more member is down. With three zones, any placement
  of *n* members puts at least ⌈*n*/3⌉ in some zone.
  - *n* = 5, placed 2-2-1: losing a two-member zone plus one more member leaves 2 of 5. That is not a majority (3), so
    it fails.
  - *n* = 7, placed 3-2-2: losing the three-member zone plus one more leaves 3 of 7. That is not a majority (4), so it
    fails.
  - *n* = 9, placed 3-3-3: losing a zone plus one more leaves 5 of 9. That is a majority (5), so it survives.

  So the strict requirement (b) needs nine members in three zones. That is above the etcd FAQ's suggested maximum of
  seven, and writes slow down as members are added [8]. The pragmatic answer is five members 2-2-1: they survive any
  zone loss (3 of 5 left) *or* any two member failures. Then schedule upgrades so a member is never down during
  elevated zone risk. More failure domains change the arithmetic. With four zones, seven members placed 2-2-2-1 survive
a zone loss plus one more failure (4 of 7 left).

The general lesson: count the members a single correlated failure removes, add the independent failures you want to
tolerate, and check that the remainder is still a majority.
</details>

---

### 2. [Core] Even-sized clusters

A teammate proposes four etcd members "for extra safety". Explain why this is worse than three, using numbers.

<details><summary>Answer</summary>

Four members need a majority of 3 and therefore tolerate only 1 failure, the same as three members [8]. But there are
four machines that can fail instead of three, so the probability that *two* fail together is higher. Every write must
also reach one more replica before it commits (3 acks instead of 2), which adds latency. A four-member cluster split
2 | 2 by a partition has no majority on either side. A three-member cluster split by a partition always has a
majority on one side. So four members cost more, are no more fault tolerant, and can be less available.
</details>

---

### 3. [Core] Partitioned leader

A five-member Raft cluster (S1–S5) has leader S1 in term 7. A partition separates {S1, S2} from {S3, S4, S5}. Describe
what happens on both sides for the next few seconds, and what a client writing to S1 experiences.

<details><summary>Answer</summary>

- **Majority side {S3, S4, S5}.** They stop receiving heartbeats. After an election timeout, one of them (say S4)
  becomes a candidate for term 8. It wins votes from S3 and S5 if its log is at least as up to date, which it is if it
  has every committed entry, and it becomes leader. Writes to S4 commit with acks from 2 of the 3 reachable members
  plus itself (3 of 5).
- **Minority side {S1, S2}.** S1 still thinks it is the term-7 leader. It can append client commands to its log but can
  never get 3 acks, so **nothing commits** and no client receives success. With the "step down when quorum is lost"
  check, S1 steps down after a timeout [6]. S2 may time out and start elections, but it can never win with only 2 votes.
- **Client writing to S1.** Its request hangs and then times out or fails. It must retry against another member,
  ideally with an idempotency key so that a retried command is not applied twice.
- **On heal.** S1 and S2 see term 8, revert to followers, and any uncommitted term-7 entries on S1 are overwritten by
  the term-8 leader's log. Safety holds because those entries were never acknowledged.
</details>

---

### 4. [Deep] Why the commit rule mentions the current term

Explain, with a concrete five-server trace, why a Raft leader may not declare an entry from a *previous* term
committed just because it is stored on a majority.

<details><summary>Answer</summary>

This is the Raft paper's Figure 8 situation [4]:

1. Term 2: leader S1 writes entry *e* at index 2 and replicates it only to S2, then crashes.
2. Term 3: S5 is elected with votes from S3, S4 and itself. Their last entries are from term 1, so S5's log is
   up to date enough. S5 appends a different entry *f* at index 2, then crashes.
3. Term 4: S1 is elected and replicates *e* to S3. Now *e* is on S1, S2 and S3, a majority.
4. If S1 counted that as committed, answered the client, then crashed: S5 could win term 5. Its last entry is from
   term 3, which is newer than *e*'s term 2, so S2, S3 and S4 would vote for it. S5 would then overwrite *e* with *f* on
   every server. An acknowledged write would be lost.

Raft's rule prevents this: S1 only commits once an entry **from term 4** is on a majority. *e* then becomes committed
indirectly via Log Matching, and S5, lacking a term-4 entry, can no longer win [4].
</details>

---

### 5. [Core] Locks without fencing

Lumen's re-indexing job takes a lock in a key-value store with a 10 s TTL. Before each write to the search index it
checks that at least 2 s of TTL remain. Construct a schedule that corrupts the index anyway, and fix the design.

<details><summary>Answer</summary>

Schedule: at t = 0, worker A acquires the lock (expires at t = 10). At t = 7 A checks: 3 s remain, so it proceeds. A
then hits a 6 s stop-the-world GC pause, or its VM is descheduled. At t = 10 the lease expires, and at t = 10.2
worker B acquires the lock and begins writing. At t = 13 A resumes and performs the write it already decided to do.
Now A and B both write the same tenant's index. The pre-write check cannot help because the pause happened
*after* the check [16].

Fix: the lock service issues a monotonically increasing **fencing token** on each grant, for example the etcd revision
of the lock key [17]. The search index, or a thin service in front of it, stores the highest token seen per tenant and
rejects writes with a lower token. A's write carries token 33, B's carries 34, so A is rejected [16]. If the index
cannot check tokens, make the operation idempotent and convergent instead. For example, a write derived
deterministically from a versioned snapshot is safe to apply twice.
</details>

---

### 6. [Core] Which clock?

For each requirement, pick the cheapest clock or ordering mechanism and justify it:
(a) display "last edited 3 minutes ago" in the UI; (b) detect that two offline edits to the same document conflict;
(c) order events emitted by 40 microservices so that every effect appears after its cause, with timestamps close to
wall time for debugging; (d) a globally distributed database must guarantee that if transaction T1 commits before T2
starts (in real time), T1's timestamp is smaller.

<details><summary>Answer</summary>

- **(a)** Wall clock (NTP-disciplined). Human-scale precision; a few ms of skew are irrelevant [24].
- **(b)** Vector clocks, or version vectors per replica. Only they can tell "concurrent" apart from "ordered"; Dynamo
  used them for exactly this [20]. Lamport clocks would impose an arbitrary order and hide the conflict.
- **(c)** Hybrid logical clocks. They preserve happened-before like Lamport clocks, stay within the clock-sync error of
  physical time, and fit in 64 bits [21]. Propagate the HLC in request headers.
- **(d)** External consistency needs bounded clock uncertainty plus commit wait, TrueTime-style: pick *s* ≥
  `TT.now().latest` and wait until `TT.after(s)` before releasing the commit [23]. Expect commit latency of at least
  about 2ε. An alternative is to route all such transactions through a single timestamp oracle, which trades a
  network hop for clock hardware.
</details>

---

### 7. [Core] Lamport clock mechanics

Processes P and Q start with clocks 0. P does a local event *a*, then sends message *m* to Q. Q, before receiving *m*,
has done three local events. Q then receives *m* (event *b*). What are C(*a*), the stamp on *m*, and C(*b*)? If Q's
clock had been 0 at receipt, what would C(*b*) be? What can and can't you infer from C(*x*) < C(*y*)?

<details><summary>Answer</summary>

Using "increment before each event, stamp messages with the send event's clock, on receive set C := max(C, stamp) + 1"
(a common rendering of Lamport's IR1/IR2 [18]):

- C(*a*) = 1. The send of *m* is event 2 on P, so *m* carries stamp 2.
- Q's three local events give it C = 3. On receipt, C(*b*) = max(3, 2) + 1 = 4.
- If Q's clock were 0, C(*b*) = max(0, 2) + 1 = 3, which is still greater than the send's 2, as the Clock Condition
  requires.

Inference: *x* → *y* implies C(*x*) < C(*y*), but C(*x*) < C(*y*) does **not** imply *x* → *y*; the events may be
concurrent. To decide causality you need vector clocks [19].
</details>

---

### 8. [Interview] Design a unique ID generator

"Design a service that generates 64-bit unique IDs for 50,000 writes per second across three regions. IDs should be
roughly time-sortable." Give the bit layout, how workers get identities, capacity, and two failure modes.

<details><summary>Answer</summary>

**CLARIFY.** 64-bit, roughly sortable, no central hot path, 50k/s now with 10× headroom.

**SKETCH.** A Snowflake-style layout [28]: 1 unused sign bit | 41-bit ms timestamp from a custom epoch | 10-bit worker
ID | 12-bit sequence. Generation happens *in-process* in each application server, a library rather than a network
service, so there is no extra hop.

**QUANTIFY.** Each worker can issue 4,096 IDs per ms, about 4.1 M/s, so 50k/s needs no more than one worker per region
for capacity. Run many for availability; 1,024 worker IDs are available. 41 bits of ms is about 69.7 years from the
chosen epoch. Optionally split the 10 bits into 3 region + 7 worker bits.

**Worker identity.** At startup each instance acquires a worker-ID lease in etcd: create `/idgen/worker/<n>` if
absent, bound to a lease that it keeps alive. On lease loss, it must stop issuing IDs until it re-acquires an ID.
Never configure worker IDs by hand.

**STRESS.**
1. *Clock moves backwards* (NTP step). Two IDs with the same timestamp and sequence would be possible. Snowflake
   refuses to generate until the clock passes the last timestamp [28]. Alert on it, and use a monotonic-adjusted clock.
2. *Worker-ID reuse* after a lease expiry while the old process is paused. That gives duplicates. Mitigate by checking
   lease validity with margin before each batch and by having the new holder wait one TTL before using the ID. The
   database's unique constraint is the backstop.
3. *Sequence exhaustion within a ms*: wait for the next millisecond.

**Alternative.** If 128 bits are acceptable, UUIDv7 needs no worker IDs at all, with 74 random bits per ms [26].
</details>

---

### 9. [Deep] Failure detectors

A GPU worker pool of 2,000 nodes uses all-to-all heartbeats every second. (a) Estimate the message rate. (b) Explain
how SWIM changes the cost and why it uses `ping-req`. (c) A phi accrual detector is configured with threshold φ = 8.
Interpret that number.

<details><summary>Answer</summary>

- **(a)** Each node sends to 1,999 others every second: 2,000 × 1,999 ≈ **4 million messages/s**. That grows as
  O(*n*²).
- **(b)** In SWIM each member pings *one* random member per protocol period. If no ack arrives, it asks *k* other
  members to probe the target (`ping-req`), and only then marks it *suspected*. Membership changes ride on these
  messages. Load per member is constant and expected detection time does not depend on group size [30]. The indirect
  probe distinguishes "target is down" from "my link to the target is bad", which reduces false positives.
- **(c)** φ = −log₁₀(P_later), so φ = 8 means the detector suspects the node once the probability that the heartbeat is
  merely late falls to about 10⁻⁸ [31]. Cassandra uses 8 as its default conviction threshold [32]. A lower threshold
  detects crashes faster but wrongly suspects more nodes.
</details>

---

### 10. [Lab] Reading the failover measurement

In lab L09 you kill the etcd leader and the script reports when the survivors elected a new leader and when the first
write succeeded. (a) List everything that contributes to the measured time besides the 1,000 ms election timeout.
Why can the measurement even come out *below* the timeout if you start the clock after the kill command returns?
(b) Why might the first successful write lag behind the new leader? (c) Predict what changes if you set
`--election-timeout=5000`, then test it.

<details><summary>Answer</summary>

- **(a)** Contributions: the time Docker takes to deliver SIGKILL; the follower's election timeout (1000 ms by
  default [7], randomized upward), counted from the *last heartbeat* it received; one RequestVote round trip; the
  script's 50 ms polling interval; and the status API call. If you start the clock *after* a slow kill command
  returns, part of the follower's timeout has already elapsed while the CLI was running, so the result can fall
  below 1,000 ms. The author's runs showed this (README test status). That is why the final script starts the clock
  before the kill and prints the kill time separately. Measuring failover honestly means stating where the clock
  starts.
- **(b)** The first write needs the new leader to commit an entry from its own term. The script also writes through
  one specific survivor, which must learn who the new leader is and forward the request. Client-side request timeouts
  (0.5 s in the script) add discretization: a write attempt that started before the election finished blocks until
  its timeout.
- **(c)** Detection and therefore unavailability grow roughly in proportion, to around 5 s or more. Spurious
  elections caused by slow disks or pauses become rarer. This is the core availability-versus-stability trade-off
  behind `broadcastTime ≪ electionTimeout ≪ MTBF` [4]. Record your own numbers; do not assume them.
</details>

---

### 11. [Interview] "Only one cron job must run"

You have three replicas of a billing reconciliation job that runs hourly. Exactly one must run each hour, and a
duplicate run double-charges customers. Give a design and say what you would tell an interviewer about its
guarantees.

<details><summary>Answer</summary>

1. **Leader election.** Each replica contends for `/billing/reconcile/leader` in etcd, bound to a lease (TTL ≈ 10 s),
   using a create-if-absent transaction. Non-leaders watch the key [6][11].
2. **Fencing.** The leader uses the revision of its leader key as a fencing token. The billing database stores
   `last_token` and every write does `... WHERE last_token <= :token`, so a deposed leader's writes fail [16][17].
3. **Idempotence per run.** Each run has a deterministic ID such as `reconcile-2026-11-19T14`. Charges are inserted
   with a unique constraint on (run_id, customer_id). Even a duplicate that slips past fencing cannot double-charge
   ([SYSDESIGN-08](../course/01-foundations/08-async-event-driven.md)).
4. **Guarantees to state.** Safety (no double charge) comes from fencing plus idempotence and does *not* depend on
   timing. Liveness (a run happens each hour) depends on etcd having a majority and a leader keeping its lease. A
   missed hour is detected by an alert on "no run record for hour H" and backfilled.

Red flag to avoid: claiming the lease alone guarantees a single run.
</details>
