# I04 — ML/LLM system design interviews (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — Why these interviews feel different
- Behavior is learned, not coded: correctness is statistical
- Quality must be measured; "we'll check outputs" is a red flag
- The expensive resource is GPU memory, counted in tokens
**Visual:** title card with a model icon between data and users. Icons: `domain-ai`, `arch-users`.
**Speaker notes:** The skeleton is the same as I01. Weight moves to framing, metrics, data and evaluation.

## Slide 2 — Classical vs ML vs LLM
- Framing: what to build → what to predict → what task with what context
- Unit of work: request → request × candidates → tokens
- Typical failure: outage → drift and skew → hallucination, injection, cost runaway
**Visual:** three-column comparison table.
**Speaker notes:** Name the column you are in early. It tells the interviewer which numbers to expect.

## Slide 3 — CLARIFY: is ML needed?
- Outcome → task → inputs and outputs → decision it drives
- "Don't be afraid to launch without ML" (Zinkevich, Rule #1)
- Data, labels, freshness, privacy; unacceptable outcomes
**Visual:** funnel from business outcome to ML task.
**Speaker notes:** Offering a rules-based baseline is a senior signal, not a cop-out.

## Slide 4 — The metric ladder
- Business outcome → online product metric → offline model metric → system SLI → guardrails
- The ML objective is a proxy; guardrails catch divergence
- Easy launch only when all metrics improve or hold (Rule #39)
**Visual:** five-rung ladder with RAG examples on each rung. Icons: `ops-metrics`, `ops-slo`.
**Speaker notes:** Interviewers listen for metrics at every rung and for the links between them.

## Slide 5 — Two loops on the diagram
- Online: API → features/context → model → post-processing
- Offline: logs → datasets → training/tuning → eval → registry → shadow → canary
- Candidates who draw one loop miss half the system
**Visual:** the two-loop diagram from the lesson. Icons: `arch-data-pipeline`, `ops-deploy`.
**Speaker notes:** Log the features used at serving time so training matches serving (Rule #29).

## Slide 6 — Evaluation, offline and online
- Golden sets, stratified; score retrieval and generation separately
- LLM judges: > 80 % human agreement in one study, with position, verbosity and self-enhancement biases
- Calibrate judges on human labels; shadow → canary → A/B
**Visual:** eval pipeline with a calibration loop. Icons: `ops-check`, `ops-dashboard`.
**Speaker notes:** Track judge–human agreement as a metric in its own right.

## Slide 7 — Serving constraints
- TTFT and inter-token latency as separate SLOs
- TTFT = queueing + prefill; ITL = gap between streamed tokens; TPOT = a request's average per output token
- Prefill compute-bound, decode bandwidth-bound; KV caps concurrency
- Scale on waiting requests and KV-cache usage (vLLM exposes both)
**Visual:** two-phase timeline (prefill block, decode ticks). Icons: `arch-memory`, `ops-latency`.
**Speaker notes:** The formulas are in I02 and derived in chapter 21.

## Slide 8 — The question bank
- Chat · RAG · gateway · recommendations · eval platform · fine-tuning · agents · moderation
- Each with clarifying questions, numbers, core design, deep dives, pitfalls, rubric
**Visual:** eight tiles. Icons: `domain-chat`, `domain-document`, `arch-api-gateway`, `domain-feed`, `domain-bot`.
**Speaker notes:** Links go to chapters 21–28 and cases C09–C12 for depth.

## Slide 9 — Worked answer A: RAG help assistant
- 1.5 M questions/day, ≈ 70 QPS peak; index ≈ 16 GB, fits in RAM
- ≈ 3,400 input + 250 output tokens per answer
- Hosted ≈ $95k/month vs self-hosted ≈ 18 H100s (2 regions × ≈ 9, each able to take the full load) ≈ $39k/month (placeholder prices)
- Eval with abstention; event-driven freshness; version-keyed cache invalidation
**Visual:** RAG sketch; cost comparison bars labelled as assumptions. Icons: `search-elasticsearch`, `arch-search-index`, `ops-cost`.
**Speaker notes:** Public corpus means no ACLs, which removes most of C10's complexity. Saying so is a signal.

## Slide 10 — Worked answer B: home-feed recommendations
- ≈ 2,800 QPS peak; 800 candidates → 200 ranked → 30 shown
- Heavy ranker ≈ 11 TFLOP/s: compute is not the problem
- Label = long dwell, aligned with retention; exploration and propensity logging
**Visual:** multi-stage funnel with per-stage latency budget (sums to 250 ms). Icons: `domain-feed`, `pattern-fan-in`.
**Speaker notes:** The two-stage structure is long established; YouTube's 2016 paper is the widely cited description.

## Slide 11 — Worked answer C: LLM content moderation
- 20 M items/day; cascade: hash → classifier → LLM judge → humans
- GPUs: a handful. Human review: ≈ 60k items/day ≈ 150 reviewers
- Per-policy thresholds; errors measured by stratified expert sampling
- 300 ms p95 covers stage 0 + classifier; uncertain items are held for a label-only judge call (≈ 0.5 s p95); rationale written asynchronously
**Visual:** cascade with escalation percentages per stage. Icons: `security-authorization`, `arch-users`.
**Speaker notes:** Thresholds are cost levers as much as quality levers, because human review is the dominant cost:
≈ $9–13 k/month of GPUs against ≈ $450–900 k/month of reviewers under the lesson's assumptions. A judge that wrote its
rationale on the publish path would take 1–3 s, which is why it emits a label only.

## Slide 12 — Red flags and follow-ups
- No eval plan; sizing by requests; no baseline; one metric, no guardrails; uncalibrated judges
- "How do you know it works?" "What if the provider goes down?" "What if the context doubles?"
**Visual:** red-flag list beside follow-up list. Icons: `ops-warning`.
**Speaker notes:** Prepare a one-line answer to each follow-up before the interview.

## Slide 13 — Worked answer D: account-actions support agent
- Route by intent: how-to stays on answer A's RAG path; account intents go to the agent (≈ 50× the cost per conversation)
- 150 k conversations/day: ≈ 1,900 concurrent chats, ≈ 78 model calls/s, ≈ $0.10 per conversation, ≈ $0.17 per resolved one
- Tokens are not the money: ten points of containment are worth $0.32 against $0.10 for doubling tokens; wrong actions × 10 cost less than doubling tokens on average; exposure ≈ $750 k/day
- Model proposes, broker and policy engine decide: identity levels, subject binding, caps, fail closed, and a rate breaker against the same time-of-week baseline (3× the daily average, ≈ 1,900 an hour, would trip at every normal peak)
- Final-state replay eval with pass^k (0.95⁸ ≈ 0.66), ≈ 900-task gate blocking below about −2.1 points (catches ≈ 81 % of 3-point drops, blocks ≈ 2.5 % of neutral changes), autonomy ladder per intent
**Visual:** answer D's sketch with the broker and policy engine boxed as "deterministic", and the second loop (log → eval → registry) drawn dashed. Icons: `domain-chat`, `ai-agent`, `arch-policy-engine`, `domain-payment`, `ops-human-approval`.
**Speaker notes:** All numbers are labelled assumptions, the same per-conversation ones as C15. The strongest sentence
in the answer is that a model outage cannot fail over to humans, because that needs about 2.5 times the staff.
