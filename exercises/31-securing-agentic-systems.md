# 31 — Exercises

Lesson: [course/03-ai-systems/31-securing-agentic-systems.md](../course/03-ai-systems/31-securing-agentic-systems.md)

## 1. [Core] Count the properties

For each workflow, mark Meta's Rule-of-Two properties [A] untrusted input, [B] sensitive data or systems, [C]
change state or communicate externally, and give the verdict. (a) A meeting-notes agent reads the user's own
calendar and writes notes into the user's private notebook. (b) A recruiting agent reads applicants' CVs, queries
the internal salary bands and emails candidates. (c) A coding agent reads a public issue, edits code in a sandbox
with no network, and returns a diff to the requester. (d) A web-research agent with no connectors fetches pages and
writes a report to the requester.

<details><summary>Answer</summary>

(a) Calendar invites can carry text from outside senders, so [A] is present more often than people assume; [B]
yes (calendar, notebook); [C] writing to a notebook *only the user reads* is a state change. Strictly that is all
three, but the impact of [C] is confined to the requester. A pragmatic design treats invite descriptions as [A],
writes notes as a draft, and never lets this session send anything.
(b) [A] CVs, [B] salary bands, [C] email: **all three**. Split it: a tool-less extraction step turns each CV into
typed fields; the session that reads salary bands never sees CV text; emails come from templates and are approved.
(c) [A] issue, [B] the private repository, [C] none if the sandbox has no network and the output is a diff for the
requester. Two properties: allowed. It becomes three the moment the agent can push, comment or reach the network.
(d) [A] web pages and [C] the fetch tool itself (a free-form URL or query is outbound). No [B]: allowed, as long
as the session truly has no connectors, no memory write and no access to the user's files. The user's own prompt
is the one sensitive input left, and it can still reach a fetch URL, so keep secrets out of it and log destinations.
</details>

## 2. [Core] Trifecta versus Rule of Two

An agent reads support tickets from the public and can close, merge and delete tickets, but it has no tool that
sends anything outside the company and reads no private data beyond the tickets. Is it safe under the lethal
trifecta? Under the Rule of Two?

<details><summary>Answer</summary>

Under the trifecta, it lacks "the ability to externally communicate" and arguably private data, so exfiltration
is unlikely. Under the Rule of Two, [A] (public tickets) and [C] (it **changes state**: deletes and merges) are
both present; with tickets as [B] (they are internal records) it holds all three. An injected ticket can make the
agent delete other tickets. That is the point of Meta's broader [C]: damage without exfiltration. Fixes: restrict
destructive actions to the ticket being processed, require approval for deletes, or run triage in a session that
can only label.
</details>

## 3. [Core] Annotations are hints

A third-party MCP server marks its `sync_notes` tool with `readOnlyHint: true` and `openWorldHint: false`. Your
broker's policy auto-approves read-only, closed-world tools. What is wrong, and what should the policy use instead?

<details><summary>Answer</summary>

In the MCP 2026-07-28 schema, annotations are hints, "not guaranteed to provide a faithful description of tool
behavior", and clients should never base tool-use decisions on annotations from untrusted servers. The server
controls those flags, so a malicious one labels its exfiltration tool read-only. The policy should use Lumen's own
classification in the tool registry (tier, data it can reach, whether its arguments can reach an outside
destination), set at admission and re-checked when the description hash changes. Annotations can be shown to
reviewers as a claim to verify.
</details>

## 4. [Core] Rug pull at the gateway

A pinned T1 server returns a new description for one of its four tools on Tuesday. Describe exactly what the
gateway does, what the user sees, and what you would *not* do.

<details><summary>Answer</summary>

The gateway compares the served description and input-schema hash with the registered hash, finds a mismatch for
one tool, and quarantines that tool only: it is removed from the filtered `tools/list` for every agent, and calls to
it are denied. It opens a review with the text diff, and emits a detection event. Users see that the tool is
temporarily unavailable; the other three tools keep working. You would not silently accept the new text, and you
would not rely on the server's `notifications/tools/list_changed`, because a malicious server need not send it. If
the change is benign, the reviewer re-registers the new hash; if not, the server drops to a lower tier or is
removed. Note the limit: a hash detects description changes, not behavior changes in the server's code.
</details>

## 5. [Deep] Confused deputy in an OAuth proxy

Lumen's MCP server fronts a third-party calendar API with one static OAuth client ID and supports dynamic client
registration. List the conditions that make it exploitable and the controls the MCP best practices require.

<details><summary>Answer</summary>

Exploitable when all hold: a **static client ID** at the third-party authorization server; **dynamic registration**
of MCP clients (each gets its own `client_id`, possibly with an attacker's redirect URI); the third-party server
sets a **consent cookie**; and the proxy does **not** do per-client consent before forwarding. The attacker
registers a client, sends the user a link, the cookie skips consent, and the MCP authorization code goes to the
attacker. Required controls: per-client consent (a registry of approved `client_id` values per user, checked before
the third-party flow), a consent page that names the client, scopes and redirect URI with CSRF and anti-framing
protection, exact redirect-URI matching, signed `__Host-` consent cookies bound to the client ID, and a single-use,
short-lived `state` set only after consent. Note that DCR is deprecated in 2026-07-28 but the attack still applies
where it is supported.
</details>

## 6. [Core] Token passthrough

A developer proposes that the CRM MCP server forward the user's access token, received from the agent, straight to
the CRM's REST API "to keep it simple". Give three concrete harms and the fix.

<details><summary>Answer</summary>

(1) **Control bypass:** downstream rate limits and policies that depend on the token's audience no longer apply as
designed. (2) **Audit confusion:** the CRM logs show the user's token, not the MCP server, so investigations cannot
tell which component made the call. (3) **Cross-service replay:** a token accepted by several services lets an
attacker who compromises one use it at others, and the MCP server becomes a proxy for a stolen token. The MCP rule
is that servers "MUST NOT accept any tokens that were not explicitly issued for the MCP server". Fix: the MCP server
validates that the token's audience is itself, then obtains a new token for the CRM by token exchange, carrying the
user as subject and the server as actor (SYSDESIGN-18).
</details>

## 7. [Deep] Proxy-injected credentials

Lumen's egress proxy injects a GitHub token for every request from a coding sandbox. The token covers all of the
tenant's repositories with `contents:write`. An injected agent asks the proxy to push to another repository. Does
credential brokering help? Redesign it.

<details><summary>Answer</summary>

Brokering kept the token out of the sandbox, so it cannot be stolen and reused later, but the proxy still *uses*
it for the hijacked agent: the push succeeds. Brokering hides the credential, not its authority. Redesign: mint a
per-task token for one repository and push to the task branch only, valid for the task's lifetime (say 30 minutes),
bound to the sandbox's workload identity; the proxy allow-lists the one repository path, not the host; the broker
logs every injection with the task ID and refuses to inject once the kill switch fires. With the lesson's
assumptions, exposure drops from 16,000 repository-hours to 0.5.
</details>

## 8. [Core] Approval arithmetic

Using the lesson's assumptions (1.2 M tool calls a day, 25% outbound-capable or state-changing, half in tainted
sessions, 10 s per approval), compute the naive approval load. Then apply plan-level approval with 8 outbound calls
per task and destination binding that removes 70% of the rest. What do you conclude?

<details><summary>Answer</summary>

Naive: 1,200,000 × 0.25 × 0.5 = 150,000 approvals a day; × 10 s = 1.5 M s ≈ 417 person-hours a day, about 75 per
tenant across 2,000 tenants. Redesigned: 150,000 / 8 = 18,750; × 0.3 ≈ 5,600 a day, under 3 per tenant.
Conclusion: approval quality comes from structure (fixed plans, bound arguments, narrow destinations) that removes
most decisions, so the few that remain get real attention. Anthropic's report that users accept 93% of
permission prompts (vendor measurement, one product) shows what happens otherwise. Alternatives such as classifier mediation can cut
the load further but have measured miss rates, so keep deterministic limits behind them.
</details>

## 9. [Deep] Kill switch design

Design a kill switch that stops one agent version across all tenants within 60 seconds. Which components enforce
it, what is the worst-case stop time under the lesson's assumptions, and what must you preserve?

<details><summary>Answer</summary>

Enforcement points outside the agent loop: the tool broker denies calls for the version, the MCP gateway stops
serving its tools, the egress proxy drops its traffic, the credential broker refuses to inject and revokes
delegated tokens, the run queue stops dispatching, and sandboxes are frozen. Delivery: a revocation topic with a
10 s polling fallback. Worst case for new external effects: 10 s propagation + 30 s for an in-flight tool call to
time out = 40 s, inside 60 s; token TTL does not matter because the injectors stop. Preserve evidence: snapshot
sandboxes, stop memory writes, keep traces and audit records, then turn the incident into a regression test. A
flag the agent loop reads between steps is not acceptable: one long step blows the budget, and a hijacked agent is
the component you trust least.
</details>

## 10. [Deep] Cross-tenant cache

Lumen's gateway caches `resources/read` results for 5 minutes, keyed by server, resource URI and arguments. A T3
server returns `cacheScope: "public"` for a resource that contains a tenant's customer list. What goes wrong and
how do you fix it?

<details><summary>Answer</summary>

In the 2026-07-28 schema, `"public"` means the response holds no user-specific data and may be served across
authorization contexts, while `"private"` responses must not be shared across authorization contexts. A cache
keyed without the authorization context, trusting the server's `"public"` label, serves tenant A's customer list
to tenant B's request for the same URI. Fixes: key caches by authorization context (tenant, user or token) by
default; honor `"public"` only for servers whose data classification Lumen has verified (T0, maybe T1);
never share caches across tenants for T2 or T3 servers; and plant per-tenant canary records to detect leaks. Note
that the hint exists only on list, `resources/read` and discovery results: `tools/call` results carry no
`cacheScope`, so a gateway must never share them across tenants at all.
</details>

## 11. [Interview] Third-party tools on an agent platform

"Customers can connect any MCP server to their agents. A server changes its tool description to steal data. Walk
me through what happens on your platform." Outline a strong answer.

<details><summary>Answer</summary>

CLARIFY which servers customers can connect (registry only, or any URL) and what data agents hold. QUANTIFY tools,
change rate and review cost. SKETCH: admission (verified publisher, pinned digest or version, sandboxed trial,
description and schema hashes, trust tier), gateway that serves only registered hashes, broker with default-deny
argument-aware policy, egress proxy with per-tenant allow-lists, credential broker, per-tenant sandboxes for
tenant-supplied servers, audit log. DEEPEN: at runtime the hash mismatch quarantines the tool before the model sees
the new text; even if a poisoned description had reached the model, the Rule-of-Two inventory, recipient binding
and egress allow-list limit what it can do; no token passthrough. STRESS: a change in server *behavior* without a
description change (detect by egress and canaries), adaptive injection in tool results, kill switch. WRAP: name the
residual risks. Red flags: relying on annotations, a classifier as the boundary, one shared cache or sandbox pool.
</details>

## 12. [Deep] Red-team plan

Draft the top of a red-team plan for Lumen's Account Assistant using MITRE ATLAS and the OWASP Agentic Top 10.

<details><summary>Answer</summary>

Pin the catalog versions (ATLAS content 2026.10; OWASP Agentic Top 10 for 2026). For each workflow, list the
properties it holds and attempt to obtain the missing one: inject through email (AML.T0051, ASI01) to trigger an
outbound call (AML.T0086, ASI02); change a pinned tool's description in staging (AML.T0110, ASI04) and expect
quarantine; plant "remember this" text (AML.T0080, ASI06) and expect blocked memory writes; look for credentials in
agent config (AML.T0083, ASI03); induce a loop (AML.T0034.002, ASI08/ASI10) and expect budget stops. Use AgentDojo
and MCPTox as a baseline, then custom fixtures; report attack success alongside task utility; include adaptive
attacks with full knowledge of prompts and policy; drill the kill switch and record stop time. Every finding becomes
a regression case gating releases.
</details>
