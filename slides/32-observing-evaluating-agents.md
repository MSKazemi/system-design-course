# 32 — Observing & evaluating agents (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- 30,000 agent tasks/day, ~15 model and 15 tool calls each
- Success fell 85% → 81% after a prompt edit, and nothing paged
- Find the guilty step in 30 minutes. Block ≥ 3-point regressions before full rollout
- Keep every failed and expensive run for 30 days, with no raw prompts in the trace store

**Visual:** flat error-rate chart next to a falling success chart; icons `ai-agent`, `ops-tracing`, `ops-warning`.
**Speaker notes:** Agents fail semantically. HTTP 200, normal latency, wrong or inconsistent outcomes. The chapter
treats observability and evaluation as one system.

## Slide 2 — Why agents are different
- Non-deterministic: debug populations of runs, not one trace
- Long, deep traces: 60+ spans over minutes, pauses, sub-agents
- Every run has a price, with a heavy tail
- Failure is semantic: outcomes, trajectories, people

**Visual:** four-quadrant card; icons `ai-agent`, `ops-cost`, `ops-clock`, `ops-error`.
**Speaker notes:** The same prompt can produce different tool sequences on two runs. Error-rate dashboards stay green
while quality drops.

## Slide 3 — The span tree of a run
- `invoke_agent` (INTERNAL in-process, CLIENT for a remote agent), `plan`
- `chat {model}` CLIENT, `execute_tool {tool}` INTERNAL
- MCP: one client-side tool span (no double count), server span joined via `params._meta`
- Sub-agent as a tool: nested `invoke_agent`

**Visual:** the lesson's span-tree flowchart; icons `observability-opentelemetry`, `ai-mcp`, `ai-tool`.
**Speaker notes:** These are the OpenTelemetry GenAI conventions, all in Development status as of 2026-11, in the
dedicated semantic-conventions-genai repository with no tagged release yet. Pin what you emit.

## Slide 4 — Attributes that earn their keep
- Agent name/id/version, `gen_ai.conversation.id`
- Tokens incl. cache read/write and reasoning; finish reasons
- Your namespace: version tuple, outcome, semantic tool results
- Sampling-relevant attributes set at span creation

**Visual:** span card with attributes grouped by colour *and* label; icon `ops-tracing`.
**Speaker notes:** The version tuple (agent, prompt, model, tool-set hash, harness, index) is what you slice by first.
An empty-but-successful tool result is the most common silent failure.

## Slide 5 — Content capture vs privacy
- Content is opt-in: `OTEL_INSTRUMENTATION_GENAI_CAPTURE_CONTENT`, default `NO_CONTENT`
- `*_ref` URIs to a governed, encrypted store, with no signed URLs
- Redact at write time. Tool output is untrusted
- Naive full-history capture is quadratic: 828 KB vs 114 KB per run

**Visual:** span → reference arrow → locked store; icons `security-encryption`, `arch-object-storage`.
**Speaker notes:** Deduplicated, content-addressed storage cuts content about 7× for a 15-step run in the worked
example. The upload hook runs regardless of sampling, so content needs its own retention.

## Slide 6 — Sampling long runs
- Collector tail sampling: `decision_wait` 30 s default vs 2–30 min runs
- Keep signals (failed, costly, escalated, security event) are known at run end
- Run-level keep decision plus a short-TTL flight recorder
- Metrics from 100% of runs, or the failure rate reads 54–64% instead of 15%

**Visual:** the lesson's flight-recorder flowchart; icons `arch-trace-sampling`, `ops-metrics`.
**Speaker notes:** Keeping all failures, all p95-cost runs and 10% of the rest keeps about 24% of runs (costly runs
are mostly failures under the 3× cost assumption; 28% if they were disjoint). Record the keep reason and weight, so
the random slice stays unbiased. Traces are sampled; the audit log and security event counts are not.

## Slide 7 — Debugging with traces
- Detect from success, not errors
- Slice by version tuple → compare distributions → read exemplars
- Loops, hidden tool errors, context blow-ups
- Replay with recorded tool results, then fork from step k

**Visual:** three pattern cards (loop, empty result, compaction); icons `ops-incident`, `ops-dashboard`.
**Speaker notes:** In the illustrative Lumen incident, v15 moved an instruction where compaction summarised it away.
Failing tasks become regression cases.

## Slide 8 — Layered evaluation
- Component: tools, retrieval, single-step validity
- Trajectory: constraints and budgets, not one prescribed path
- End-to-end: end-state graders, k trials, clean environments
- Simulated users when the agent talks to people (τ²-bench)

**Visual:** the lesson's eval-loop flowchart; icons `ai-evaluation`, `ops-check`, `arch-sandbox`.
**Speaker notes:** Grade the outcome first. τ-bench compares the final database with the goal state, and notes this
is necessary but not sufficient, which is where trajectory constraints come in.

## Slide 9 — Graders and their limits
- Code graders wherever an outcome is checkable
- LLM judges: >80% human agreement (Zheng 2023), with known biases
- Newer evidence: near-random on hard pairs (JudgeBench), well behind humans (Judging the Judges)
- Humans: calibration, new failure types, agreement measurement

**Visual:** three-column grader table; icons `ai-llm-judge`, `arch-users`.
**Speaker notes:** Narrow rubric items, an "unknown" option, a pinned and versioned judge, and calibration per task
family. Record scores as `gen_ai.evaluation.result` events on the evaluated span.

## Slide 10 — pass@k vs pass^k
- pass@k: at least one of k succeeds (candidate generation)
- pass^k: all k succeed (customer-facing reliability)
- Same 0.8 average: pass^4 0.41 vs 0.80
- Unbiased estimator C(c,k)/C(n,k). The plug-in overstates

**Visual:** two agents' per-task bars and their pass^4; icon `ai-evaluation`.
**Speaker notes:** τ-bench introduced pass^k and found GPT-4o-based agents under 50% task success with pass^8 below
25% in retail.

## Slide 11 — A gate with statistical power
- 200 tasks: ±4.9 points, blind to a 3-point drop
- Unpaired: ~2,400 tasks per version. Paired (10% discordance): ~870
- Rule at n = 900: block if the paired difference is below about −2.1 points (81% of 3-point drops, 2.5% of neutral)
- A/A run measures the noise floor; don't lower the temperature
- Tiers: smoke per PR, full paired gate per release, canary for hours

**Visual:** interval bars shrinking with n; icons `ops-ci-cd`, `ops-check`.
**Speaker notes:** A full gate of 900 × 3 × 2 runs costs about $356 at the chapter's cached price. Affordable per
release, not per pull request. A non-inferiority rule (lower bound above −3) at the same n would block about one
neutral change in five. Test the eval harness itself.

## Slide 12 — Benchmarks lose validity
- SWE-bench Verified: OpenAI stopped reporting it (Feb 2026)
- 59.4% of 138 audited hard tasks had material issues, plus contamination
- Epoch AI (Sep 2026): "Flawed", with a reward hack to a perfect score
- Hold out data, audit graders, report the scaffold

**Visual:** timeline Feb 2026 (OpenAI audit) → Sep 2026 (Epoch review); icons `ops-warning`, `ai-evaluation`.
**Speaker notes:** OpenAI recommended SWE-bench Pro, which adds held-out and commercial splits that are not publicly accessible. Audit its graders
like any other. Your private suite is the number you can defend.

## Slide 13 — SLOs for agents
- Task success (final and provisional), hard-failure rate, escalation rate
- Cost per resolved task: $0.078 → $0.098 in the illustrative worked regression
- Burn rate is capped at 1/budget: an 85% SLO tops out at 6.7×
- Burn-rate alerts on hard failures, change detection on success

**Visual:** gauge row; icons `ops-slo`, `ops-alert`, `ops-cost`, `ops-human-approval`.
**Speaker notes:** At 1,250 tasks/h, one hour's success estimate has about 1 point of standard error. A 10% canary
needs hours to see a 4-point drop.

## Slide 14 — Interview wrap
- CLARIFY success definition, when it is known, pass@k vs pass^k, privacy
- QUANTIFY spans, content, keep share, suite size, canary hours
- SKETCH span tree, run-level sampling, governed content, layered evals, gate, canary
- Red flags: log everything, uncalibrated judge, 50-task gate, public benchmark as gate

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip; icon `ai-agent`.
**Speaker notes:** Observe populations of runs, grade outcomes first, size the gate statistically, and watch cost per
resolved task.
