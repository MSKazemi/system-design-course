# C02 — Exercises

Lesson: [course/04-case-studies/C02-news-feed.md](../course/04-case-studies/C02-news-feed.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Fan-out arithmetic

50 M DAU open the app 8 times a day. 6 M posts are created per day; the mean author has 300 followers, of whom 35 % are
active. Compute average and peak (3×) feed loads/s and fan-out inserts/s if you push only to active followers.

<details><summary>Answer</summary>

Feed loads = 400 M/day → ≈ 4,630 /s average, ≈ 13,900 /s peak. Inserts = 6 M × 300 × 0.35 = 630 M/day → ≈ 7,300 /s
average, ≈ 21,900 /s peak. Note that inserts/s exceed feed loads/s: push trades write amplification for cheap reads.
Pushing to *all* followers would be 1.8 B/day (≈ 62,500 /s peak) — skipping inactive followers removes 65 % of the work.
</details>

## 2. [Core] Why the celebrity breaks push

An account with 40 M followers (30 % active) posts during peak. Fan-out workers sustain 2 M inserts/s in total, and are
already 60 % busy with ordinary traffic. How long until the post reaches all active followers? What does that do to
everyone else's freshness?

<details><summary>Answer</summary>

Active followers = 12 M. Spare capacity = 40 % × 2 M = 0.8 M inserts/s → 12 M / 0.8 M = **15 s** if the celebrity gets
all the spare capacity, longer if fairly shared. Meanwhile ordinary posts queue behind it, so freshness p95 degrades
for everyone — the celebrity's cost is paid by other users. Pulling celebrity posts at read time removes this: one
append to the author index, read by followers on their next load.
</details>

## 3. [Deep] Placing the threshold

With threshold *T*, a feed load reads the timeline plus the author index of every followed account above *T*. Suppose:
at *T* = 1 M followers users follow on average 3 such accounts; at *T* = 100 k, 15; at *T* = 10 k, 60. Each author-index
read costs 1 ms of p99 budget if done in parallel batches of 20. Which *T* fits a 15 ms in-network budget, and what
does lowering *T* buy on the write side?

<details><summary>Answer</summary>

Batches of 20 in parallel: 3 or 15 lists fit in one batch (≈ 1 ms plus timeline read); 60 lists need 3 batches
(≈ 3 ms) plus higher tail risk from more fan-in. All fit 15 ms on paper, but more fan-in raises p99 (the slowest of 60
reads), so *T* = 100 k is a reasonable middle. Lowering *T* bounds the maximum fan-out per post (at *T* = 10 k, no post
causes more than 10 k inserts → ≈ 5 ms of a 2 M/s worker fleet) and removes freshness spikes. The point is that *T*
trades read fan-in against write fan-out and should be tuned from measured distributions, not guessed.
</details>

## 4. [Core] Timeline memory

Size the timeline cache for 120 M DAU with 800 entries each (16 B per entry), 1.5× overhead and 2 replicas. How many
nodes with 96 GB usable RAM? What if you keep timelines only for users active in the last 3 days (assume 70 % of DAU)?

<details><summary>Answer</summary>

Raw = 120 M × 800 × 16 B = 1.536 TB → × 1.5 × 2 ≈ 4.6 TB → ÷ 96 GB ≈ **48 nodes**. Keeping only 70 % of DAU → ≈ 3.2 TB →
≈ 34 nodes; the other users rebuild on their next load. Also acceptable: cap at 500 entries (the ranker rarely needs
more), which saves 37.5 %.
</details>

## 5. [Deep] Rebuild on miss

A user who follows 900 accounts returns after 6 weeks. Describe the rebuild, estimate its latency with batched parallel
reads (batches of 50, 3 ms each, 6 batches in flight at once), and say how you protect the system if a cache node with
5 M timelines is lost.

<details><summary>Answer</summary>

Fetch the following list (1 read), then recent posts for 900 authors from the author index: 18 batches of 50; with 6 in
flight that is 3 rounds × 3 ms ≈ **9 ms** plus merge and write-back — fine for one user. Losing a node means up to 5 M
rebuilds hitting the graph and author index at once: rate-limit rebuilds, serve those users a cheaper feed (recent
posts from their top followed authors) until rebuilt, and rebuild lazily on access rather than eagerly. Replicas reduce
how often this happens; the rate limit makes it survivable when it does.
</details>

## 6. [Interview] Pagination under change

Explain why offset pagination produces duplicates and gaps in a ranked feed, and design a cursor that avoids both. What
does the "new posts" pill do to the cursor?

<details><summary>Answer</summary>

Offsets index into a list that keeps changing: new posts shift everything down (duplicates on the next page), re-ranking
reorders items (gaps and repeats). The cursor should reference a **ranked snapshot ID** (the ordered candidate list
stored for a few minutes), a position in it, and a compact record of already-shown IDs (e.g. a Bloom filter or the
last N IDs) so a refreshed snapshot can skip them. The "new posts" pill starts a new snapshot from the top; the old
cursor is abandoned. Good answers also note that cursors must be opaque and signed so clients cannot forge positions.
</details>

## 7. [Deep] Ranking cost

At peak you serve 70,000 first-page loads/s. The light ranker keeps 500 of 1,500 candidates; the heavy ranker scores
those 500. If one accelerator scores 20,000 candidates/s at your latency target (assumption), how many accelerators do
you need for the heavy ranker at peak? What happens if you cache scores and 40 % of candidates were scored in the last
10 minutes for the same viewer?

<details><summary>Answer</summary>

70,000 × 500 = 35 M scores/s → ÷ 20,000 = **1,750 accelerators** (plus headroom, say 2,100 at 80 % target utilization).
With 40 % reuse: 21 M scores/s → 1,050 (≈ 1,300 with headroom). Score caching is valid only if the score does not depend
on other candidates in the batch — the "candidate isolation" property described in the X repository. Also acceptable:
shrinking the heavy-ranker set from 500 to 300 (−40 %) if offline evaluation shows little quality loss.
</details>

## 8. [Core] Visibility at read time

Why should blocks and deletes be enforced by a read-time filter instead of deleting entries from followers'
timelines? Give two reasons and one cost.

<details><summary>Answer</summary>

Reasons: (1) **immediacy** — a block is effective on the next load without waiting for any fan-out to run; (2)
**idempotency and simplicity** — fan-out only ever appends IDs; a delete needs no fan-out to millions of timelines.
Cost: every feed load runs the filter, so block/mute lists must be fast to read (in memory, replicated) and the filter
must be correct under partial data — for safety labels, fail closed (hide when unsure).
</details>

## 9. [Lab] Idempotent fan-out

In [labs/08-async-event-driven](../labs/08-async-event-driven/), treat each message as a `PostCreated` event and the
consumer as a fan-out worker. Kill the consumer mid-batch and restart it. Without the idempotent-consumer option, count
duplicate side effects; with it, confirm none. Map what you observed to timeline inserts.

<details><summary>Answer</summary>

Expect duplicates without idempotency because the broker redelivers unacknowledged messages (at-least-once delivery);
record the counts you actually observe. With an idempotency key (here, `post_id` + follower), redelivery becomes a
no-op. For timelines, the equivalent is inserting into a set-like structure or de-duplicating by `post_id` on read —
either way the fan-out worker can safely retry.
</details>

## 10. [Interview] Should we stop materializing timelines?

Your product's feed is now 70 % recommended posts and 30 % from followed accounts. A colleague proposes removing
per-user timelines and pulling in-network posts from an in-memory recent-posts-by-author index at read time. Argue both
sides and decide.

<details><summary>Answer</summary>

For: timelines cost TBs of RAM and billions of inserts per day to supply only 30 % of candidates; an author-indexed
recent-posts store is much smaller (one copy per post, not one per follower) and removes fan-out lag entirely; X's 2026
open-source feed uses this shape (Thunder). Against: read fan-in grows with follows (merge hundreds of author lists per
load), and the "Following" chronological mode — required in the EU as a non-profiling option for very large platforms —
needs fast in-network reads. Decision: likely move to pull with a well-partitioned in-memory author index and keep
materialized timelines only for heavy users who follow thousands of accounts, after measuring p99 fan-in latency.
</details>
