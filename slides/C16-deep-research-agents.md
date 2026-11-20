# C16 — Deep-research multi-agent system (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The prompt
- Question in, cited report out: lead plans, researchers search in parallel, verifier checks citations
- Web and internal documents; 50,000 reports a day
- Usually < 10 min, p95 < 15 min, hard cap $5 per report
**Visual:** question card → lead → three researcher lanes → report with footnotes. Icons: `ai-agent`, `pattern-fan-out`, `domain-document`.
**Speaker notes:** The design multiplies tokens on purpose; the job is to make that pay.

## Slide 2 — CLARIFY and rank
- Sync or async? Value per report? Web only or internal too? Plan review?
- Rank: citation accuracy > data boundaries > cost cap > wall time > breadth
- Out of scope: building a search index, unlicensed paywalled content, training models
**Visual:** ranked list. Icons: `ops-check`, `security-lock`.
**Speaker notes:** Multi-agent research is only worth its bill for questions worth several dollars of compute.

## Slide 3 — QUANTIFY tokens bottom-up
- Lead 8 calls × 20 k; 5 researchers × 15 steps × 30 k; citation 50 k
- ≈ 2.46 M input, ≈ 42 k output per deep report
- Published ratios (≈ 4× agent, ≈ 15× multi-agent vs chat) are sanity checks, not inputs
**Visual:** stacked bar by agent role. Icons: `ai-tokens`, `domain-analytics`.
**Speaker notes:** The post does not size its chat baseline, so do not turn "15×" into a token count.

## Slide 4 — QUANTIFY cost
- One strong model: ≈ $4.4 per report; researcher input ≈ two thirds of it
- Smaller researcher model at one third the price: ≈ $2.1
- ≈ 150 claims to verify (≈ $0.30): an 8 k-token report has a lot of sentences
- Simple question with one agent: ≈ $0.24, about 18× cheaper
**Visual:** three bars: deep strong, deep tiered, simple. Icons: `ops-cost`, `ops-budget`.
**Speaker notes:** Effort routing and the researcher model are the two biggest levers. Only the tiered column leaves headroom under the $5 cap once the budget is split per agent.

## Slide 5 — Wall time and concurrency
- Plan → round 1 (3 researchers) → review → round 2 (2) → synthesis → verify ≈ 7 min
- Rounds are synchronous; synthesis is decode-bound (≈ 2 min for 8 k tokens)
- 3 s steps assume the faster researcher model; on the strong model rounds hit the 150 s deadline (≈ 8.5 min)
- ≈ 730 concurrent reports at peak; ≈ 4.3 M input tokens/s; 52 searches/s
**Visual:** Gantt chart of the phases. Icons: `ops-clock`, `ops-throughput`.
**Speaker notes:** The bottlenecks are model quota, search quota and per-host politeness, not GPUs.

## Slide 6 — SKETCH
- Admission → fair run queue → durable orchestrator → lead
- Researchers in two zones; search-and-fetch gateway; artefact store; verifier; LLM gateway
- The fetch gateway enforces robots rules, per-host limits, quotas and a gate on outgoing queries
**Visual:** the lesson flowchart. Icons: `arch-queue`, `devops-temporal`, `arch-object-storage`, `ai-llm-gateway`.
**Speaker notes:** Contexts hold references; pages and findings live in the artefact store.

## Slide 7 — When multi-agent pays: the evidence for
- Anthropic: multi-agent beat single agent by 90.2 % on its internal eval
- Token use explained 80 % of BrowseComp variance (three factors 95 %)
- 3–5 parallel researchers cut time by up to 90 % on complex queries
**Visual:** scatter "tokens vs quality" with a fitted line. Icons: `ai-anthropic`, `ops-metrics`.
**Speaker notes:** Quality and cost are coupled, so measure quality per dollar.

## Slide 8 — …and against
- Cognition: share context; conflicting implicit decisions give bad results
- 2026 follow-up: works best when writes stay single-threaded
- Controlled study: +80.8 % to −70.0 % vs single agent depending on task shape
**Visual:** two-column "fits / does not fit" table: research vs coding. Icons: `ai-agent`, `ops-warning`.
**Speaker notes:** Research is breadth-first and read-only with a single writer, the favourable case.

## Slide 9 — Control the fan-out
- Effort classes: simple (1 agent), comparison (2–4), deep (5); published heuristic for complex research is > 10
- Depth 1; typed briefs with objective, output, tools, boundaries, budget
- Budget split: lead 15 %, citations 15 % (ring-fenced), researchers 65 %, wrap-up reserve 5 %
- Sized for the tiered models: ≈ $0.26 expected of a $0.65 share; one strong model funds only about 3 researchers
- Reserve the expected cost before each call (cached part at the read price)
**Visual:** budget tree from $5 down to each researcher. Icons: `ops-budget`, `pattern-rate-limiter`.
**Speaker notes:** "50 sub-agents for a simple query" was an early failure in the published system. More than 10 researchers would cost about $8 on the strong model, so our deep class is a cost-driven adaptation of the published heuristics.

## Slide 10 — Long runs
- Durable workflow; researchers as child workflows; resume, never restart
- References, not content: inline contexts would put ≈ 10 MB in one history
- Straggler deadline per round → partial findings + coverage note
- Pin each run to its version (rainbow-style drain)
**Visual:** timeline with a crash and a resume. Icons: `devops-temporal`, `pattern-retry`, `ops-deploy`.
**Speaker notes:** A 7-minute run is shorter than the deploy interval, so pinning is enough here.

## Slide 11 — Citations you can check
- Claims carry source hashes and quote spans
- Locate: a claim citing a page never fetched fails immediately
- Verify with a small judge on (claim, passage); store snapshots with fetch time
- Rubric eval: accuracy, citation accuracy, completeness, source quality, tool efficiency
**Visual:** claim → snapshot passage → supported / partial / unsupported. Icons: `ai-evaluation`, `pattern-deduplication`.
**Speaker notes:** Early agents preferred SEO content farms; encode source preference in the brief.

## Slide 12 — Trust zones
- Rule of Two: at most two of untrusted input, private data, outbound or state change, per context
- Web researchers: no private data. Internal researchers: no egress
- A brief is an outbound channel: web briefs are written before the lead reads internal findings
- Synthesis-phase lead holds both inputs, so it has no outbound tools and issues no web briefs
- Gateway gate on queries; reports render without auto-loading URLs
**Visual:** 3×3 table of components vs properties. Icons: `security-prompt-injection`, `security-zero-trust`, `arch-egress`.
**Speaker notes:** A fetch is an outbound channel, and so is every brief that reaches a web researcher. Zones alone fail by delegation; per-context taint and a two-phase lead close the gap.

## Slide 13 — STRESS and ×10
- Runaway fan-out, stragglers, search outage, invented citations, deep-mode rush
- Admission control: quotas, fair queue, ETA, offer the cheaper mode
- ×10: 43 M tokens/s at peak, 15 M searches/day → contracted throughput, own crawl at break-even
**Visual:** failure grid. Icons: `ops-incident`, `pattern-load-shedding`, `search-opensearch`.
**Speaker notes:** At scale, routing a question to one agent instead of five saves about $4 each time.

## Slide 14 — WRAP
- Junior: one agent with search and fetch, max steps, links
- Senior: orchestrator-worker, typed briefs, budgets, durable runs, fetch gateway, citation checks, rubric eval
- Staff: correct use of published ratios, effort routing, counter-evidence, ring-fenced verification, engine limits, trust zones, quality per dollar
- Red flags: "more agents = better", unchecked citations, one agent with web + private data + email
**Visual:** level ladder. Icons: `ops-check`.
**Speaker notes:** End with the decision rule for single versus multi and how you would measure it.
