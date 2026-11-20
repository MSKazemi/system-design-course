# 19 — Privacy, compliance & data sovereignty (slide outline)

**Status:** Draft, text-first outline, not a rendered deck.

Not legal advice: every slide describes engineering consequences of EU law as of 2026-11, as checked in the lesson.

## Slide 1 — The requirement

- Lumen signs an EU hospital group
- Data of EU users stays in the EU and cannot be read in clear from outside it
- Erasure across every copy within the GDPR one-month response window (Art. 12(3))
- An auditor can verify it from logs Lumen cannot silently rewrite

**Visual:** Contract clause cards pointing at a stack diagram. Icons: `domain-document`, `arch-region`, `security-lock`, `ops-logs`.

**Speaker notes:** Each clause hits a different layer. Most of the work is about copies you did not know you
had. This deck is about engineering, not legal advice.

## Slide 2 — Privacy is a non-functional requirement

- GDPR Art. 5: minimisation, purpose limitation, storage limitation, integrity/confidentiality, accountability
- Art. 25: data protection by design and by default, "state of the art", pseudonymisation
- EDPB Guidelines 4/2019: applies to existing systems and to your processors too
- Treat it like availability: designed in, measured, operated

**Visual:** Table: principle → mechanism (TTL, purpose tags, encryption, data map). Icons: `ops-check`, `ops-slo`.

**Speaker notes:** The law states outcomes; the architect picks mechanisms. "We will add deletion later" is a
design defect, the same as "we will add redundancy later".

## Slide 3 — Where personal data actually lives

- Primary DB, cache, keyword index, vector store, object storage
- Kafka topics, lakehouse, logs, traces
- Fine-tuning datasets and model weights
- Backups of most of the above

**Visual:** One user record exploding into ~12 copies across stores. Icons: `arch-database`, `cache-redis`, `search-opensearch`, `messaging-kafka`, `arch-object-storage`, `pattern-backup`, `domain-ai`.

**Speaker notes:** In the Lumen estimate, ~27 erasure requests per day fan out to ~12 stores. The work is small;
the coordination is the problem.

## Slide 4 — Residency ≠ localisation ≠ sovereignty

- Residency: where bytes are stored and processed
- Localisation: a legal duty that data stays in a country
- Sovereignty: whose law can compel access; who holds keys; who operates
- US 18 U.S.C. § 2713 (CLOUD Act): disclosure regardless of data location

**Visual:** Three concentric rings: location → operator → key custody. Icons: `arch-region`, `arch-datacenter`, `security-key`.

**Speaker notes:** Residency is necessary but not sufficient. A provider's nationality and key custody matter as
much as the data centre's address.

## Slide 5 — Transfers after Schrems II

- C-311/18 (16 July 2020): Privacy Shield invalid; SCCs valid with a transfer assessment
- EU–US DPF adopted 10 July 2023; upheld in Latombe (T-553/23, 3 Sept 2025); appeal C-703/25 P pending
- EDPB Rec. 01/2020: keys kept in the EEA can help for storage-only; no technical fix envisaged when the provider needs plaintext and destination-state access exceeds what is necessary and proportionate
- Meta: EUR 1.2 bn fine (May 2023, Irish DPC after an EDPB binding decision) for an architecture decision

**Visual:** Decision tree: adequacy → safeguards → impact assessment → supplementary measures → no transfer. Icons: `pattern-geo-distribution`, `security-encryption`.

**Speaker notes:** Treat an adequacy decision as a dependency with an uncertain lifetime. Keep a tested plan B.

## Slide 6 — Crypto-shredding

- Per-user DEK, wrapped by a per-tenant KEK, wrapped by a regional root key
- Destroy the key: every copy (backups, events, archives) becomes unreadable at once
- Key store is tiny (~200 MB for 2 M users, assumption) — give it short backup retention
- NIST SP 800-88r2 (Sept 2025) lists cryptographic erase with conditions

**Visual:** Key hierarchy tree; a scissors cut at one user DEK greys out its ciphertexts. Icons: `security-key`, `cloud-aws-kms`, `devops-vault`.

**Speaker notes:** The idea is simple. The details are where it fails: key copies, cached keys, and plaintext
copies that were never encrypted.

## Slide 7 — How crypto-shredding fails

- Key-store backups with long retention keep "shredded" keys alive
- Cloud KMS waits 7–30 days before key deletion (AWS KMS default 30)
- Cached unwrapped DEKs keep data readable until TTL
- Indexes, embeddings, logs built from plaintext are untouched

**Visual:** Four red warning badges on the hierarchy. Icons: `ops-warning`, `pattern-backup`, `arch-cache`.

**Speaker notes:** Per-user keys belong in your own key table wrapped by a KMS key, not one KMS key per user.
Shred first, then delete physically.

## Slide 8 — The erasure pipeline

- Verify identity, check Art. 17(3) exceptions (e.g. legal claims)
- Shred key → query data map → fan out idempotent per-store tasks
- Signed receipt in audit log, without personal data
- Restores must replay the erasure ledger (EDPB CEF 2025)

**Visual:** Sequence diagram: subject → privacy API → key service → data map → stores → audit log. Icons: `arch-user`, `arch-api-gateway`, `pattern-saga`, `ops-logs`.

**Speaker notes:** Model it as a durable saga. Separate the "effective" SLO (72 h, assumption) from the
"complete" SLO (30 days).

## Slide 9 — Streams, logs and backups

- Kafka `retention.ms` default 7 days; tombstones kept `delete.retention.ms` 1 day
- `max.compaction.lag.ms` default is effectively unlimited — set it
- Pseudonymise user IDs in logs at write time; short raw-log retention
- Backups: shred keys or track erasures and replay on restore

**Visual:** Kafka log segments with a tombstone; one old segment still holding the value. Icons: `messaging-kafka`, `arch-event-stream`, `ops-logs`.

**Speaker notes:** Among the seven recurring issues in the EDPB's 2025 coordinated action, backups and weak
anonymisation are the two engineering problems. Hashing an email is not anonymisation.

## Slide 10 — AI artefacts

- RAG chunks/embeddings: delete by ID (easy)
- Fine-tuning data and weights: lineage + retraining (hard)
- LLMs can emit memorised training data (Carlini et al. 2021)
- SISA training limits retraining to one shard (Bourtoule et al. 2021)

**Visual:** Difficulty ladder from vector delete to model retrain. Icons: `domain-ai`, `arch-data-pipeline`.

**Speaker notes:** Prefer retrieval over fine-tuning for personal or tenant data. EDPB Opinion 28/2024: where an
infringement is found, authorities may order erasure up to the whole dataset and/or the model, weighing retraining
when judging proportionality.

## Slide 11 — Regional cells

- Global control plane: tenant → region directory, config, aggregates — no personal data
- Each cell: own stores, own keys, own backups and DR targets in jurisdiction
- In-jurisdiction support with audited break-glass
- Inference for EU tenants on EU GPUs

**Visual:** Global box over EU and US cells; edge routes by tenant. Icons: `arch-region`, `arch-load-balancer`, `arch-servers-cluster`.

**Speaker notes:** The usual leak is login: a global user-email table quietly defeats the cell boundary.

## Slide 12 — Tamper-evident audit logs

- Hash chain: h_i = H(h_{i-1} || entry_i)
- Merkle tree + signed tree heads (RFC 9162 style)
- Inclusion proof ≈ 960 B for 10⁹ entries (30 × 32 B, our arithmetic)
- Anchor tree heads outside your control; no personal data in entries

**Visual:** Merkle tree with a highlighted proof path. Icons: `arch-blockchain-ledger`, `security-encryption`.

**Speaker notes:** An audit log full of personal data is a store you cannot change but must erase. Design that
contradiction away.

## Slide 13 — Regulation calendar (as of 2026-11)

- AI Act in force 1 Aug 2024; general application 2 Aug 2026
- Digital Omnibus on AI (Reg. 2026/1744): Annex III high-risk → 2 Dec 2027; Annex I → 2 Aug 2028
- Data Act applies 12 Sept 2025; switching charges banned from 12 Jan 2027
- GDPR "Digital Omnibus" (2025/0360(COD)): Council mandate 21 Oct 2026, not adopted

**Visual:** Timeline 2024–2030 with milestones. Icons: `ops-calendar`, `ops-clock`.

**Speaker notes:** Dates move. Make region and transfer policies configuration, not code, and review the calendar
each quarter.

## Slide 14 — Interview wrap

- CLARIFY residency vs sovereignty and Art. 17(3) exceptions
- QUANTIFY erasure rate × stores; backup retention vs one month
- SKETCH cells, keys, data map, erasure saga, audit log
- STRESS restores, key backups, DR region, adequacy plan B
- Red flags: "just DELETE", hashing = anonymising, "GDPR compliant" box

**Visual:** CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP strip. Icons: `ops-check`.

**Speaker notes:** A strong answer names the copies, the keys, and the proof. It never claims legal certainty.
