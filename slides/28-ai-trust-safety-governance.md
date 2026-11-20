# 28 — Trust, safety & governance for AI systems (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

## Slide 1 — The line between code and data is gone
- In an LLM app, every input is text in one context window
- Retrieved pages, emails and tool outputs can act as instructions
- So assume the model can be talked into anything
- Then limit what a talked-into model can do

**Visual:** A context window as one long strip: system prompt, user prompt, retrieved chunk (red, untrusted), tool output (red).
**Speaker notes:** This is the root cause of prompt injection and the organizing idea of the unit. Not legal
advice: the regulation parts are there to help derive system requirements.

## Slide 2 — Threat model: five trust boundaries
- User → system (direct injection, abuse)
- External content → context (indirect injection)
- Model → tools (the blast radius)
- Model → renderer (improper output handling)
- Supply chain → runtime (weights, adapters, datasets)

**Visual:** Threat-model flowchart from the lesson. Icons: arch-user, arch-api-gateway, arch-search-index, arch-worker, security-lock.
**Speaker notes:** Draw boundaries before choosing defenses. The model-to-tools boundary matters most because
that is where text becomes action.

## Slide 3 — The OWASP lists (LLM Top 10 2026, Aug 2026)
- LLM Top 10 2026: LLM01 Prompt Injection through LLM10 Improper Output Handling; Excessive Agency now LLM03
- Agentic Top 10 for 2026 (Dec 2025): ASI01 Agent Goal Hijack, ASI03 Identity and Privilege Abuse, …
- Many entries are classical security problems in new clothes
- Use them as a control checklist, not as a ranking

**Visual:** Two columns of ten codes, with lines from each to a control (policy engine, ACL retrieval, signing, quotas).
**Speaker notes:** The 2026 LLM edition was released in August 2026 and renumbered the list, so System Prompt
Leakage (LLM07 in 2025) is now Hidden Context Exposure (LLM08). Map older documents by name, not number.

## Slide 4 — Indirect prompt injection
- Greshake et al. 2023: LLM apps "blur the line between data and instructions"
- The attacker never talks to your system; they write a page, an email, a PDF
- Demonstrated against Bing's GPT-4-powered chat
- Filters miss paraphrases, languages, encodings and split instructions

**Visual:** Sequence diagram: attacker → shared doc → assistant → email tool → attacker.
**Speaker notes:** Classifiers are telemetry and a speed bump, not a boundary.

## Slide 5 — Exfiltration without a "send" tool
- Markdown images and links that carry data in the URL
- Tool arguments (a search query containing the secret)
- Persisted state (memory, shared docs)
- Lethal trifecta: private data + untrusted content + external communication

**Visual:** Rendered chat bubble with an invisible image whose URL contains "?d=secret", arrow to attacker.example.
**Speaker notes:** No auto-loading of images, link allow-lists, and inspection of tool arguments by policy.
Break the trifecta where a workflow doesn't need all three legs.

## Slide 6 — Jailbreaks are why model safety isn't enough
- Wei et al.: competing objectives and mismatched generalization
- Zou et al.: optimized suffixes transferred to ChatGPT, Bard and Claude
- Model-level safety is necessary but probabilistic
- Consequential actions need controls outside the model

**Visual:** Two failure-mode cards; an arrow labelled "outside the model" pointing to a policy box.
**Speaker notes:** Keep both papers' claims as stated. The point is architectural, not about any model being bad.

## Slide 7 — Guardrails in layers
- AuthN/Z + quotas → input checks → ACL-filtered context → LLM
- Tool calls → policy engine → allow / approve / deny
- Output checks → response with AI disclosure
- The policy engine is the security boundary: deterministic and outside the model

**Visual:** Guardrail flowchart from the lesson. Icons: arch-api-gateway, arch-firewall, security-authorization, arch-user.
**Speaker notes:** Llama Guard and NeMo Guardrails are classifier and rail layers. They reduce how often the
policy engine has to say no, but they do not replace it. The engine is a boundary only for what it can inspect:
constrain the channel, and render approval prompts from the structured call, not from model-written text.

## Slide 8 — Secure-by-design agent patterns
- Action-selector, plan-then-execute, LLM map-reduce
- Dual LLM, code-then-execute, context-minimization
- Principle: after untrusted input, no consequential actions possible
- CaMeL: authors report 77% of AgentDojo tasks with provable security vs 84% undefended (arXiv v2)

**Visual:** Dual-LLM diagram: privileged LLM with tools, quarantined LLM reading untrusted docs, symbolic references between them.
**Speaker notes:** The seven-point utility gap is the honest price of a guarantee. Lead with that number in an
interview.

## Slide 9 — PII, provenance, supply chain
- PII: detect (NER + regex + checksums), mask or pseudonymize; Presidio says no guarantee of finding all
- Provenance: C2PA manifest = assertions + claim + signature, hash-bound to the asset; can be stripped
- Supply chain: pickle can execute code; prefer safetensors; sign models (OpenSSF model-signing v1.0)
- Model cards and datasheets: the human-readable lineage

**Visual:** Three panels: redaction (PERSON_17), signed media with manifest, signed model directory manifest.
Icons: security-key, security-encryption, arch-file-storage.
**Speaker notes:** Each control has a stated limit. Say the limit out loud, because that is what senior answers do.

## Slide 10 — Audit logs that answer "what happened?"
- Versions: model, adapter, prompt, policy
- Retrieved document IDs, tool calls, policy decisions, approvers
- Append-only, tamper-evident (WORM or hash chain)
- Split content (short retention) from events (longer retention)

**Visual:** Hash-chained log entries; two storage tiers labelled content and events. Icons: ops-logs, storage-aws-s3, security-lock.
**Speaker notes:** Log at the gateway so that no service can skip it. Under the stated assumptions this is
~730 GB of events per six months, so storage is cheap and governance is the cost.

## Slide 11 — EU AI Act as requirements (not legal advice)
- Art. 12 logging over the lifetime; Arts. 19 and 26(6): keep logs at least six months
- Art. 14 human oversight; Art. 50 disclosure and machine-readable marking (grace to 2 Dec 2026 for systems already on the market)
- Art. 53 GPAI documentation, copyright policy, training-content summary
- Omnibus (Reg. 2026/1744): high-risk Annex III from 2 Dec 2027, Annex I from 2 Aug 2028

**Visual:** Timeline: 2 Feb 2025 → 2 Aug 2025 → 2 Aug 2026 → 2 Dec 2026 → 2 Dec 2027 → 2 Aug 2028.
**Speaker notes:** The Omnibus entered into force in July 2026. Anyone quoting "high-risk applies August 2026"
is out of date. Obligations depend on role and use case, so involve counsel.

## Slide 12 — NIST AI RMF and the GenAI profile
- Govern, Map, Measure, Manage (AI 100-1, January 2023)
- AI 600-1 (July 2024): twelve GenAI risks, from confabulation to value-chain integration
- Use NIST as the operating model and the AI Act as the obligation list
- Artifacts overlap: threat model, evals, release gates, incident process

**Visual:** Four-quadrant wheel with an artifact in each quadrant.
**Speaker notes:** NIST says AI RMF 1.0 is being revised (as of 2026-11). Version your requirements.

## Slide 13 — Interview angle
- CLARIFY tools, principals, untrusted inputs, jurisdiction and risk tier
- SKETCH: policy engine at the tool boundary; output renderer; audit log
- STRESS: guard model down, so fail closed for tools
- Red flags: "the system prompt says don't", shared service accounts, stale AI Act dates

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip.
**Speaker notes:** Interviewers listen for whether you put the boundary in deterministic code and whether you
can produce evidence afterwards.
