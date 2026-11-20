# 30 — Context engineering & agent memory (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- About 150 tool calls over 200 contract pages, in a 200k-token window
- Under $5 per task (product assumption)
- Remember customer preferences across sessions, across 2,000 tenants with no leaks
- Every memory sourced. Erasure from every tier within the GDPR deadline

**Visual:** title card; icons `ai-agent`, `ai-tokens`, `arch-database`, `security-lock`.
**Speaker notes:** The window is finite, priced on every step, and degrades before it is full. Memory is a database
that an agent writes while reading untrusted text. This chapter designs both.

## Slide 2 — What is in the window
- Tool definitions, system instructions, skills index, injected memory
- History, retrieved knowledge, scratchpad
- Output reserve: part of the budget, not left over
- Order from most stable to least stable

**Visual:** stacked bar of the window: tools 5k, system 3k, skills 1k, memory 1k, summary, recent turns, output 8k
(the lesson's assumptions); icon `ai-prompt`.
**Speaker notes:** Every call is assembled from the same parts. The order matters because caches reuse prefixes, so
put stable content first and anything per-request last.

## Slide 3 — The window is priced
- Agents re-send history: tokens grow roughly with steps squared
- Cache reads at 0.1x; writes 1.25x (5 min) or 2x (1 h) on Anthropic, as of 2026-11
- OpenAI GPT-5.6+: 1.25x for 30 min, 2.5x for 12 h; Gemini 2.5+ caches implicitly
- A tool-definition change invalidates the whole cached prefix

**Visual:** prefix diagram `tools → system → messages` with a red cut where a timestamp sits at the top; icons
`ai-kv-cache`, `ops-cost`.
**Speaker notes:** Multipliers vary by model, so always check the pricing page. The structural rule does not change:
a byte that changes early invalidates everything after it.

## Slide 4 — More context is not better
- Lost in the Middle: best at start and end, worse in the middle
- RULER: only half of 17 models held up at 32K
- NoLiMa: 11 of 13 models below 50% of baseline at 32K; GPT-4o 99.3% → 69.7%
- Context Rot: 18 models degrade with length, even on simple tasks

**Visual:** U-shaped accuracy curve over position; a second curve falling with input length; icon `ai-llm`.
**Speaker notes:** These are 2023–2025 models; newer ones may do better, but none of these sources tests them.
Context Rot is a vendor technical report, the others are academic. The direction has held across several groups, so
re-measure on your model and task.

## Slide 5 — Six levers to keep the window small
- Tool output design: caps, pagination, concise mode (72 vs 206 tokens in one example)
- Just-in-time retrieval by id
- Tool-result clearing (default trigger 100k, keep 3, in Anthropic's API)
- Compaction, structured notes, sub-agent digests

**Visual:** six tiles, each with "loss" and "cache effect" badges; icons `pattern-compression`, `ai-tool`.
**Speaker notes:** Each lever trades information for tokens. Clearing and compaction invalidate the cached prefix,
so trigger them rarely and remove a lot each time.

## Slide 6 — Compaction loses information
- Brevity bias and context collapse (ACE, ICLR 2026)
- A summary schema: goal, constraints verbatim, decisions, open questions, ids, plan
- Notes outside the window survive. Never summarise a summary blindly
- Test it: long traces, questions with early answers, before and after

**Visual:** a document passing through three rewrite cycles, losing lines each time; beside it a notes file that
stays intact.
**Speaker notes:** Compaction is a lossy codec written by a model. Treat it like one: specify it, test it, and keep
the raw transcript as ground truth.

## Slide 7 — The numbers
- 150 steps: final context 188,800 tokens (94% of the window)
- 14.91M input tokens: ≈ $45.40 uncached, ≈ $5.80 cached
- Compaction at 100k: 8.35M tokens, ≈ $4.11 cached
- With caching, compaction saves fewer dollars (29%) than tokens (44%)

**Visual:** three bars (uncached, cached, cached + compaction); icons `ops-cost`, `ai-tokens`.
**Speaker notes:** Illustrative prices of $3 and $15 per million tokens. Caching is the 8x lever. Compaction's bigger
win is headroom and working in the shorter range where models do better.

## Slide 8 — Retrieval, fine-tuning or long context
- Long context: small, whole-document, within a task
- Retrieval-as-memory: large, changing, per-tenant, erasable
- Fine-tuning: shared behaviour and style, not per-user facts
- Evidence: RAG beat unsupervised fine-tuning for knowledge injection (Ovadia et al.)

**Visual:** three columns with "wins when" and "erasure difficulty" rows; icons `ai-vector-db`,
`ai-model-training`.
**Speaker notes:** For per-user memory, retrieval is the default. Erasing a row is easy, and erasing a fact from
weights is not.

## Slide 9 — Memory taxonomy and stores
- Working, session, semantic, episodic, procedural (CoALA plus a session tier)
- Facts as rows with provenance; episodes in a vector index; notes as files
- Graph only for genuinely multi-hop questions
- Write path: extract → policy check → merge → provenance → store

**Visual:** the write/read path diagram from the lesson; icons `arch-database`, `ai-vector-db`, `arch-file-storage`.
**Speaker notes:** Memory is ordinary data engineering with an untrusted author. The read path starts with a tenant
scope filter, which is a security boundary, not a ranking signal.

## Slide 10 — Skills: procedural memory as files
- `SKILL.md`: name (≤ 64 chars), description (≤ 1,024), instructions, optional scripts
- Progressive disclosure: about 100 tokens metadata, under 5,000 for a body, resources on demand
- 60 skills ≈ 6,000 tokens per call. All bodies up front would not fit
- Third-party skills are supply chain: trusted sources, review, pinning

**Visual:** folder tree `skill-name/SKILL.md, scripts/, references/, assets/`; three-level disclosure funnel; icons
`ai-skill` (missing), `security-sbom`.
**Speaker notes:** Agent Skills began at Anthropic and became an open standard in December 2025. CoALA warns that writes
to procedural memory are riskier than other memory writes; by analogy, agents propose skills and humans publish them.

## Slide 11 — Poisoning, provenance and erasure
- MINJA: poison memory through queries alone. AgentPoison: over 80% success with under 0.1% poison
- Every memory: tenant, subject, origin, evidence ref, writer, taint, validity, TTL, version
- Quarantine tainted sessions (except verbatim user statements); write authorisation by key; roll back by session
- Erasure covers rows, embeddings, wikis, summaries, checkpoints, traces, caches, backups

**Visual:** memory lifecycle with a taint tag and a quarantine store; erasure fan-out to eight kinds of copy; icons
`security-prompt-injection`, `security-key-shred`, `arch-audit-log`.
**Speaker notes:** A memory is a delayed prompt injection with persistence. Per-claim source ids decide whether you
can erase a person from a consolidated page at all.

## Slide 12 — Interview angle
- CLARIFY: task length, window, cost target, what to remember, tenancy, erasure
- QUANTIFY: growth per step, cost cached and uncached, memory size and rates
- SKETCH: context layout, levers, memory tiers, write and read paths
- DEEPEN → STRESS → WRAP: compaction loss, poisoning, erasure, cache collapse

**Visual:** the six-step framework strip with this chapter's prompts; icon `ai-agent`.
**Speaker notes:** Red flags include "just use a million-token window", agent-written memory with no taint check, and
erasure that ignores summaries and traces. Close by naming what you would measure.
