# 18 — Security by design (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Source lesson: [course/02-modern-requirements/18-security-by-design.md](../course/02-modern-requirements/18-security-by-design.md)

## Slide 1 — The requirement

- Lumen: 2,000 enterprise tenants on shared Kubernetes
- One compromised pod, leaked credential or poisoned dependency must not cross tenants
- Every production binary traceable to reviewed source
- EU sales: 24-hour early warning for actively exploited vulnerabilities from 11 Sep 2026 (CRA Art. 14)

**Visual:** Lumen box with three attack arrows (pod, key, dependency) stopping at a tenant wall. Icons: arch-servers-cluster, security-key, security-bug, devops-kubernetes.

**Speaker notes:** The attacker needs one weak link, and the links include code you did not write and machines you do not own. This chapter turns that into concrete boxes, each with a reason.

## Slide 2 — Threat model before controls

- Data-flow diagram + trust boundaries
- STRIDE: Spoofing, Tampering, Repudiation, Information disclosure, DoS, Elevation of privilege
- Origin: Kohnfelder & Garg, Microsoft, 1999
- Output = requirements with owners, not a document

**Visual:** DFD with dashed trust boundaries; STRIDE letters tagged on each crossing. Icons: arch-user, arch-api-gateway, arch-database.

**Speaker notes:** Every control in the rest of the deck answers one STRIDE letter at one boundary. If a control answers none, ask why it is there.

## Slide 3 — Zero trust (NIST SP 800-207)

- Network location alone does not imply trust
- Per-session, least-privilege access decided by dynamic policy
- Policy decision point (engine + administrator) vs policy enforcement point
- PEPs in Lumen: gateway, mesh sidecar, DB proxy, admission controller, agent tool router

**Visual:** Subject → PEP → PDP (identity, posture, policy stores) → resource; audit log tap. Icons: security-authorization, arch-api-gateway, ops-logs.

**Speaker notes:** The useful idea is separating decision from enforcement. Then the design question becomes where the PDP lives: central and fresh, or embedded and fast.

## Slide 4 — Authn is not authz

- Authentication: who is calling
- Authorisation: may this identity do this action on this resource now
- OWASP Top 10:2025 A01 = Broken Access Control
- Models: ACL → RBAC → ABAC → ReBAC (Zanzibar: p95 < 10 ms, > 99.999% availability)

**Visual:** Two gates in sequence: "who?" then "may?"; a valid tenant-A token blocked at tenant-B data. Icons: security-auth, security-authorization.

**Speaker notes:** The classic multi-tenant bug is a valid token plus an endpoint that reads tenant_id from the URL. Authentication succeeded; authorisation never happened.

## Slide 5 — OAuth 2.0 + OIDC, the 2025 floor

- OAuth = delegation (access token); OIDC = identity layer (ID token: iss, sub, aud, exp, iat)
- RFC 9700 (BCP 240, Jan 2025): code flow + PKCE; no password grant; exact redirect URI match
- Sender-constrained tokens (mTLS RFC 8705, DPoP RFC 9449), audience restriction
- OAuth 2.1 still an Internet-Draft (as of 2026-11)

**Visual:** Sequence: client → AS (code_challenge) → code → token exchange with verifier → API validates aud. Icons: security-oauth, security-jwt, security-token.

**Speaker notes:** ID tokens are for the client, access tokens are for APIs. Deep dives on Keycloak and flows live in the companion course MSKazemi/security.

## Slide 6 — Workload identity: SPIFFE/SPIRE + mTLS

- SPIFFE ID: spiffe://trust-domain/path
- X.509-SVID (preferred) or JWT-SVID, from the Workload API, rotated automatically
- SPIRE: node attestation + workload attestation; CNCF graduated 2022
- mTLS authenticates workloads, not users; still needs authz policy

**Visual:** SPIRE server → node agent → pods over Unix socket; pods talk mTLS. Icons: security-encryption, security-lock, proxy-envoy, devops-kubernetes.

**Speaker notes:** Services cannot type passwords, so give them identities that the platform proves on their behalf. CI gets the same treatment through OIDC federation.

## Slide 7 — Short-lived credentials are cheap

- 6,000 workloads, 1 h SVIDs, rotate at half-life → ≈ 3.3 signatures/s
- 10 min lifetime → 20 signatures/s
- Static key rotated every 90 days leaks → valid ~45 days on average vs ≤ 1 h
- Cost is operational (HA CA, monitoring), not CPU

**Visual:** Bar chart: exposure window 45 days vs 1 hour. Icons: security-key, ops-clock.

**Speaker notes:** These are labelled assumptions from the lesson. The method matters: lifetime bounds exposure, and the CA becomes a tier-0 dependency.

## Slide 8 — Secrets and least privilege

- Prefer no secret (federation) → dynamic secrets (Vault leases: default TTL 1 h, max 24 h) → static as last resort
- Kubernetes Secrets: unencrypted in etcd by default; pod-create implies secret-read in namespace
- Envelope encryption; per-tenant keys enable crypto-shredding
- Delete permissions unused for 90 days

**Visual:** Ladder: none → dynamic → static. Icons: devops-vault, security-key, security-encryption.

**Speaker notes:** Least privilege multiplies every other control. Measure unused permissions and remove them.

## Slide 9 — The isolation ladder

- Rung 0–1: tenant column; namespace + RBAC + NetworkPolicy + quotas (shared kernel)
- Rung 2: gVisor user-space kernel (runsc) — per-syscall overhead
- Rung 3: microVM — Firecracker (Lambda, Fargate), Kata Containers
- Rung 4–5: dedicated nodes; cluster or account per tenant

**Visual:** Staircase with blast radius shrinking and cost rising. Icons: arch-containers, arch-server, arch-servers-cluster, arch-cloud.

**Speaker notes:** Pick the rung from the threat model. Untrusted code (plugins, agent execution) never sits on rung 1 alone. With 40 pods per node, one escape on rung 1 exposes up to about 40 tenants.

## Slide 10 — Supply chain: four questions

- SBOM: what is inside? (SPDX 3.0 / ISO/IEC 5962:2021; CycloneDX = ECMA-424)
- Provenance: where and from what was it built? (SLSA v1.2 Build L1–L3)
- Signature: unchanged, and by whom? (Sigstore: cosign, Fulcio, Rekor)
- Reproducible build: same bytes from same source?

**Visual:** Pipeline: source → isolated CI → image+SBOM+provenance → sign → registry → admission check → prod. Icons: devops-git, ops-ci-cd, devops-github-actions, devops-kubernetes.

**Speaker notes:** Each control answers one question and misses others. A correct signature on malicious code is still malicious code.

## Slide 11 — xz-utils (CVE-2024-3094)

- 29 Mar 2024: Andres Freund reports backdoor in xz 5.6.0/5.6.1 tarballs
- Found via slow, CPU-heavy SSH logins (≈ 0.299 s → 0.807 s)
- Reached sshd through libsystemd → liblzma; CVSS 10.0
- Build-from-git provenance + reproducible diff would expose tarball-only content; SBOM speeds response

**Visual:** Dependency chain sshd → libsystemd → liblzma with a red tarball diff. Icons: security-bug, devops-linux, devops-git.

**Speaker notes:** Signatures would not have helped: the releaser was a trusted maintainer. Observability found it. The root cause was a social attack on an under-resourced project.

## Slide 12 — Regulation becomes requirements

- CRA, Regulation (EU) 2024/2847: applies 11 Dec 2027
- Art. 14 from 11 Sep 2026: 24 h early warning, 72 h notification, final report ≤ 14 days after fix
- ENISA Single Reporting Platform live 11 Sep 2026
- Needs: SBOM inventory, exploit telemetry, named on-call owner

**Visual:** Timeline 2024-11-20 → 2026-06-11 → 2026-09-11 → 2027-12-11. Icons: ops-calendar, ops-alert, ops-incident.

**Speaker notes:** Work backwards from 24 hours: a quarterly dependency spreadsheet cannot meet that clock.

## Slide 13 — Agent identity and delegation chains

- Agent = workload (own SPIFFE ID, kept out of the model's context) + delegate (acts for a user); never impersonate
- RFC 8693 token exchange: subject = user, actor = agent; nested `act` records the chain, only the outermost actor is used for access control
- Each hop narrows: one audience (RFC 8707), subset scope, ≤ 5 min, sender-constrained; MCP forbids token passthrough
- Other trust domains: ID-JAG (draft -06, 31 Oct 2026) and identity chaining (draft -17); inside one domain: Transaction Tokens (draft -11, 30 Jul 2026)
- Audit = token-service record per minted token (jti, parent jti, sub, actor chain, scope); revoke by refusing to mint for the agent's ID

**Visual:** Sequence: Lumen app → agent runtime → token service → Docs API, and agent runtime → Acme IdP (ID-JAG) → CRM authorisation server → CRM MCP server, with claim tags (sub, act, aud, scope, exp) on each arrow. Icons: ai-agent, security-token, security-jwt, security-oauth, ai-mcp, ops-logs.

**Speaker notes:** The agent is both a service and a delegate, so it needs both identities in one token. Authority only shrinks as it travels, and chain-wide rules belong at the token service because resource servers ignore prior actors. Every draft on this slide is still an Internet-Draft as of 2026-11.

## Slide 14 — Interview angle

- CLARIFY trust boundaries and tenants running code
- QUANTIFY blast radius, credential lifetime, revocation lag
- SKETCH PEPs, PDP, OIDC + SPIFFE; DEEPEN isolation ladder or supply chain
- STRESS: IdP down, CA expired, dependency backdoored; WRAP with security SLOs
- Red flags: "inside the VPC is trusted", tenant_id from request body, shared API key

**Visual:** Six-step framework strip with security callouts. Icons: ops-check, ops-slo.

**Speaker notes:** Security is usually asked inside another design. Show the reason for each box and the numbers behind the trade-offs.
