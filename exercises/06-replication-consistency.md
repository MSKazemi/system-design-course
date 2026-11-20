# 06 — Exercises

Lesson: [course/01-foundations/06-replication-consistency.md](../course/01-foundations/06-replication-consistency.md) ·
Lab: [labs/06-replication-consistency](../labs/06-replication-consistency/README.md) · Bracketed numbers refer to the
lesson's References.

## 1. [Core] RPO and RTO from settings

A PostgreSQL leader in AZ-a has one asynchronous replica in AZ-b. AZ-a is lost. What is the RPO? What changes with
`synchronous_standby_names = 'replica_b'` and `synchronous_commit = on`, and what new failure appears?

<details><summary>Answer</summary>

**Async:** RPO = whatever the replica had not yet received when AZ-a died: usually milliseconds to seconds of
acknowledged commits, unbounded under load or after a network problem. Those commits are lost (or must be recovered
from AZ-a's disks later, then reconciled).

**Sync (`on`):** a commit returns only after the standby has flushed the WAL, so RPO = 0 for an AZ-a loss. New failure:
if replica_b (or the link to it) fails, **every commit waits** until it returns or the configuration changes: you
traded data loss for unavailability. Fix: two standbys in two AZs with `ANY 1 (b, c)` so one standby can fail without
blocking writes, and an HA manager that reconfigures safely. Lab L06's `sync` experiment shows the blocked commit.
</details>

## 2. [Core] Read-your-writes with tokens

Design the read-your-writes mechanism for Lumen chat using PostgreSQL functions. Specify what the API returns on write,
what the client stores, and how a read chooses a replica.

<details><summary>Answer</summary>

On write: after `COMMIT`, run `SELECT pg_current_wal_lsn()` (or `pg_current_wal_insert_lsn()`) and return it to the
client as an opaque token, e.g. in a response header or session cookie (`min_lsn=0/3000148`).
Client: stores the highest token it has seen for the session (tokens only move forward).
On read: the router keeps a recent `pg_last_wal_replay_lsn()` per replica (polled every ~100 ms). It sends the read to
any replica with `replay_lsn ≥ min_lsn`; if none qualifies, it waits briefly (bounded, e.g. 50 ms) or reads from the
leader. This gives read-your-writes and, because the token never decreases, monotonic reads. It degrades gracefully: high
lag shifts reads to the leader instead of returning stale data. Alternative accepted: `synchronous_commit = remote_apply`
on the replicas you read from, at the cost of commit latency.
</details>

## 3. [Core] Quorum arithmetic

N = 5. List all (R, W) with R + W > N and R, W ≥ 1. Which do you choose for (a) a write-heavy event store; (b) a
read-heavy profile store; (c) maximum tolerance of failed nodes for both reads and writes? How many node failures does
each tolerate?

<details><summary>Answer</summary>

Pairs: (1,5), (2,4), (3,3), (4,2), (5,1).
(a) Write-heavy: **W = 2, R = 4** (writes wait for 2 acks; tolerate 3 failed nodes for writes, 1 for reads).
(b) Read-heavy: **R = 2, W = 4** (mirror image).
(c) Balanced tolerance: **R = W = 3**, tolerating 2 failed nodes for both.
(1,5)/(5,1) make one operation unavailable on any single failure. Remember: even with overlap, this is not
linearizable (sloppy quorums, concurrent reads during writes, partial failed writes [3][6]).
</details>

## 4. [Deep] Why R + W > N is not linearizable

Construct a concrete sequence with N = 3, R = W = 2 in which a client reads a new value and a later client reads the
old value.

<details><summary>Answer</summary>

Initial value v0 on A, B, C. Writer W1 starts writing v1; it reaches A only so far (B and C pending).
Reader X reads from A and B: sees v1 (A) and v0 (B), returns the newest, **v1**, at time t1.
Reader Y starts after X finished (t2 > t1), reads from B and C: both still v0, returns **v0**.
Real-time order says Y started after X saw v1, so a linearizable system must return v1 to Y: violation. Fixes:
the reader performs a write-back (read repair synchronously to a quorum before returning, as in the ABD algorithm) or
the system uses consensus. Sloppy quorums (writes landing on non-home nodes) break even the overlap argument.
</details>

## 5. [Core] CAP, carefully

Your colleague says: "Our three-node etcd cluster is CP, so it's not highly available." Correct the statement, using
Gilbert and Lynch's definitions.

<details><summary>Answer</summary>

Gilbert and Lynch's availability means *every request to a non-failing node gets a response*, even a node isolated in a
minority partition [5]. etcd (Raft) refuses writes (and linearizable reads) on the minority side, so it is not
"available" in CAP's strict sense: that is the "CP" label. But "highly available" in the SLO sense means the service
keeps answering for most clients: with 3 nodes, etcd tolerates 1 failed or isolated node and keeps serving through the
majority. So: it gives up CAP-availability in the minority, and it is highly available for majority-side clients.
Better vocabulary: "linearizable; available while a majority can communicate" [9].
</details>

## 6. [Core] PACELC classification

Classify, with reasons: (a) PostgreSQL leader + async replicas, reads from replicas; (b) the same, reads from the
leader only, with a synchronous standby; (c) Cassandra at `ONE`/`ONE`; (d) Spanner.

<details><summary>Answer</summary>

(a) **EL** in normal operation (replica reads trade freshness for latency/scale); during a partition that isolates the
leader, writes stop until failover → **PC** for writes, while replicas keep answering stale reads (PA for reads).
Systems are often different per operation, which is exactly why labels mislead [9].
(b) **PC/EC**: writes wait for the standby (latency for consistency); a partition that isolates the standby blocks
writes.
(c) **PA/EL**, matching Abadi's classification of default Dynamo-style systems [6].
(d) **PC/EC**: Paxos majorities and commit wait pay latency for external consistency; the minority side of a partition
cannot commit.
</details>

## 7. [Deep] G-Counter and PN-Counter

Three replicas hold PN-Counter states P = {a:4, b:2, c:0}, N = {a:1, b:0, c:3} and P = {a:3, b:5, c:1},
N = {a:1, b:2, c:3}. Merge them and give the value. Why can't you implement "never below zero" with this CRDT?

<details><summary>Answer</summary>

Merge is element-wise max on both vectors: P = {a:4, b:5, c:1}, N = {a:1, b:2, c:3}. Value = (4+5+1) − (1+2+3) = 10 − 6
= **4**.
"Never below zero" requires knowing the global value before allowing a decrement. Two replicas that each see value 1
can each accept a decrement concurrently (each locally valid), and after merging the value is −1. Preventing it needs
coordination: route decrements through one owner, use consensus, or use escrow (pre-assign each replica a share of the
available amount it may spend locally).
</details>

## 8. [Deep] Design the failover

Lumen's RTO is 30 s and RPO 0. Describe detection, election, fencing and client redirection, and give the timeout
values you would start with and why.

<details><summary>Answer</summary>

- **Detection:** HA agent on each node (e.g. Patroni) renews a leader key with a TTL in etcd (e.g. TTL 15–30 s, renew
  every ~10 s). A missed renewal, not a single failed ping, means "leader lost".
- **Election:** candidates compete for the leader key via a compare-and-set in etcd (a linearizable decision); only a
  synchronous standby that has all acknowledged WAL is eligible (RPO 0).
- **Fencing:** the old leader must stop accepting writes *before* the new one starts: it demotes itself when it cannot
  renew its key (it knows its lease expired), and the platform can STONITH it or cut its network/storage access;
  storage-level fencing tokens (term numbers) are the strongest form.
- **Redirection:** clients connect through a proxy or DNS/service name that follows the leader key (e.g. HAProxy with
  health checks against the HA agent's REST endpoint).
Timeouts: TTL ~30 s minus margin keeps total RTO (detect + elect + promote + redirect) within 30 s; shorter TTLs risk
false failovers on GC pauses or brief network blips, and each false failover is itself an outage. Validate with game
days and measure.
</details>

## 9. [Interview] "Explain eventual consistency to the PM"

The PM asks why a user's new message sometimes disappears on refresh. Explain in three sentences and propose the fix.

<details><summary>Answer</summary>

To handle load we keep copies of the database, and the copies receive new messages a fraction of a second after the
main one; your refresh happened to read a copy that had not received the message yet. That is "eventual consistency":
every copy gets it, just not at the same instant. The fix is to make each user's own reads go to a copy that is known to
have their latest message (we pass a small "you have written up to here" marker with each request), which costs almost
nothing and removes the problem for the person who wrote.
</details>

## 10. [Lab] Read the lab's split brain

After running `./experiments.sh failover` and `./experiments.sh splitbrain`, both nodes report ids for new rows.
Explain why the ids can collide, what you would have to do to merge the two histories, and which single mechanism would
have prevented the situation.

<details><summary>Answer</summary>

Each node has its own `bigserial` sequence and advances it independently. In the recorded run the promoted replica
continued from 34 (PostgreSQL WAL-logs sequence values in batches of 32, so a standby's copy of the sequence is ahead of
the values actually used) while the old primary continued from 4: no collision yet, but the old primary reaches 34
after about 30 more inserts, and from then on both nodes can issue the **same id** for different rows. Merging requires a conflict-resolution pass: extract
the old primary's divergent writes (since the promotion point, e.g. with logical decoding or by comparing tables),
re-insert them on the new primary with new ids, fix references, and only then rebuild the old primary as a replica
(`pg_rewind` or fresh `pg_basebackup`). **Fencing** the old primary before promotion (STONITH, revoked network, or a
leader lease it cannot renew) would have prevented it; a consensus-based HA manager provides that decision safely.
</details>
