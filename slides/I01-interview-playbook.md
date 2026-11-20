# I01 — The interview playbook (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — What the interview really tests
- A compressed design review: ambiguous prompt, a peer, a clock
- Interviewers collect quotable evidence per rubric dimension, not a matching diagram
- Most failures come from time spent in the wrong places, not missing knowledge
**Visual:** title card, a clock over a whiteboard. Icons: `arch-users`, `ops-clock`.
**Speaker notes:** Two different designs can both be strong hires. What matters is that every choice is justified and
its costs are known.

## Slide 2 — The framework
- CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP
- Each step has a goal, a time budget and an artifact on the board
- Loop back when a later step proves an earlier one wrong, and say so
**Visual:** six-step flow with two dashed back-arrows (STRESS → CLARIFY, DEEPEN → QUANTIFY).
**Speaker notes:** The loop-backs are a feature. An iterative design method is what Google's SRE Workbook teaches as
non-abstract large system design.

## Slide 3 — Time budgets
- 45 min: CLARIFY 5 · QUANTIFY 4 · SKETCH 8 · DEEPEN 13 · STRESS 6 · WRAP 2 · questions 4
- 60 min: CLARIFY 6 · QUANTIFY 5 · SKETCH 10 · DEEPEN 20 · STRESS 8 · WRAP 3 · questions 5
- Announce transitions; check the clock when SKETCH ends (minute 19 of 45)
**Visual:** two stacked horizontal bars, one per format, segments labelled.
**Speaker notes:** Meta's guide notes the interviewer usually keeps the last five minutes for your questions. Running out
of time before STRESS is the most common way to lose the reliability signal.

## Slide 4 — CLARIFY
- Restate; functional verbs (4–7); rank the non-functional adjectives
- "If I had to choose between X and Y, which would the business pick?"
- Scale anchors; out-of-scope list
- Every question needs a "because"
**Visual:** board zone 1 with three lists: functional, ranked NFRs, out of scope. Icons: `ops-check`.
**Speaker notes:** Ranking NFRs separates seniors from juniors more reliably than any other move, because you will trade
them against each other later.

## Slide 5 — QUANTIFY
- Assumptions column first, then derive
- Peak, not average; reads and writes split
- Size state: storage, working set, connections (Little's law)
- End every number with "so …"
**Visual:** assumptions column → derived values → one "so what" line. Icons: `ops-metrics`, `ops-throughput`.
**Speaker notes:** The SRE Workbook says sound reasoning and assumptions matter more than final values. A number you
never use again produces no signal.

## Slide 6 — SKETCH
- Follow one request from client to storage; number the arrows
- One-sentence reason per box ("why is this here?")
- API (3–5 endpoints) and data model with keys matched to access patterns
- Flag what is deliberately naive
**Visual:** main diagram zone with numbered request path. Icons: `arch-client`, `arch-api-gateway`, `arch-queue`, `arch-database`.
**Speaker notes:** The interviewer must see a whole system before deep expertise in one part counts.

## Slide 7 — DEEPEN
- Choose by: where naive breaks first, correctness risk, interviewer interest
- Offer the choice: "fan-out or dedup, or something else?"
- Go two levels below the box: mechanism → trade-off → edge case and failure
**Visual:** four-level ladder (box, mechanism, trade-off, failure) using the dedup example.
**Speaker notes:** Level 2 is the senior bar. Strong-hire signals usually come from level 3.

## Slide 8 — STRESS
- Walk the path and break each hop: failure → impact → detection → mitigation
- Hot spots; ×10 bottleneck; overload behavior
- SLOs with numbers, plus one cost line
**Visual:** failure table with a highlighted "detection" column. Icons: `ops-incident`, `pattern-circuit-breaker`, `ops-slo`.
**Speaker notes:** "Add replicas" is not an answer. A mitigation nobody can trigger because nobody notices the failure
is not a mitigation.

## Slide 9 — WRAP and driving
- WRAP: decisions with trade-offs, top risks, next steps, under 2 minutes
- Drive with "propose, check, proceed"
- Follow redirects at once: park your thread, go
- Treat hints as information, and correct visibly
**Visual:** "propose → check → proceed" loop; parking-lot box on the board.
**Speaker notes:** A redirect tells you where the rubric still needs evidence. Ignoring it is a red flag at every level.

## Slide 10 — "I don't know": bound, reason, commit
- Bound what you know
- Reason from first principles to a range
- Commit to a decision and say how you'd validate it
- Never bluff a specific fact
**Visual:** three-step arrow with the Cassandra lightweight-transaction example.
**Speaker notes:** A bounded range is a correct answer for an estimate. A confident wrong fact costs more than an honest
bound.

## Slide 11 — Trade-off language
- "I'll choose X because R dominates; it costs C; I'd switch to Y if T"
- The trigger turns an opinion into a revisitable decision
- Replace "scalable/fast/reliable" with numbers
**Visual:** sentence template with four colored-and-labelled slots (labels carry the meaning).
**Speaker notes:** Most candidates leave out the trigger. Senior engineers name it in real design reviews.

## Slide 12 — Levels and remote interviews
- Junior → principal: scope, depth, autonomy, judgment
- Staff+: the signal is knowing what not to build
- Remote: practice the tool, narrate the pointer, pause longer, write more
- Use only permitted aids, and ask if unsure
**Visual:** level table excerpt; remote checklist. Icons: `arch-desktop`.
**Speaker notes:** The level table is this course's synthesis. No universal definition exists, so calibrate rather than
treat it as a contract.

## Slide 13 — The Lumen notification mock in one slide
- Shaping requirement: two traffic classes (transactional vs bulk)
- Numbers: ≈ 3,500 req/s peak; digest burst ≈ 5,500/s; SMS is the dominant cost
- Deep dives: idempotent sends with an unknown-outcome state; quiet hours via scheduled store with jitter
- STRESS: provider breakers, per-producer quotas, 99.95 % reasoned against 99.99 %
**Visual:** the mock's sketch diagram, two priority lanes highlighted by label. Icons: `domain-notification`, `domain-sms`, `domain-email`, `arch-queue`.
**Speaker notes:** Every number in the mock is a labelled assumption chosen during the interview. The point is how each
one turned into a decision.
