# Modern System Design

**An open, requirement-driven system design course: the classical foundations, and — above all — the new
requirements of AI-era systems.** Theory you can read, labs you can run on a laptop, and an interview track.

> Most system design material teaches 2015's architecture for 2015's interviews. Systems in 2026 also serve LLMs on
> GPUs, retrieve from vector indexes, run agents that call tools, answer to cost and energy budgets, and must keep EU
> data in the EU. This course teaches all of it — and teaches *why each box is on the diagram*.

**Status:** draft course under active development. Lessons are marked `DRAFT` or `SOURCES_CHECKED`; every lab states
its real test status. Found an error? Open an issue.

## What makes this course different

- **Requirement-first.** Every chapter starts from a concrete, quantified requirement ("serve a 70B-class model to
  10k concurrent users under a 2 s time-to-first-token SLO") and introduces building blocks only because the
  requirement needs them.
- **The requirement loop**, used in every chapter and case: *Requirement → Numbers → Design → Deep dive → Break it →
  Operate (SLO, cost, energy) → Interview angle.*
- **Mostly new, still classical.** A full classical foundation (caching, replication, sharding, consensus, queues),
  then modern requirements (platform engineering, multi-region & edge, cost, energy & carbon, supply-chain security,
  GDPR / EU AI Act) and a whole part on **AI-native systems**: LLM inference, **vLLM** and serving at scale, GPU
  infrastructure, RAG and vector search, LLM gateways, ML platforms, AI safety and governance — and **agentic
  applications**, single- and multi-agent: architectures, context and memory, security, observability and evaluation,
  and the platform that runs them, with agentic case studies.
- **Hands-on.** Labs run locally with Docker Compose or kind — load it, break it, measure it.
- **Interview-strong.** An original six-step framework — **CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP** — a
  question bank with rubrics by level, cheat sheets, and an *Interview angle* section in every chapter.
- **Sourced.** Claims link to papers, RFCs, specifications and official docs; fast-moving facts are dated.

## Start here

1. [How to use this course](course/00-orientation/00-how-to-use-this-course.md) — learning paths and the method.
2. [Requirements to numbers](course/00-orientation/01-requirements-to-numbers.md) — SLOs and estimation, used everywhere.
3. Pick a path: **learner** (in order), **practitioner** (Parts II–III first), or **interview** (Part V + case studies).

Full syllabus with learning outcomes: [SYLLABUS.md](SYLLABUS.md).

## Contents

### Part 0 — Orientation
| # | Lesson |
|---|---|
| 00 | [How to use this course](course/00-orientation/00-how-to-use-this-course.md) |
| 01 | [Requirements to numbers: SLOs, estimation, queueing](course/00-orientation/01-requirements-to-numbers.md) |

### Part I — Classical foundations
| # | Lesson |
|---|---|
| 02 | [Anatomy of a request](course/01-foundations/02-anatomy-of-a-request.md) |
| 03 | [Scaling compute and load balancing](course/01-foundations/03-scaling-compute.md) |
| 04 | [Caching everywhere](course/01-foundations/04-caching.md) |
| 05 | [Choosing storage](course/01-foundations/05-choosing-storage.md) |
| 06 | [Replication and consistency](course/01-foundations/06-replication-consistency.md) |
| 07 | [Partitioning and sharding](course/01-foundations/07-partitioning-sharding.md) |
| 08 | [Asynchronous and event-driven systems](course/01-foundations/08-async-event-driven.md) |
| 09 | [Coordination and consensus](course/01-foundations/09-coordination-consensus.md) |
| 10 | [APIs, communication and rate limiting](course/01-foundations/10-apis-communication.md) |
| 11 | [Reliability engineering](course/01-foundations/11-reliability-engineering.md) |
| 12 | [Observability](course/01-foundations/12-observability.md) |
| 13 | [Data at scale: object storage, lakehouse, search](course/01-foundations/13-data-at-scale.md) |

### Part II — Modern requirements
| # | Lesson |
|---|---|
| 14 | [Cloud-native and platform engineering](course/02-modern-requirements/14-cloud-native-platforms.md) |
| 15 | [Multi-region and edge](course/02-modern-requirements/15-multi-region-edge.md) |
| 16 | [Cost as a requirement](course/02-modern-requirements/16-cost-as-requirement.md) |
| 17 | [Energy- and carbon-aware design](course/02-modern-requirements/17-energy-carbon-aware.md) |
| 18 | [Security by design and supply chain](course/02-modern-requirements/18-security-by-design.md) |
| 19 | [Privacy, compliance and data sovereignty](course/02-modern-requirements/19-privacy-compliance-sovereignty.md) |
| 20 | [Real-time and streaming systems](course/02-modern-requirements/20-real-time-streaming.md) |

### Part III — AI-native systems
| # | Lesson |
|---|---|
| 21 | [Anatomy of LLM inference](course/03-ai-systems/21-llm-inference-anatomy.md) |
| 22 | [Serving LLMs at scale: vLLM and beyond](course/03-ai-systems/22-serving-llms-at-scale.md) |
| 23 | [GPU and accelerator infrastructure](course/03-ai-systems/23-gpu-infrastructure.md) |
| 24 | [Retrieval and vector systems (RAG)](course/03-ai-systems/24-retrieval-vector-systems.md) |
| 25 | [Agentic systems: tools, MCP, sandboxes](course/03-ai-systems/25-agentic-systems.md) |
| 26 | [LLM gateways and LLMOps](course/03-ai-systems/26-llm-gateways-llmops.md) |
| 27 | [ML platforms and data for AI](course/03-ai-systems/27-ml-platforms.md) |
| 28 | [Trust, safety and governance for AI systems](course/03-ai-systems/28-ai-trust-safety-governance.md) |
| 29 | [Agent architectures and orchestration](course/03-ai-systems/29-agent-architectures-orchestration.md) |
| 30 | [Context engineering and agent memory](course/03-ai-systems/30-context-engineering-memory.md) |
| 31 | [Securing agentic systems](course/03-ai-systems/31-securing-agentic-systems.md) |
| 32 | [Observing and evaluating agents](course/03-ai-systems/32-observing-evaluating-agents.md) |
| 33 | [Agent platform runtime: queues, tenancy, fairness, rollout](course/03-ai-systems/33-agent-platform-runtime.md) |

### Part IV — Case studies
| # | Classical | # | AI era | # | Agentic |
|---|---|---|---|---|---|
| C01 | [URL shortener + rate limiter](course/04-case-studies/C01-url-shortener-rate-limiter.md) | C09 | [ChatGPT-style LLM chat service](course/04-case-studies/C09-llm-chat-service.md) | C11 | [AI coding-agent platform](course/04-case-studies/C11-coding-agent-platform.md) |
| C02 | [News feed](course/04-case-studies/C02-news-feed.md) | C10 | [Enterprise RAG assistant](course/04-case-studies/C10-enterprise-rag-assistant.md) | C15 | [Customer-support agent platform](course/04-case-studies/C15-support-agent-platform.md) |
| C03 | [Chat and presence](course/04-case-studies/C03-chat-presence.md) | C12 | [Real-time fraud detection](course/04-case-studies/C12-realtime-fraud-recsys.md) | C16 | [Deep-research multi-agent system](course/04-case-studies/C16-deep-research-agents.md) |
| C04 | [Video upload and streaming](course/04-case-studies/C04-video-streaming.md) | C13 | [GPU/HPC cluster telemetry](course/04-case-studies/C13-gpu-cluster-telemetry.md) | C17 | [Workflow-automation agent](course/04-case-studies/C17-workflow-automation-agent.md) |
| C05 | [Ride-hailing and proximity](course/04-case-studies/C05-ride-hailing-proximity.md) | | | | |
| C06 | [Payments and ledger](course/04-case-studies/C06-payments-ledger.md) | | | | |
| C07 | [Distributed key-value store](course/04-case-studies/C07-distributed-kv-store.md) | | | | |
| C08 | [Web crawler and search](course/04-case-studies/C08-web-crawler-search.md) | | | | |
| C14 | [Global flash sale](course/04-case-studies/C14-global-flash-sale.md) | | | | |

### Part V — Interview track
| # | Lesson |
|---|---|
| I01 | [The interview playbook: CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP](course/05-interview/I01-interview-playbook.md) |
| I02 | [Numbers and cheat sheets](course/05-interview/I02-numbers-cheat-sheets.md) |
| I03 | [Question bank and rubrics](course/05-interview/I03-question-bank-rubrics.md) |
| I04 | [ML and LLM system design interviews](course/05-interview/I04-ml-llm-interviews.md) |

## Repository layout

```
course/       lessons (the canonical text)        labs/        runnable labs (Docker Compose / kind)
slides/       text-first slide outlines           exercises/   exercises with reasoned answers
```

Every lesson has a matching slide outline and exercise set with the same file name.

## Labs

Labs need Docker with Compose v2+; a few use [kind](https://kind.sigs.k8s.io/). They are CPU-only by default and cost
nothing to run locally. Each lab README states its **test status** (`illustrative`, `syntax-reviewed`,
`runtime-tested`) — nothing is claimed as tested unless it was run.

## Related courses

- [Security, Explained Simply](https://github.com/MSKazemi/security) — OAuth 2.0, OIDC, Keycloak, JWT, API security.
- [AI Agent Systems Course](https://github.com/MSKazemi/ai-agent-systems-course) — MCP, A2A, LangGraph, hands-on agents.

## Author

**Mohsen Seyedkazemi Ardebili** — AI Platform & Agentic Systems Engineer.
[mskazemi.github.io](https://mskazemi.github.io) · [GitHub](https://github.com/MSKazemi) ·
[LinkedIn](https://www.linkedin.com/in/mskazemi/)

All companies, products and logos mentioned are trademarks of their respective owners and are referenced only to
identify the technologies discussed. The running example "Lumen" is fictional.
