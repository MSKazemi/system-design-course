# 32 — Exercises

Lesson: [SYSDESIGN-32 Observing & evaluating agents](../course/03-ai-systems/32-observing-evaluating-agents.md)

### 1. [Core] Why didn't anything page?

Lumen's agent success rate fell from 85% to 81% after a prompt edit. Error rate, p99 latency and saturation stayed
flat. Explain why classic RED/golden-signal alerting missed it, and name three signals that would have caught it.

<details><summary>Answer</summary>

Agent failures are **semantic**. A run that loops until its step budget, skips a search, or confidently answers
wrong still returns HTTP 200 with normal latency, so RED metrics see nothing. Signals that would catch it:

1. **Task success from final outcomes**, computed from 100% of runs and sliced by version tuple (prompt version
   shows v15 alone dropped).
2. **Trajectory metrics**: the tail of `gen_ai.invoke_agent.tool_calls`, repeated identical tool calls (same
   argument hash), share of runs ending in `budget_exhausted`.
3. **Cost per resolved task**, which rises when failures loop (lesson Numbers 8: $0.078 to $0.098, +27%, in the
   illustrative worked example, while mean cost per run rises about 21%).

Also acceptable: escalation rate, judge scores on sampled runs, compaction rate followed by repeated work.
</details>

### 2. [Core] Draw the span tree

A run plans, makes three model calls, calls `search_docs` through an MCP server twice, and hands one sub-task to a
sub-agent exposed as a tool. List the spans with operation names and span kinds, and say how the MCP server's span
joins the trace.

<details><summary>Answer</summary>

- `invoke_agent lumen-tasks`, INTERNAL (in-process agent; a remote agent service would use a CLIENT
  `gen_ai.client.invoke_agent` span).
- `plan lumen-tasks`, INTERNAL, with the `chat` call that writes the plan as its child.
- 3 × `chat {model}`, CLIENT.
- 2 × `execute_tool search_docs`, INTERNAL. The conventions prefer that the MCP instrumentation add its attributes
  to this span rather than emit a second client span `tools/call …` (CLIENT); if both exist, set
  `gen_ai.operation.name = execute_tool` on only one, or tool counts and durations double. On the server, a matching
  `tools/call` span of kind SERVER.
- `execute_tool <subagent-tool>`, INTERNAL, with `gen_ai.transfer.*` attributes, containing the sub-agent's own
  `invoke_agent` and `chat` spans when the framework reports the sub-agent as its own entrypoint (otherwise the
  conventions discourage extra spans for the transfer).

The MCP client injects W3C `traceparent`/`tracestate`/`baggage` into the request's `params._meta`. The server
extracts them and uses them as the remote parent, so its span is in the same trace. All of this is OTel GenAI
Development status as of 2026-11, so pin the semconv version you emit.
</details>

### 3. [Core] Content capture policy

Security says "no prompts or tool outputs in the observability backend". Debugging and offline judging need
content for failed runs. Design the policy using the GenAI conventions.

<details><summary>Answer</summary>

- Instrumentation runs with `OTEL_INSTRUMENTATION_GENAI_CAPTURE_CONTENT=NO_CONTENT` (the default), so spans carry
  only metadata: tokens, models, versions, tool names, argument hashes, result sizes and outcome.
- An upload hook writes **redacted** content to a governed store that is encrypted, tenant-partitioned and
  access-controlled, with its own retention and erasure. Spans carry `gen_ai.input.messages_ref` /
  `gen_ai.output.messages_ref` URIs. These must not embed credentials such as signed URLs, and a reference does not
  prove the upload succeeded.
- The hook runs regardless of the span sampling decision, so set content retention separately: for example keep
  content only for runs the keep decision retains, for 30 days, deleted on tenant erasure.
- Deduplicate content by hash, so the per-step history is not stored quadratically.

Acceptable alternative: `EVENT_ONLY` into a log pipeline that already has redaction and retention, noting that GenAI
events are not available in every SDK.
</details>

### 4. [Deep] Tail sampling vs a two-minute agent run

Your collector uses the tail-sampling processor with defaults and a `status_code` ERROR policy plus 10%
probabilistic. Agent runs last 2 minutes on average and up to 30 minutes with approvals. What goes wrong, and what
would you do instead?

<details><summary>Answer</summary>

Defaults: `decision_wait` 30 s, `num_traces` 50,000, and all spans of a trace must reach one collector. After 30 s
the processor decides on the spans it has. Most of a two-minute run, including the final outcome, has not arrived.
Late spans inherit the decision while the trace is buffered. After it leaves memory they are treated as a new trace
unless a decision cache (`sampled_cache_size`) is configured. A run that fails at minute 3 may be dropped, or split
into fragments with different decisions. Also, "failed" for an agent often is not a span ERROR at all.

Better: decide at the **run level**. The agent runtime knows the outcome, cost and step count when the run ends. It
writes all spans to a short-TTL flight recorder, emits a run summary, and promotes kept runs (failed, cost > p95,
budget-exhausted, escalated, any run where a security event fired, plus a 10% random slice with recorded weight)
into the trace backend. Compute metrics from 100% of runs before sampling, and keep the unsampled audit log for tool
calls and policy decisions. Newer collectors offer `sampling_strategy: span-ingest`, but it still cannot see an
outcome the runtime has not written. Raising `decision_wait` to 30 min is a possible alternative: ≈ 200 MB of
serialized spans (a lower bound) per collector at 113 spans/s × 1 KB in the lesson's numbers. Runs paused for hours still escape, though.
</details>

### 5. [Core] pass@k or pass^k?

For each, choose pass@k or pass^k and justify: (a) a coding agent that generates 5 candidate patches, which CI tests
before a human reviews one; (b) a customer-support agent; (c) a research agent where a human picks the best of 3
drafts.

<details><summary>Answer</summary>

- (a) **pass@k**. An automatic verifier (tests) selects a passing candidate, so one success in k is enough, at k×
  the cost.
- (b) **pass^k**. Each customer meets the agent once and expects it to work every time. Consistency is the product.
- (c) **pass@k**, with caveats. A human acts as the selector, so you also pay human time, and the human must be able
  to recognise the good draft. If the drafts go straight to users, switch to pass^k.

At k = 1 both equal the mean success rate. They diverge as k grows: pass@k towards 1, pass^k towards 0.
</details>

### 6. [Deep] Same average, different product

Agent A: on every task, success probability 0.8. Agent B: 80% of tasks always succeed, 20% always fail. Compute
pass@1, pass@4 and pass^4 for both. Then, for one task with n = 8 trials and c = 6 successes, compute the unbiased
pass^4 estimate and compare it with (c/n)⁴.

<details><summary>Answer</summary>

- pass@1: A = 0.8, B = 0.8.
- pass@4: A = 1 − 0.2⁴ ≈ **0.998**. B = 0.8 (the failing 20% never succeed).
- pass^4: A = 0.8⁴ ≈ **0.41**. B = **0.80**.

Unbiased per-task pass^4 = C(6,4)/C(8,4) = 15/70 ≈ **0.214**. The plug-in (6/8)⁴ ≈ 0.316 overstates reliability.
The bias is upward because xᵏ is convex (Jensen's inequality), and it is large at small n. B is the better
customer-facing agent, and its failures are a nameable set of tasks to fix.
</details>

### 7. [Deep] Size the regression gate

Baseline task success is 85%. You want to block changes that lower it by 3 points (80% power, two-sided α = 0.05).
(a) What is the 95% interval on a single run of a 200-task suite? (b) How many tasks per version does an unpaired
comparison need? (c) In an A/A run, 10% of tasks flip outcome between two runs of the same version. How many tasks
does a paired comparison need?

<details><summary>Answer</summary>

(a) SE = √(0.85 × 0.15 / 200) ≈ 0.025, so the interval is about **±4.9 points**. A 3-point drop is invisible.

(b) n ≈ (1.96 + 0.84)² × (0.85·0.15 + 0.82·0.18) / 0.03² ≈ 7.84 × 0.275 / 0.0009 ≈ **2,400 tasks per version**.

(c) Paired differences take values −1/0/+1, so Var ≈ d (discordant share) and SE ≈ √(d/n).
n ≈ 7.84 × 0.10 / 0.0009 ≈ **870 tasks**, so a ~900-task paired gate. This sizes a *significance* test: at n = 900,
SE ≈ √(0.10/900) ≈ 1.05 points, so block when the observed difference is below −1.96 × 1.05 ≈ −2.1 points. That
blocks about 81% of true 3-point drops and 2.5% of neutral changes. A non-inferiority rule ("pass only if the 95%
lower bound is above −3") at the same n swaps the errors: 2.5% of 3-point drops get through, but about 19% of
neutral changes are blocked. Running k = 3 trials per task further cuts
within-task noise, but not between-task variance. Other notes: fix n in advance (no re-running until it passes),
cluster standard errors for related tasks, and never "fix" variance by lowering temperature (Miller 2024). An
acceptable alternative is to gate only at 5–6 points offline and rely on a powered canary for smaller effects.
</details>

### 8. [Core] Grade the outcome or the path?

A refund agent's eval checks that the agent called `lookup_order`, `check_policy`, `issue_refund` in that order. A
new version solves the same tasks by calling `check_policy` first and passes fewer evals. What is wrong with the
grader, and how would you redesign it?

<details><summary>Answer</summary>

The grader prescribes one path. Anthropic calls rigid step-sequence checks "overly brittle", and they punish valid
alternatives. Redesign:

- **End-to-end grader on the end state:** the refund row exists, the amount is within policy, the order is updated,
  and the customer message contains the required facts (τ-bench-style database comparison plus required outputs).
- **Trajectory constraints** only for what must *never* happen or must *always* happen: `issue_refund` never before
  a successful `check_policy` in the same run, no write without approval, steps and cost within budget, no repeated
  identical calls.
- Optionally, a **model-based rubric** for tone, calibrated against human labels.

Also audit the grader: try to pass a task without doing it. An empty reply counted as success is a known benchmark
flaw (ABC checklist on τ-bench).
</details>

### 9. [Deep] Can you trust the judge?

Your team wants an LLM judge to gate releases on "report quality". It agrees with humans 85% of the time on a sample.
List what else you need to know or do before it gates anything.

<details><summary>Answer</summary>

- **Percent agreement is not enough.** Thakur et al. found that judges with high percent agreement can still assign
  very different scores. Report a chance-corrected statistic and the score error, with a confidence interval, per
  task family.
- **Known biases** (Zheng et al. 2023): position, verbosity, self-enhancement, limited reasoning. Swap order,
  control length, use a different model family from the agent, and give reference answers.
- **Hard cases.** JudgeBench (ICLR 2025) found many strong judges only slightly better than random on hard,
  objectively checkable pairs. Test the judge on your hardest cases, not the average.
- **Narrow rubric items** (one question per call), an "unknown" option, and a pinned, versioned judge model and
  prompt. Re-score a frozen reference set whenever either changes.
- **Leniency check.** Seed known-bad outputs and confirm they fail.

Even then, prefer a code grader wherever an outcome is checkable, and keep humans for calibration and new failure
types.
</details>

### 10. [Interview] SLOs for a support agent

Define SLIs and SLOs for a customer-support agent (C15-style) and an alerting scheme. Explain why a 14.4× burn-rate
page on "task success ≥ 85%" is a mistake.

<details><summary>Answer</summary>

SLIs, per tenant, task type and version tuple:

- **Task success**, final outcome (ticket stays closed 7 days), plus a provisional version at run end.
- **Hard-failure rate**: error, timeout, budget exhausted, loop stop.
- **Escalation rate**, split into policy-required and agent-initiated.
- **Cost per resolved task**, including failed and escalated runs.
- **Steps/tool calls p95**, **time to outcome p95**, and tool error and empty-result rate per MCP server.

Example SLOs: hard failures ≤ 1% of runs (28-day); provisional success ≥ 85%; agent-initiated escalation ≤ 10%; cost
per resolved task ≤ a budget.

Burn rate = error ratio ÷ budget, so it is capped at 1/budget. With an 85% target the budget is 0.15, and the burn
rate cannot exceed ≈ 6.7, so a 14.4× page **can never fire**. Use multi-window burn-rate alerts on the
**hard-failure** SLI (budget 0.01, where 14.4× = 14.4% hard failures is meaningful). Use **change detection** on
success: a statistical test against a baseline, by version tuple, with a minimum n. At 1,250 tasks/h, one hour's SE
is ≈ 1 point. Aggregate low-volume tenants for alerting.
</details>

### 11. [Deep] Benchmark hygiene

A vendor pitches its model with "80% on SWE-bench Verified". What do you say, and what do you do instead?

<details><summary>Answer</summary>

As of 2026-11, SWE-bench Verified is not a credible yardstick. OpenAI's February 2026 audit of 138 hard tasks
(27.6%) found material test or problem-statement issues in 59.4% of them. It found evidence that frontier models had
seen problems and gold patches in training, and OpenAI stopped reporting the benchmark, recommending SWE-bench Pro.
Epoch AI (2026-09-03) rated it "Flawed", with all tasks and solutions public and a known reward hack that reaches a
perfect score. A score also belongs to a model *and* scaffold pair.

Instead: shortlist on several recent, contamination-resistant benchmarks if needed (for example the public split of
SWE-bench Pro, which OpenAI recommends; its held-out and commercial splits are not available to run yourself). Decide on **your own** private suite built from your traffic, run in your harness,
with k trials, paired against your current model, and read transcripts. Audit graders on the tasks the best agents
fail.
</details>

### 12. [Lab] (planned) Find the injected fault

*The L32 lab is planned, not yet built.* In the planned lab a scripted agent has three fault switches: loop, empty
tool results, and context loss after compaction. For each, say which metric shows it first (without sampling) and
what you would look for in a trace.

<details><summary>Answer</summary>

- **Loop:** the tail of `gen_ai.invoke_agent.tool_calls`/`inference_calls` and the `budget_exhausted` share rise.
  In the trace: the same `execute_tool` with the same argument hash repeated, with no new information.
- **Empty tool results:** the empty-result rate (`result_count = 0`) for that tool rises while its error rate stays
  flat. In the trace: successful tool spans followed by the model rephrasing the query, or answering without
  evidence.
- **Context loss after compaction:** the compaction rate and p95 input tokens per step rise, and success is lower
  for runs that compact. In the trace: `gen_ai.conversation.compacted = true` followed by repeated earlier work.

No results are given here, because the lab has not been run.
</details>
