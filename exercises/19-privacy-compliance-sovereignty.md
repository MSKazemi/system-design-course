# 19 — Exercises

Companion to [course/02-modern-requirements/19-privacy-compliance-sovereignty.md](../course/02-modern-requirements/19-privacy-compliance-sovereignty.md).
Not legal advice; the answers explain engineering reasoning about EU law as verified in 2026-11.

## 1. Crypto-shredding and key backups [Core]

Lumen encrypts each user's fields with a per-user DEK stored (wrapped) in a key table. The key table is in the same
Postgres cluster as the data and shares its backup policy: daily full backups kept for 365 days. A user is erased
by deleting their DEK row. Is the user erased? What would you change?

<details><summary>Answer</summary>

Not effectively. Each of the up-to-365 daily backups contains the DEK row, and the same backups (or others)
contain the ciphertext. Restoring any backup from the last year restores both key and ciphertext, so the data is
readable for up to a year.

Changes:
- Move the key table to a **separate store** with **separate custody** and much shorter backup retention (for
  example 7 days, chosen to be well inside the erasure budget). At ~100 B per user the store is tiny (2 M users ≈
  200 MB), so frequent, short-lived backups are cheap.
- Keep a **shredded-keys ledger** (subject tokens only) and replay it after any key-store restore.
- Invalidate caches of unwrapped DEKs on shred; their TTL bounds residual readability.
- Accept that the data backups still contain ciphertext for 365 days — this is fine as long as no copy of the key
  survives and the encryption is strong (document algorithm, key length, key-copy analysis; see NIST SP 800-88r2's
  conditions for cryptographic erase).

Alternative acceptable answer: shorten data-backup retention instead — but that often conflicts with business or
regulatory recovery needs, which is why crypto-shredding exists.
</details>

## 2. Kafka compaction trap [Deep]

A compacted topic `user-profile` (key = user ID) feeds several services. On erasure you produce a tombstone for
`u-17`. A week later an auditor reads raw segments and finds u-17's old profile. Explain two plausible causes and
the configuration or design fixes.

<details><summary>Answer</summary>

1. **The segment holding the old value was never compacted.** Compaction runs only on non-active segments that the
   cleaner selects; `max.compaction.lag.ms` defaults to effectively unlimited (Kafka 4.2 docs), so there is no
   upper bound on how long an old value can remain uncompacted. Fix: set `max.compaction.lag.ms` (and segment
   roll settings such as `segment.ms`) so compaction is guaranteed within the erasure SLO.
2. **Copies outside the topic.** Consumers materialised the profile in their own stores, a tiered-storage or
   archive copy exists, or a mirror cluster has not compacted yet. Fix: data map + lineage for every consumer,
   tombstones propagated via CDC to derived stores, and crypto-shredding of payload fields so all copies die with
   the key.

Also worth mentioning: tombstones themselves are retained for `delete.retention.ms` (default 1 day) so consumers
can see the delete; a consumer offline longer than that may miss it and keep stale data — so derived stores need
periodic reconciliation against the source of truth.
</details>

## 3. Residency vs sovereignty [Core]

A customer asks for "EU data sovereignty". Your team proposes: deploy in the Frankfurt region of a US-headquartered
hyperscaler. Which part of the requirement does this meet, which does it not, and what additional levers exist?

<details><summary>Answer</summary>

It meets **residency** (bytes stored and processed in the EU) if backups, DR, logs and support access also stay in
the EU. It does not by itself meet **sovereignty**, because the operator's parent is subject to US law; 18 U.S.C.
§ 2713 requires providers to disclose data in their possession, custody or control regardless of where it is
located.

Levers:
- **Key custody:** customer- or Lumen-EU-held keys in an external key manager, so the provider holds only
  ciphertext — effective for storage, weak for processing that needs plaintext (the EDPB's Rec. 01/2020 found no
  effective technical measure where the provider needs data in the clear).
- **Operations:** EU-resident operations and support staff, audited break-glass.
- **Operator jurisdiction:** an EU-controlled provider or sovereign offering; the Commission's Cloud Sovereignty
  Framework (SEAL-0 to SEAL-4) is a useful vocabulary for this conversation.
- **Contractual:** clarify which of these the customer actually requires — "sovereignty" is often used to mean
  residency. CLARIFY first.
</details>

## 4. Erasure fan-out estimate [Interview]

Estimate the daily erasure workload for a service with 5 M EU users, an assumed 0.4 % yearly erasure rate and 15
stores holding personal data. Then propose two SLOs and say which store you expect to be the long pole.

<details><summary>Answer</summary>

5,000,000 × 0.004 = 20,000 requests/year ≈ 55/day. 55 × 15 ≈ 820 per-store deletion tasks/day — trivial load, but
every one must be confirmed.

SLOs (assumptions, set with legal):
- **Effective** erasure (unreadable in all online stores, key shredded, caches invalidated) within 72 h for 99 % of
  requests.
- **Complete** erasure (physically deleted or crypto-shredded in every store including backups) within 30 days for
  100 % — inside the GDPR Art. 12(3) one-month response window.

Long pole: **backups** (retention often exceeds a month) and, if any personal data entered training, **model
weights**. Crypto-shredding addresses backups; dataset lineage plus a retraining policy (or keeping personal data
out of training) addresses models.
</details>

## 5. Audit log design [Deep]

Design an audit log for erasure receipts that an external auditor can trust even if Lumen's administrators are
malicious. Estimate the proof size for 2³⁰ entries.

<details><summary>Answer</summary>

- Append-only Merkle-tree log (Certificate Transparency / RFC 9162 style). Each entry: request ID, random subject
  token (no name/email), stores touched, counts, timestamps, signer.
- Periodically sign the tree head and **anchor it outside Lumen's control** — send it to the customer, write it to
  write-once storage in a separate account, or a public transparency log. Without anchoring, an admin can rewrite
  history and recompute every hash.
- Auditors verify **inclusion proofs** (an entry is in the tree) and **consistency proofs** (a newer tree extends an
  older one).
- Proof size: at most log₂(2³⁰) = 30 hashes × 32 B (SHA-256) = 960 B.

Key point: no personal data in the log, otherwise it becomes a store you must erase but cannot modify.
</details>

## 6. RAG vs fine-tuning under erasure [Interview]

Lumen wants to "teach the model each tenant's internal documents". Compare fine-tuning a model per tenant with
retrieval-augmented generation from the point of view of erasure and sovereignty.

<details><summary>Answer</summary>

- **RAG:** documents, chunks and embeddings live in per-tenant indexes in the tenant's region; erasing a document
  or person means deleting vectors and chunks by ID and rebuilding affected segments — hours, not weeks. ACLs can
  be enforced at retrieval time. The base model never sees the data during training.
- **Fine-tuning:** personal data is encoded in weights; LLMs can memorise and emit training data (Carlini et al.
  2021). Erasure means excluding the data from the dataset and retraining (or SISA-style shard retraining, which
  must be designed in up front). EDPB Opinion 28/2024 notes authorities can order erasure of datasets or
  retraining.
- Sovereignty: both need in-region compute; RAG also needs in-region embedding and inference.

Prefer RAG for tenant and personal data; if fine-tuning is needed (style, format), train on minimised or synthetic
data with dataset lineage.
</details>

## 7. AI Act dates [Core]

Your product roadmap assumed "high-risk AI obligations apply 2 August 2026". What changed, and what still applies
on 2 August 2026?

<details><summary>Answer</summary>

Regulation (EU) 2026/1744 (Digital Omnibus on AI, OJ 24 July 2026) moved high-risk obligations to **2 December
2027** for Annex III (stand-alone) systems and **2 August 2028** for Annex I (product-embedded) systems. The
Regulation's general application date of **2 August 2026** was not changed, so other provisions still apply then;
prohibitions and AI literacy have applied since 2 February 2025 and general-purpose AI model obligations since 2
August 2025. New prohibited practices inserted by the Omnibus apply from 2 December 2026. The engineering lesson:
keep a dated compliance calendar sourced from the Official Journal and treat dates as configuration.
</details>

## 8. The global control plane leak [Deep]

Lumen's EU cell is clean, but the global login service stores `email → tenant_id` for all users worldwide in a US
region. Why is this a problem, and how would you redesign login?

<details><summary>Answer</summary>

The email address is personal data; storing every EU user's email in the US is a transfer and breaks the residency
promise, regardless of how clean the cell is. Redesign options:
- Ask for the organisation (domain or tenant slug) first and route to the home cell, which holds the user table.
- Use an email-domain → tenant directory (domain names of organisations, not personal emails) in the global plane.
- If a global lookup is unavoidable, store a keyed HMAC of the email with a key held per region, accepting that it
  is still pseudonymised personal data and therefore still in scope — so this is weaker than the first two options.
</details>

## 9. Logs that can be forgotten [Lab]

Write the pseudocode for a logging middleware that lets you erase a user from 90 days of logs without rewriting
log files. State what you must never log.

<details><summary>Answer</summary>

```text
on_request(req):
    token = pseudonym_service.token_for(req.user_id)   # random token, mapping stored in-region
    log.info(event=req.route, user=token, status=resp.status, latency_ms=…)
    # never: request bodies, prompts, completions, emails, names, auth headers, IPs unless justified
on_erasure(user_id):
    pseudonym_service.delete_mapping(user_id)           # log lines now unlinkable
```

The logs keep operational value (rates, errors, latency per token) but cannot be linked back once the mapping is
deleted. Use random tokens rather than an unkeyed hash of the user ID (dictionary-attackable). Keep raw debug logs
with any direct identifiers on short retention. Note: linkage via other fields (rare routes, timestamps) can still
re-identify — minimise fields too.
</details>

## 10. Plan B for transfers [Interview]

Your analytics pipeline sends EU event data to a US-based SaaS under the EU–US Data Privacy Framework. What is
your risk, and what would a robust design look like?

<details><summary>Answer</summary>

Risk: the transfer's legality depends on one adequacy decision (Implementing Decision (EU) 2023/1795). Its
predecessor, Privacy Shield, was invalidated by Schrems II (C-311/18); the DPF was upheld at first instance in
Latombe (T-553/23) but is under appeal (C-703/25 P). If it falls, the flow must stop or move to SCCs with a
transfer impact assessment — and for processing in clear by the importer, effective supplementary measures may not
exist.

Robust design: aggregate or pseudonymise in the EU before export (with keys staying in the EU); make the
destination configurable; maintain and periodically test an EU-hosted alternative; keep a data map so you know
exactly which flows depend on the decision.
</details>
