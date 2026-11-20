# Modern System Design — Syllabus

Generated automatically from lesson front matter; do not edit by hand.
Status values: `DRAFT` (written, under review) · `SOURCES_CHECKED` (every source verified).

**Audience:** software, platform and ML engineers from beginner to advanced; students; interview candidates.
**Prerequisites:** basic programming, HTTP and a relational database, a Linux shell; Docker for labs.

## Part 0 — Orientation

### 00 — How to use this course: paths, the requirement loop, what changed in system design

*Requirement:* Know what a 2026 system designer must master that a 2016 one did not, and pick the shortest path through this course that gets you there  
*Time:* 1h reading + 15 min setup check · *Status:* `SOURCES_CHECKED` · [lesson](course/00-orientation/00-how-to-use-this-course.md) · [slides](slides/00-how-to-use-this-course.md) · [exercises](exercises/00-how-to-use-this-course.md)

You will be able to:

- Explain the requirement loop (Requirement → Numbers → Design → Deep dive → Break it → Operate → Interview angle) and apply it to a small feature
- Choose a learning path (learner, practitioner, interview candidate) and the unit order that goes with it
- Interpret the [Core], [Deep] and [Frontier] markers and the lab test-status labels
- Describe the running example, Lumen, and which stage of its growth each part of the course covers
- Summarise, with sources, six ways system design changed between 2016 and 2026

### 01 — Requirements to numbers: SLIs/SLOs, estimation, latency numbers, Little's law, queueing

*Requirement:* Decide, before launch day, whether one server survives 500,000 daily active users with 99.9% of requests succeeding and p99 latency under 300 ms  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/00-orientation/01-requirements-to-numbers.md) · [slides](slides/01-requirements-to-numbers.md) · [exercises](exercises/01-requirements-to-numbers.md) · [lab](labs/01-requirements-to-numbers/)

You will be able to:

- Turn vague requirements (fast, reliable, scalable) into SLIs, SLOs and error budgets
- Estimate requests/s, concurrency, storage and bandwidth from user numbers, stating every assumption
- Apply Little's law and the M/M/1 utilisation–latency curve to size servers, pools and queues
- Explain why tail latency dominates fan-out systems and how hedging and headroom address it
- Estimate an LLM workload in tokens/s and concurrent streams instead of requests/s

## Part I — Classical foundations

### 02 — Anatomy of a request: DNS, TCP, QUIC/HTTP/3, TLS 1.3, proxies, CDN edge

*Requirement:* A first-time Lumen user anywhere in Europe sees the first byte of the app shell within 200 ms at p75, and a returning user within 100 ms  
*Time:* 2.5h reading + 30 min hands-on with curl · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/02-anatomy-of-a-request.md) · [slides](slides/02-anatomy-of-a-request.md) · [exercises](exercises/02-anatomy-of-a-request.md)

You will be able to:

- Explain every step between typing a hostname and receiving the first byte: DNS, TCP, TLS 1.3, HTTP, proxies, CDN
- Estimate a request's latency budget from round-trip times and count the round trips each protocol stack costs
- Compare HTTP/1.1, HTTP/2 and HTTP/3 (QUIC) and say when each one wins
- Design DNS TTLs, connection reuse and edge termination for a stated latency and failover requirement
- Diagnose common failures: stale DNS, keep-alive mismatches, blocked UDP, certificate expiry, connection storms

### 03 — Scaling compute: stateless services, L4/L7 load balancing, algorithms, health checks, autoscaling

*Requirement:* Serve 6,000 requests/s at peak with p99 < 300 ms, lose any one instance or one zone without user-visible errors, and deploy 20 times a day without dropping a request  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/03-scaling-compute.md) · [slides](slides/03-scaling-compute.md) · [exercises](exercises/03-scaling-compute.md) · [lab](labs/03-scaling-compute/)

You will be able to:

- Explain when to scale up versus out, and what makes a service safe to scale out (statelessness)
- Compare L4 and L7 load balancing and choose the right layer for a protocol and a requirement
- Compare round robin, least connections, power of two choices and consistent hashing, with the maths behind them
- Design health checks, connection draining and autoscaling that survive failures and deploys
- Diagnose thundering herds, retry storms and autoscaler oscillation, and apply the standard mitigations

### 04 — Caching everywhere

*Requirement:* Serve 50,000 catalogue reads/s at p99 < 50 ms from a database that saturates near 5,000 queries/s, and never show a price more than 60 s stale  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/04-caching.md) · [slides](slides/04-caching.md) · [exercises](exercises/04-caching.md) · [lab](labs/04-caching/)

You will be able to:

- Explain the five cache read/write patterns and choose one from a consistency and failure requirement
- Estimate the hit ratio a design needs from the request rate, the backend's capacity and the latency SLO
- Compare LRU, LFU, ARC, W-TinyLFU and FIFO-family eviction and explain admission versus eviction
- Diagnose the stale-set race, stampedes, penetration and hot keys, and design mitigations (leases, XFetch, coalescing, negative caching)
- Design HTTP/CDN caching with correct Cache-Control directives and cache keys
- Relate classical caching to LLM KV-cache prefix reuse and semantic caching

### 05 — Choosing storage

*Requirement:* Store Lumen's billing, chat history, sessions, usage metrics and document embeddings with zero lost invoices, 20,000 chat writes/s at peak, and as few database products as the requirements allow  
*Time:* 3.5h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/05-choosing-storage.md) · [slides](slides/05-choosing-storage.md) · [exercises](exercises/05-choosing-storage.md)

You will be able to:

- Compare relational, key-value, document, wide-column, graph, time-series and vector data models by access pattern
- Explain B-tree and LSM-tree storage engines and estimate their write, read and space amplification
- Choose indexes for a query and explain what each index costs on writes
- Diagnose isolation anomalies (dirty read, lost update, read skew, write skew, phantoms) and choose an isolation level or a locking strategy that prevents them
- Design a storage decision for a multi-workload product and defend when one engine (Postgres) is enough and when it is not

### 06 — Replication & consistency

*Requirement:* Survive the loss of any one availability zone with zero acknowledged writes lost and under 30 s of write unavailability, while every user always sees their own messages  
*Time:* 3.5h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/06-replication-consistency.md) · [slides](slides/06-replication-consistency.md) · [exercises](exercises/06-replication-consistency.md) · [lab](labs/06-replication-consistency/)

You will be able to:

- Explain single-leader, multi-leader and leaderless replication and the failure each one handles
- Estimate the latency and availability cost of synchronous replication and of quorums (R + W > N)
- Diagnose replication-lag anomalies (read-your-writes, monotonic reads, consistent prefix) and design fixes
- State CAP precisely, correct its common misreadings, and classify systems with PACELC
- Compare linearizable, sequential, causal, session and eventual consistency and their availability limits
- Design conflict resolution with last-writer-wins, version vectors and CRDTs, and design failover that cannot split brain

### 07 — Partitioning & sharding

*Requirement:* Spread 40 TB of chat history and 20,000 writes/s over a cluster that grows from 8 to 64 nodes online, keeping every node under 1.25x average load and 'latest messages of a conversation' a single-partition read  
*Time:* 3h reading + 1h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/07-partitioning-sharding.md) · [slides](slides/07-partitioning-sharding.md) · [exercises](exercises/07-partitioning-sharding.md) · [lab](labs/07-partitioning-sharding/)

You will be able to:

- Compare hash, range, compound and directory partitioning by query support and hot-spot risk
- Explain consistent hashing, virtual nodes, rendezvous hashing and jump hash, and estimate how many keys move on resize
- Design a rebalancing strategy (fixed partitions, split/merge, per-node tokens) and an online resharding procedure
- Choose local or global secondary indexes and explain the read/write cost of each
- Diagnose hot partitions and mitigate them with key salting, splitting and caching
- Explain how distributed SQL systems (Spanner, CockroachDB, Vitess, Citus) partition and what cross-partition work costs

### 08 — Asynchronous & event-driven systems

*Requirement:* Lumen must accept 2,000 document-ingest events per second at peak, never lose one, never charge a tenant twice, and keep the upload API under 150 ms p99 even when the embedding workers are down for 30 minutes  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/08-async-event-driven.md) · [slides](slides/08-async-event-driven.md) · [exercises](exercises/08-async-event-driven.md) · [lab](labs/08-async-event-driven/)

You will be able to:

- Explain the difference between a work queue and a replicated log, and choose between them for a given workload
- Explain why at-least-once delivery plus idempotent processing is the practical route to effectively-once effects, and where Kafka transactions fit
- Design a transactional outbox and an inbox (deduplication) table, and say exactly which failure each one closes
- Compare orchestrated and choreographed sagas and design compensations for a multi-service workflow
- Estimate partition counts, retention storage and backlog drain time from stated assumptions
- Diagnose poison messages, consumer lag and backpressure failures, and size a dead-letter policy

### 09 — Coordination & consensus

*Requirement:* Lumen must run exactly one active job scheduler and one ledger writer across three availability zones: fail over in under 5 s, never let two writers act at once, and never lose an acknowledged configuration change.  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/09-coordination-consensus.md) · [slides](slides/09-coordination-consensus.md) · [exercises](exercises/09-coordination-consensus.md) · [lab](labs/09-coordination-consensus/)

You will be able to:

- Explain what consensus guarantees, what the FLP result rules out, and why real systems are safe under asynchrony but live only under partial synchrony.
- Explain Raft's terms, elections, log matching, commit rule and membership changes well enough to reason about a failure trace.
- Design leader election on top of a consensus store using leases, and protect shared resources with fencing tokens.
- Compare physical, Lamport, vector, hybrid logical and TrueTime-style clocks and choose one for a given ordering requirement.
- Choose a unique-ID scheme (UUIDv7, ULID, Snowflake-style, database sequence) from stated requirements and estimate its capacity.
- Diagnose coordination failures (election storms, quorum loss, clock skew, expired leases, false failure suspicions) from their SLIs.

### 10 — APIs & communication

*Requirement:* Expose Lumen's chat and document APIs to 3,000 tenant apps: stream LLM tokens to 20k concurrent users, survive client retries without double-charging, and keep any one tenant from starving the others — with < 2 ms added per request for admission control  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/10-apis-communication.md) · [slides](slides/10-apis-communication.md) · [exercises](exercises/10-apis-communication.md) · [lab](labs/10-apis-communication/)

You will be able to:

- Compare REST, gRPC and GraphQL on coupling, performance, caching, tooling and failure behavior, and pick one for a given boundary
- Choose between polling, SSE, WebSockets and gRPC streaming, and explain why SSE became the default for LLM token streaming
- Design an idempotent POST endpoint with an Idempotency-Key, including storage, concurrency and expiry
- Explain and implement token bucket, leaky bucket, fixed window, sliding window log, sliding window counter and GCRA, and estimate their memory and accuracy
- Design a distributed rate limiter and decide what happens when its store is down
- Evolve an API and its protobuf/JSON schemas without breaking existing clients, and choose a versioning and pagination strategy

### 11 — Reliability engineering

*Requirement:* Lumen's answer API must hold 99.95% monthly availability, survive the loss of one availability zone with no human action, and recover on its own within five minutes after any dependency brownout ends  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/11-reliability-engineering.md) · [slides](slides/11-reliability-engineering.md) · [exercises](exercises/11-reliability-engineering.md) · [lab](labs/11-reliability-engineering/)

You will be able to:

- Classify a failure as crash, omission, timing, arbitrary (Byzantine) or gray, and explain why gray failure defeats naive health checks
- Choose timeouts from latency percentiles and propagate deadlines across a call chain
- Estimate retry amplification across layers and design retries with capped exponential backoff, jitter and a retry budget
- Compare circuit breakers, bulkheads, load shedding, admission control and graceful degradation, and place each in a request path
- Explain metastable failure (trigger, vulnerable state, sustaining effect) and diagnose one from a public postmortem
- Design multi-AZ static stability and pick a disaster-recovery strategy from RPO/RTO targets and cost
- Plan a chaos experiment with a steady-state hypothesis and a bounded blast radius

### 12 — Observability

*Requirement:* Page a human within minutes when Lumen's answer API is burning its 99.5% monthly availability budget fast, never page for blips, and let the on-call engineer go from alert to the guilty span in under five minutes  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/12-observability.md) · [slides](slides/12-observability.md) · [exercises](exercises/12-observability.md) · [lab](labs/12-observability/)

You will be able to:

- Explain what metrics, logs, traces and profiles are each good and bad at, and how they are correlated
- Estimate metric cardinality and telemetry volume, and diagnose a cardinality explosion
- Apply the RED and USE methods to pick the first dashboards for a service and a resource
- Design an OpenTelemetry pipeline (SDK, Collector, backends) including head and tail sampling
- Derive multi-window, multi-burn-rate alert thresholds from an SLO and an error budget
- Compare observability architectures on cost, and evaluate AI-assisted operations claims critically

### 13 — Data at scale: object storage, lakehouse, batch vs stream, search

*Requirement:* Keep 2 PB of documents durably and cheaply, answer analytics over 90 days of events in seconds, and serve keyword search over 500 M chunks at p99 < 200 ms  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/01-foundations/13-data-at-scale.md) · [slides](slides/13-data-at-scale.md) · [exercises](exercises/13-data-at-scale.md)

You will be able to:

- Explain the consistency, durability and request-rate semantics of a modern object store and what conditional writes add
- Estimate the raw-capacity and repair cost of replication versus Reed-Solomon erasure coding
- Explain how a table format (Iceberg, Delta Lake, Hudi) turns immutable files on object storage into ACID tables
- Estimate bytes scanned by a columnar query and design file sizes, partitioning and compaction
- Compare batch, Lambda and Kappa architectures and choose one for a stated freshness requirement
- Design an inverted-index search tier and explain BM25 scoring, segments, refresh and merging
- Diagnose the classic failure modes: small files, metadata bloat, commit contention, hot prefixes, merge storms

## Part II — Modern requirements

### 14 — Cloud-native & platform engineering

*Requirement:* Let 40 Lumen product engineers ship 50 deploys a day to a shared fleet, safely, without each team learning Kubernetes internals, while traffic swings 10x between night and day  
*Time:* 3.5h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/14-cloud-native-platforms.md) · [slides](slides/14-cloud-native-platforms.md) · [exercises](exercises/14-cloud-native-platforms.md) · [lab](labs/14-cloud-native-platforms/)

You will be able to:

- Explain how namespaces and cgroups turn a process into a container, and what isolation that does and does not give
- Explain Kubernetes' declarative model and the controller reconciliation loop, and design a simple operator
- Compare HPA, VPA, KEDA and cluster autoscaling, and estimate how fast each reacts
- Design a GitOps delivery flow with rolling and canary releases
- Compare containers, serverless functions and WebAssembly components on cold start, density and isolation
- Design an internal developer platform and a multi-tenancy model for a shared Kubernetes fleet

### 15 — Multi-region & edge

*Requirement:* Serve Lumen users in the EU, the US and Asia-Pacific with p95 < 200 ms for interactive API calls, survive the loss of a whole region with RTO ≤ 5 min and RPO = 0 for billing, and keep EU tenants' data in the EU  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/15-multi-region-edge.md) · [slides](slides/15-multi-region-edge.md) · [exercises](exercises/15-multi-region-edge.md)

You will be able to:

- Explain the three reasons to go multi-region (latency, availability, sovereignty) and which design each one forces
- Estimate the physical lower bound on round-trip time between two cities and build a latency budget from it
- Compare backup-and-restore, pilot light, warm standby, hot standby and active-active by RPO, RTO, cost and complexity
- Design a geo-partitioned data layer and choose a conflict-resolution strategy (single home, LWW, CRDT, application merge, consensus)
- Compare Spanner, CockroachDB, DynamoDB global tables and Aurora Global Database by their consistency and latency behavior
- Diagnose the failure modes of geo-DNS, anycast and edge compute, and use cells and shuffle sharding to limit blast radius

### 16 — Cost as a requirement

*Requirement:* Serve Lumen's API at 300M requests/month for at most $6 per million requests all-in, and know every tenant's cost within 24 hours  
*Time:* 2.5h reading + 1h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/16-cost-as-requirement.md) · [slides](slides/16-cost-as-requirement.md) · [exercises](exercises/16-cost-as-requirement.md) · [lab](labs/16-cost-as-requirement/)

You will be able to:

- Explain cost as a non-functional requirement with an SLI, a target and a budget, alongside latency and availability
- Estimate the monthly cost of a design from first principles, separating usage (quantity) from rate (price)
- Compare capacity-priced, consumption-priced, committed and spot capacity and find the break-even traffic between them
- Identify the cost drivers architects routinely miss: egress, cross-zone traffic, NAT, storage retrieval and minimum durations, managed-service premiums, idle capacity
- Design cost observability: allocation, unit metrics (per request, per tenant, per 1k tokens), FOCUS-normalised billing data and OpenCost for Kubernetes
- Diagnose cost incidents (runaway scaling, retry storms, chatty services, idle GPUs) and define guardrails

### 17 — Energy- & carbon-aware design

*Requirement:* Report Lumen's carbon per 1,000 chat answers with an auditable method, and cut it by 40% within 12 months without breaking the 2 s time-to-first-token SLO  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/17-energy-carbon-aware.md) · [slides](slides/17-energy-carbon-aware.md) · [exercises](exercises/17-energy-carbon-aware.md)

You will be able to:

- Explain PUE, carbon intensity (average vs marginal), embodied carbon and the SCI score, and what each one does and does not measure
- Estimate energy and carbon per request for a GPU-backed service from power, utilisation, PUE, grid intensity and hardware lifetime
- Compare efficiency, temporal shifting, spatial shifting and hardware choices as levers, and predict which one dominates for a given grid
- Design an energy-measurement pipeline from RAPL, BMC, DCGM and Kepler up to a per-request SLI, and name its accuracy limits
- Describe the EU data-centre reporting obligations (Directive (EU) 2023/1791, Delegated Regulation (EU) 2024/1364) as system requirements

### 18 — Security by design

*Requirement:* Lumen hosts 2,000 enterprise tenants on shared Kubernetes. One compromised pod, one stolen credential or one poisoned dependency must not expose another tenant's data, and every artefact running in production must be traceable to reviewed source.  
*Time:* 3h reading + 1h exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/18-security-by-design.md) · [slides](slides/18-security-by-design.md) · [exercises](exercises/18-security-by-design.md)

You will be able to:

- Explain the zero-trust model of NIST SP 800-207 and map its policy decision and enforcement points onto a service architecture.
- Distinguish authentication from authorisation, user identity from workload identity, and choose OAuth 2.0 / OIDC flows that follow RFC 9700.
- Design workload identity with SPIFFE/SPIRE and mutual TLS, and estimate the cost of short-lived credentials.
- Compare multi-tenant isolation levels (namespace, sandboxed runtime, microVM, dedicated cluster) by blast radius and cost.
- Design a software supply chain with SBOMs, SLSA build provenance and Sigstore signatures, and explain what each would and would not have caught in the xz-utils backdoor (CVE-2024-3094).
- Run a STRIDE threat model on a data-flow diagram and turn the EU Cyber Resilience Act's reporting deadlines into system requirements.

### 19 — Privacy, compliance & data sovereignty

*Requirement:* Keep EU tenants' personal data under EU jurisdiction, honour an erasure request across every store (primary DBs, caches, search and vector indexes, logs, streams, backups, training data) inside the one-month GDPR response window, and prove all of it to an auditor  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/19-privacy-compliance-sovereignty.md) · [slides](slides/19-privacy-compliance-sovereignty.md) · [exercises](exercises/19-privacy-compliance-sovereignty.md)

You will be able to:

- Explain how the GDPR principles of data minimisation, purpose limitation, storage limitation and data protection by design (Art. 5, 25) become concrete architecture requirements
- Distinguish data residency, data localisation and data sovereignty, and explain why Schrems II made the distinction an engineering problem
- Design an erasure pipeline that reaches backups, logs, event streams and derived ML artefacts, using crypto-shredding where physical deletion is impractical
- Design regional cells with per-tenant keys and a personal-data-free global control plane
- Build a tamper-evident audit log and estimate its proof size and cost
- Map the EU AI Act and EU Data Act application dates (as amended by 2026) to system requirements, and say what is still pending

### 20 — Real-time & streaming systems

*Requirement:* Reflect every document edit in Lumen's search and RAG answers within 5 s (p99), show per-tenant usage dashboards with ≤ 10 s freshness at 50k events/s peak, and never lose or double-count a billable token  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/02-modern-requirements/20-real-time-streaming.md) · [slides](slides/20-real-time-streaming.md) · [exercises](exercises/20-real-time-streaming.md)

You will be able to:

- Explain change data capture (CDC) from a database log and why it beats dual writes
- Distinguish event time from processing time and explain how watermarks, windows, triggers and allowed lateness trade completeness against latency
- Explain how Flink's asynchronous barrier snapshots make stateful stream processing fault tolerant
- Compare at-least-once, effectively-once (idempotent sinks) and transactional exactly-once, and estimate their latency cost
- Design a streaming pipeline from an OLTP database to a vector index, a real-time analytics store and an ML feature store
- Diagnose consumer lag, stuck watermarks, state growth and replication-slot WAL bloat

## Part III — AI-native systems

### 21 — Anatomy of LLM inference

*Requirement:* Lumen chat must show the first token within 500 ms (p95) and stream at least 20 tokens/s to every user. How many users can one GPU carry, and what limits it?  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/21-llm-inference-anatomy.md) · [slides](slides/21-llm-inference-anatomy.md) · [exercises](exercises/21-llm-inference-anatomy.md) · [lab](labs/21-llm-inference-anatomy/)

You will be able to:

- Explain the two phases of LLM inference (prefill and decode) and why one is compute-bound and the other memory-bandwidth-bound
- Estimate model-weight memory at BF16, FP8 and INT4, and KV-cache memory per token for a named open model, including the effect of GQA/MQA
- Estimate a lower bound on decode step time from memory bandwidth, and the batch size at which decode stops being bandwidth-bound (roofline intuition)
- Define and measure TTFT, TPOT, ITL, end-to-end latency, throughput and goodput, and explain why p99 matters for LLM products
- Describe how sampling, stopping and token streaming over Server-Sent Events work end to end
- Diagnose a slow LLM endpoint by asking which phase, which resource and which percentile is failing

### 22 — Serving LLMs at scale

*Requirement:* Serve a 32B-class open model to 10,000 concurrently active Lumen users with TTFT p95 < 2 s and TPOT p95 < 50 ms, at a cost per million tokens finance can sign off.  
*Time:* 4h reading + 2h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/22-serving-llms-at-scale.md) · [slides](slides/22-serving-llms-at-scale.md) · [exercises](exercises/22-serving-llms-at-scale.md) · [lab](labs/22-serving-llms-at-scale/)

You will be able to:

- Explain PagedAttention, continuous (iteration-level) batching, automatic prefix caching and chunked prefill, and what each does to memory, throughput and tail latency
- Describe vLLM's V1 engine architecture (API server, engine core, workers, token-budget scheduler) as of v0.34.0
- Compare speculative decoding, quantisation (FP8, AWQ, GPTQ) and tensor/pipeline/data/expert parallelism, and choose among them for a workload
- Compare vLLM, SGLang, TensorRT-LLM, TGI and llama.cpp/Ollama and say where each fits
- Design a Kubernetes serving stack with prefix/KV-aware routing, disaggregated prefill/decode and autoscaling on queue depth and KV utilisation
- Produce a capacity plan (users → requests/s → tokens/s → GPUs) and a cost per million tokens with every assumption labelled

### 23 — GPU & accelerator infrastructure

*Requirement:* Lumen's platform team must run inference fleets and weekly fine-tuning jobs on a shared pool of 64 GPUs, keep tail latency inside SLO, survive hardware faults, and report cost per token and per training run.  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/23-gpu-infrastructure.md) · [slides](slides/23-gpu-infrastructure.md) · [exercises](exercises/23-gpu-infrastructure.md)

You will be able to:

- Explain the GPU features that matter to system designers: HBM capacity and bandwidth, tensor-core throughput (dense vs sparse), and the ridge point they imply
- Compare interconnect tiers (HBM, NVLink/NVSwitch, PCIe, InfiniBand, RoCE/Ethernet) and estimate why tensor parallelism must stay inside the NVLink domain
- Describe how Kubernetes schedules GPUs: device plugin, NVIDIA GPU Operator, Dynamic Resource Allocation (GA in v1.34), and the sharing options MIG, time-slicing and MPS
- Choose between gang/topology-aware schedulers (Kueue, Volcano, native Workload API) and between Slurm and Kubernetes (including Slinky)
- Monitor GPUs correctly (DCGM profiling metrics vs 'GPU utilisation') and design for failures (Xid errors, ECC, stragglers) using published large-cluster data
- Reason about power, cooling and fleet economics, and compare NVIDIA, AMD, Google TPU and AWS Trainium neutrally

### 24 — Retrieval & vector systems

*Requirement:* Answer questions over 50 million chunks from 2,000 tenant workspaces with p95 retrieval under 150 ms, zero cross-tenant or cross-ACL leakage, and edits visible within 15 minutes  
*Time:* 3.5h reading + 2h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/24-retrieval-vector-systems.md) · [slides](slides/24-retrieval-vector-systems.md) · [exercises](exercises/24-retrieval-vector-systems.md) · [lab](labs/24-retrieval-vector-systems/)

You will be able to:

- Estimate the memory and disk footprint of a vector index from dimension, precision, count and graph degree
- Explain how HNSW, IVF, product quantization and DiskANN trade recall for latency and memory
- Compare pre-, post- and in-filtering and choose one for a multi-tenant, ACL-aware retriever
- Design a RAG pipeline end to end: ingestion, chunking, metadata, indexing, hybrid retrieval, reranking, generation with citations
- Evaluate a retriever (recall@k, MRR, nDCG) and a RAG system (faithfulness, context precision/recall), and diagnose which stage failed
- Argue when long-context prompting, GraphRAG or plain RAG is the better design

### 25 — Agentic systems

*Requirement:* Run multi-step research-and-analysis tasks for 10,000 daily users: tasks up to 30 minutes, every tool call least-privileged and audited, risky actions approved by a human, a hard cost cap per task, and no duplicated side effects after a worker crash  
*Time:* 3.5h reading + 2h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/25-agentic-systems.md) · [slides](slides/25-agentic-systems.md) · [exercises](exercises/25-agentic-systems.md) · [lab](labs/25-agentic-systems/)

You will be able to:

- Explain the agent loop (ReAct-style reason/act/observe) and why its cost grows super-linearly with the number of steps
- Compare orchestration patterns (single agent, router, supervisor/hierarchical, graph/state machine) and choose one for a requirement
- Describe MCP and A2A as of 2026-11: what each standardises, transports, and governance
- Design state, memory and checkpointing so a long-running agent survives crashes without repeating side effects
- Design a sandbox and permission model for tool execution, including human approval gates and budgets
- Evaluate and observe agents: task success, pass^k reliability, trajectories, and traces

### 26 — LLM gateways & LLMOps

*Requirement:* Give 40 internal teams one API to four model providers and a self-hosted vLLM fleet at 2,000 requests/s peak, with per-team token quotas, under 10 ms of added gateway latency at p95, cost attributed per team, automatic fallback on provider failure, and every model or prompt change gated by evaluations  
*Time:* 3h reading + 1.5h lab · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/26-llm-gateways-llmops.md) · [slides](slides/26-llm-gateways-llmops.md) · [exercises](exercises/26-llm-gateways-llmops.md) · [lab](labs/26-llm-gateways-llmops/)

You will be able to:

- Explain the LLM gateway pattern and what belongs in it (and what does not)
- Design routing across providers and self-hosted models for cost, latency and quality, with retries, fallbacks and cooldowns
- Design token-based rate limiting and quotas, including reservation for unknown output length
- Diagnose streaming problems through proxies (buffering, timeouts, cancellation, usage accounting)
- Evaluate the correctness risks of semantic caching and decide when it is safe
- Build an LLMOps loop: prompt/version management, offline evals, online experiments, LLM-as-judge caveats, monitoring with OpenTelemetry GenAI conventions, cost attribution, drift and model-regression incident response

### 27 — ML platforms & data for AI

*Requirement:* Ship a model change from a notebook to production in under a day, serve features at p99 < 10 ms, and prove that what the model saw in training is what it sees in production  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/27-ml-platforms.md) · [slides](slides/27-ml-platforms.md) · [exercises](exercises/27-ml-platforms.md)

You will be able to:

- Explain the ML lifecycle (data → features → training → evaluation → registry → serving → monitoring) as a system with owners, contracts and failure modes
- Design an online/offline feature store and explain point-in-time correctness and training-serving skew
- Estimate GPU memory for full fine-tuning vs LoRA and choose data, tensor or pipeline parallelism
- Compute a checkpoint interval from failure rate and checkpoint cost
- Design a two-tower retrieval + ranking recommender and size its embedding index
- Diagnose data drift, concept drift and silent data-quality failures, and choose a detection method

### 28 — Trust, safety & governance for AI systems

*Requirement:* Let an LLM assistant read untrusted documents and call tools on customers' behalf without leaking their data, and be able to show a regulator what it did and why  
*Time:* 3h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/03-ai-systems/28-ai-trust-safety-governance.md) · [slides](slides/28-ai-trust-safety-governance.md) · [exercises](exercises/28-ai-trust-safety-governance.md)

You will be able to:

- Build a threat model for an LLM application using the OWASP Top 10 for LLM Applications (2026) and the Agentic Top 10 (2026)
- Explain direct and indirect prompt injection and why filtering alone cannot solve it
- Design a layered guardrail architecture with input/output controls, a policy engine and capability-scoped tools
- Design PII redaction, content provenance and model supply-chain controls, and state their limits
- Translate EU AI Act obligations (Articles 12, 14, 50, 53) and NIST AI RMF functions into system requirements
- Design tamper-evident audit logging with retention that fits both the AI Act and GDPR

## Part IV — Case studies

### C01 — URL shortener + distributed rate limiter

*Requirement:* Design a public URL shortener that takes 100 million new links a month and serves 10 billion redirects a month with p99 < 50 ms from the edge, plus a rate limiter that enforces per-API-key quotas across three regions and blocks abusive traffic before it reaches the origin.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C01-url-shortener-rate-limiter.md) · [slides](slides/C01-url-shortener-rate-limiter.md) · [exercises](exercises/C01-url-shortener-rate-limiter.md)

You will be able to:

- Estimate write rate, read rate, key-space size and storage for a shortener, labelling every assumption
- Compare short-code generation schemes (hash, counter, random, keyed permutation) on collisions, coordination and enumerability
- Choose redirect status codes and cache headers from RFC 9110 semantics and explain the analytics trade-off
- Design a distributed rate limiter: algorithm, state placement, multi-region quota sharing, failure policy and client signalling
- Diagnose hot links, cache stampedes, limiter outages and abuse, and state SLOs, cost and energy per redirect

### C02 — News feed / timeline

*Requirement:* Design the home feed for a social app with 200 million daily users: the feed loads in under 300 ms at p99, a new post reaches followers' feeds within 5 seconds at p95, some accounts have tens of millions of followers, and the feed is ranked by a model rather than sorted by time.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C02-news-feed.md) · [slides](slides/C02-news-feed.md) · [exercises](exercises/C02-news-feed.md)

You will be able to:

- Estimate feed reads, post writes, fan-out inserts and timeline memory, labelling every assumption
- Compare fan-out on write, fan-out on read and hybrid strategies with a cost model, and place the celebrity threshold
- Design the timeline store, the read path latency budget and cursor pagination that survives inserts and deletes
- Explain a multi-stage ranking pipeline (candidate sources, feature hydration, light and heavy rankers, filters) and its cost
- Diagnose fan-out backlogs, hot authors and ranker overload, and state SLOs, cost and energy per feed load

### C03 — Chat & presence

*Requirement:* Design a chat service for 100 million daily users with 1:1 and group conversations up to 1,000 members, real-time delivery under 500 ms at p99 to online devices, reliable offline delivery and multi-device sync, ordered history, presence and typing indicators, and an end-to-end-encrypted mode.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C03-chat-presence.md) · [slides](slides/C03-chat-presence.md) · [exercises](exercises/C03-chat-presence.md)

You will be able to:

- Estimate message rate, delivery fan-out, concurrent connections and storage for a chat system, labelling every assumption
- Design the connection layer: WebSocket gateways, session routing, draining and reconnect storms
- Explain per-conversation ordering, idempotent sends and at-least-once delivery with client-side deduplication
- Design message storage partitioned by conversation and time bucket, and justify it with published production designs
- Explain how MLS (RFC 9420) end-to-end encryption and on-device or confidential-computing AI assistants change server responsibilities

### C04 — Video upload, transcoding & streaming

*Requirement:* Design a video platform that ingests 1 million uploads a day from phones and studios, makes each video playable within minutes, and streams 100 million hours a day worldwide with start-up under 2 seconds and rare rebuffering — at a delivery cost the business can carry.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C04-video-streaming.md) · [slides](slides/C04-video-streaming.md) · [exercises](exercises/C04-video-streaming.md)

You will be able to:

- Estimate ingest bandwidth, transcode compute, storage growth and peak delivery bandwidth, labelling every assumption
- Design resumable, direct-to-object-storage uploads and an idempotent transcoding workflow
- Explain bitrate ladders, per-title and per-shot encoding, and quality metrics such as VMAF
- Design adaptive-bitrate delivery with HLS/DASH segments, CDN tiers and ISP-embedded caches
- Decide when an expensive codec (AV1) pays for itself, and explain what AV2, hardware encoders and AI captioning change in 2026

### C05 — Ride-hailing & proximity search

*Requirement:* Design the real-time core of a ride-hailing service in 600 cities: 2 million online drivers report location every 4 seconds, riders see nearby cars live, a ride request is matched to a driver within 2 seconds at p99, no driver is ever assigned two rides, and prices react to local supply and demand.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C05-ride-hailing-proximity.md) · [slides](slides/C05-ride-hailing-proximity.md) · [exercises](exercises/C05-ride-hailing-proximity.md)

You will be able to:

- Estimate location-update rate, index memory, nearby-car query load and trip-trace storage, labelling every assumption
- Compare geohash, quadtree, S2 and H3 spatial indexes and choose a resolution from cell sizes
- Design a location ingestion path whose state is soft and self-healing, partitioned by city
- Design matching with a driver state machine and leases so no driver is double-assigned
- Explain ETA prediction, supply–demand pricing on hexagonal cells, and location-privacy obligations

### C06 — Payments & ledger

*Requirement:* Design the payments core for a marketplace processing 10 million payments a day by card and instant bank transfer: no customer is ever charged twice, every cent is accounted for in a double-entry ledger, sellers are paid out correctly, the books reconcile with payment providers daily, and instant transfers settle in seconds, 24/7.  
*Time:* 2.5h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C06-payments-ledger.md) · [slides](slides/C06-payments-ledger.md) · [exercises](exercises/C06-payments-ledger.md)

You will be able to:

- Estimate payment, posting and storage volumes and identify hot accounts, labelling every assumption
- Design end-to-end idempotency from client to payment provider and back (webhooks)
- Design an immutable double-entry ledger with journal entries, postings, holds and derived balances
- Achieve exactly-once effects with an outbox, a payment state machine and explicit handling of unknown outcomes
- Explain reconciliation and what 24/7 instant payments (SEPA Instant, FedNow) and the EU payments package change

### C07 — Distributed key-value store (Dynamo-style)

*Requirement:* Design a key-value store that is always writable, serves 1 million operations per second with p99.9 under 10 ms within a region, holds 100 TB of data across three availability zones, survives the loss of any node or zone without losing acknowledged writes, and lets each application choose its own consistency/latency trade-off.  
*Time:* 2.5h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C07-distributed-kv-store.md) · [slides](slides/C07-distributed-kv-store.md) · [exercises](exercises/C07-distributed-kv-store.md)

You will be able to:

- Estimate node count, per-node load, network and repair time for a replicated KV store, labelling every assumption
- Explain consistent hashing with virtual nodes, preference lists and zone-aware replica placement
- Reason about quorums (N, R, W), sloppy quorums, hinted handoff, vector clocks and last-write-wins, including what each does not guarantee
- Describe an LSM-tree storage engine, tombstones and why repair must run within the tombstone grace period
- Compare the Dynamo design with 2026 alternatives: leader-based replication (Multi-Paxos/Raft), transactional metadata, and object-storage-tiered engines

### C08 — Web crawler & search engine

*Requirement:* Design a polite web crawler that keeps a 5-billion-page index fresh and a search service that answers 10,000 queries/s with p95 < 300 ms — and that also feeds a retrieval-augmented (RAG) product.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C08-web-crawler-search.md) · [slides](slides/C08-web-crawler-search.md) · [exercises](exercises/C08-web-crawler-search.md)

You will be able to:

- Estimate crawl rate, bandwidth, storage and index size from a target corpus size and refresh period
- Design a URL frontier that enforces per-host politeness and RFC 9309 robots.txt rules
- Explain URL normalisation, exact-hash and SimHash near-duplicate detection, and their costs
- Design an inverted-index build and a sharded query path with BM25 and link-based signals
- Compare recrawl policies for freshness and explain AI-crawler controls and hybrid lexical + vector search

### C09 — ChatGPT-style LLM chat service

*Requirement:* Design a ChatGPT-style chat service for 10 million daily users: streamed answers that start in under 1 s, multiple models, paid tiers with token quotas, conversation history, EU data residency, and a cost per conversation you can defend.  
*Time:* 2.5h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C09-llm-chat-service.md) · [slides](slides/C09-llm-chat-service.md) · [exercises](exercises/C09-llm-chat-service.md)

You will be able to:

- Estimate the GPU fleet for a chat product by converting users into requests/s, tokens/s and GPU count, with every assumption labelled
- Design the token-streaming path (SSE) through edge, gateway and inference tiers without buffering, timeouts or lost tokens
- Explain how continuous batching, prefix caching and KV-aware routing change the capacity estimate, and when disaggregated prefill/decode pays off
- Design per-tier quotas and token-based rate limits, conversation storage and context assembly
- Diagnose failure modes (KV-cache exhaustion, cold starts, retry storms, safety-filter latency) and state SLOs, cost and energy per conversation

### C10 — Enterprise RAG assistant

*Requirement:* Design a multi-tenant assistant that answers employees' questions from their company's documents (wiki, drive, tickets, chat) with citations, never shows a document the asker cannot open, reflects edits within 15 minutes and permission revocations within 5 minutes, keeps EU tenants' data in the EU, and costs under one cent per answer.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C10-enterprise-rag-assistant.md) · [slides](slides/C10-enterprise-rag-assistant.md) · [exercises](exercises/C10-enterprise-rag-assistant.md)

You will be able to:

- Estimate index size, ingestion and re-embedding cost, query load and cost per answer for a multi-tenant RAG service
- Design connector-based ingestion with incremental sync, chunking and embeddings, and choose a tenant-isolation model
- Compare index-time and query-time permission enforcement and design permission sync as a security SLA
- Design hybrid retrieval with reranking, citations and groundedness checks, and an evaluation harness
- Diagnose indirect prompt injection from documents and design layered mitigations

### C11 — AI coding-agent platform

*Requirement:* Design a multi-tenant platform where developers assign issues to autonomous coding agents that run in cloud sandboxes for up to an hour, use tools via MCP, ask a human before risky actions, never leak secrets, stay within per-task budgets, and open a pull request — for 200,000 tasks per day.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C11-coding-agent-platform.md) · [slides](slides/C11-coding-agent-platform.md) · [exercises](exercises/C11-coding-agent-platform.md)

You will be able to:

- Estimate concurrent sessions, sandbox fleet, LLM token demand and cost per task from task volume and agent behaviour
- Compare containers, gVisor and Firecracker microVMs for running untrusted agent code, and design repo checkout caching
- Design the tool layer with MCP, secrets isolation and human approval gates
- Design durable long-running sessions with checkpoints, idempotent tools, budgets and loop detection
- Define agent-trace observability, SWE-bench-style evaluation and multi-tenant fairness of LLM capacity

### C12 — Real-time fraud detection (and recommendations)

*Requirement:* Score every card payment for fraud inline in the authorization path, at 15,000 payments/s peak, with a p99 decision latency under 100 ms, and explain every decline  
*Time:* 2h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C12-realtime-fraud-recsys.md) · [slides](slides/C12-realtime-fraud-recsys.md) · [exercises](exercises/C12-realtime-fraud-recsys.md)

You will be able to:

- Design a streaming feature pipeline and online feature store for velocity features
- Allocate a per-hop p99 latency budget and design fallbacks for each dependency
- Combine a rules engine and an ML model with shadow and canary rollouts
- Explain label delay, investigator feedback bias and model-induced selection bias, and design around them
- Design decision logs that support explanation, audit and retraining
- Adapt the same architecture to a real-time recommender and name what changes

### C13 — Telemetry & observability platform for a GPU/HPC cluster

*Requirement:* Collect GPU, node, network and facility telemetry from a 10,240-GPU cluster at 1–10 s resolution, detect failing hardware before it kills jobs, and report energy per job  
*Time:* 2h reading · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C13-gpu-cluster-telemetry.md) · [slides](slides/C13-gpu-cluster-telemetry.md) · [exercises](exercises/C13-gpu-cluster-telemetry.md)

You will be able to:

- Estimate active series, samples per second and storage for a GPU cluster's telemetry
- Explain why job IDs must not be metric labels and design the job-to-series join
- Compare Prometheus+Thanos/Mimir, VictoriaMetrics, ClickHouse and TimescaleDB for HPC telemetry
- Design retention and downsampling tiers, and explain why downsampling alone does not save space
- Design rule-based, statistical and ML anomaly detection for thermal, power and GPU hardware failures
- Compute job-level energy, including shared node power and facility overhead

### C14 — Global flash sale

*Requirement:* Sell exactly 100,000 units of a limited item worldwide at 12:00:00 UTC to an audience of 20 million, with zero oversell, one unit per customer, fair access, bots kept out, and a site that stays up for everyone else.  
*Time:* 2h reading + exercises · *Status:* `SOURCES_CHECKED` · [lesson](course/04-case-studies/C14-global-flash-sale.md) · [slides](slides/C14-global-flash-sale.md) · [exercises](exercises/C14-global-flash-sale.md)

You will be able to:

- Estimate the arrival spike, waiting-room load and safe admission rate from downstream checkout and payment capacity
- Design inventory that never oversells under extreme contention, using conditional updates, stock buckets and reservations with TTL
- Design a virtual waiting room with signed queue tickets and a fair admission policy
- Design idempotent checkout and payment integration with reservation expiry and reconciliation
- Plan bot defences, pre-scaling, degradation and multi-region placement, and explain failover risks to the zero-oversell invariant

## Part V — Interview track

### I01 — The interview playbook: CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP

*Requirement:* In 45 minutes, with a stranger watching, turn a one-line prompt into a defensible, quantified design and show the interviewer how you think about trade-offs, failure and cost.  
*Time:* 2.5h reading + 3 timed mock interviews · *Status:* `SOURCES_CHECKED` · [lesson](course/05-interview/I01-interview-playbook.md) · [slides](slides/I01-interview-playbook.md) · [exercises](exercises/I01-interview-playbook.md)

You will be able to:

- Run a system design interview with the six-step CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP framework inside a 45- or 60-minute budget
- Explain what interviewers listen for at each step and produce the matching artifact on the board
- Drive the conversation without ignoring the interviewer, and recover from redirects, gaps in knowledge and wrong turns
- State trade-offs in a falsifiable form (choice, reason, cost, switching trigger)
- Calibrate depth and scope to the level being interviewed for, from junior to principal
- Diagnose your own mock interviews against a step-by-step checklist

### I02 — Numbers & cheat sheets: latency, throughput, storage, capacity, cost & GPU numbers

*Requirement:* Produce a defensible order-of-magnitude estimate for any design prompt in under four minutes, using constants you can source and assumptions you label.  
*Time:* 1.5h reading + 1h drills · *Status:* `SOURCES_CHECKED` · [lesson](course/05-interview/I02-numbers-cheat-sheets.md) · [slides](slides/I02-numbers-cheat-sheets.md) · [exercises](exercises/I02-numbers-cheat-sheets.md)

You will be able to:

- Convert between powers of two and ten, time units, and bandwidth units without a calculator
- Explain which classic latency numbers have drifted since 2009 and which have not, and why
- Estimate peak QPS, storage growth, bandwidth and concurrency from DAU-style inputs
- Compute the downtime budget for any availability target and the availability of composed components
- Estimate LLM weight memory, KV-cache size per token, GPU count and cost per million tokens from datasheet numbers

### I03 — Question bank & rubrics: 77 questions by category and level, what good looks like, red flags

*Requirement:* Practice any system design prompt you might be asked in 2026, know which unit of this course prepares you for it, and score your answer the way an interviewer would.  
*Time:* Reference unit — 1h to read the rubric; 45–60 min per practice question · *Status:* `SOURCES_CHECKED` · [lesson](course/05-interview/I03-question-bank-rubrics.md) · [slides](slides/I03-question-bank-rubrics.md) · [exercises](exercises/I03-question-bank-rubrics.md)

You will be able to:

- Select practice questions by category and level, and map each one to the course units that prepare for it
- Score a design answer against a six-dimension rubric with level-specific anchors
- Recognize the ten most common red flags and the ten strongest signals in system design interviews
- Plan a 4- or 8-week preparation schedule tied to course units and timed mocks

### I04 — ML/LLM system design interviews: how they differ, question bank, worked answers

*Requirement:* Answer an ML or LLM system design prompt so that the interviewer sees product framing, the right metrics, a data and evaluation plan, and serving constraints quantified in tokens, GPU memory and cost.  
*Time:* 3h reading + 3 timed mocks · *Status:* `SOURCES_CHECKED` · [lesson](course/05-interview/I04-ml-llm-interviews.md) · [slides](slides/I04-ml-llm-interviews.md) · [exercises](exercises/I04-ml-llm-interviews.md)

You will be able to:

- Explain how ML/LLM system design interviews differ from classical ones in framing, metrics, data, evaluation and serving constraints
- Adapt CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP to systems whose behavior is learned rather than coded
- Define a metric ladder from business outcome to model metric to system SLI for any ML/LLM product
- Design an offline and online evaluation plan, including LLM-as-judge with calibration
- Estimate GPU count, latency budget and cost per request for an LLM or recommendation workload
