# 18 — Exercises

Companion to [course/02-modern-requirements/18-security-by-design.md](../course/02-modern-requirements/18-security-by-design.md).
Numbers marked "assumption" are illustrative, not measurements.

## 1. STRIDE on a RAG query path [Core]

Lumen's query path is: browser → API gateway → chat service → retrieval service → vector store (shared by all
tenants, partitioned by tenant) → LLM serving. Draw the trust boundaries and give one STRIDE threat and one control
for at least four of the six letters.

<details><summary>Answer</summary>

Trust boundaries: internet→gateway; gateway→internal mesh; retrieval→vector store (data store boundary); service→LLM
serving (model boundary); tenant A data → tenant B data (logical boundary inside the store).

- **S**: a pod impersonates the retrieval service to the vector store → X.509-SVIDs + mTLS, and the store authorises
  `spiffe://…/retrieval` only.
- **T**: tampered image of the retrieval service → signed images, admission policy that verifies signer identity and
  provenance.
- **R**: an admin deletes a tenant index and denies it → append-only audit log in a separate account, with the
  admin's identity from the IdP.
- **I**: retrieval returns another tenant's chunks → tenant ID taken from the verified token, enforced as a mandatory
  partition/filter at the store's enforcement point (pre-filter), plus cross-tenant tests in CI.
- **D**: one tenant floods retrieval → per-tenant quotas and rate limits, bulkheads per tier.
- **E**: prompt-injected agent calls an admin tool → tool router authorises per tool with least-privilege, audience-bound
  tokens.

Acceptable alternatives: any threat correctly mapped to the property it violates, with a control at the boundary
where the threat crosses.
</details>

## 2. ID token or access token? [Core]

A front-end team sends the OIDC ID token as `Authorization: Bearer` to the Lumen API "because it already has the user's
email". What is wrong, and what should change?

<details><summary>Answer</summary>

The ID token's audience (`aud`) is the client, not the API; it asserts that authentication happened and is meant to be
consumed by the client [OIDC Core]. Using it at the API means the API either skips audience validation (so any ID
token for any client of that IdP could be replayed) or accepts a token not designed to carry API scopes. Fix: request
an access token whose audience is the Lumen API (with scopes), have the API validate `iss`, `aud`, `exp`, scopes and
tenant claim, and obtain user attributes from claims in the access token or a userinfo call. RFC 9700 also recommends
audience-restricted, ideally sender-constrained, access tokens.
</details>

## 3. Revocation lag versus authorisation-server load [Core]

The gateway receives 20,000 requests/s; each fans out to 5 internal calls. Compare (a) introspecting every token at
every hop with (b) local JWT validation with a 15-minute token lifetime. Propose a design that keeps revocation lag
under 5 minutes without loading the authorisation server.

<details><summary>Answer</summary>

(a) 100,000 introspection calls/s (RFC 7662) reach the AS, plus one network round trip at every hop; the AS becomes a
tier-0 bottleneck. Revocation is immediate.

(b) Near-zero AS load; each hop verifies a signature with cached keys. A revoked token stays valid up to 15 minutes.

Design: shorten access tokens to ≤ 5 minutes (refresh tokens handle the user experience; refresh is where revocation is
checked); validate once at the edge; inside the mesh, carry user context in a short-lived internal token obtained by
token exchange (RFC 8693) with the downstream audience, verified locally. Optionally push a small deny-list of
revoked session IDs to PEPs for high-risk events. Load on the AS becomes proportional to refreshes (users/5 min), not
to requests.
</details>

## 4. Certificate rotation load [Deep]

Lumen runs 12,000 workloads across 3 clusters with one SPIRE deployment per cluster. You want 15-minute X.509-SVIDs.
Assume rotation at half-life. What signing rate does each SPIRE server need, and what is the real risk of this design?

<details><summary>Answer</summary>

Per cluster: 4,000 workloads / (7.5 × 60 s = 450 s) ≈ 8.9 signatures/s. Even with a 10× burst after a mass restart,
roughly 90/s — small for a CA. The real risk is availability: if the SPIRE server (or its upstream CA) is down longer
than the remaining SVID lifetime, workloads cannot renew and mTLS fails fleet-wide. Mitigations: HA SPIRE servers with
a shared datastore, alerts on remaining-lifetime percentiles, lifetimes long enough to ride out a realistic outage
(trade-off with exposure window), and staged trust-bundle rollover.
</details>

## 5. Choose an isolation rung [Interview]

Lumen will let tenants upload Python "skills" that its AI agent runs on retrieved documents. Interviewer: "Why not just
a namespace per tenant?" Answer in five sentences and name the cost you accept.

<details><summary>Answer</summary>

Tenant code is untrusted, and a namespace boundary still shares the host kernel, so one kernel exploit crosses
tenants; with ~40 pods per node (assumption) that could mean ~40 tenants per escape. I would run skills in a sandboxed
runtime — gVisor (`runsc`) for syscall-light Python, or a Firecracker/Kata microVM if skills need broad Linux
compatibility — on a dedicated node pool, with no service-account token mounted, default-deny egress and per-execution
time/memory budgets. Credentials, if any, are short-lived and scoped to that tenant's data. Results return through a
narrow API, never via shared volumes. The costs I accept are per-syscall overhead (gVisor) or VM start and memory
overhead (microVMs), lower packing density and a separate node pool. Acceptable alternative: a per-tenant cluster for
regulated tenants, priced as a premium tier.
</details>

## 6. xz-utils: which control, when? [Deep]

For CVE-2024-3094, classify each control as helping *before disclosure*, *after disclosure*, or *not at all*: SBOM,
cosign signature on the tarball, SLSA provenance stating the git commit, reproducible build compared against the
tarball, CPU/latency observability on sshd.

<details><summary>Answer</summary>

- **SBOM**: after — instant inventory of hosts with xz 5.6.0/5.6.1.
- **Signature**: not at all for prevention — the release came from a legitimate maintainer identity; a signature
  proves who, not intent. It does help after, to confirm which artefacts are genuine.
- **Provenance from git**: before — part of the injection logic was in the release tarball but not in git, so a policy
  of building only from the attested commit removes that channel (though the disguised test files were in git, so it
  is not a complete defence).
- **Reproducible build / diff**: before — a rebuild from git would not match the tarball's contents.
- **Observability**: before — this is how it was actually found: slow, CPU-heavy SSH logins and valgrind errors.
</details>

## 7. SLSA level for Lumen's CI [Deep]

Lumen builds images on self-hosted runners that are reused between jobs; the signing key is a repository secret
available to all workflow steps. Which SLSA Build level does this reach at best, and what would L3 require?

<details><summary>Answer</summary>

If provenance is generated automatically and distributed, L1. If a hosted platform signs the provenance and consumers
verify it, L2. L3 is not met: SLSA v1.2 Build L3 requires that runs cannot influence each other (reused runners leak
state between jobs) and that signing secrets are not accessible to user-defined build steps (a repo secret available to
every step violates this). Fix: ephemeral, isolated runners per job; signing performed by the platform (e.g. keyless
signing with a workload identity token, or a separate signing service), never by user steps.
</details>

## 8. The CRA 24-hour drill [Interview]

You are told at 09:00 that a library Lumen ships in its on-premise connector is being actively exploited. List what
must already exist in your architecture to meet Article 14 of the CRA, and the three deadlines.

<details><summary>Answer</summary>

Deadlines (Art. 14(2)): early warning within 24 hours of becoming aware; vulnerability notification within 72 hours;
final report no later than 14 days after a corrective or mitigating measure is available; submitted via the ENISA
Single Reporting Platform (live since 11 September 2026).

Must already exist: (1) SBOMs for every shipped version, queryable by component and version; (2) a mapping from version
to customers/deployments; (3) telemetry or customer channels to confirm exploitation; (4) a named security owner and
on-call rotation; (5) a rebuild-and-release pipeline that can ship a fix quickly, with signed artefacts; (6) templates
for the notifications. Without SBOM inventory the 24-hour clock is mostly spent finding out whether you are affected.
</details>

## 9. Token passthrough in an agent [Deep]

Lumen's agent receives a user's access token for the Lumen API and forwards it unchanged to a customer's MCP tool
server. Name two problems and the fix.

<details><summary>Answer</summary>

(1) The token's audience is the Lumen API; if the tool server accepts it, it is not validating `aud`, and anyone who
steals tokens for Lumen can use them at the tool server. (2) Confused deputy: the tool server cannot tell whether the
agent validated the token, and the downstream may trust it as if the agent vouched for it; it also hands a third
party a credential usable against Lumen. Fix: the MCP authorization spec (revision 2026-07-28) says servers "MUST NOT accept or transit any other tokens" and
clients must send only tokens issued by the MCP server's own authorisation server, so passthrough is forbidden; obtain a new token for the
tool server's audience (RFC 8707 resource indicator, or RFC 8693 token exchange carrying `act` = agent), scoped to the
tool's needs and short-lived.
</details>

## 10. Kubernetes Secrets review [Core]

A team stores the vector-store admin password in a Kubernetes Secret in a namespace where 30 developers can create
Deployments. Encryption at rest is not configured. What are the exposures and the fixes, in priority order?

<details><summary>Answer</summary>

Exposures: anyone with etcd or backup access reads it in plaintext (Secrets are unencrypted in etcd by default);
anyone who can create a pod or Deployment in the namespace can mount and read it; the password is shared and static.
Fixes in order: (1) replace with dynamic, per-service database credentials (e.g. Vault database engine leases) or
workload-identity-based auth, so there is no shared admin password; (2) restrict who can create workloads in that
namespace and separate admin tooling; (3) enable encryption at rest with a KMS provider; (4) consider an external
secret store via the Secrets Store CSI driver; (5) rotate the current password now, assuming it is compromised.
</details>

## 11. Read a delegation chain [Deep]

A Lumen document API receives this token (claims only): `sub` = `alice@acme.example.com`, `tenant` = `acme`,
`aud` = the document API, `scope` = `docs.read`, `exp` in 4 minutes, and
`act` = `{ "sub": "spiffe://lumen.example.org/agent/summariser", "act": { "sub": "spiffe://lumen.example.org/agent/assistant" } }`.
(a) Who is the subject, who is the current actor, and who is a prior actor? (b) Acme's policy says "no
third-party agent may appear anywhere in a chain that reads Acme documents". Can the document API enforce it from
this token? (c) Is this delegation or impersonation?

<details><summary>Answer</summary>

(a) Subject: Alice of tenant Acme. Current actor: the summariser (the outermost `act`). Prior actor: the assistant
(nested `act`). (b) Not reliably at the resource server. RFC 8693 says prior actors in nested `act` claims "are
informational only" and are not to be considered in access-control decisions, so a conforming API authorises on
`sub` plus the current actor. Enforce chain-wide rules at the token service, which sees every exchange and can refuse
to mint a token when any hop breaks policy (for example via a per-user allow-list in the spirit of `may_act`). The
API should still log the full chain for audit. (c) Delegation: the agent is named as actor and keeps its own
identity. Impersonation would show `sub` = Alice and no `act`, which erases the agent from every log, the mode to
avoid for agents. Acceptable alternative for (b): the API may apply an *extra* local deny on nested actors as
defence in depth, but it must not rely on that as the primary control, because it departs from RFC 8693 semantics.
</details>

## 12. Design the CRM hop [Deep]

Lumen's assistant, acting for Alice, must call a CRM MCP server run by a third party for Acme, with its own
authorisation server. An engineer proposes: "Forward the Lumen access token we already have, the CRM can call our
introspection endpoint." Give two reasons this fails the 2026-07-28 MCP rules, then design the hop using current
IETF work, stating which documents are drafts.

<details><summary>Answer</summary>

Why it fails: (1) the token's audience is Lumen, not the CRM MCP server; MCP servers "MUST validate that access tokens
were issued specifically for them" and "MUST NOT accept or transit any other tokens", and clients must send only
tokens issued by the MCP server's own authorisation server. (2) It is token passthrough: a stolen Lumen token becomes
usable at the CRM, the CRM's own policy and rate limits are bypassed, and its audit shows the wrong caller. It also
makes the CRM depend on Lumen's AS, which is in another trust domain.

Design: Alice signed in to Lumen through Acme's enterprise IdP, so Lumen holds an IdP-issued ID token or refresh
token. The agent runtime (not the model) sends it to Acme's IdP in an RFC 8693 token exchange requesting an ID-JAG
for the CRM's authorisation server. Acme's IdP evaluates administrator policy ("may `lumen-agent` reach this CRM for
Alice?") and returns the ID-JAG. The runtime redeems it at the CRM AS with the RFC 7523 `jwt-bearer` grant (or the
DPoP-bound variant) and receives a short-lived token whose audience is the CRM MCP server, scoped to the task (say
`contacts.read`). Status: ID-JAG is draft-ietf-oauth-identity-assertion-authz-grant-06 (31 October 2026), an IETF
working-group draft; the general cross-domain pattern is draft-ietf-oauth-identity-chaining-17 (19 July 2026, in the
RFC Editor queue, not yet an RFC). MCP's Enterprise-Managed Authorization extension (stable, 2026-07-28) profiles
ID-JAG but cites revision -04, so check the differences. Acceptable alternative: if Acme has no IdP that supports
ID-JAG, an interactive OAuth flow per user against the CRM AS with RFC 8707 resource indicators, at the cost of a
consent screen per user and no central enterprise policy.
</details>

## 13. Revoke a hijacked agent [Interview]

At 02:00 monitoring shows the summariser agent build 42 issuing unusual document reads across many Acme users. Lumen
uses per-hop RFC 8693 exchange with 5-minute tokens, sender-constrained with DPoP, and the token service logs every
exchange. What do you do in the first ten minutes, what is the worst-case window, and what can you prove by morning?

<details><summary>Answer</summary>

First minutes: stop the token service from minting for `spiffe://lumen.example.org/agent/summariser` (or only build
42 if the identity encodes the version). No new hop succeeds from that moment. Tokens already issued expire within
5 minutes, so the worst-case window after the deny is about 5 minutes, and DPoP binding means a token copied out of the
runtime is not usable from elsewhere. If the agent may hold user refresh tokens, revoke those grants (RFC 7009: revoking
a refresh token SHOULD also invalidate access tokens from the same grant when the server supports it). Also stop the
agent's pods, but do not rely on that alone: the identity deny is what blocks every enforcement point at once.

By morning: join the token service's exchange records (`jti`, parent `jti`, `sub`, tenant, full actor chain, audience,
scope, policy decision, agent version) with the document API's accepted-`jti` log. That lists every user, document
scope and parent agent involved, from logs the agent could not write. Why per-hop exchange helps: a single long-lived
service-account token would have no per-user subject, no actor chain and a much longer window. Follow-ups: tie this to
the kill-switch design in [SYSDESIGN-31](../course/03-ai-systems/31-securing-agentic-systems.md) and add the case to the
red-team regression suite.
</details>
