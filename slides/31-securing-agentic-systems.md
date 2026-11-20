# 31 — Securing agentic systems (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The requirement
- 2,000 tenants, about 300 first- and third-party MCP tools and skills
- A third-party server can change a tool description tomorrow
- No cross-tenant reads, no unchecked outbound action, every call attributable
- One action stops a bad agent version everywhere within 60 s

**Visual:** Lumen platform box with 300 tool icons around it, three marked third-party. Icons: ai-agent, ai-mcp, ai-tool, arch-users.
**Speaker notes:** This chapter builds on 28 (injection, OWASP, taint, patterns) and 25 (runtime, sandbox) and does
not repeat them. The question here is the platform as a system to threat-model.

## Slide 2 — 2025–2026: the surface became real
- Tool poisoning, shadowing, rug pulls (Invariant Labs, April 2025)
- GitHub MCP "toxic agent flow": private data into a public PR (May 2025)
- CVE-2025-6514 in mcp-remote; EchoLeak (CVE-2025-32711)
- `postmark-mcp` backdoor at 1.0.16; ClawHavoc: 341 of 2,857 ClawHub skills malicious (reported)

**Visual:** Timeline April 2025 → February 2026 with six dated markers. Icons: security-bug, ai-mcp, domain-email.
**Speaker notes:** Every item is a published advisory or report. The GitHub case was not a server bug; it was an
architectural combination. ClawHavoc counts come via press reporting of a vendor audit.

## Slide 3 — Lethal trifecta and the Rule of Two
- Willison: private data + untrusted content + external communication
- Meta: no more than two of [A] untrusted input, [B] sensitive data, [C] change state or communicate
- All three needed and not splittable → supervision, not autonomy
- Meta's own limits: not sufficient for other threats, still needs least privilege

**Visual:** Rule-of-Two decision flowchart from the lesson. Icons: security-threat-model, ops-human-approval.
**Speaker notes:** The Rule of Two widens [C] from "communicate" to "change state", which matters for agents that
delete or merge. The session is the unit, because the context window carries influence forward.

## Slide 4 — Inventory, don't sloganize
- List every workflow, mark A, B, C
- Often missed [A]: tool descriptions, tool results, skills, repo config
- Often missed [C]: "read" tools with free-form queries, rendered images
- Fresh-context session splits are a real control

**Visual:** Three-column table A/B/C with ticks per workflow. Icons: security-threat-model, domain-document.
**Speaker notes:** The deliverable of a security review is this table with a verdict per row.

## Slide 5 — Tool trust tiers and capability scoping
- A tool brings code, a description and results, each with its own trust
- Tiers: T0 first-party, T1 vetted and pinned, T2 remote unpinned, T3 tenant or community
- Scope at three layers: what the model sees, what the broker executes, what the token allows
- Annotations such as `readOnlyHint` are hints, never policy inputs

**Visual:** Four stacked tier bands; three concentric scoping rings. Icons: ai-tool, arch-policy-engine, security-token.
**Speaker notes:** The MCP schema says clients should never make tool use decisions based on annotations from
untrusted servers. Classify tools yourself by what leaves the system.

## Slide 6 — The MCP and skills supply chain
- Poisoning, shadowing, rug pull, impersonation and typosquatting
- Install-time execution: startup commands, skill "prerequisites"
- MCPTox: 1,348 cases on 45 servers, refusals under 3% for the best model tested
- Skills: `allowed-tools` is experimental and widens, never sandboxes

**Visual:** Attack-class table with an evidence column. Icons: security-bug, security-sbom, ai-mcp.
**Speaker notes:** Model refusals are not a control. A skill is code plus a prompt, so admit it as both.

## Slide 7 — The admission pipeline
- Verify publisher (MCP Registry namespaces: who, not whether safe)
- Pin digest or version, sign and verify like images
- Hash each description and input schema; serve only registered hashes
- Mismatch at runtime → quarantine that tool, review the diff

**Visual:** Admission flowchart from the lesson. Icons: security-sigstore, arch-policy-engine, ops-check.
**Speaker notes:** The registry delegates security scanning to package registries and aggregators. The hash diff is
the rug-pull control; it cannot catch behavior changes that leave the description alone.

## Slide 8 — Confused deputies and token passthrough
- OAuth proxy deputy: static client ID + DCR + consent cookie → per-client consent MUST
- Token passthrough: servers MUST NOT accept tokens not issued for them
- SSRF during discovery: block private and link-local ranges, use an egress proxy
- State handles are not authentication: key by verified user

**Visual:** Sequence sketch: client → MCP proxy → third-party auth server, with the skipped consent screen crossed out. Icons: security-oauth, security-token, arch-egress.
**Speaker notes:** All of these are normative text in MCP's 2026-07-28 security best practices. Identity and
delegation chains live in SYSDESIGN-18.

## Slide 9 — Containment architecture
- Sandbox tier chosen by who wrote the code
- Stated limits: gVisor no hardware side-channel protection; Firecracker cannot mitigate host hardware flaws
- Egress default deny, allow at path or org, DNS via proxy, metadata blocked
- Credential broker hides the token, not its authority: scope per task

**Visual:** Containment flowchart from the lesson. Icons: arch-sandbox, arch-egress, devops-vault, arch-firewall.
**Speaker notes:** An allow-listed public host is still an exfiltration path, which is the GitHub MCP lesson.
Per-task tokens shrink exposure from 16,000 to 0.5 repository-hours under the lesson's assumptions.

## Slide 10 — Patterns, judged by evidence
- Plan-then-execute: fixes which tools run, not the data flowing through
- Dual LLM: privileged model sees only variable names; complexity and social engineering remain
- CaMeL: 77% of AgentDojo tasks with provable security vs 84% undefended (v2)
- Adaptive attacks bypassed 12 defenses at >90% success for most

**Visual:** Four-row comparison table: guarantee, gap, cost. Icons: ai-guardrail, ai-evaluation.
**Speaker notes:** Prefer guarantees that are checkable system properties over detection rates.

## Slide 11 — Approvals that people actually read
- Naive gating: 150,000 approvals a day (assumed load)
- Plan-level approval plus destination binding: about 5,600
- Render from the structured call, never from the model's words
- Mediation helps, but measured misses exist (17% on 52 real overeager actions, one product)

**Visual:** Funnel 150,000 → 18,750 → 5,600. Icons: ops-human-approval, ops-dashboard.
**Speaker notes:** Users accepted 93% of permission prompts in Anthropic's measurement (vendor measurement, one product). Structure, not faster
clicking, makes the gate mean something.

## Slide 12 — Detect and stop
- Signals: hash mismatch, new egress destination, denial spikes, canary use, spend velocity
- Kill switch levels: session, agent version, tool, tenant, global
- Enforce at broker, gateway, proxy, credential broker, queue: not in the loop
- Security events go to their own stream at 100%; traces are sampled, the audit log is the complete record
- Worst case 40 s under the lesson's assumptions; freeze and preserve evidence

**Visual:** Timeline: detect → deny at broker and proxy → revoke → freeze → regress. Icons: ops-alert, ops-incident, security-lock.
**Speaker notes:** Canaries give near-zero false positives, so automatic stops can hang on them. Drill the stop time.

## Slide 13 — Red team and tenancy
- ATLAS 2026.10 agent techniques (T0051, T0086, T0110 …) and case studies
- OWASP ASI01–ASI10 as coverage checklist; AgentDojo and MCPTox as a floor
- Per-tenant sandboxes, caches (`cacheScope` only on list and read results, never share `tools/call` results), handles, memory, credentials, quotas
- Interview: CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP

**Visual:** Matrix of tenants × shared components with every cell isolated. Icons: arch-cell, security-threat-model, ai-evaluation.
**Speaker notes:** Pin catalog versions in the test plan. Red flags in interviews: a classifier as the boundary,
annotation-based auto-approval, token forwarding, shared caches.
