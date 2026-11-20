# 29 — Exercises

Lesson: [SYSDESIGN-29 Agent architectures & orchestration](../course/03-ai-systems/29-agent-architectures-orchestration.md)

Unless stated otherwise, use the lesson's assumptions: base prompt 3,000 tokens, +1,500 tokens of history per step,
300 output tokens per step, $1.00 / M input and $4.00 / M output (illustrative), 8.5 s per step, per-step success 0.98.

### 1. [Core] Workflow, agent or team?

Place each feature on the spectrum and name the pattern: (a) tag every incoming support ticket with one of 12 product
areas; (b) "find every clause in our 300 supplier contracts that allows termination with under 30 days' notice";
(c) a nightly job that converts scanned delivery notes into ledger entries, with a human sign-off above €10,000;
(d) "upgrade this service from framework v4 to v5 and keep the tests green".

<details><summary>Answer</summary>

(a) **Routing workflow**: one classifier call (or a small fine-tuned classifier). Steps are known, latency and cost
should be minimal, and errors are cheap to fix.
(b) **Parallelisation (sectioning) workflow**: the same extraction prompt over each contract in parallel, then a
merge. It looks like "research", but the subtasks are identical and known, so no model needs to *decide* the
decomposition. An orchestrator-workers design adds a planning call for nothing.
(c) **Graph / state machine**: extract → validate → match → approval node above the threshold → post. It must be
auditable and resumable, so it belongs on a checkpointed graph or a durable workflow (SYSDESIGN-25 §7).
(d) **Single agent** (one writer), optionally with an **evaluator-optimiser** loop: a reviewer with a clean context
and the test suite as external feedback. Parallel writers would conflict ("writes stay single-threaded").
Acceptable alternative for (b): an agent per contract *if* clauses need multi-hop reasoning across documents, but
justify the extra cost.
</details>

### 2. [Core] Quadratic versus isolated

A single agent researches 6 competitors at 6 steps each (36 steps), then writes a 2,000-token report. An
orchestrator-workers design plans (3,000 in, 500 out), runs 6 workers of 7 steps each (6 research steps, so the same
36 research steps in total, then a digest step that returns a 1,000-token digest), then synthesises (2,000 out).
Compute input tokens, output tokens and uncached cost for both.

<details><summary>Answer</summary>

**Single agent.** Research input = 36 × 3,000 + 1,500 × (36 × 35 / 2) = 108,000 + 1,500 × 630 = 1,053,000.
Report step input = 3,000 + 36 × 1,500 = 57,000. Total input **1,110,000**. Output 36 × 300 + 2,000 = **12,800**.
Cost ≈ $1.110 + $0.051 = **≈ $1.16**.

**Orchestrator-workers.** Per worker: input 7 × 3,000 + 1,500 × 21 = 52,500. Output 6 × 300 + 1,000 = 2,800. Six
workers: 315,000 input, 16,800 output. Synthesis input = 3,000 + 500 + 6 × 1,000 = 9,500. Totals: input 3,000 +
315,000 + 9,500 = **327,500**, output 500 + 16,800 + 2,000 = **19,300**. Cost ≈ $0.328 + $0.077 = **≈ $0.40**.

About 2.9× cheaper for the same research work, because isolation removes the cross-competitor term in the quadratic
sum. Note that the team writes *more* output tokens. A common slip is to count the digest as one of the research
steps, which quietly gives the team less work and flatters it.
</details>

### 3. [Core] Critical path

For the two designs in exercise 2, estimate elapsed time. Assume workers run concurrently and decode at 50 tokens/s.
Then say what happens if one worker hits a slow API and takes 3× longer.

<details><summary>Answer</summary>

**Single agent:** 36 × 8.5 s + (0.5 + 2,000 / 50) s = 306 + 40.5 = **≈ 347 s**.

**Team:** plan 0.5 + 500 / 50 = 10.5 s. Worker = 6 × 8.5 + (0.5 + 1,000 / 50) = 51 + 20.5 = 71.5 s. Synthesis
40.5 s. Critical path = 10.5 + 71.5 + 40.5 = **≈ 123 s**, about 2.8× faster, but just over a 2-minute budget if you
had one. Cutting a research step per worker, or parallel tool calls inside each worker, would be needed to fit.

A 3× straggler makes the worker phase ≈ 215 s, and the critical path becomes ≈ 266 s. The barrier at synthesis means
the slowest worker sets the latency. Mitigations: a per-worker deadline with a partial result ("competitor 4: not
checked, API timeout"), incremental synthesis as digests arrive, or speculative re-dispatch of the straggler.
</details>

### 4. [Deep] Caching changes the verdict

Recompute exercise 2 with Anthropic-style caching: write 1.25×, read 0.1×, 5-minute TTL, every call writes only new
tokens. Assume the workers start cold and in parallel. Which design is cheaper now, by how much, and what is the
largest remaining cost line for the team?

<details><summary>Answer</summary>

**Single agent:** writes = 3,000 + 36 × 1,500 = 57,000 → 57,000 × 1.25 × $1/M = $0.071. Reads = 1,110,000 − 57,000 =
1,053,000 → × 0.1 = $0.105. Output $0.051. Total **≈ $0.23**.

**Team:** per worker, writes = 3,000 + 6 × 1,500 = 12,000 ($0.0150), reads = 52,500 − 12,000 = 40,500 ($0.0041),
so $0.0191 × 6 = $0.114. Lead plan writes 3,000 ($0.0038). Synthesis reads 3,000 ($0.0003) and writes 6,500
($0.0081). Input ≈ $0.126, output $0.077. Total **≈ $0.20**.

The team is still cheaper, but by about 1.1× rather than 2.9×. Output tokens ($0.077) are now nearly 40% of its cost,
and caching does not discount them. Warming the shared worker prefix first (one worker, wait for its first token,
then five more) saves 5 × 3,000 × 1.15 × $1/M ≈ $0.017 (to ≈ $0.19, about 1.2×), because a cache entry only becomes
available after the first response starts. Conclusion: choose the team for latency, not for dollars.
</details>

### 5. [Core] Handoff or agents-as-tools?

Lumen Support has a triage agent and three specialists (billing, technical, account security). (a) A customer wants
to dispute a charge and keep talking to whoever handles it. (b) An internal "account health report" needs input from
all three specialists. Which mechanism fits each, and what context does each specialist see?

<details><summary>Answer</summary>

(a) **Handoff.** The billing specialist should take over the conversation. In the OpenAI Agents SDK a handoff is a
`transfer_to_<agent>` tool, and by default the new agent sees the entire previous conversation. Filter that history
(drop the triage agent's internal reasoning, any untrusted pasted content, and secrets) with an input filter.
(b) **Agents as tools (supervisor).** The report agent keeps control and calls the three specialists, possibly in
parallel. Each sees only the brief the supervisor writes and returns a digest. Its context grows only by those
digests.
Risk in (a): confusion and injected text carried forward. Risk in (b): a thin brief that omits what the specialist
needs. See C15 for the full support design.
</details>

### 6. [Deep] Reliability with per-worker retries

Using exercise 2's team (6 workers × 7 steps, 2 lead steps, p = 0.98 per step, independent), compute task success
(a) with no retries, (b) with one retry per failed worker. Compare with the single agent (37 steps) retried once as a
whole. What assumption is most fragile?

<details><summary>Answer</summary>

Worker success = 0.98⁷ ≈ 0.868. Lead = 0.98² ≈ 0.960.
(a) 0.868⁶ × 0.960 ≈ 0.428 × 0.960 ≈ **0.41**. The single agent is 0.98³⁷ ≈ **0.47**, slightly better, because the
team runs 44 steps (six digest steps and a plan step more).
(b) Retried worker success = 1 − 0.132² ≈ 0.983. 0.983⁶ ≈ 0.90, × 0.960 ≈ **0.86**. The expected extra cost is
6 × 0.132 ≈ 0.79 workers.
Single agent retried once as a whole: 1 − 0.53² ≈ **0.72**, at up to 2× the whole cost. A single agent with
checkpoints (SYSDESIGN-25 §7) retries only the failed step, which narrows the gap. The team's lasting advantages are
that a bad digest can be detected and re-run in isolation, and that partial results are usable.
The most fragile assumption is **independence plus detection**. Retries help only if the lead can *tell* that a
worker failed (schema checks, citation checks, a verifier). An undetected wrong digest flows into the report.
Google's study reports 17.2× error amplification for independent agents versus 4.4× with central coordination.
Also, workers that share a bad source fail together, not independently.
</details>

### 7. [Deep] Diagnose from a trace

A research task's trace shows: the lead spawns 4 workers; worker 2 returns "insufficient data, need broader
search"; the lead spawns a new worker with the same brief; that worker returns the same; this repeats 9 times
before the step budget ends the task. Name the failure modes (MAST vocabulary where it fits) and give three fixes.

<details><summary>Answer</summary>

This is a **coordination loop**: MAST "step repetition" and "unaware of termination conditions" (system design
issues), plus arguably "fail to ask for clarification" (inter-agent misalignment). The lead re-delegates an
unchanged brief and expects a different result.
Fixes: (1) a **loop detector in code**: same (agent role, brief hash) N times → stop and return a partial result
with the gap marked (SYSDESIGN-25 §10). (2) A **digest schema** with a typed "blocked" status and a reason, which the
lead must answer by *changing* the brief (scope, sources) or escalating, never by resending it. (3) **Per-task caps**
on workers spawned and re-dispatches. Then add this trace to the evaluation set (SYSDESIGN-32).
</details>

### 8. [Core] Who executes the call?

Your agent uses a provider-hosted web-search tool and a provider-hosted code-execution tool, plus your own
`send_invoice` client tool. For each, say who executes the call and which of your runtime controls (approval,
budget check before the call, argument logging, egress allow-list) still apply.

<details><summary>Answer</summary>

- **`send_invoice` (client tool):** your runtime executes it. All controls apply: policy and approval before
  execution, idempotency key, budget check, full argument logging, your egress rules.
- **Hosted web search and code execution:** the **provider** executes them during the model request (Anthropic: server
  tools "run on Anthropic's infrastructure"; OpenAI: hosted tools "execute for the model on OpenAI servers"). Your
  runtime sees results, not a chance to veto each call. Per-call approval and pre-call budget checks do not apply
  unless the provider offers hooks. Logging depends on what the response returns. Egress is the provider's sandbox
  policy, not your allow-list.
Design consequence: enable hosted tools only for tasks where those calls are acceptable without per-call control, or
replace them with your own tools behind your gateway when you need the control. The phrase "the model never executes
anything" is true of the model, but with hosted tools someone else's runtime does.
</details>

### 9. [Deep] A portability boundary

Your team built the vendor-research feature on framework X. X's next major version changes its checkpoint format and
its multi-agent API. List what you should already own so the migration is a rewrite of glue code only, and say why
each matters.

<details><summary>Answer</summary>

1. **Task-state schema in your own database** (plan, steps, budgets, digests, handles). Then in-flight and historical
   tasks survive, and X's checkpoints are only a cache.
2. **Prompts and tool schemas versioned in your repository**, with evals in CI. The new version must pass the same
   suite before rollout.
3. **Tools behind MCP.** Integrations do not depend on X's tool-plugin format.
4. **OpenTelemetry GenAI traces.** Dashboards, alerts and trace-based evals keep working.
5. **Model access through your gateway.** Routing, quotas and cost attribution are unchanged.
6. **Budgets and policy in your runtime.** They are tested independently of X's callbacks.
Churn is real: as of 2026-11 AutoGen's README declares it archived (successor Microsoft Agent Framework), and Google
ADK deprecated its Sequential/Parallel/Loop agents in Python and TypeScript for graph workflows. Run old and new versions side by side and pin
in-flight runs to their version (rainbow deploy, SYSDESIGN-33).
</details>

### 10. [Interview] "Make our multi-agent prototype cheaper"

A prototype research assistant uses a planner, 12 always-on role agents (researcher, fact-checker, writer, editor,
and so on) that all see the full shared conversation, and a debate round before every answer. It costs $4 per query
and takes 6 minutes. The target is $0.50 and 2 minutes. Outline your answer using CLARIFY → QUANTIFY → SKETCH →
DEEPEN → STRESS → WRAP.

<details><summary>Answer</summary>

- **CLARIFY:** query mix (simple fact lookups versus broad comparisons), quality bar and how it is measured, what is
  written (just a report), latency target per class.
- **QUANTIFY:** shared full context across 12 agents means every agent re-reads everything, so tokens scale with
  agents × history. Debate multiplies by agents × rounds. Show how isolated workers (Numbers #2) cut tokens processed
  by several times, and how caching and output tokens shift the dollars.
- **SKETCH:** replace role agents with **orchestrator-workers**: a lead that sizes fan-out to the query (1 agent for
  simple lookups, 2–4 for comparisons, per Anthropic's published scaling rules), isolated workers with structured
  briefs and digests, handles in an artefact store, and one writer (the lead). Use a **routing workflow** in front to
  send simple queries to a single agent or a plain RAG chain.
- **DEEPEN:** verification by a separate evaluator with explicit criteria instead of debate on every query (debate
  only when the evaluator flags low confidence). Smaller models for workers. Warm the shared prefix.
- **STRESS:** over-spawning (hard cap), straggler workers (deadline plus partial result), wrong digest (citation
  check), deploy mid-run (version pinning).
- **WRAP:** measure cost per *successful* query on a paired eval set before and after. The goal is the cheapest
  design that holds quality, not the fewest agents for their own sake.
Red flag to avoid: cutting agents without measuring quality. Anthropic reports token usage explains 80% of
BrowseComp variance, so some spend is buying quality.
</details>
