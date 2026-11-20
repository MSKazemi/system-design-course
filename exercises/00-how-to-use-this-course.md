# 00 — Exercises

Lesson: [course/00-orientation/00-how-to-use-this-course.md](../course/00-orientation/00-how-to-use-this-course.md)

### 1. [Core] Name the loop

Name the seven steps of the requirement loop in order. For each, give the one artefact it produces.

<details><summary>Answer</summary>

1. **Requirement**: one quantified sentence (metric, threshold, population, condition).
2. **Numbers**: a worked estimate with labelled assumptions (peak rate, concurrency, storage, budget).
3. **Design**: a diagram where every box is justified by a requirement, plus a trade-off table.
4. **Deep dive**: the analysis of the hardest part (algorithm, data structure, protocol, paper).
5. **Break it**: a failure-mode list. What fails, what users see, how you detect it.
6. **Operate**: SLIs/SLOs, alerts, deploy and capacity plan, cost and energy per unit of work.
7. **Interview angle**: how the topic is asked, an answer outline, red flags, follow-ups.

Two arrows are commonly forgotten: breaking a design sends you back to Design, and operating it produces new
Requirements. The loop is iterative.
</details>

### 2. [Core] Adjective to requirement

Rewrite each as a requirement with metric, threshold, population and window: (a) "search should be fast";
(b) "uploads must never be lost"; (c) "the chat must scale".

<details><summary>Answer</summary>

(a) "99% of search requests from logged-in users return results within 400 ms (client-measured), over a rolling
30 days."

(b) "Once an upload is acknowledged, the annual probability of losing it is below 10⁻¹¹. An acknowledged upload
is readable within 5 s from any region." *Durability* and *visibility* are separate requirements. Say both.

(c) "Sustain 3× the forecast peak of concurrent chat streams for one hour while keeping time to first token
p95 under 1 s." "Scale" is meaningless without the multiple and the latency you must hold while scaling.

Acceptable alternatives use other thresholds. What matters is that all four parts are present.
</details>

### 3. [Core] Pick a path

Pick a path and the first five units for each person: (a) a final-year student with no production experience;
(b) a platform engineer moving to an inference team; (c) a mid-level engineer with a staff-level interview in
four weeks.

<details><summary>Answer</summary>

(a) **Path A**: 00 → 01 → 02 → 03 → 04. Foundations first, with every lab. The labs make up for the missing
production experience.

(b) **Path B**: 01 → 21 → 22 → 23 → 26, after skimming 00. Do 01 properly, because Little's law and utilisation
drive inference capacity. Then go straight to inference anatomy, serving, GPUs and gateways. 11 and 12 are
probably already familiar and can be used as reference.

(c) **Path C**: I01 → 01 → I02 → 03 → 04. Method, then numbers, then high-frequency topics. Staff level means
adding 12, 15, 16 and 18 before mock interviews, because operations, geography, cost and security are where staff
answers stand apart. With four weeks, read [Core] plus [Deep] for 03–08, and do cases C01, C02, C06, C07, C09.
</details>

### 4. [Core] Markers

A colleague says: "I skipped every [Deep] section and I'm ready for a senior interview." Do you agree?

<details><summary>Answer</summary>

Not quite. [Core] sections give the standard designs and numbers, enough for a solid mid-level answer.
Senior interviews spend most of their time in DEEPEN and STRESS: *why* power of two choices beats "least
loaded", *how* consistency is achieved, *what* fails and how you'd detect it. That is [Deep] material. A
reasonable compromise under time pressure is to read [Deep] for the five or six topics you are most likely to be
asked about (scaling, caching, replication, sharding, async, reliability).
</details>

### 5. [Core] Test-status labels

A lab's README says "Test status: syntax-reviewed". What can you rely on, and what can't you? What would it take
to say "runtime-tested"?

<details><summary>Answer</summary>

*Syntax-reviewed* means the configuration was validated, for example with `docker compose config` or a linter,
but the lab was **not run end to end**. Images might fail to pull, services might not start, and the expected
results are reasoned, not observed. To be *runtime-tested*, someone must run the lab on a stated date, host OS
and tool versions, and record a summary of the observed output. *Reproduced* additionally requires an
independent second run. The labels exist so that the course never claims more than was done.
</details>

### 6. [Core] Evidence from the 2016 → 2026 shifts

For three of the six shifts in the lesson, give one dated piece of evidence and one design consequence.

<details><summary>Answer</summary>

Any three of:

- **LLM inference**: vLLM's PagedAttention (SOSP 2023) reported 2–4× throughput by paging KV-cache memory.
  Consequence: GPU memory management and batching are design decisions.
- **GPUs**: memory bandwidth went from 732 GB/s (P100, 2016) to 3.35 TB/s (H100), and to about 8 TB/s per GPU in
  a DGX B200. Consequence: decode throughput is often bounded by memory bandwidth, so capacity planning is done
  in tokens/s per GPU.
- **Cost and energy**: the IEA estimates 415 TWh of data-centre electricity in 2024 (about 1.5% of the global
  total), heading to about 945 TWh by 2030. Consequence: energy per request becomes a requirement alongside
  latency.
- **Regulation**: the AI Act applies from 2 August 2026 with exceptions, and the high-risk Annex III obligations
  moved to 2 December 2027 under Regulation (EU) 2026/1744. Consequence: logging, oversight and data governance
  are system requirements with dates.
- **Supply chain**: xz-utils backdoor CVE-2024-3094 (March 2024); SLSA v1.0 (April 2023). Consequence: signed
  artefacts and provenance are pipeline components.
- **Platforms**: Kubernetes went from 1.0 (July 2015) to 1.37 (2026). The CNCF Platforms White Paper appeared in
  2023. Consequence: autoscaling, rollouts and identity are platform capabilities that designs reuse.
</details>

### 7. [Deep] Run the loop on a feature

Apply the full loop to the Lumen feature "users can export a conversation as PDF". Keep each step to two or
three lines.

<details><summary>Answer</summary>

1. **Requirement**: "An export of a conversation of up to 500 messages is downloadable within 10 s at p95.
   Exports respect the user's current access rights."
2. **Numbers** (assumptions): 1% of 500,000 DAU export once a day = 5,000 exports/day ≈ 0.06/s on average, maybe
   1/s at peak. 2 s of CPU per PDF, so about 2 cores at peak. Output about 500 KB each, so about 2.5 GB/day,
   kept for 24 h.
3. **Design**: asynchronous job. The API enqueues it, a worker renders the PDF to object storage, and the client
   polls or is notified and then downloads through a pre-signed URL. Synchronous rendering would tie up API
   workers for seconds.
4. **Deep dive**: authorisation at render time *and* at download time (rights may change in between). Expire
   download links and artefacts.
5. **Break it**: the worker crashes mid-render (retry with an idempotency key). A huge conversation (cap the size,
   or stream the rendering). A link shared publicly (short expiry, bind to the user).
6. **Operate**: SLI = fraction of exports ready within 10 s. Queue age alert. Cost: storage TTL of 24 h keeps
   storage negligible.
7. **Interview angle**: a good miniature of "async job + object storage + pre-signed URL". The red flag is doing
   it synchronously in the request path.

Alternatives are acceptable if each step is present and the numbers justify the design (here, they justify a
queue but not a big cluster).
</details>

### 8. [Interview] Map the loop to the interview

How does CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP map onto the requirement loop? Where do candidates
most often run out of time, and what's the fix?

<details><summary>Answer</summary>

CLARIFY = Requirement. QUANTIFY = Numbers. SKETCH = Design. DEEPEN = Deep dive. STRESS = Break it + Operate.
WRAP = summary of trade-offs (the Interview-angle step turned inwards). Candidates most often over-spend on
SKETCH: drawing every box and naming technologies, then arriving at DEEPEN with five minutes left. The fix is
time-boxing (about 5 / 5 / 10 / 15 / 7 / 3 minutes in a 45-minute slot, as recommended in the lesson), and
sketching only the boxes the numbers demand.
</details>

### 9. [Core] What did not change

Give three things that did not change between 2016 and 2026 and that still constrain every design.

<details><summary>Answer</summary>

Any three of: the speed of light in fibre (≈ 200,000 km/s, so cross-continent round trips stay tens of
milliseconds or more); the queueing curve (latency explodes as utilisation approaches 100%); Little's law
(L = λW); the CAP trade-off under partitions; the fact that components fail, often together. Many "new" ideas
are old ones applied to new constraints. PagedAttention is virtual memory. KV-aware routing is affinity routing
with a new key.
</details>
