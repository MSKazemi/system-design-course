# C04 — Exercises

Lesson: [course/04-case-studies/C04-video-streaming.md](../course/04-case-studies/C04-video-streaming.md).
All numbers are assumptions unless the lesson gives a source.

## 1. [Core] Ingest sizing

200,000 uploads/day, average 12 minutes, average source bitrate 8 Mbps, peak-to-average 2.5×. Compute daily ingest
volume and peak ingest bandwidth.

<details><summary>Answer</summary>

Per upload: 720 s × 8 Mbps ÷ 8 = 720 MB. Daily: 200,000 × 720 MB = 144 TB. Average bandwidth: 144 TB × 8 ÷ 86,400 ≈
13.3 Gbit/s; peak ≈ **33 Gbit/s**. Object storage handles this easily if uploads go directly to it in parallel parts;
an API tier proxying the bytes would need to be sized for 33 Gbit/s of pure copying.
</details>

## 2. [Core] Delivery sizing and what 10 % buys

50 M hours watched per day, average delivered bitrate 4 Mbps, peak concurrency 8 M streams. Compute daily bytes and
peak bandwidth. What does a 10 % average-bitrate reduction save at peak?

<details><summary>Answer</summary>

Daily: 50 M × 3,600 s × 4 Mbps ÷ 8 = 90 PB/day. Peak: 8 M × 4 Mbps = **32 Tbit/s**. A 10 % reduction saves 3.2 Tbit/s at
peak and 9 PB/day — far more value than most encode-side costs, which is why encoding efficiency is a business
priority.
</details>

## 3. [Core] Multipart part size

A creator uploads a 40 GB studio master. S3 multipart allows part numbers 1–10,000. What is the minimum part size
that fits? What part size would you choose for a flaky 20 Mbit/s uplink, and why?

<details><summary>Answer</summary>

Minimum: 40 GB ÷ 10,000 = 4 MB per part (round up to a power of two, e.g. 8 MB, for headroom). On a 20 Mbit/s uplink a
64 MB part takes ≈ 26 s; a failure loses at most that much work. Much larger parts (1 GB ≈ 7 minutes) lose too much on
each failure; much smaller ones add request overhead and approach the part-count limit. Choose something like 32–64 MB,
and upload 2–4 parts in parallel if bandwidth allows. Also: lifecycle rule to abort incomplete uploads, and a checksum
per part.
</details>

## 4. [Deep] Time to playable

A 10-minute 1080p upload. Single-machine fast-preset encoding of 360p + 720p runs at 2× real time. With chunking into
10-second chunks across 60 workers, estimate time to playable. What overheads remain?

<details><summary>Answer</summary>

Single machine: 600 s ÷ 2 = 300 s just for encoding (plus everything else). Chunked: 60 chunks of 10 s, one per worker,
each takes 5 s → encoding ≈ 5 s. Remaining overheads dominate: fetching the source from object storage, probing,
splitting at keyframes (sources may have sparse keyframes, forcing larger chunks), scheduling 60 tasks, concatenation,
packaging and CDN availability — realistically tens of seconds to a couple of minutes. The lesson's p95 < 5 min target
leaves room for queueing during peaks.
</details>

## 5. [Deep] Ladder design

Explain why a fixed ladder wastes bits on a cartoon and starves an action film. Use Netflix's per-title numbers to
illustrate, and say what extra work per-title encoding requires.

<details><summary>Answer</summary>

Visual complexity differs: a cartoon reaches high quality at low bitrate, so 5,800 kbps at 1080p is "far more than
needed"; noisy, grainy content can still show blockiness at 5,800 kbps. Netflix's per-title example: the top 1080p
rung dropped to 4,640 kbps (20 % savings) and 1080p started at 1,540 kbps where the fixed ladder served 480p at
1,750 kbps. Extra work: trial encodes at several resolutions/quality points to build the title's rate–quality curve,
plus a perceptual metric (VMAF) to choose points — multiplying encode compute, which is why it is applied to
content that will be watched a lot.
</details>

## 6. [Interview] When does AV1 pay for itself?

An 8-minute video. Assumptions: AV1 encoding costs 16 core-hours at $0.03 per core-hour; an average view streams
4 minutes at 3 Mbps; AV1 saves one-third of bytes (Netflix's reported figure vs AVC/HEVC); delivery costs $0.01/GB;
60 % of views are on AV1-capable devices. How many views until AV1 breaks even?

<details><summary>Answer</summary>

Encode cost = 16 × $0.03 = $0.48. Bytes per view = 240 s × 3 Mbps ÷ 8 = 90 MB; saving = 30 MB = 0.03 GB → $0.0003
per AV1-capable view. Break-even = $0.48 ÷ $0.0003 = 1,600 AV1 views ÷ 0.6 ≈ **2,700 total views**. Policy: encode AV1
once a video crosses ~3,000 views (or is predicted to). Every input here is an assumption — the useful skill is the
formula: extra encode cost ÷ (bytes saved per capable view × price × capable share). Also count rebuffering
improvements, which have value beyond bandwidth.
</details>

## 7. [Core] Cache hit ratio

At peak the platform serves 3 M segment requests/s. Origin (object storage behind a shield) can take 30,000 requests/s
comfortably. What edge+shield hit ratio do you need? What content characteristics make it hard?

<details><summary>Answer</summary>

Misses allowed = 30,000 / 3 M = 1 % → hit ratio ≥ **99 %** at the combined cache layers. Hard cases: a long tail of
rarely watched videos (each first view is a miss), premieres where everyone requests the same new segments
simultaneously (coalescing at the shield fixes the burst), and many renditions per video (each rung is a separate
object). Pre-positioning popular content in edge or ISP-embedded caches raises hit ratio for the head of the
distribution. Try [labs/04-caching](../labs/04-caching/) to see how p99 changes with hit ratio.
</details>

## 8. [Deep] Start-up budget

Write a start-up-time budget for p95 < 2 s on a mobile network with 80 ms RTT to the edge. Which steps can be
removed entirely?

<details><summary>Answer</summary>

Example: TLS + connection reuse 1–2 RTT (≈ 160 ms; 0 if already connected); playback API 200 ms; master + media
playlist fetch 2 × 100 ms; first segment (2 s of 400 kbps video ≈ 100 KB) ≈ 300 ms; decoder start 200 ms; total ≈
1.2 s, leaving slack for the p95 tail. Removable: the playback API round trip if the manifest URL is embedded in the
page/app response; playlist fetches if prefetched on hover or near the end of the previous episode; TLS if the
connection is warm (or 0-RTT/QUIC, [SYSDESIGN-02](../course/01-foundations/02-anatomy-of-a-request.md)).
</details>

## 9. [Lab] Poison sources and idempotent encoders

In [labs/08-async-event-driven](../labs/08-async-event-driven/), configure the poison-message experiment so one
message always fails. Treat it as a corrupt upload. Observe where it ends up and how many attempts are made. Then
explain how you would key encode tasks so that a redelivered task does not create duplicate renditions.

<details><summary>Answer</summary>

Record what you observe: after the configured number of attempts the message should move to the dead-letter queue
instead of blocking the queue. For video, the DLQ entry maps to "quarantine the video, notify the creator, keep the
source". Idempotency: key each task by `(video_id, codec, height, chunk)` and write output to a deterministic object
key; a redelivered task overwrites the same object (or skips it if the object exists with the expected checksum), so
duplicates are impossible by construction.
</details>

## 10. [Interview] AV2 and captions in 2026

A product manager asks to "ship AV2 next quarter" and "auto-caption everything". Respond with a plan for each.

<details><summary>Answer</summary>

AV2: the specification was announced by AOMedia in June 2026, but client decoders — especially hardware decoders in
TVs and phones — lag by years. Plan: an encoding-team evaluation (quality and encode cost vs AV1 on your content),
software-decoder pilots on capable devices, and a playback-API capability check so AV2 renditions can be added later
without changing the architecture. Captions: auto-generate on upload with a speech model (Whisper-class), publish as a
separate rendition, let creators edit, and measure error rates by language; machine captions are drafts, not ground
truth. Note that in the EU the European Accessibility Act applies from 28 June 2025 and covers access to audiovisual
media services — legal review decides what is mandatory for your platform.
</details>
