# 00 — How to use this course (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Lesson: [course/00-orientation/00-how-to-use-this-course.md](../course/00-orientation/00-how-to-use-this-course.md)

## Slide 1 — What changed in ten years?

- The question: what must a 2026 system designer know that a 2016 one didn't?
- The classics still run the world: caches, replicas, shards, queues, consensus
- New workloads, new constraints, new threats
- This course teaches both, through one method

**Visual:** Split screen: "2016" (web servers, databases) vs "2026" (GPUs, tokens, regulation); icons `arch-servers-cluster`, `arch-database`, `domain-ai`, `arch-cpu`.

**Speaker notes:** Open with the question from the lesson's requirement. The answer is not "throw away the
classics". It is "add six new constraints to the same reasoning".

## Slide 2 — Reason from requirements, not boxes

- Every chapter opens with one quantified requirement
- Components appear *because* a requirement needs them
- Every box must answer: "why is this here?"

**Visual:** A diagram where each box carries a small tag naming the requirement it serves; icons `arch-load-balancer`, `arch-cache`, `arch-queue`.

**Speaker notes:** Most material teaches the standard diagram. Here the requirement comes first and the diagram is
derived from it, which is also what interviewers grade.

## Slide 3 — The requirement loop

- Requirement → Numbers → Design → Deep dive → Break it → Operate → Interview angle
- Break it → back to Design; Operate → new Requirements
- Iterative, not a waterfall

**Visual:** Seven-step loop (Mermaid flowchart from the lesson) with two feedback arrows; icons `ops-slo`, `ops-cost`, `ops-incident`.

**Speaker notes:** Walk each step and its artefact: the requirement line, the worked estimate, the trade-off
table, the deep dive, the failure table, the SLO and cost section, the interview outline.

## Slide 4 — Steps 5 and 6 are where designs prove themselves

- Break it: kill, slow, overload, expire
- Operate: SLIs, SLOs, alerts, deploys, cost, energy
- A design that meets latency at 3× the budget has failed

**Visual:** A design being "attacked": a node with a cross, a latency spike, a cost meter; icons `ops-incident`, `ops-latency`, `ops-cost`.

**Speaker notes:** These two steps are what most courses skip, and what the labs focus on.

## Slide 5 — Depth markers

- [Core]: everyone, the standard design with numbers
- [Deep]: senior engineers, the *why*, maths and papers
- [Frontier]: 2024–2026 state of the art, dated "as of 2026-11"

**Visual:** Three stacked layers labelled Core / Deep / Frontier, with a calendar on the Frontier layer; icon `ops-calendar`.

**Speaker notes:** A first pass can read only Core. Senior interviews live in Deep. Frontier is the first to go out
of date, so it carries versions and dates.

## Slide 6 — Meet Lumen

- A fictional AI knowledge and chat product (`example.com`)
- Upload documents, search, ask, get answers with citations, later agents
- Grows from one server to a global, GPU-backed, multi-tenant service
- All numbers are labelled assumptions

**Visual:** Lumen's growth as five stages on a timeline, from one server to multi-region GPUs; icons `arch-server`, `arch-servers-cluster`, `arch-region`, `domain-ai`, `domain-chat`.

**Speaker notes:** Lumen is a teaching device, not a real company. Real systems are cited from published sources
when used as examples.

## Slide 7 — Three paths

- Learner: everything in order, every lab (≈ 140 h)
- Practitioner: 01, 11–12, Part II, all of Part III, AI cases (≈ 77 h)
- Interview candidate: I01, 01, I02, high-frequency topics, cases, AI round (≈ 65 h)

**Visual:** Three coloured routes over the course map, each also labelled with text (A, B, C), not colour alone; icons `arch-user`, `arch-users`.

**Speaker notes:** The estimates in the lesson come from per-unit time assumptions. Halve them for a Core-only
pass.

## Slide 8 — Shift 1–2: LLM inference and GPUs

- Transformer 2017; ChatGPT 30 Nov 2022
- vLLM PagedAttention (SOSP 2023): 2–4× throughput by paging the KV cache
- GPU memory bandwidth: 732 GB/s (P100, 2016) → 3.35 TB/s (H100) → ≈ 8 TB/s per GPU (DGX B200)

**Visual:** Bar chart of memory bandwidth P100 / H100 / B200 per GPU, with numbers printed on the bars; icons `domain-ai`, `arch-cpu`.

**Speaker notes:** Decode is memory-bandwidth bound, so bandwidth, not peak FLOPS, often limits tokens per second.
Power per device also more than doubled from P100 to H100.

## Slide 9 — Shift 3: cost and energy are requirements

- Data centres: ≈ 415 TWh in 2024, ≈ 1.5% of global electricity (IEA)
- Projection: ≈ 945 TWh by 2030
- Average PUE stuck at about 1.55–1.59: further gains must come from the workload

**Visual:** Two numbers in large type (415 TWh → 945 TWh) and a flat PUE line; icons `ops-cost`, `arch-datacenter`.

**Speaker notes:** Facilities stopped getting more efficient on average, so utilisation, batching and scheduling
are now the levers.

## Slide 10 — Shift 4: regulation is an architectural input

- GDPR applies since 25 May 2018
- AI Act: in force 1 Aug 2024; applicable 2 Aug 2026 with exceptions
- Digital Omnibus (Reg. 2026/1744): Annex III high-risk obligations from 2 Dec 2027
- Data Act from 12 Sep 2025; CRA reporting from 11 Sep 2026

**Visual:** Timeline 2016–2028 with regulation milestones; icons `security-lock`, `ops-calendar`, `domain-document`.

**Speaker notes:** These dates turn into requirements: residency, erasure across replicas, logging, human
oversight. Dated as of 2026-11.

## Slide 11 — Shifts 5–6: supply chain and platforms

- SolarWinds ED 21-01 (Dec 2020), Log4Shell (Dec 2021), xz backdoor CVE-2024-3094 (Mar 2024)
- SLSA v1.0 (Apr 2023): provenance as a pipeline component
- Kubernetes 1.0 (Jul 2015) → 1.37 (2026); platform engineering (CNCF white paper, 2023)

**Visual:** Dependency tree with one poisoned node; a platform "paved road"; icons `security-bug`, `devops-kubernetes`, `ops-ci-cd`.

**Speaker notes:** The attack moved into your dependencies, and the platform became the place where autoscaling,
identity and policy live.

## Slide 12 — What did not change

- Speed of light in fibre
- The queueing curve and Little's law
- CAP, and the fact that everything fails
- New ideas are old ones under new constraints: PagedAttention is virtual memory

**Visual:** A ruler labelled "physics" alongside a hockey-stick latency curve; icons `ops-latency`, `arch-network`.

**Speaker notes:** This is why Part I stays in the course. Close by pointing to SYSDESIGN-01 as the next stop.

## Slide 13 — How to read the evidence

- Numbered references, primary sources first
- Every number is sourced or labelled an assumption
- Labs say what was actually run: illustrative / syntax-reviewed / runtime-tested / reproduced

**Visual:** Four status badges, each with its word printed; icon `ops-check`.

**Speaker notes:** The course never claims more than was done. That includes its own labs.
