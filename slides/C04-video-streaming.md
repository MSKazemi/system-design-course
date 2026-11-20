# C04 — Video upload, transcoding & streaming (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/04-case-studies/C04-video-streaming.md](../course/04-case-studies/C04-video-streaming.md)

## Slide 1 — The requirement

- 1 M uploads/day; playable within minutes
- 100 M hours watched per day
- Start-up < 2 s, rebuffering rare
- Delivery cost is the number finance watches

**Visual:** Three panels: upload arrow, factory (encoding), firehose (delivery).
Icons: `domain-upload`, `domain-video`, `arch-cdn`, `ops-cost`.

**Speaker notes:** Three very different halves: bursty ingest, heavy batch compute, and a terabit read path. Spending
more on the middle makes the last one affordable.

## Slide 2 — The numbers

- Ingest ≈ 600 TB/day, ≈ 110 Gbit/s peak
- Software H.264 ladder ≈ 67,000 cores busy
- Delivery ≈ 135 PB/day, ≈ 45 Tbit/s peak
- 10 % fewer bits ≈ 4.5 Tbit/s saved at peak

**Visual:** Bar chart with delivery towering over ingest and storage.
Icons: `ops-throughput`, `arch-cpu`, `arch-object-storage`.

**Speaker notes:** All labelled assumptions. The asymmetry — encode once, deliver millions of times — drives every
decision.

## Slide 3 — Sketch

- Upload service → object storage (bytes never touch API servers)
- Upload-complete event → workflow orchestrator → encode queues → encoder fleet
- Renditions → origin shield → CDN / ISP caches → player
- Playback API picks codecs and signs URLs

**Visual:** The lesson's 13-node flowchart.
Icons: `arch-object-storage`, `arch-worker`, `arch-queue`, `arch-cdn`, `pattern-api`.

**Speaker notes:** The playback API is small but decides how much each view costs.

## Slide 4 — Uploads that survive the subway

- Multipart: parts 1–10,000, retried independently; recommended ≥ 100 MB
- Resumable protocol: tus 1.0.0 (HEAD → offset, PATCH from offset)
- IETF Resumable Uploads draft-15 (Nov 2026)
- Lifecycle rule aborts orphan uploads; checksums; conditional complete

**Visual:** A file split into parts; one part fails and is resent alone.
Icons: `domain-upload`, `storage-aws-s3`, `pattern-retry`.

**Speaker notes:** Orphaned parts are billed until aborted — the lifecycle rule is part of the design, not ops trivia.

## Slide 5 — The transcoding DAG

- Probe → split at keyframes → parallel chunk encodes
- Fast lane (360p/720p) → playable in minutes
- Full ladder + VMAF QC → complete
- Captions in parallel; AV1 later for popular videos

**Visual:** The lesson's DAG diagram.
Icons: `arch-data-pipeline`, `pattern-fan-out`, `pattern-fan-in`.

**Speaker notes:** Chunking turns "time to encode the video" into "time to encode a chunk".

## Slide 6 — Durable, idempotent steps

- Task key `(video_id, codec, height, chunk)`
- Deterministic output object keys → retries are harmless
- Orchestrator persists step state; crashed workers' tasks re-run
- Poison sources → quarantine after N attempts

**Visual:** A worker crashes mid-task; the orchestrator reassigns; output object key is unchanged.
Icons: `pattern-idempotency`, `pattern-saga`, `arch-worker`.

**Speaker notes:** Same idempotency principle as payments and chat, applied to batch work.

## Slide 7 — Hardware encoders

- Google VCU: 20–33× efficiency over a tuned non-accelerated baseline (ASPLOS 2021)
- Meta MSVP (2023): ≈ 10 W module; ≈ 9× H.264, ≈ 50× VP9 throughput vs software presets
- First-gen MSVP did not encode AV1
- Keep a software path for new codecs

**Visual:** A rack of CPUs collapsing into a few accelerator cards.
Icons: `arch-cpu`, `company-google`, `company-meta`.

**Speaker notes:** Hardware buys efficiency at the price of lead time and codec lag.

## Slide 8 — Per-title and per-shot encoding

- Fixed ladder: one size fits nobody
- Netflix per-title: top 1080p rung 5,800 → 4,640 kbps (20 %) for one title
- Dynamic Optimizer (per-shot): ≈ 28–38 % over fixed-QP/CRF across codecs
- Needs trial encodes + a perceptual metric (VMAF)

**Visual:** Two rate–quality curves (cartoon vs action) with different ladder points.
Icons: `company-netflix`, `domain-video`, `ops-metrics`.

**Speaker notes:** More encode compute per title — worth it for content watched a lot, not for the long tail.

## Slide 9 — Popularity-tiered encoding

- Every upload: standard H.264 ladder
- Crosses a view threshold: per-shot AV1
- Break-even = extra encode cost ÷ (bytes saved × price × capable share)
- Example in exercises: ≈ 2,700 views under stated assumptions

**Visual:** View-count axis with a threshold line; AV1 badge appears past it.
Icons: `ops-cost`, `domain-video`.

**Speaker notes:** Every number in the break-even is an assumption; the formula is the deliverable.

## Slide 10 — Adaptive streaming and caches

- HLS (RFC 8216): master + media playlists, target duration
- Player switches rungs per segment (ABR)
- Edge → shield → origin; immutable segments cache forever
- Open Connect: appliances embedded in 1,000+ ISP partners

**Visual:** Player switching between rungs as bandwidth drops; cache tiers below.
Icons: `arch-cdn`, `company-netflix`, `arch-client`.

**Speaker notes:** 3.75 M segment requests/s at peak must almost all be cache hits.

## Slide 11 — Failures and QoE

- Spot preemption → durable workflow re-runs tasks
- Premiere → pre-position + coalescing at shield
- CDN degraded → multi-CDN steering from the playback API
- Measure QoE on the client: start-up, rebuffer ratio, by ISP/region

**Visual:** Client telemetry dashboard: start-up p95, rebuffer %.
Icons: `ops-dashboard`, `ops-slo`, `pattern-failover`.

**Speaker notes:** Server logs cannot see a stalled player.

## Slide 12 — Modern twist

- Netflix (Dec 2025): AV1 ≈ 30 % of viewing; one-third less bandwidth than AVC/HEVC; 45 % fewer buffering interruptions
- Film grain synthesis: send a grain model, not grain
- AV2 spec announced June 2026 — decoders lag; pilot, don't ship
- AI captions (Whisper: 680,000 h training data); EAA applies from 28 June 2025

**Visual:** Codec timeline H.264 → AV1 → AV2 with a "device support" band lagging behind.
Icons: `domain-video`, `domain-ai`, `company-netflix`.

**Speaker notes:** Design a codec portfolio chosen per device, and treat captions as a rendition with its own SLO.

## Slide 13 — WRAP

- Junior: object storage, queue, resolutions, CDN, HLS/DASH
- Senior: resumable multipart, chunked idempotent DAG, ladder + ABR, hit ratio, client QoE
- Staff: delivery economics, per-title + popularity tiering, codec portfolio, hardware trade-off, retention, accessibility
- Red flags: uploads through API servers, one giant encode job, server-only QoE

**Visual:** Staircase junior / senior / staff.
Icons: `ops-check`.

**Speaker notes:** Close with cost per hour watched and what moves it.
