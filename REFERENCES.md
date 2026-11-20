# References

Every source cited by the lessons, grouped by unit. Generated from each lesson's `## References` section by
`scripts/build_references.py`; do not edit by hand. Citation numbers match the numbers used inside each lesson.

**935 distinct URLs** across **1066 references** in **47 units**. Source status per unit: `SOURCES_CHECKED` = every source was opened and checked against the claim it supports; `DRAFT` = written but sources not fully verified yet. Fast-moving facts carry an “as of 2026-11” marker in the lesson text. Nothing here is legal advice.

## Most widely used sources

Cited by three or more units.

| Source | Units |
|---|---|
| <https://www.nvidia.com/en-us/data-center/h100/> | 00, 21, 22, 23, C09, I02, I04 |
| <https://arxiv.org/abs/2407.21783> | 21, 23, 27, C13, I02 |
| <https://docs.vllm.ai/en/latest/design/metrics.html> | 21, 22, C09, I02, I04 |
| <https://eur-lex.europa.eu/eli/reg/2024/1689/oj> | 19, 28, C09, C10, C12 |
| <https://github.com/vllm-project/vllm/releases/tag/v0.34.0> | 00, 21, 22, 23, I02 |
| <https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett> | 05, 06, 07, 09, 15 |
| <https://arxiv.org/abs/1910.02054> | 23, 27, I02, I04 |
| <https://arxiv.org/abs/2309.06180> | 00, 21, 22, C09 |
| <https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/> | 10, C01, C06, C14 |
| <https://docs.stripe.com/api/idempotent_requests> | 08, 10, C06, C14 |
| <https://eur-lex.europa.eu/eli/reg/2016/679/oj> | 19, C09, C10, C12 |
| <https://gateway-api-inference-extension.sigs.k8s.io/> | 03, 14, 26, C09 |
| <https://github.com/open-telemetry/semantic-conventions-genai> | 12, 25, 26, C11 |
| <https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/> | 27, C02, C12, I04 |
| <https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf> | 06, 07, 09, C07 |
| <https://www.usenix.org/conference/nsdi20/presentation/agache> | 14, 18, 25, C11 |
| <https://arxiv.org/abs/2106.09685> | 27, I02, I04 |
| <https://arxiv.org/abs/2302.12173> | 25, 28, C10 |
| <https://arxiv.org/abs/2312.06674> | 28, C09, I04 |
| <https://developers.google.com/machine-learning/guides/rules-of-ml> | 27, C12, I04 |
| <https://docs.vllm.ai/en/latest/configuration/optimization.html> | 21, 22, C09 |
| <https://docs.vllm.ai/en/latest/design/prefix_caching.html> | 04, 22, C09 |
| <https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html> | 21, 22, 26 |
| <https://github.com/pgvector/pgvector> | 05, 24, C10 |
| <https://gvisor.dev/docs/> | 18, 25, C11 |

## Most-cited hosts

| Host | Distinct URLs |
|---|---|
| arxiv.org | 83 |
| github.com | 73 |
| rfc-editor.org | 52 |
| doi.org | 43 |
| docs.aws.amazon.com | 29 |
| kubernetes.io | 24 |
| usenix.org | 23 |
| aws.amazon.com | 22 |
| docs.vllm.ai | 16 |
| eur-lex.europa.eu | 14 |
| huggingface.co | 11 |
| nvidia.com | 11 |
| opentelemetry.io | 10 |
| cncf.io | 9 |
| kafka.apache.org | 9 |

## Part 0 — Orientation

### 00 — How to use this course: paths, the requirement loop, what changed in system design

Lesson: [`course/00-orientation/00-how-to-use-this-course.md`](course/00-orientation/00-how-to-use-this-course.md) · source status: `DRAFT`

1. A. Vaswani et al., *Attention Is All You Need*, arXiv:1706.03762, June 2017 (NeurIPS 2017). https://arxiv.org/abs/1706.03762
2. OpenAI, *Introducing ChatGPT*, 30 November 2022. https://openai.com/index/chatgpt/
3. W. Kwon, Z. Li, S. Zhuang, Y. Sheng, L. Zheng, C. H. Yu, J. E. Gonzalez, H. Zhang, I. Stoica, *Efficient Memory Management for Large Language Model Serving with PagedAttention*, Proc. ACM SOSP 2023; arXiv:2309.06180. https://arxiv.org/abs/2309.06180
4. vLLM project, *Release v0.34.0*, GitHub, 16 November 2026. https://github.com/vllm-project/vllm/releases/tag/v0.34.0
5. NVIDIA, *NVIDIA Tesla P100 Data Sheet* (732 GB/s HBM2; 300 W max power). https://images.nvidia.com/content/tesla/pdf/nvidia-tesla-p100-datasheet.pdf
6. NVIDIA, *NVIDIA H100 Tensor Core GPU* product page (H100 SXM: 3.35 TB/s; up to 700 W, configurable). https://www.nvidia.com/en-us/data-center/h100/
7. NVIDIA, *NVIDIA DGX B200* product page (8 Blackwell GPUs; 1,440 GB total GPU memory; 64 TB/s HBM3e bandwidth; ≈ 14.3 kW max). https://www.nvidia.com/en-us/data-center/dgx-b200/
8. International Energy Agency, *Energy and AI*, 10 April 2025, Executive summary. https://www.iea.org/reports/energy-and-ai/executive-summary
9. Uptime Institute, *Global PUEs — are they going anywhere?*, Uptime Institute Journal, 4 December 2023. https://journal.uptimeinstitute.com/global-pues-are-they-going-anywhere/
10. European Commission, *Legal framework of EU data protection* (GDPR in force 24 May 2016, applies since 25 May 2018). https://commission.europa.eu/law/law-topic/data-protection/legal-framework-eu-data-protection_en
11. European Commission, *NIS2 Directive* policy page. https://digital-strategy.ec.europa.eu/en/policies/nis2-directive
12. European Commission, *Data Act* policy page. https://digital-strategy.ec.europa.eu/en/policies/data-act
13. European Commission, *Cyber Resilience Act* policy page. https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act
14. European Commission, *AI Act — Regulatory framework for AI* policy page. https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
15. Regulation (EU) 2026/1744 (Digital Omnibus amendments to the AI Act), Official Journal of the EU, 24 July 2026; amended Article 113. https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng
16. CISA, *Emergency Directive 21-01: Mitigate SolarWinds Orion Code Compromise*, 13 December 2020 (since closed). https://www.cisa.gov/news-events/directives/ed-21-01-mitigate-solarwinds-orion-code-compromise
17. Executive Order 14028, *Improving the Nation's Cybersecurity*, 12 May 2021, published in the Federal Register on 17 May 2021. https://www.federalregister.gov/documents/2021/05/17/2021-10460/improving-the-nations-cybersecurity
18. NIST National Vulnerability Database, *CVE-2021-44228*, published 10 December 2021. https://nvd.nist.gov/vuln/detail/CVE-2021-44228
19. SLSA project, *SLSA v1.0 is now final!*, 19 April 2023. https://slsa.dev/blog/2023/04/slsa-v1-final
20. NIST National Vulnerability Database, *CVE-2024-3094*, published 29 March 2024. https://nvd.nist.gov/vuln/detail/CVE-2024-3094
21. Kubernetes blog, *10 Years of Kubernetes*, 6 June 2024 (v1.0 released 21 July 2015). https://kubernetes.io/blog/2024/06/06/10-years-of-kubernetes/
22. Kubernetes, *Releases*. https://kubernetes.io/releases/
23. CNCF TAG App Delivery, *Platforms White Paper*, v1, 2023. https://tag-app-delivery.cncf.io/whitepapers/platforms/
24. W3Techs, *Usage statistics of HTTP/3 for websites*, November 2026. https://w3techs.com/technologies/details/ce-http3

### 01 — Requirements to numbers: SLIs/SLOs, estimation, latency numbers, Little's law, queueing

Lesson: [`course/00-orientation/01-requirements-to-numbers.md`](course/00-orientation/01-requirements-to-numbers.md) · source status: `DRAFT`

1. B. Beyer, C. Jones, J. Petoff, N. R. Murphy (eds.), *Site Reliability Engineering*, O'Reilly, 2016, ch. 4 *Service Level Objectives* (SLI and SLO definitions). https://sre.google/sre-book/service-level-objectives/
2. Ibid., ch. 3 *Embracing Risk* (error budgets). https://sre.google/sre-book/embracing-risk/
3. B. Beyer, N. R. Murphy, D. K. Rensin, K. Kawahara, S. Thorne (eds.), *The Site Reliability Workbook*, O'Reilly, 2018, ch. 2 *Implementing SLOs*, https://sre.google/workbook/implementing-slos/ ; ch. 5 *Alerting on SLOs* (14.4× burn rate = 2% of a 30-day budget in 1 hour), https://sre.google/workbook/alerting-on-slos/
4. J. D. C. Little, *A Proof for the Queuing Formula: L = λW*, Operations Research 9(3):383–387, 1961. https://doi.org/10.1287/opre.9.3.383
5. J. D. C. Little, *Little's Law as Viewed on Its 50th Anniversary*, Operations Research 59(3):536–549, 2011. https://doi.org/10.1287/opre.1110.0940
6. J. Dean, *Designs, Lessons and Advice from Building Large Distributed Systems*, keynote, LADIS 2009 ("Numbers Everyone Should Know"). https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf
7. C. Scott, *Latency Numbers Every Programmer Should Know* (interactive, with per-year extrapolation; based on P. Norvig's 2002 numbers). https://colin-scott.github.io/personal_website/research/interactive_latency.html
8. I. N. Bozkurt, W. Aqeel, D. Bhattacherjee, B. Chandrasekaran, P. B. Godfrey, G. Laughlin, B. M. Maggs, A. Singla, *Dissecting Latency in the Internet's Fiber Infrastructure*, arXiv:1811.10737, 2018 (speed of light in fibre ≈ 204,000 km/s). https://arxiv.org/abs/1811.10737
9. Samsung Electronics, *Samsung NVMe SSD 990 PRO Data Sheet*, Rev. 2.0 (sequential read 7,450 MB/s; random read QD1 22K IOPS). https://download.semiconductor.samsung.com/resources/data-sheet/samsung_nvme_ssd_990_pro_datasheet_rev.2.0.pdf
10. WonderNetwork, *Global Ping Statistics: London to New York* (daily averages ≈ 70–71 ms, 5–19 Nov 2026). https://wondernetwork.com/pings/London/New%20York
11. M. Harchol-Balter, *Performance Modeling and Design of Computer Systems: Queueing Theory in Action*, Cambridge University Press, 2013 (M/M/1 response-time distribution; M/M/k). https://doi.org/10.1017/CBO9781139226424
12. J. F. C. Kingman, *The single server queue in heavy traffic*, Mathematical Proceedings of the Cambridge Philosophical Society 57(4):902–904, 1961. https://doi.org/10.1017/S0305004100036094
13. J. Dean, L. A. Barroso, *The Tail at Scale*, Communications of the ACM 56(2):74–80, February 2013. https://www.barroso.org/publications/TheTailAtScale.pdf
14. Grafana Labs, *Open and closed models*, k6 documentation (coordinated omission; `constant-arrival-rate` and `ramping-arrival-rate` executors). https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/
15. OpenAI, *What are tokens and how to count them?*, OpenAI Help Center (1 token ≈ 4 characters ≈ ¾ word in English). https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
16. L. Kleinrock, *Queueing Systems, Volume 1: Theory*, Wiley, 1975 (the G/M/1 queue; D/M/1 as a special case). https://www.wiley.com/en-us/Queueing+Systems%2C+Volume+1%3A+Theory-p-9780471491101
17. Y. Zhong, S. Liu, J. Chen, J. Hu, Y. Zhu, X. Liu, X. Jin, H. Zhang, *DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving*, Proc. USENIX OSDI 2024. https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin
18. International Energy Agency, *Energy and AI*, April 2025, Executive summary. https://www.iea.org/reports/energy-and-ai/executive-summary

## Part I — Classical foundations

### 02 — Anatomy of a request: DNS, TCP, QUIC/HTTP/3, TLS 1.3, proxies, CDN edge

Lesson: [`course/01-foundations/02-anatomy-of-a-request.md`](course/01-foundations/02-anatomy-of-a-request.md) · source status: `DRAFT`

1. P. Mockapetris, RFC 1034, *Domain Names — Concepts and Facilities*, 1987. https://www.rfc-editor.org/rfc/rfc1034
2. P. Mockapetris, RFC 1035, *Domain Names — Implementation and Specification*, 1987. https://www.rfc-editor.org/rfc/rfc1035
3. M. Andrews, RFC 2308, *Negative Caching of DNS Queries (DNS NCACHE)*, 1998, §5. https://www.rfc-editor.org/rfc/rfc2308.html
4. B. Schwartz, M. Bishop, E. Nygren, RFC 9460, *Service Binding and Parameter Specification via the DNS (SVCB and HTTPS Resource Records)*, November 2023. https://www.rfc-editor.org/info/rfc9460
5. D. Lawrence, W. Kumari, P. Sood, RFC 8767, *Serving Stale Data to Improve DNS Resiliency*, March 2020, §4–5. https://www.rfc-editor.org/rfc/rfc8767.html
6. E. Rescorla, RFC 8446, *The Transport Layer Security (TLS) Protocol Version 1.3*, August 2018, §2.3, §8, Appendix E.5. https://www.rfc-editor.org/rfc/rfc8446.html
7. E. Rescorla, K. Oku, N. Sullivan, C. A. Wood, RFC 9849, *TLS Encrypted Client Hello*, March 2026. https://www.rfc-editor.org/info/rfc9849
8. J. Iyengar, M. Thomson (eds.), RFC 9000, *QUIC: A UDP-Based Multiplexed and Secure Transport*, May 2021, §9 (connection migration); M. Thomson, S. Turner, RFC 9001, *Using TLS to Secure QUIC*, May 2021; J. Iyengar, I. Swett, RFC 9002, *QUIC Loss Detection and Congestion Control*, May 2021. https://www.rfc-editor.org/rfc/rfc9000.html
9. M. Thomson, C. Benfield (eds.), RFC 9113, *HTTP/2*, June 2022 (obsoletes RFC 7540 and RFC 8740). https://www.rfc-editor.org/rfc/rfc9113.html
10. M. Bishop (ed.), RFC 9114, *HTTP/3*, June 2022; C. Krasic, M. Bishop, A. Frindell, RFC 9204, *QPACK: Field Compression for HTTP/3*, June 2022. https://www.rfc-editor.org/rfc/rfc9114.html
11. W. Eddy (ed.), RFC 9293, *Transmission Control Protocol (TCP)*, August 2022 (obsoletes RFC 793). https://www.rfc-editor.org/rfc/rfc9293.html
12. J. Chu, N. Dukkipati, Y. Cheng, M. Mathis, RFC 6928, *Increasing TCP's Initial Window*, April 2013 (Experimental). https://www.rfc-editor.org/info/rfc6928
13. Y. Cheng, J. Chu, S. Radhakrishnan, A. Jain, RFC 7413, *TCP Fast Open*, December 2014 (Experimental). https://www.rfc-editor.org/info/rfc7413
14. M. Thomson, M. Nottingham, W. Tarreau, RFC 8470, *Using Early Data in HTTP*, September 2018. https://www.rfc-editor.org/info/rfc8470
15. R. Fielding, M. Nottingham, J. Reschke (eds.), RFC 9110, *HTTP Semantics*, June 2022; RFC 9111, *HTTP Caching*, June 2022. https://www.rfc-editor.org/info/rfc9110
16. D. Schinazi, T. Pauly, RFC 8305, *Happy Eyeballs Version 2: Better Connectivity Using Concurrency*, December 2017. https://www.rfc-editor.org/info/rfc8305
17. Amazon Web Services, *Edit attributes for your Application Load Balancer — Connection idle timeout*, Elastic Load Balancing documentation. https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-load-balancer-attributes.html
18. A. Petersson, M. Nilsson, RFC 7239, *Forwarded HTTP Extension*, June 2014, https://www.rfc-editor.org/info/rfc7239 ; W. Tarreau, *The PROXY protocol*, HAProxy Technologies, https://www.haproxy.org/download/3.4/doc/proxy-protocol.txt
19. J. Abley, K. Lindqvist, RFC 4786, *Operation of Anycast Services* (BCP 126), December 2006. https://www.rfc-editor.org/info/rfc4786
20. W3Techs, *Usage statistics of HTTP/3 for websites*, November 2026. https://w3techs.com/technologies/details/ce-http3
21. Cloudflare, *The 2025 Cloudflare Radar Year in Review*, December 2025. https://blog.cloudflare.com/radar-2025-year-in-review/
22. I. N. Bozkurt, W. Aqeel, D. Bhattacherjee, B. Chandrasekaran, P. B. Godfrey, G. Laughlin, B. M. Maggs, A. Singla, *Dissecting Latency in the Internet's Fiber Infrastructure*, arXiv:1811.10737, 2018 (speed of light in fibre ≈ 2/3 c ≈ 204,000 km/s). https://arxiv.org/abs/1811.10737
23. X. Zhang, S. Jin, Y. He, A. Hassan, Z. M. Mao, F. Qian, Z.-L. Zhang, *QUIC is not Quick Enough over Fast Internet*, Proc. ACM Web Conference (WWW) 2024, pp. 2713–2722; arXiv:2310.09423. https://arxiv.org/abs/2310.09423
24. S. Janardhan, *More details about the October 4 outage*, Engineering at Meta, 5 October 2021. https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/
25. Amazon Web Services, *Summary of the Amazon DynamoDB Service Disruption in the Northern Virginia (US-EAST-1) Region*, October 2025. https://aws.amazon.com/message/101925/

### 03 — Scaling compute: stateless services, L4/L7 load balancing, algorithms, health checks, autoscaling

Lesson: [`course/01-foundations/03-scaling-compute.md`](course/01-foundations/03-scaling-compute.md) · source status: `DRAFT`

1. M. Mitzenmacher, *The Power of Two Choices in Randomized Load Balancing*, IEEE Transactions on Parallel and Distributed Systems 12(10):1094–1104, October 2001. https://www.eecs.harvard.edu/~michaelm/postscripts/tpds2001.pdf
2. Y. Azar, A. Z. Broder, A. R. Karlin, E. Upfal, *Balanced Allocations*, SIAM Journal on Computing 29(1):180–200, 1999. https://homes.cs.washington.edu/~karlin/papers/AzarBKU99.pdf
3. M. Mitzenmacher, *How Useful Is Old Information?*, IEEE Transactions on Parallel and Distributed Systems 11(1):6–20, January 2000. https://doi.org/10.1109/71.824633
4. D. Karger, E. Lehman, T. Leighton, R. Panigrahy, M. Levine, D. Lewin, *Consistent Hashing and Random Trees*, Proc. STOC 1997, pp. 654–663, https://doi.org/10.1145/258533.258660 ; V. Mirrokni, M. Thorup, M. Zadimoghaddam, *Consistent Hashing with Bounded Loads*, Proc. SODA 2018, pp. 587–604, arXiv:1608.01350, https://arxiv.org/abs/1608.01350
5. D. E. Eisenbud et al., *Maglev: A Fast and Reliable Software Network Load Balancer*, Proc. USENIX NSDI 2016, pp. 523–535. https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/eisenbud
6. Envoy project, *Supported load balancers* and *Panic threshold*, Envoy documentation (latest). https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers and https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/panic_threshold
7. HAProxy, *Configuration Manual*, version 3.4 (`balance random(<draws>)`, `hash-type`, `hash-balance-factor`, `slowstart`, environment variables). https://git.haproxy.org/?p=haproxy-3.4.git;a=blob_plain;f=doc/configuration.txt
8. N. J. Gunther, *Guerrilla Capacity Planning: A Tactical Approach to Planning for Highly Scalable Applications and Services*, Springer, 2007 (Universal Scalability Law). https://doi.org/10.1007/978-3-540-31010-5
9. NGINX, *Module ngx_http_upstream_module* (`random [two [method]]`, `least_conn`) and *Module ngx_http_upstream_hc_module* ("available as part of our commercial subscription"). https://nginx.org/en/docs/http/ngx_http_upstream_module.html and https://nginx.org/en/docs/http/ngx_http_upstream_hc_module.html
10. Kubernetes, *Horizontal Pod Autoscaling* (algorithm, 15 s sync period, 0.1 tolerance, 300 s downscale stabilisation; per-HPA tolerance stable since v1.37). https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/
11. Kubernetes, *Releases* (latest minor 1.37). https://kubernetes.io/releases/
12. Kubernetes blog, *Kubernetes 1.35: In-Place Pod Resize Graduates to Stable*, 19 December 2025. https://kubernetes.io/blog/2025/12/19/kubernetes-v1-35-in-place-pod-resize-ga/
13. Kubernetes, *Pod termination* (default `terminationGracePeriodSeconds` 30 s). https://kubernetes.io/docs/concepts/workloads/pods/pod-termination/
14. Kubernetes, *EndpointSlices — Conditions* (ready, serving, terminating). https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/
15. Amazon Web Services, *Edit target group attributes for your Application Load Balancer* (deregistration delay default 300 s; slow start mode). https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html
16. Amazon Web Services, *Predictive scaling for Amazon EC2 Auto Scaling*. https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-predictive-scaling.html
17. Google Cloud, *Scaling based on predictions* (Compute Engine predictive autoscaling). https://docs.cloud.google.com/compute/docs/autoscaler/predictive-autoscaling
18. M. Brooker, *Exponential Backoff And Jitter*, AWS Architecture Blog, 4 March 2015. https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
19. *Handling Overload*, in B. Beyer, C. Jones, J. Petoff, N. R. Murphy (eds.), *Site Reliability Engineering*, O'Reilly, 2016, ch. 21; and *Addressing Cascading Failures*, ch. 22. https://sre.google/sre-book/handling-overload/ and https://sre.google/sre-book/addressing-cascading-failures/
20. *Load Balancing in the Datacenter*, in *Site Reliability Engineering*, O'Reilly, 2016, ch. 20 (subsetting). https://sre.google/sre-book/load-balancing-datacenter/
21. J. Dean, L. A. Barroso, *The Tail at Scale*, Communications of the ACM 56(2):74–80, February 2013. https://www.barroso.org/publications/TheTailAtScale.pdf
22. Kubernetes SIGs, *Gateway API Inference Extension*. https://gateway-api-inference-extension.sigs.k8s.io/
23. L. A. Barroso, U. Hölzle, *The Case for Energy-Proportional Computing*, IEEE Computer 40(12):33–37, December 2007. https://doi.org/10.1109/MC.2007.443

### 04 — Caching everywhere

Lesson: [`course/01-foundations/04-caching.md`](course/01-foundations/04-caching.md) · source status: `SOURCES_CHECKED`

1. R. Nishtala et al., "Scaling Memcache at Facebook," NSDI 2013. https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala
2. A. Vattani, F. Chierichetti, K. Lowenstein, "Optimal Probabilistic Cache Stampede Prevention," PVLDB 8(8):886–897, 2015. DOI 10.14778/2757807.2757813. https://www.vldb.org/pvldb/vol8/p886-vattani.pdf
3. D. Karger et al., "Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web," STOC 1997. https://dl.acm.org/doi/10.1145/258533.258660
4. Memcached project, "memcached: a distributed memory object caching system." https://memcached.org/
5. E. O'Neil, P. O'Neil, G. Weikum, "The LRU-K Page Replacement Algorithm for Database Disk Buffering," SIGMOD 1993. https://dl.acm.org/doi/10.1145/170035.170081
6. N. Megiddo, D. Modha, "ARC: A Self-Tuning, Low Overhead Replacement Cache," FAST 2003. https://www.usenix.org/conference/fast-03/arc-self-tuning-low-overhead-replacement-cache
7. G. Einziger, R. Friedman, B. Manes, "TinyLFU: A Highly Efficient Cache Admission Policy," ACM Transactions on Storage 13(4), 2017, DOI 10.1145/3149371; preprint arXiv:1512.00727. https://arxiv.org/abs/1512.00727
8. J. Yang, Y. Zhang, Z. Qiu, Y. Yue, R. Vinayak, "FIFO Queues Are All You Need for Cache Eviction," SOSP 2023. https://dl.acm.org/doi/10.1145/3600006.3613147
9. Y. Zhang, J. Yang, Y. Yue, Y. Vigfusson, K. V. Rashmi, "SIEVE is Simpler than LRU: an Efficient Turn-Key Eviction Algorithm for Web Caches," NSDI 2024. https://www.usenix.org/conference/nsdi24/presentation/zhang-yazhuo
10. Redis documentation, "Key eviction." https://redis.io/docs/latest/develop/reference/eviction/
11. Redis documentation, "Redis cluster specification." https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/
12. B. Manes, Caffeine wiki, "Efficiency." https://github.com/ben-manes/caffeine/wiki/Efficiency
13. Redis Ltd., "Licenses" (RSALv2, SSPLv1 and, from Redis 8, AGPLv3). https://redis.io/legal/licenses/
14. Valkey project (Linux Foundation), releases. https://github.com/valkey-io/valkey/releases
15. Memcached documentation, "Performance" (worker threads, slab classes). https://docs.memcached.org/serverguide/performance/
16. vLLM documentation, "Automatic Prefix Caching" (design). https://docs.vllm.ai/en/latest/design/prefix_caching.html
17. R. Fielding, M. Nottingham, J. Reschke, "HTTP Caching," RFC 9111, 2022. https://www.rfc-editor.org/rfc/rfc9111
18. M. Nottingham, "HTTP Cache-Control Extensions for Stale Content," RFC 5861, 2010. https://www.rfc-editor.org/rfc/rfc5861
19. M. Andrews, "Negative Caching of DNS Queries (DNS NCACHE)," RFC 2308, 1998. https://www.rfc-editor.org/rfc/rfc2308
20. B. Cooper et al., "Benchmarking Cloud Serving Systems with YCSB," SoCC 2010; YCSB `ZipfianGenerator` (constant 0.99). https://github.com/brianfrankcooper/YCSB/blob/master/core/src/main/java/site/ycsb/generator/ZipfianGenerator.java
21. S. Ludin, M. Nottingham, Y. Wu, "Targeted HTTP Cache Control," RFC 9213, 2022. https://www.rfc-editor.org/rfc/rfc9213
22. M. Nottingham, "The Cache-Status HTTP Response Header Field," RFC 9211, 2022. https://www.rfc-editor.org/rfc/rfc9211

### 05 — Choosing storage

Lesson: [`course/01-foundations/05-choosing-storage.md`](course/01-foundations/05-choosing-storage.md) · source status: `SOURCES_CHECKED`

1. R. Bayer, E. McCreight, "Organization and Maintenance of Large Ordered Indexes," Acta Informatica 1(3), 1972. https://doi.org/10.1007/BF00288683
2. P. O'Neil, E. Cheng, D. Gawlick, E. O'Neil, "The Log-Structured Merge-Tree (LSM-Tree)," Acta Informatica 33(4), 1996. https://www.cs.umb.edu/~poneil/lsmtree.pdf
3. RocksDB wiki, "RocksDB Tuning Guide." https://github.com/facebook/rocksdb/wiki/RocksDB-Tuning-Guide
4. M. Athanassoulis et al., "Designing Access Methods: The RUM Conjecture," EDBT 2016. https://openproceedings.org/2016/conf/edbt/paper-12.pdf
5. B. H. Bloom, "Space/Time Trade-offs in Hash Coding with Allowable Errors," Communications of the ACM 13(7), 1970. https://doi.org/10.1145/362686.362692
6. H. Berenson, P. Bernstein, J. Gray, J. Melton, E. O'Neil, P. O'Neil, "A Critique of ANSI SQL Isolation Levels," SIGMOD 1995; MSR-TR-95-51; arXiv:cs/0701157. https://arxiv.org/abs/cs/0701157
7. PostgreSQL 18 documentation, "13.2 Transaction Isolation." https://www.postgresql.org/docs/18/transaction-iso.html
8. D. R. K. Ports, K. Grittner, "Serializable Snapshot Isolation in PostgreSQL," PVLDB 5(12), 2012. https://vldb.org/pvldb/vol5/p1850_danrkports_vldb2012.pdf
9. Jepsen, "MySQL 8.0.34," analysis, 2023-12-19. https://jepsen.io/analyses/mysql-8.0.34
10. PostgreSQL 18 documentation, "24.1.5 Preventing Transaction ID Wraparound Failures." https://www.postgresql.org/docs/18/routine-vacuuming.html
11. M. J. Cahill, U. Röhm, A. D. Fekete, "Serializable Isolation for Snapshot Databases," SIGMOD 2008. https://doi.org/10.1145/1376616.1376690
12. J. C. Corbett et al., "Spanner: Google's Globally-Distributed Database," OSDI 2012. https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
13. R. Taft et al., "CockroachDB: The Resilient Geo-Distributed SQL Database," SIGMOD 2020. https://doi.org/10.1145/3318464.3386134
14. PostgreSQL Global Development Group, "PostgreSQL 18 Released!" 2025-09-25. https://www.postgresql.org/about/news/postgresql-18-released-3142/
15. pgvector repository, tags (v0.8.7 latest as of 2026-11). https://github.com/pgvector/pgvector
16. Neon documentation, "The lakebase architecture" (architecture overview). https://neon.com/docs/introduction/architecture-overview
17. A. Ghodsi, A. Tavakoli-Shiraji, P. Wendell, R. Xin, M. Zaharia, "Databricks + Neon," Databricks blog, 2025-05-14. https://www.databricks.com/blog/databricks-neon
18. AWS, "Amazon Aurora DSQL is now generally available," 2025-05-27. https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-aurora-dsql-generally-available/
19. AWS, Aurora DSQL User Guide, "Concurrency control in Aurora DSQL." https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html
20. SlateDB project. https://slatedb.io/
21. PingCAP, TiDB documentation, "TiDB Storage" (Regions, Raft, Percolator) and "TiDB Transaction Isolation Levels." https://docs.pingcap.com/tidb/stable/tidb-storage/ and https://docs.pingcap.com/tidb/stable/transaction-isolation-levels/
22. Yugabyte, YugabyteDB documentation, "DocDB sharding layer," "Replication in DocDB" and "Transaction isolation levels." https://docs.yugabyte.com/stable/architecture/docdb-sharding/, https://docs.yugabyte.com/stable/architecture/docdb-replication/replication/ and https://docs.yugabyte.com/stable/architecture/transactions/isolation-levels/

### 06 — Replication & consistency

Lesson: [`course/01-foundations/06-replication-consistency.md`](course/01-foundations/06-replication-consistency.md) · source status: `SOURCES_CHECKED`

1. PostgreSQL 18 documentation, "19.5 Write Ahead Log" (synchronous_commit), "19.6 Replication" (synchronous_standby_names, max_slot_wal_keep_size) and "26.2 Log-Shipping Standby Servers." https://www.postgresql.org/docs/18/runtime-config-wal.html, https://www.postgresql.org/docs/18/runtime-config-replication.html and https://www.postgresql.org/docs/18/warm-standby.html
2. PostgreSQL 18 documentation, "27.2 The Cumulative Statistics System — pg_stat_replication." https://www.postgresql.org/docs/18/monitoring-stats.html
3. G. DeCandia et al., "Dynamo: Amazon's Highly Available Key-value Store," SOSP 2007. https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
4. E. Brewer, "Towards Robust Distributed Systems," PODC 2000 keynote. https://people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf
5. S. Gilbert, N. Lynch, "Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services," ACM SIGACT News 33(2), pp. 51–59, 2002. https://doi.org/10.1145/564585.564601
6. D. Abadi, "Consistency Tradeoffs in Modern Distributed Database System Design: CAP Is Only Part of the Story," IEEE Computer 45(2), pp. 37–42, 2012. https://doi.org/10.1109/MC.2012.33; author copy https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf
7. E. Brewer, "CAP Twelve Years Later: How the 'Rules' Have Changed," IEEE Computer 45(2), pp. 23–29, 2012. https://doi.org/10.1109/MC.2012.37
8. D. Terry, A. Demers, K. Petersen, M. Spreitzer, M. Theimer, B. Welch, "Session Guarantees for Weakly Consistent Replicated Data," Proc. 3rd Int. Conf. on Parallel and Distributed Information Systems (PDIS), 1994, pp. 140–149. https://doi.org/10.1109/PDIS.1994.331722
9. M. Kleppmann, "Please stop calling databases CP or AP," 2015-05-11. https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html
10. Jepsen, "Consistency Models." https://jepsen.io/consistency/models
11. M. Shapiro, N. Preguiça, C. Baquero, M. Zawirski, "Conflict-free Replicated Data Types," SSS 2011, LNCS 6976, pp. 386–400. https://doi.org/10.1007/978-3-642-24550-3_29
12. M. Herlihy, J. Wing, "Linearizability: A Correctness Condition for Concurrent Objects," ACM TOPLAS 12(3), pp. 463–492, 1990. https://doi.org/10.1145/78969.78972
13. L. Lamport, "How to Make a Multiprocessor Computer That Correctly Executes Multiprocess Programs," IEEE Transactions on Computers C-28(9), pp. 690–691, 1979. https://doi.org/10.1109/TC.1979.1675439
14. J. C. Corbett et al., "Spanner: Google's Globally-Distributed Database," OSDI 2012. https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
15. Patroni documentation. https://patroni.readthedocs.io/
16. Jepsen, analyses index. https://jepsen.io/analyses
17. Jepsen, "MySQL 8.0.34," 2023-12-19 (uses the Elle checker). https://jepsen.io/analyses/mysql-8.0.34
18. M. Kleppmann, A. Wiggins, P. van Hardenberg, M. McGranaghan, "Local-First Software: You Own Your Data, in Spite of the Cloud," Onward! 2019. https://www.inkandswitch.com/local-first/
19. GitHub, "October 21 post-incident analysis," 2018-10-30. https://github.blog/2018-10-30-oct21-post-incident-analysis/
20. P. Bailis, S. Venkataraman, M. Franklin, J. Hellerstein, I. Stoica, "Probabilistically Bounded Staleness for Practical Partial Quorums," PVLDB 5(8), pp. 776–787, 2012. https://vldb.org/pvldb/vol5/p776_peterbailis_vldb2012.pdf

### 07 — Partitioning & sharding

Lesson: [`course/01-foundations/07-partitioning-sharding.md`](course/01-foundations/07-partitioning-sharding.md) · source status: `SOURCES_CHECKED`

1. D. Karger, E. Lehman, T. Leighton, R. Panigrahy, M. Levine, D. Lewin, "Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web," STOC 1997, pp. 654–663. https://doi.org/10.1145/258533.258660
2. D. Thaler, C. Ravishankar, "Using Name-Based Mappings to Increase Hit Rates," IEEE/ACM Transactions on Networking 6(1):1–14, 1998. https://www.cs.ucr.edu/~ravi/Papers/Jrnl/HRW98.pdf
3. G. DeCandia et al., "Dynamo: Amazon's Highly Available Key-value Store," SOSP 2007. https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
4. J. Lamping, E. Veach, "A Fast, Minimal Memory, Consistent Hash Algorithm," arXiv:1406.2294, 2014 (preprint). https://arxiv.org/abs/1406.2294
5. J. C. Corbett et al., "Spanner: Google's Globally-Distributed Database," OSDI 2012. https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
6. R. Taft et al., "CockroachDB: The Resilient Geo-Distributed SQL Database," SIGMOD 2020, pp. 1493–1509. https://doi.org/10.1145/3318464.3386134
7. F. Chang et al., "Bigtable: A Distributed Storage System for Structured Data," OSDI 2006. https://www.usenix.org/conference/osdi-06/bigtable-distributed-storage-system-structured-data
8. V. Mirrokni, M. Thorup, M. Zadimoghaddam, "Consistent Hashing with Bounded Loads," SODA 2018, pp. 587–604; arXiv:1608.01350. https://arxiv.org/abs/1608.01350
9. D. E. Eisenbud et al., "Maglev: A Fast and Reliable Software Network Load Balancer," NSDI 2016. https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/eisenbud
10. AWS, DynamoDB Developer Guide, "Best practices for designing and using partition keys effectively" (and "Using write sharding"). https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html
11. Apache Cassandra 4.0 documentation, "cassandra.yaml: num_tokens, allocate_tokens_for_local_replication_factor." https://cassandra.apache.org/doc/4.0/cassandra/configuration/cass_yaml_file.html
12. Redis documentation, "Redis cluster specification" (hash slots, MOVED and ASK redirections). https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/
13. Vitess documentation, "Reshard" (VReplication workflow; v24). https://vitess.io/docs/24.0/reference/vreplication/reshard/
14. Citus documentation, "Concepts" (coordinator, workers, distribution column, co-location). https://docs.citusdata.com/en/stable/get_started/concepts.html
15. AWS, DynamoDB Developer Guide, "Using Global Secondary Indexes in DynamoDB." https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html
16. Cockroach Labs documentation, "Load-Based Splitting" and "Replication Controls" (`range_max_bytes` default 536870912 bytes = 512 MiB). https://docs.cockroachlabs.com/docs/stable/load-based-splitting and https://docs.cockroachlabs.com/docs/stable/configure-replication-zones
17. AWS, Aurora DSQL User Guide, "Concurrency control in Aurora DSQL." https://docs.aws.amazon.com/aurora-dsql/latest/userguide/working-with-concurrency-control.html
18. Cockroach Labs documentation, "Index Sequential Keys with Hash-sharded Indexes." https://docs.cockroachlabs.com/docs/stable/hash-sharded-indexes

### 08 — Asynchronous & event-driven systems

Lesson: [`course/01-foundations/08-async-event-driven.md`](course/01-foundations/08-async-event-driven.md) · source status: `SOURCES_CHECKED`

1. J. Kreps, N. Narkhede, J. Rao, "Kafka: a Distributed Messaging System for Log Processing," NetDB 2011 (LinkedIn). https://people.csail.mit.edu/matei/courses/2015/6.S897/readings/kafka.pdf
2. Apache Kafka, "Design — Message Delivery Semantics / Persistence," Kafka 4.4 documentation. https://kafka.apache.org/44/design/design/
3. Apache Kafka, "KIP-98 — Exactly Once Delivery and Transactional Messaging." https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging
4. Amazon Web Services, "Using dead-letter queues in Amazon SQS," SQS Developer Guide. https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html
5. Apache Kafka, "Upgrading to 4.0" (upgrade notes, 4.0 documentation). https://kafka.apache.org/40/getting-started/upgrade/
6. Apache Kafka, "Download" (release list with dates). https://kafka.apache.org/community/downloads/
7. Apache Kafka, "KIP-932: Queues for Kafka." https://cwiki.apache.org/confluence/display/KAFKA/KIP-932%3A+Queues+for+Kafka
8. Apache Kafka, "Apache Kafka 4.2.0 Release Announcement," 2026-02-17. https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/
9. RabbitMQ, "Quorum Queues" (documentation, current series 4.4). https://www.rabbitmq.com/docs/quorum-queues
10. RabbitMQ, "Consumer Acknowledgements and Publisher Confirms." https://www.rabbitmq.com/docs/confirms
11. RabbitMQ, "Streams and Super Streams." https://www.rabbitmq.com/docs/streams
12. RabbitMQ, "Release Information." https://www.rabbitmq.com/release-information
13. RabbitMQ, "Dead Letter Exchanges." https://www.rabbitmq.com/docs/dlx
14. Amazon Web Services, "Amazon SQS visibility timeout," SQS Developer Guide. https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
15. Amazon Web Services, "Exactly-once processing in Amazon SQS," SQS Developer Guide. https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/FIFO-queues-exactly-once-processing.html
16. H. Garcia-Molina, K. Salem, "Sagas," Proc. ACM SIGMOD 1987, pp. 249–259. https://doi.org/10.1145/38713.38742 ; technical report TR-070-87, Princeton University, 1987: https://www.cs.princeton.edu/research/techreps/598
17. C. Richardson, "Pattern: Saga," microservices.io. https://microservices.io/patterns/data/saga.html
18. C. Richardson, "Pattern: Transactional outbox," microservices.io. https://microservices.io/patterns/data/transactional-outbox.html
19. Debezium, "Outbox Event Router," Debezium reference documentation (stable). https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html
20. M. Fowler, "Event Sourcing," 2005. https://martinfowler.com/eaaDev/EventSourcing.html
21. M. Fowler, "CQRS," 2011. https://martinfowler.com/bliki/CQRS.html
22. P. Helland, "Life beyond Distributed Transactions: an Apostate's Opinion," CIDR 2007. https://ics.uci.edu/~cs223/papers/cidr07p15.pdf
23. Temporal Technologies, "Temporal Workflow," Temporal documentation. https://docs.temporal.io/workflows
24. Temporal Technologies, "Retry Policies," Temporal documentation. https://docs.temporal.io/encyclopedia/retry-policies
25. Temporal Technologies, "Activity Definition," Temporal documentation. https://docs.temporal.io/activity-definition
26. OpenAI, "Batch API" guide. https://developers.openai.com/api/docs/guides/batch
27. Anthropic, "Batch processing" (Message Batches API). https://platform.claude.com/docs/en/build-with-claude/batch-processing
28. Apache Kafka, "KIP-500: Replace ZooKeeper with a Self-Managed Metadata Quorum." https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum
29. Stripe, "Idempotent requests," Stripe API reference. https://docs.stripe.com/api/idempotent_requests
30. Apache Kafka JIRA, "KAFKA-10619: Producer will enable EOS by default" (KIP-679). https://issues.apache.org/jira/browse/KAFKA-10619

### 09 — Coordination & consensus

Lesson: [`course/01-foundations/09-coordination-consensus.md`](course/01-foundations/09-coordination-consensus.md) · source status: `DRAFT`

1. M. J. Fischer, N. A. Lynch, M. S. Paterson. "Impossibility of Distributed Consensus with One Faulty Process." *Journal of the ACM* 32(2):374–382, 1985. https://doi.org/10.1145/3149.214121 (full text: https://www.cs.princeton.edu/courses/archive/spring22/cos418/papers/flp.pdf)
2. L. Lamport. "The Part-Time Parliament." *ACM Transactions on Computer Systems* 16(2):133–169, 1998. https://www.microsoft.com/en-us/research/publication/part-time-parliament/
3. L. Lamport. "Paxos Made Simple." 2001. https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
4. D. Ongaro, J. Ousterhout. "In Search of an Understandable Consensus Algorithm." USENIX ATC 2014, pp. 305–319. https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro (extended version: https://raft.github.io/raft.pdf)
5. D. Ongaro. "Consensus: Bridging Theory and Practice." PhD dissertation, Stanford University, 2014. https://purl.stanford.edu/qr033xr6097 (PDF: https://github.com/ongardie/dissertation)
6. etcd-io/raft. README: features and notable users. https://github.com/etcd-io/raft
7. etcd documentation v3.6. "Tuning." https://etcd.io/docs/v3.6/tuning/
8. etcd documentation v3.6. "Frequently Asked Questions (FAQ)." https://etcd.io/docs/v3.6/faq/
9. etcd documentation v3.7. "Configuration options" (`--pre-vote`). https://etcd.io/docs/v3.7/op-guide/configuration/
10. etcd documentation v3.6. "Metrics." https://etcd.io/docs/v3.6/metrics/
11. Kubernetes documentation. "Operating etcd clusters for Kubernetes." https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
12. Kubernetes documentation. "Leases." https://kubernetes.io/docs/concepts/architecture/leases/
13. Kubernetes documentation. "Coordinated Leader Election." https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/
14. P. Hunt, M. Konar, F. P. Junqueira, B. Reed. "ZooKeeper: Wait-free Coordination for Internet-scale Systems." USENIX ATC 2010. https://www.usenix.org/conference/usenix-atc-10/zookeeper-wait-free-coordination-internet-scale-systems
15. M. Burrows. "The Chubby lock service for loosely-coupled distributed systems." OSDI 2006. https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf
16. M. Kleppmann. "How to do distributed locking." 8 February 2016. https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
17. Jepsen (K. Kingsbury). "etcd 3.4.3." 30 January 2020. https://jepsen.io/analyses/etcd-3.4.3
18. L. Lamport. "Time, Clocks, and the Ordering of Events in a Distributed System." *Communications of the ACM* 21(7):558–565, 1978. https://doi.org/10.1145/359545.359563 (PDF: https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
19. F. Mattern. "Virtual Time and Global States of Distributed Systems." 1989. https://pages.cs.wisc.edu/~remzi/Classes/739/Fall2018/Papers/mattern89.pdf
20. G. DeCandia et al. "Dynamo: Amazon's Highly Available Key-value Store." SOSP 2007. https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
21. S. Kulkarni, M. Demirbas, D. Madappa, B. Avva, M. Leone. "Logical Physical Clocks." OPODIS 2014, LNCS 8878. https://doi.org/10.1007/978-3-319-14472-6_2 (tech report: https://cse.buffalo.edu/tech-reports/2014-04.pdf)
22. Cockroach Labs. "Transaction Layer" (CockroachDB architecture docs, stable). https://docs.cockroachlabs.com/docs/stable/architecture/transaction-layer
23. J. C. Corbett et al. "Spanner: Google's Globally-Distributed Database." OSDI 2012. https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
24. D. Mills, J. Martin (Ed.), J. Burbank, W. Kasch. RFC 5905, "Network Time Protocol Version 4: Protocol and Algorithms Specification." June 2010. https://www.rfc-editor.org/rfc/rfc5905
25. AWS. "Amazon Time Sync Service now supports microsecond-accurate time." 16 November 2023. https://aws.amazon.com/about-aws/whats-new/2023/11/amazon-time-sync-service-microsecond-accurate-time
26. K. Davis, B. Peabody, P. Leach. RFC 9562, "Universally Unique IDentifiers (UUIDs)." May 2024. https://www.rfc-editor.org/rfc/rfc9562
27. ULID specification. https://github.com/ulid/spec
28. Twitter. Snowflake README (2010 branch; repository archived 2021). https://github.com/twitter-archive/snowflake/tree/snowflake-2010
29. PostgreSQL 18 documentation. "UUID Functions." https://www.postgresql.org/docs/18/functions-uuid.html
30. A. Das, I. Gupta, A. Motivala. "SWIM: Scalable Weakly-consistent Infection-style Process Group Membership Protocol." DSN 2002, pp. 303–312, doi:10.1109/DSN.2002.1028914. https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf
31. N. Hayashibara, X. Défago, R. Yared, T. Katayama. "The φ Accrual Failure Detector." SRDS 2004, pp. 66–78 (JAIST tech report IS-RR-2004-010). https://dspace02.jaist.ac.jp/dspace/bitstream/10119/4784/1/IS-RR-2004-010.pdf
32. Apache Cassandra. `conf/cassandra.yaml` (trunk), `phi_convict_threshold`. https://github.com/apache/cassandra/blob/trunk/conf/cassandra.yaml
33. HashiCorp. memberlist. https://github.com/hashicorp/memberlist
34. etcd blog. "Announcing etcd v3.7.0." July 2026. https://etcd.io/blog/2026/announcing-etcd-3.7/
35. Apache Kafka 4.0 documentation. "Upgrading." https://kafka.apache.org/40/getting-started/upgrade/
36. Apache ZooKeeper. "ZooKeeper Recipes and Solutions." https://zookeeper.apache.org/doc/current/recipes.html
37. etcd-io/etcd. GitHub releases (v3.7.4, v3.6.17, v3.5.36, November 2026). https://github.com/etcd-io/etcd/releases
38. L. Lamport, R. Shostak, M. Pease. "The Byzantine Generals Problem." *ACM TOPLAS* 4(3):382–401, 1982. https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/

### 10 — APIs & communication

Lesson: [`course/01-foundations/10-apis-communication.md`](course/01-foundations/10-apis-communication.md) · source status: `SOURCES_CHECKED`

1. R. T. Fielding, *Architectural Styles and the Design of Network-based Software Architectures*, PhD dissertation, UC Irvine, 2000, ch. 5 "Representational State Transfer". https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm
2. R. Fielding, M. Nottingham, J. Reschke (eds.), *RFC 9110: HTTP Semantics*, IETF, 2022. https://www.rfc-editor.org/rfc/rfc9110.html
3. M. Thomson, C. Benfield (eds.), *RFC 9113: HTTP/2*, IETF, 2022. https://www.rfc-editor.org/rfc/rfc9113.html
4. M. Bishop (ed.), *RFC 9114: HTTP/3*, IETF, 2022. https://www.rfc-editor.org/rfc/rfc9114.html
5. gRPC Authors, "Core concepts, architecture and lifecycle". https://grpc.io/docs/what-is-grpc/core-concepts/
6. gRPC Authors, "gRPC over HTTP2" (PROTOCOL-HTTP2.md). https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md
7. GraphQL Foundation, *GraphQL Specification* (editions list; September 2025 and September 2026 editions). https://spec.graphql.org/ ; https://spec.graphql.org/September2025/ ; https://spec.graphql.org/September2026/
8. GraphQL Foundation, DataLoader. https://github.com/graphql/dataloader
9. GitHub Docs, "Rate limits and query limits for the GraphQL API". https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api
10. WHATWG, *HTML Living Standard*, §9.2 "Server-sent events". https://html.spec.whatwg.org/multipage/server-sent-events.html
11. I. Fette, A. Melnikov, *RFC 6455: The WebSocket Protocol*, IETF, 2011. https://www.rfc-editor.org/rfc/rfc6455.html
12. Anthropic, "Streaming messages" (Claude API docs). https://platform.claude.com/docs/en/build-with-claude/streaming
13. OpenAI, "Streaming API responses". https://developers.openai.com/api/docs/guides/streaming-responses
14. B. Leach, "APIs as infrastructure: future-proofing Stripe with versioning", Stripe blog, 2017-08-05. https://stripe.com/blog/api-versioning
15. GitHub Docs, "API Versions" (REST API). https://docs.github.com/en/rest/about-the-rest-api/api-versions
16. Google, *AIP-158: Pagination*. https://google.aip.dev/158
17. M. Winand, "We need tool support for keyset pagination" (no-offset), Use The Index, Luke. https://use-the-index-luke.com/no-offset
18. J. Jena, S. Dalal, D. Tishkin, *The Idempotency-Key HTTP Header Field*, draft-ietf-httpapi-idempotency-key-header-08, IETF Internet-Draft (work in progress), 2026-10-22. https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
19. Stripe, "Idempotent requests" (API reference). https://docs.stripe.com/api/idempotent_requests
20. B. Leach, "Implementing Stripe-like Idempotency Keys in Postgres", 2017-10-27. https://brandur.org/idempotency-keys
21. M. Nottingham, R. Fielding, *RFC 6585: Additional HTTP Status Codes*, IETF, 2012, §4 (429). https://www.rfc-editor.org/rfc/rfc6585.html
22. P. Tarjan, "Scaling your API with rate limiters", Stripe blog, 2017-03-30. https://stripe.com/blog/rate-limiters
23. Cloudflare, "How we built rate limiting capable of scaling to millions of domains", Cloudflare blog, 2017-06-07. https://blog.cloudflare.com/counting-things-a-lot-of-different-things/
24. B. Leach, "Rate Limiting, Cells, and GCRA", 2015-09-18. https://brandur.org/rate-limiting
25. Redis, "Scripting with Lua" (Redis docs). https://redis.io/docs/latest/develop/programmability/eval-intro/
26. Envoy Project, "Global rate limiting" (architecture overview). https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/other_features/global_rate_limiting
27. Envoy Project, envoyproxy/ratelimit (reference rate-limit service, Go + Redis). https://github.com/envoyproxy/ratelimit
28. R. Polli, A. Martinez Ruiz, D. Miller, *RateLimit header fields for HTTP*, draft-ietf-httpapi-ratelimit-headers-11, IETF Internet-Draft (work in progress), 2026-05-23. https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/
29. Istio, "Fast, Secure, and Simple: Istio's Ambient Mode Reaches General Availability in v1.24", 2024-11. https://istio.io/latest/blog/2024/ambient-reaches-ga/
30. Istio, "Ambient mode overview" (docs, site version 1.32). https://istio.io/latest/docs/ambient/overview/
31. Linkerd, "Architecture" (2-edge docs). https://linkerd.io/2-edge/reference/architecture/
32. Protocol Buffers, "Language Guide (proto 3)" — Updating a Message Type, Reserved Fields. https://protobuf.dev/programming-guides/proto3/
33. Google, *AIP-180: Backwards compatibility*. https://google.aip.dev/180
34. L. Dusseault, J. Snell, *RFC 5789: PATCH Method for HTTP*, IETF, 2010. https://www.rfc-editor.org/rfc/rfc5789.html
35. M. Nottingham, P-H. Kamp, *RFC 9651: Structured Field Values for HTTP*, IETF, 2024. https://www.rfc-editor.org/rfc/rfc9651.html
36. J. Heinanen, R. Guerin, *RFC 2697: A Single Rate Three Color Marker*, IETF, 1999. https://www.rfc-editor.org/rfc/rfc2697.html

### 11 — Reliability engineering

Lesson: [`course/01-foundations/11-reliability-engineering.md`](course/01-foundations/11-reliability-engineering.md) · source status: `DRAFT`

1. F. Cristian, "Understanding fault-tolerant distributed systems," *Communications of the ACM* 34(2):56–78, 1991. https://doi.org/10.1145/102792.102801
2. L. Lamport, R. Shostak, M. Pease, "The Byzantine Generals Problem," *ACM TOPLAS* 4(3):382–401, 1982. https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/
3. P. Huang, C. Guo, L. Zhou, J. R. Lorch, Y. Dang, M. Chintalapati, R. Yao, "Gray Failure: The Achilles' Heel of Cloud-Scale Systems," HotOS '17, 2017. https://www.microsoft.com/en-us/research/publication/gray-failure-achilles-heel-cloud-scale-systems/
4. N. Bronson, A. Aghayev, A. Charapko, T. Zhu, "Metastable Failures in Distributed Systems," HotOS '21, 2021. https://sigops.org/s/conferences/hotos/2021/papers/hotos21-s11-bronson.pdf
5. L. Huang, M. Magnusson, A. B. Muralikrishna, S. Estyak, R. Isaacs, A. Aghayev, T. Zhu, A. Charapko, "Metastable Failures in the Wild," OSDI '22, 2022. https://www.usenix.org/conference/osdi22/presentation/huang-lexiang
6. M. Brooker, "Exponential Backoff And Jitter," AWS Architecture Blog, 2015 (updated 2023). https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
7. M. Brooker, "Timeouts, retries, and backoff with jitter," Amazon Builders' Library. https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ (now served at builder.aws.com; accessed 2026-11)
8. M. Brooker, "What is Backoff For?," Marc's Blog, 2022. https://brooker.co.za/blog/2022/08/11/backoff.html
9. D. Yanacek, "Using load shedding to avoid overload," Amazon Builders' Library, 2019. https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/ (now served at builder.aws.com; accessed 2026-11)
10. A. Forero Cuervo, "Handling Overload," in *Site Reliability Engineering* (Google), ch. 21, 2016. https://sre.google/sre-book/handling-overload/
11. M. Ulrich, "Addressing Cascading Failures," in *Site Reliability Engineering* (Google), ch. 22, 2016. https://sre.google/sre-book/addressing-cascading-failures/
12. Envoy Proxy, `config.cluster.v3.CircuitBreakers.Thresholds.RetryBudget` API reference (latest). https://www.envoyproxy.io/docs/envoy/latest/api-v3/config/cluster/v3/circuit_breaker.proto
13. Envoy Proxy, "Adaptive Concurrency" HTTP filter documentation (latest). https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/adaptive_concurrency_filter
14. M. Fowler, "CircuitBreaker," bliki, 6 March 2014. https://martinfowler.com/bliki/CircuitBreaker.html
15. M. T. Nygard, *Release It! Design and Deploy Production-Ready Software*, 2nd ed., Pragmatic Bookshelf, 2018. https://pragprog.com/titles/mnee2/release-it-second-edition/
16. B. Weiss, M. Furr, "Static stability using Availability Zones," Amazon Builders' Library. https://aws.amazon.com/builders-library/static-stability-using-availability-zones/
17. AWS, *Disaster Recovery of Workloads on AWS: Recovery in the Cloud* (whitepaper), sections "Business Continuity Plan" and "Disaster recovery options in the cloud." https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
18. Principles of Chaos Engineering. https://principlesofchaos.org/
19. A. Basiri, N. Behnam, R. de Rooij, L. Hochstein, L. Kosewski, J. Reynolds, C. Rosenthal, "Chaos Engineering," *IEEE Software* 33(3):35–41, 2016. https://doi.org/10.1109/MS.2016.60
20. AWS, "Summary of the AWS Service Event in the Northern Virginia (US-EAST-1) Region" (7 December 2021). https://aws.amazon.com/message/12721/
21. AWS, "Summary of the Amazon DynamoDB Service Disruption in the Northern Virginia (US-EAST-1) Region" (19–20 October 2025). https://aws.amazon.com/message/101925/
22. Cloudflare, "Cloudflare outage on November 18, 2025." https://blog.cloudflare.com/18-november-2025-outage/
23. Google Cloud Service Health, incident report for 12 June 2025 (Service Control). https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW
24. CrowdStrike, "External Technical Root Cause Analysis — Channel File 291," 2024-08-06. https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf
25. R. Fielding, M. Nottingham, J. Reschke (eds.), RFC 9110 *HTTP Semantics*, §10.2.3 Retry-After, 2022. https://www.rfc-editor.org/rfc/rfc9110.html#name-retry-after
26. M. Nottingham, R. Fielding, RFC 6585 *Additional HTTP Status Codes*, §4 429 Too Many Requests, 2012. https://www.rfc-editor.org/rfc/rfc6585.html
27. Shopify, Toxiproxy (v2.13.0). https://github.com/Shopify/toxiproxy

### 12 — Observability

Lesson: [`course/01-foundations/12-observability.md`](course/01-foundations/12-observability.md) · source status: `DRAFT`

1. OpenTelemetry, "Specification Status Summary," https://opentelemetry.io/docs/specs/status/
2. OpenTelemetry, "OpenTelemetry Profiles Enters Public Alpha," blog, 2026, https://opentelemetry.io/blog/2026/profiles-alpha/ ; and "Profiles" concept page (Status: Alpha), https://opentelemetry.io/docs/concepts/signals/profiles/
3. OpenTelemetry, "OpenTelemetry eBPF Instrumentation reaches v1.0.0," blog, 2026, https://opentelemetry.io/blog/2026/obi-v1-release/ ; release v1.0.0 (2026-10-30), https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases
4. Grafana Labs, "OpenTelemetry eBPF Instrumentation: why we donated Grafana Beyla to OpenTelemetry," 2025-05-07, https://grafana.com/blog/2025/05/07/opentelemetry-ebpf-instrumentation-beyla-donation/
5. OpenTelemetry, "Elastic Contributes its Continuous Profiling Agent to OpenTelemetry," blog, 2024, https://opentelemetry.io/blog/2024/elastic-contributes-continuous-profiling-agent/
6. OpenTelemetry, GenAI semantic conventions (docs/gen-ai/: gen-ai-spans.md, gen-ai-metrics.md, gen-ai-token-metrics.md; all "Status: Development"), https://github.com/open-telemetry/semantic-conventions-genai (main branch, accessed 2026-11).
7. Prometheus, "Metric and label naming," https://prometheus.io/docs/practices/naming/
8. OpenTelemetry, "Metrics Data Model" (temporality, exponential histograms, exemplars), https://opentelemetry.io/docs/specs/otel/metrics/data-model/
9. OpenTelemetry, "Logs" specification overview (Logs Bridge API, trace context in log records), https://opentelemetry.io/docs/specs/otel/logs/
10. B. H. Sigelman et al., "Dapper, a Large-Scale Distributed Systems Tracing Infrastructure," Google Technical Report dapper-2010-1, 2010, https://research.google/pubs/pub36356/
11. W3C, "Trace Context" (Level 1), W3C Recommendation, 23 November 2021 (first Recommendation 6 February 2020), https://www.w3.org/TR/trace-context/
12. G. Ren et al., "Google-Wide Profiling: A Continuous Profiling Infrastructure for Data Centers," IEEE Micro, 2010, https://research.google/pubs/google-wide-profiling-a-continuous-profiling-infrastructure-for-data-centers/
13. OpenTelemetry, Resource semantic conventions, https://opentelemetry.io/docs/specs/semconv/resource/
14. OpenTelemetry, "Semantic conventions for HTTP metrics" (`http.server.request.duration`), https://opentelemetry.io/docs/specs/semconv/http/http-metrics/
15. B. Beyer et al. (eds.), *Site Reliability Engineering*, ch. 6 "Monitoring Distributed Systems," O'Reilly/Google, 2016, https://sre.google/sre-book/monitoring-distributed-systems/
16. T. Wilkie, "The RED Method: How to instrument your services," Grafana Labs blog, 2018-08-02, https://grafana.com/blog/2018/08/02/the-red-method-how-to-instrument-your-services/ ; slides, GrafanaCon EU 2018, https://grafana.com/files/grafanacon_eu_2018/Tom_Wilkie_GrafanaCon_EU_2018.pdf
17. B. Gregg, "The USE Method," https://www.brendangregg.com/usemethod.html
18. S. Murphy et al. (eds.), *The Site Reliability Workbook*, ch. 5 "Alerting on SLOs," O'Reilly/Google, 2018, https://sre.google/workbook/alerting-on-slos/
19. T. Pelkonen et al., "Gorilla: A Fast, Scalable, In-Memory Time Series Database," PVLDB 8(12), 2015, https://www.vldb.org/pvldb/vol8/p1816-teller.pdf
20. OpenTelemetry, "Collector" documentation (agent and gateway deployment patterns), https://opentelemetry.io/docs/collector/
21. OpenTelemetry Collector Contrib, "Tail Sampling Processor" README (stability beta; decision_wait 30 s; num_traces 50,000), https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/tailsamplingprocessor
22. OpenTelemetry Collector Contrib, "Load Balancing Exporter" README (routing by traceID), https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/loadbalancingexporter
23. C. Majors, L. Fong-Jones, G. Miranda, *Observability Engineering*, O'Reilly, 2022, ISBN 9781492076438, https://www.oreilly.com/library/view/observability-engineering/9781492076438/ (publisher page; not fetchable by script, accessed 2026-11).
24. Prometheus, CHANGELOG — 3.8.0 (2025-11-28) "Native histograms are now a stable, but optional feature"; 3.9.0 (2026-01-06) feature flag made a no-op, https://github.com/prometheus/prometheus/blob/main/CHANGELOG.md
25. eBPF.io, "What is eBPF?", https://ebpf.io/what-is-ebpf/
26. OpenTelemetry, semantic-conventions releases (v1.45.0, 2026-11-02), https://github.com/open-telemetry/semantic-conventions/releases
27. T. Ahmed et al., "Recommending Root-Cause and Mitigation Steps for Cloud Incidents using Large Language Models," ICSE 2023, arXiv:2301.03797, https://arxiv.org/abs/2301.03797
28. grafana/docker-otel-lgtm, v0.41.0 (2026-11-13), https://github.com/grafana/docker-otel-lgtm

### 13 — Data at scale: object storage, lakehouse, batch vs stream, search

Lesson: [`course/01-foundations/13-data-at-scale.md`](course/01-foundations/13-data-at-scale.md) · source status: `DRAFT`

1. Amazon Web Services, "Amazon S3 now delivers strong read-after-write consistency automatically for all applications," What's New, 2020-12-01. https://aws.amazon.com/about-aws/whats-new/2020/12/amazon-s3-now-delivers-strong-read-after-write-consistency-automatically-for-all-applications/
2. Amazon Web Services, "Data protection in Amazon S3," Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html
3. Amazon Web Services, "How to prevent object overwrites with conditional writes," Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html
4. Amazon Web Services, "Amazon S3 now supports conditional writes," What's New, 2024-08-20. https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes/
5. Amazon Web Services, "Best practices design patterns: optimizing Amazon S3 performance," Amazon S3 User Guide. https://docs.aws.amazon.com/AmazonS3/latest/userguide/optimizing-performance.html
6. Apache Software Foundation, "HDFS Erasure Coding," Apache Hadoop 3.3.5 documentation. https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSErasureCoding.html
7. S. Muralidhar, W. Lloyd, S. Roy, C. Hill, E. Lin, W. Liu, S. Pan, S. Shankar, V. Sivakumar, L. Tang, S. Kumar, "f4: Facebook's Warm BLOB Storage System," OSDI 2014, pp. 383–398. https://www.usenix.org/conference/osdi14/technical-sessions/presentation/muralidhar
8. M. Armbrust, A. Ghodsi, R. Xin, M. Zaharia, "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics," CIDR 2021. https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf
9. M. Armbrust et al., "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores," PVLDB 13(12): 3411–3424, 2020. https://www.vldb.org/pvldb/vol13/p3411-armbrust.pdf
10. Apache Iceberg, "Iceberg Table Spec" (format versions 1–3 adopted; v4 in development). https://iceberg.apache.org/spec/ — source: https://github.com/apache/iceberg/blob/main/format/spec.md
11. Apache Iceberg, GitHub releases (1.10.0 2025-09-11; 1.12.0 2026-09-30). https://github.com/apache/iceberg/releases
12. Apache Hudi, "Table & Query Types." https://hudi.apache.org/docs/table_types
13. V. Chandar, P. Rajaperumal, "Hudi: Uber Engineering's Incremental Processing Framework on Apache Hadoop," Uber Engineering blog, 2017-03-11. https://www.uber.com/blog/hoodie/
14. Apache Parquet, "File Format." https://parquet.apache.org/docs/file-format/
15. Apache Parquet, "Configurations." https://parquet.apache.org/docs/file-format/configurations/
16. J. Dean, S. Ghemawat, "MapReduce: Simplified Data Processing on Large Clusters," OSDI 2004, pp. 137–150. https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/
17. M. Zaharia et al., "Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing," NSDI 2012. https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia
18. N. Marz, "How to beat the CAP theorem," 2011. http://nathanmarz.com/blog/how-to-beat-the-cap-theorem.html
19. J. Kreps, "Questioning the Lambda Architecture," O'Reilly Radar, 2014-07-02. https://www.oreilly.com/radar/questioning-the-lambda-architecture/
20. S. Robertson, H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," Foundations and Trends in Information Retrieval 3(4), 2009. https://doi.org/10.1561/1500000019 (DOI not fetchable by automated client this session; bibliographic details from the publisher record)
21. Apache Lucene, "Lucene 10.3 file format / index structure" (package summary). https://lucene.apache.org/core/10_3_0/core/org/apache/lucene/codecs/lucene103/package-summary.html
22. Elastic, "Similarity settings," Elasticsearch reference. https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity
23. Elastic, "Index settings / index modules," Elasticsearch reference. https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules
24. Elastic, "Elastic Announces Open Source License for Elasticsearch and Kibana Source Code," press release, 2024-08-29. https://www.businesswire.com/news/home/20240829537786/en
25. The Linux Foundation, "Linux Foundation Announces OpenSearch Software Foundation to Foster Open Collaboration in Search and Analytics," press release, 2024-09-16. https://www.linuxfoundation.org/press/linux-foundation-announces-opensearch-software-foundation-to-foster-open-collaboration-in-search-and-analytics
26. Apache Kafka, "KIP-405: Kafka Tiered Storage." https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage
27. WarpStream, "Architecture overview," WarpStream documentation. https://docs.warpstream.com/warpstream/overview/architecture
28. J. Kreps, "Confluent + WarpStream = Large-Scale Streaming in your Cloud," Confluent blog, 2024-09-09. https://www.confluent.io/blog/confluent-acquires-warpstream/
29. J. Prat (Aiven), "KIP-1150 accepted and the road ahead," 2026-03-12, https://aiven.io/blog/kip-1150-accepted-and-the-road-ahead ; KIP page: https://cwiki.apache.org/confluence/display/KAFKA/KIP-1150:+Diskless+Topics
30. DuckDB, "Announcing DuckDB 2.0.0," 2026-10-21. https://duckdb.org/2026/10/21/announcing-duckdb-200.html
31. Amazon Web Services, "Announcing Amazon S3 Tables," What's New, 2024-12-03. https://aws.amazon.com/about-aws/whats-new/2024/12/amazon-s3-tables-apache-iceberg-tables-analytics-workloads/
32. Elastic, "Size your shards," Elasticsearch documentation. https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/size-shards
33. Amazon Web Services, "Amazon S3 adds new functionality for conditional writes," What's New, 2024-11-25. https://aws.amazon.com/about-aws/whats-new/2024/11/amazon-s3-functionality-conditional-writes/

## Part II — Modern requirements

### 14 — Cloud-native & platform engineering

Lesson: [`course/02-modern-requirements/14-cloud-native-platforms.md`](course/02-modern-requirements/14-cloud-native-platforms.md) · source status: `SOURCES_CHECKED`

1. Kubernetes, "Releases," https://kubernetes.io/releases/ ; GitHub releases (v1.37.2, 2026-10-28), https://github.com/kubernetes/kubernetes/releases
2. Kubernetes blog, "Kubernetes 1.35: In-Place Pod Resize Graduates to Stable," 2025-12-19, https://kubernetes.io/blog/2025/12/19/kubernetes-v1-35-in-place-pod-resize-ga/
3. Kubernetes blog, "Kubernetes v1.33: Octarine" (sidecar containers stable), 2025-04-23, https://kubernetes.io/blog/2025/04/23/kubernetes-v1-33-release/
4. Kubernetes docs, "Ingress" (API frozen; Gateway API recommended), https://kubernetes.io/docs/concepts/services-networking/ingress/
5. Kubernetes blog, "Ingress NGINX Retirement: What You Need to Know," 2025-11-11, https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/
6. Kubernetes SIG Network, Gateway API documentation, https://gateway-api.sigs.k8s.io/docs/ ; releases (v1.7.0, 2026-10-29), https://github.com/kubernetes-sigs/gateway-api/releases
7. CNCF, "Flux graduates from CNCF Incubator," 2022-11-30, https://www.cncf.io/announcements/2022/11/30/flux-graduates-from-cncf-incubator/
8. CNCF / ITOps Times, "Argo graduates from CNCF incubator," 2022-12-06, https://www.cncf.io/news/2022/12/06/itops-times-argo-graduates-from-cncf-incubator-following-massive-community-growth/
9. CNCF, "Cloud Native Computing Foundation announces graduation of Kubernetes autoscaler KEDA," 2023-08-22, https://www.cncf.io/announcements/2023/08/22/cloud-native-computing-foundation-announces-graduation-of-kubernetes-autoscaler-keda/ ; KEDA docs, https://keda.sh/
10. CNCF, "Cloud Native Computing Foundation Announces Knative's Graduation," 2025-10-08, https://www.cncf.io/announcements/2025/10/08/cloud-native-computing-foundation-announces-knatives-graduation/
11. WASI.dev, "Releases" (0.3 stable, current; 0.2 released end of January 2024), https://wasi.dev/releases
12. CNCF TAG App Delivery, Platforms Working Group, "CNCF Platforms White Paper," v1.0, 2023, https://tag-app-delivery.cncf.io/whitepapers/platforms/
13. Linux man-pages, namespaces(7), https://man7.org/linux/man-pages/man7/namespaces.7.html
14. Linux kernel documentation, "Control Group v2," https://docs.kernel.org/admin-guide/cgroup-v2.html
15. A. Agache et al., "Firecracker: Lightweight Virtualization for Serverless Applications," NSDI 2020, https://www.usenix.org/conference/nsdi20/presentation/agache
16. A. Verma et al., "Large-scale cluster management at Google with Borg," EuroSys 2015, https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/
17. B. Burns, B. Grant, D. Oppenheimer, E. Brewer, J. Wilkes, "Borg, Omega, and Kubernetes," ACM Queue 14(1), 2016, https://research.google/pubs/borg-omega-and-kubernetes/
18. Kubernetes docs, "Deployments," https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
19. Kubernetes docs, "Service," https://kubernetes.io/docs/concepts/services-networking/service/
20. Kubernetes docs, "Controllers," https://kubernetes.io/docs/concepts/architecture/controller/
21. Kubernetes docs, "Operator pattern," https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
22. Kubernetes docs, "Horizontal Pod Autoscaling" (algorithm, 15 s sync period, 0.1 tolerance, 300 s scale-down stabilisation), https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/
23. Kubernetes Autoscaler, "Vertical Pod Autoscaler," https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler
24. OpenGitOps, "GitOps Principles v1.0.0," https://opengitops.dev/
25. Knative, "Knative Serving" documentation, https://knative.dev/docs/serving/
26. AWS, "Understanding the Lambda execution environment lifecycle," https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html
27. AWS, "Improving startup performance with Lambda SnapStart" (runtimes, provisioned concurrency comparison), https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html
28. Bytecode Alliance, "The WebAssembly Component Model," https://component-model.bytecodealliance.org/
29. CNCF, "SpinKube" project page (Sandbox, accepted 2025-01-21), https://www.cncf.io/projects/spinkube/
30. Kubernetes docs, "Multi-tenancy," https://kubernetes.io/docs/concepts/security/multi-tenancy/
31. CNCF TAG App Delivery, "Platform Engineering Maturity Model," https://tag-app-delivery.cncf.io/whitepapers/platform-eng-maturity-model/
32. kind v0.33.0 release notes (default node image kindest/node:v1.37.0), 2026-08-26, https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0
33. Kubernetes SIG Network, "Gateway API Inference Extension," https://gateway-api-inference-extension.sigs.k8s.io/

### 15 — Multi-region & edge

Lesson: [`course/02-modern-requirements/15-multi-region-edge.md`](course/02-modern-requirements/15-multi-region-edge.md) · source status: `SOURCES_CHECKED`

1. Amazon Web Services, "Disaster recovery options in the cloud", *Disaster Recovery of Workloads on AWS: Recovery in the Cloud* (whitepaper), https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
2. Amazon Web Services, "Static stability", *AWS Fault Isolation Boundaries* (whitepaper), https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/static-stability.html
3. Amazon Web Services, "How DynamoDB global tables work", *Amazon DynamoDB Developer Guide* (global tables version 2019.11.21), https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html
4. Amazon Web Services, "Amazon DynamoDB global tables with multi-Region strong consistency is now generally available", What's New, 2025-06-30, https://aws.amazon.com/about-aws/whats-new/2025/06/amazon-dynamo-db-global-tables-multi-region-strong-consistency-generally-available
5. Amazon Web Services, "Using Amazon Aurora Global Database", *Amazon Aurora User Guide*, https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html
6. Cockroach Labs, "Table Localities", CockroachDB documentation v26.4, https://docs.cockroachlabs.com/docs/stable/table-localities
7. Cockroach Labs, "Multi-Region Survival Goals", CockroachDB documentation v26.4, https://docs.cockroachlabs.com/docs/stable/multiregion-survival-goals
8. J. C. Corbett, J. Dean, M. Epstein, et al., "Spanner: Google's Globally-Distributed Database", *10th USENIX Symposium on Operating Systems Design and Implementation (OSDI '12)*, 2012, https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett
9. G. DeCandia, D. Hastorun, M. Jampani, et al., "Dynamo: Amazon's Highly Available Key-Value Store", *21st ACM Symposium on Operating Systems Principles (SOSP 2007)*, https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html
10. M. Shapiro, N. Preguiça, C. Baquero, M. Zawirski, "Conflict-Free Replicated Data Types", *Stabilization, Safety, and Security of Distributed Systems (SSS 2011)*, LNCS 6976, pp. 386–400, https://doi.org/10.1007/978-3-642-24550-3_29
11. J. Abley, K. Lindqvist, "Operation of Anycast Services", RFC 4786 / BCP 126, IETF, December 2006, https://www.rfc-editor.org/rfc/rfc4786
12. C. Contavalli, W. van der Gaast, D. Lawrence, W. Kumari, "Client Subnet in DNS Queries", RFC 7871 (Informational), IETF, May 2016, https://www.rfc-editor.org/rfc/rfc7871
13. Amazon Web Services, "Choosing a routing policy", *Amazon Route 53 Developer Guide*, https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html
14. Amazon Web Services, "How AWS Global Accelerator works", *AWS Global Accelerator Developer Guide*, https://docs.aws.amazon.com/global-accelerator/latest/dg/introduction-how-it-works.html
15. Amazon Web Services, "Differences between CloudFront Functions and Lambda@Edge", *Amazon CloudFront Developer Guide*, https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions-choosing.html
16. Cloudflare, "How Workers works", *Cloudflare Workers docs*, https://developers.cloudflare.com/workers/reference/how-workers-works/
17. Cloudflare, "Limits", *Cloudflare Workers docs*, https://developers.cloudflare.com/workers/platform/limits/
18. Cloudflare, "What are Durable Objects?", *Cloudflare Durable Objects docs*, https://developers.cloudflare.com/durable-objects/concepts/what-are-durable-objects/
19. A. Singla, B. Chandrasekaran, P. B. Godfrey, B. Maggs, "The Internet at the Speed of Light", *HotNets-XIII*, 2014, doi:10.1145/2670518.2673876; author copy https://www.andrew.cmu.edu/course/15-440-sp15/assets/READINGS/singla2014.pdf
20. Amazon Web Services, *Reducing the Scope of Impact with Cell-Based Architecture*, AWS Well-Architected guidance, 2023-09-20, https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/reducing-scope-of-impact-with-cell-based-architecture.html ; sections "What is a cell-based architecture?" https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html and "Cell sizing" https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/cell-sizing.html
21. C. MacCárthaigh, "Workload isolation using shuffle-sharding", Amazon Builders' Library, 2019, https://builder.aws.com/content/3F06NpJ8YeoIGP8VHTw4n81pFn8/workload-isolation-using-shuffle-sharding (originally https://aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/)
22. Cloudflare, "Workers AI", *Cloudflare docs*, https://developers.cloudflare.com/workers-ai/
23. Cloudflare, "Cloudflare Enhances AI Inference Platform with Powerful GPU Upgrade, Faster Inference, Larger Models, Observability, and Upgraded Vector Database", press release, 2024-09-26, https://www.cloudflare.com/press/press-releases/2024/cloudflare-enhances-ai-inference-platform-with-powerful-gpu-upgrade/

### 16 — Cost as a requirement

Lesson: [`course/02-modern-requirements/16-cost-as-requirement.md`](course/02-modern-requirements/16-cost-as-requirement.md) · source status: `SOURCES_CHECKED`

1. FinOps Foundation, "What is FinOps?", https://www.finops.org/introduction/what-is-finops/
2. FinOps Foundation, "FinOps Framework" (principles, phases, maturity, personas, domains and capabilities, scopes, technology categories; 2026 framework updates), https://www.finops.org/framework/
3. FinOps Foundation, "FinOps Phases", https://www.finops.org/framework/phases/
4. FinOps Foundation, "Unit Economics" capability, https://www.finops.org/framework/capabilities/unit-economics/
5. FinOps Foundation, "State of FinOps 2026" (6th annual survey, 1,192 respondents), https://data.finops.org/
6. FinOps Foundation / Joint Development Foundation, "FOCUS Specification v1.4", https://focus.finops.org/focus-specification/ and https://focus.finops.org/
7. FOCUS v1.4, "Effective Cost" column, https://focus.finops.org/docs/specification/v1-4/columns/cost-and-usage/effective-cost/
8. OpenCost, "OpenCost Specification", https://opencost.io/docs/specification
9. Cloud Native Computing Foundation, "OpenCost" project page (accepted 2022-06-17, Incubating 2024-10-25), https://www.cncf.io/projects/opencost/
10. Amazon Web Services, AWS Price List Bulk API, us-east-1 offer files for AmazonEC2, AWSLambda, AmazonApiGateway, AWSELB, AmazonS3 and AWSDataTransfer, `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<offer>/current/us-east-1/index.json` (EC2 via `index.csv`), publication dates 2026-11-12 to 2026-11-19
11. Amazon Web Services, "Savings Plans pricing", https://aws.amazon.com/savingsplans/compute-pricing/
12. Amazon Web Services, "Amazon EC2 Spot Instances", https://aws.amazon.com/ec2/spot/
13. Amazon Web Services, "Spot Instance interruption notices", Amazon EC2 User Guide, https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html
14. Google Cloud, "Spot VMs", Compute Engine documentation, https://docs.cloud.google.com/compute/docs/instances/spot
15. Amazon Web Services, "Elastic Load Balancing pricing" (LCU dimensions), https://aws.amazon.com/elasticloadbalancing/pricing/
16. Amazon Web Services, "Amazon VPC pricing" (NAT gateway example, public IPv4), https://aws.amazon.com/vpc/pricing/
17. Amazon Web Services, "Understanding and managing Amazon S3 storage classes", Amazon S3 User Guide, https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
18. Amazon Web Services, "Amazon S3 pricing" (100 GB/month free data transfer out), https://aws.amazon.com/s3/pricing/
19. Amazon Web Services, "Design principles", Cost Optimization Pillar, AWS Well-Architected Framework, https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/design-principles.html
20. Karpenter, "Disruption" (consolidation), docs v1.15, https://karpenter.sh/docs/concepts/disruption/
21. Datadog, "Datadog's State of Cloud Costs 2024 Report …", press release, 2024-06-13, https://www.datadoghq.com/about/latest-news/press-releases/datadogs-state-of-cloud-costs-2024-report-finds-spending-on-gpu-instances-growing-40-as-organizations-experiment-with-ai/ Vendor data from its own customer base.
22. R. Gancarz, "Prime Video Switched from Serverless to EC2 and ECS to Save Costs", InfoQ, 2023-05-03, https://www.infoq.com/news/2023/05/prime-ec2-ecs-saves-costs/ Reports on M. Kolny's March 2023 Prime Video tech-blog post, whose original URL now redirects.
23. S. Wang and M. Casado, "The Cost of Cloud, a Trillion Dollar Paradox", Andreessen Horowitz, 2021-05-27, https://a16z.com/the-cost-of-cloud-a-trillion-dollar-paradox/
24. Cloudflare, "R2 pricing", https://developers.cloudflare.com/r2/pricing/
25. Regulation (EU) 2023/2854 (Data Act), Arts. 29 and 34, Official Journal of the EU, https://eur-lex.europa.eu/eli/reg/2023/2854/oj/eng

### 17 — Energy- & carbon-aware design

Lesson: [`course/02-modern-requirements/17-energy-carbon-aware.md`](course/02-modern-requirements/17-energy-carbon-aware.md) · source status: `DRAFT`

1. Green Software Foundation, *Software Carbon Intensity (SCI) Specification*, v1.1.0, 2024. https://sci.greensoftware.foundation/
2. ISO/IEC, *ISO/IEC 21031:2024 Information technology — Software Carbon Intensity (SCI) specification*, 1st ed., 2024. https://webstore.iec.ch/publication/93436
3. V. Avelar, D. Azevedo, A. French (eds.), *PUE™: A Comprehensive Examination of the Metric*, The Green Grid White Paper #49, 2012. https://datacenters.lbl.gov/sites/default/files/WP49-PUE%20A%20Comprehensive%20Examination%20of%20the%20Metric_v6.pdf
4. Uptime Institute, *Global Data Center Survey 2025* (summary page), 2025. https://intelligence.uptimeinstitute.com/resource/uptime-institute-global-data-center-survey-2025
5. Google, *Data center efficiency*, 2026. https://datacenters.google/efficiency
6. International Energy Agency, *Energy and AI: Energy demand from AI*, 2025. https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai
7. Directive (EU) 2023/1791 of 13 September 2023 on energy efficiency (recast), Art. 12 and Art. 26(6). https://eur-lex.europa.eu/eli/dir/2023/1791/oj/eng
8. Commission Delegated Regulation (EU) 2024/1364 of 14 March 2024 on the first phase of the establishment of a common Union rating scheme for data centres. https://eur-lex.europa.eu/eli/reg_del/2024/1364/oj/eng
9. European Commission, press release IP/26/1667, "Commission enhances energy efficiency and sustainability of data centres in the EU", 21 September 2026. https://ec.europa.eu/commission/presscorner/detail/en/ip_26_1667
10. Electricity Maps, "Marginal vs average: which one to use for real-time decisions?" (blog). https://www.electricitymaps.com/blog/marginal-vs-average-real-time-decision-making
11. WattTime, "Marginal CO2" data signal. https://watttime.org/data-science/data-signals/marginal-co2/
12. Ember, *European Electricity Review 2025: Five years of progress*, 2025. https://ember-energy.org/latest-insights/european-electricity-review-2025/five-years-of-progress/
13. P. Wiesner, I. Behnke, D. Scheinert, K. Gontarska, L. Thamsen, "Let's Wait Awhile: How Temporal Workload Shifting Can Reduce Carbon Emissions in the Cloud", ACM Middleware 2021. https://arxiv.org/abs/2110.13234
14. T. Sukprasert, A. Souza, N. Bashir, D. Irwin, P. Shenoy, "On the Limitations of Carbon-Aware Temporal and Spatial Workload Shifting in the Cloud", EuroSys 2024. https://arxiv.org/abs/2306.06502
15. A. Radovanović et al., "Carbon-Aware Computing for Datacenters", arXiv:2106.11750, 2021 (preprint). https://arxiv.org/abs/2106.11750
16. U. Gupta et al., "Chasing Carbon: The Elusive Environmental Footprint of Computing", IEEE HPCA 2021. https://arxiv.org/abs/2011.02839
17. L. A. Barroso, U. Hölzle, "The Case for Energy-Proportional Computing", IEEE Computer 40(12), 2007. https://research.google/pubs/the-case-for-energy-proportional-computing/
18. A. S. Luccioni, Y. Jernite, E. Strubell, "Power Hungry Processing: Watts Driving the Cost of AI Deployment?", ACM FAccT 2024. https://arxiv.org/abs/2311.16863
19. A. S. Luccioni, S. Viguier, A.-L. Ligozat, "Estimating the Carbon Footprint of BLOOM, a 176B Parameter Language Model", JMLR 24(253), 2023. https://www.jmlr.org/papers/v24/23-0069.html
20. D. Patterson et al., "Carbon Emissions and Large Neural Network Training", arXiv:2104.10350, 2021 (preprint). https://arxiv.org/abs/2104.10350
21. C. Elsworth et al., "Measuring the environmental impact of delivering AI at Google Scale", arXiv:2508.15734, 2025 (preprint). https://arxiv.org/abs/2508.15734
22. S. Samsi et al., "From Words to Watts: Benchmarking the Energy Costs of Large Language Model Inference", IEEE HPEC 2023. https://arxiv.org/abs/2310.03003
23. J. You, J.-W. Chung, M. Chowdhury, "Zeus: Understanding and Optimizing GPU Energy Consumption of DNN Training", USENIX NSDI 2023. https://www.usenix.org/conference/nsdi23/presentation/you
24. Linux kernel documentation, "Power Capping Framework". https://docs.kernel.org/power/powercap/powercap.html
25. Intel, "Running Average Power Limit Energy Reporting / CVE-2020-8694, CVE-2020-8695 / INTEL-SA-00389". https://www.intel.com/content/www/us/en/develop/articles/software-security-guidance/advisory-guidance/running-average-power-limit-energy-reporting.html
26. Kepler maintainers, *Kepler (Kubernetes-based Efficient Power Level Exporter)*, GitHub repository. https://github.com/sustainable-computing-io/kepler
27. CNCF blog, "Kepler re-architected: improved power accuracy and a community call to action", 30 June 2026. https://www.cncf.io/blog/2026/06/30/kepler-re-architected-improved-power-accuracy-and-a-community-call-to-action/
28. NVIDIA, *DCGM Exporter Metrics* (DCGM documentation). https://docs.nvidia.com/datacenter/dcgm/latest/reference/dcgm-exporter-metrics.html
29. F. Beneventi, A. Bartolini, C. Cavazzoni, L. Benini, "Continuous learning of HPC infrastructure models using big data analytics and in-memory processing tools", DATE 2017, pp. 1038–1043, doi:10.23919/DATE.2017.7927143. https://past.date-conference.com/proceedings-archive/2017/html/0668.html
30. A. Bartolini et al., "Paving the way toward energy-aware and automated datacentre", Workshop Proceedings of the 48th International Conference on Parallel Processing (ICPP Workshops), 2019. Listed at https://examonhpc.github.io/examon/latest/publications/
31. A. Borghesi et al., "M100 ExaData: a data collection campaign on the CINECA's Marconi100 Tier-0 supercomputer", *Scientific Data* 10, 2023, doi:10.1038/s41597-023-02174-3. https://www.nature.com/articles/s41597-023-02174-3
32. A. Libri, A. Bartolini, L. Benini, "DiG: Enabling Out-of-Band Scalable High-Resolution Monitoring for Data-Center Analytics, Automation and Control (Extended)", arXiv:1806.02698, 2018. https://arxiv.org/abs/1806.02698
33. ExaMon project documentation. https://examonhpc.github.io/examon/latest/
34. TOP500, *Green500 List — November 2026*. https://top500.org/lists/green500/2026/11/
35. Green Software Foundation, "SCI for AI specification ratified", 17 December 2025. https://greensoftware.foundation/articles/sci-ai-specification-ratified-standard-for-measuring-ai-emissions-across-the/
36. Green Software Foundation, *Carbon Aware SDK* documentation. https://carbon-aware-sdk.greensoftware.foundation/docs/overview
37. Z. Yang, K. Adámek, W. Armour, "Part-time Power Measurements: nvidia-smi's Lack of Attention", arXiv:2312.02741, v3 2024 (preprint). https://arxiv.org/abs/2312.02741

### 18 — Security by design

Lesson: [`course/02-modern-requirements/18-security-by-design.md`](course/02-modern-requirements/18-security-by-design.md) · source status: `SOURCES_CHECKED`

1. S. Rose, O. Borchert, S. Mitchell, S. Connelly. *Zero Trust Architecture*, NIST SP 800-207, August 2020. https://doi.org/10.6028/NIST.SP.800-207 (landing page https://csrc.nist.gov/pubs/sp/800/207/final)
2. Kubernetes documentation. *Network Policies* (pods are non-isolated by default; enforcement requires a supporting network plugin). https://kubernetes.io/docs/concepts/services-networking/network-policies/
3. D. Hardt (ed.). *The OAuth 2.0 Authorization Framework*, RFC 6749, October 2012. https://www.rfc-editor.org/rfc/rfc6749
4. T. Lodderstedt, J. Bradley, A. Labunets, D. Fett. *Best Current Practice for OAuth 2.0 Security*, RFC 9700 (BCP 240), January 2025. https://www.rfc-editor.org/rfc/rfc9700.html
5. N. Sakimura et al. *OpenID Connect Core 1.0 incorporating errata set 2*, 15 December 2023. https://openid.net/specs/openid-connect-core-1_0.html
6. N. Sakimura, J. Bradley, N. Agarwal. *Proof Key for Code Exchange by OAuth Public Clients*, RFC 7636, September 2015. https://www.rfc-editor.org/rfc/rfc7636
7. B. Campbell et al. *OAuth 2.0 Mutual-TLS Client Authentication and Certificate-Bound Access Tokens*, RFC 8705, February 2020. https://www.rfc-editor.org/rfc/rfc8705
8. D. Fett et al. *OAuth 2.0 Demonstrating Proof of Possession (DPoP)*, RFC 9449, September 2023. https://www.rfc-editor.org/rfc/rfc9449
9. IETF OAuth WG. *The OAuth 2.1 Authorization Framework*, draft-ietf-oauth-v2-1-17, 31 October 2026 (Internet-Draft). https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/
10. SPIFFE project. *SPIFFE Concepts*. https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/
11. Regulation (EU) 2024/2847 (Cyber Resilience Act), OJ L, 20.11.2024; Art. 14 and Art. 71. https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng
12. A. Freund. "backdoor in upstream xz/liblzma leading to ssh server compromise", oss-security, 29 March 2024. https://www.openwall.com/lists/oss-security/2024/03/29/4
13. NIST NVD. *CVE-2024-3094*, published 2024-03-29, CVSS 3.1 base 10.0. https://nvd.nist.gov/vuln/detail/CVE-2024-3094
14. NIST NVD. *CVE-2021-44228* (Log4Shell), published 2021-12-10, CVSS 3.1 base 10.0. https://nvd.nist.gov/vuln/detail/CVE-2021-44228
15. Kubernetes documentation. *Multi-tenancy*. https://kubernetes.io/docs/concepts/security/multi-tenancy/
16. L. Kohnfelder, P. Garg. *The Threats to Our Products*, Microsoft internal paper, 1 April 1999 (copy hosted by A. Shostack). https://threatmodelingbook.com/files/microsoft/The-Threats-To-Our-Products.docx
17. Microsoft. *Threats — Microsoft Threat Modeling Tool* (STRIDE categories). https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats
18. Kubernetes documentation. *Secrets*. https://kubernetes.io/docs/concepts/configuration/secret/
19. R. Pang et al. *Zanzibar: Google's Consistent, Global Authorization System*, USENIX ATC 2019, pp. 33–46. https://www.usenix.org/conference/atc19/presentation/pang
20. CNCF. "SPIFFE and SPIRE projects graduate from Cloud Native Computing Foundation incubator", 20 September 2022. https://www.cncf.io/announcements/2022/09/20/spiffe-and-spire-projects-graduate-from-cloud-native-computing-foundation-incubator
21. E. Rescorla. *The Transport Layer Security (TLS) Protocol Version 1.3*, RFC 8446, August 2018. https://www.rfc-editor.org/rfc/rfc8446
22. GitHub Docs. *About security hardening with OpenID Connect*. https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
23. HashiCorp. *Vault: Database secrets engine*. https://developer.hashicorp.com/vault/docs/secrets/databases
24. OWASP. *OWASP Top 10:2025*. https://top10.owasp.org/2025
25. gVisor documentation. *What is gVisor?* https://gvisor.dev/docs/
26. A. Agache et al. *Firecracker: Lightweight Virtualization for Serverless Applications*, USENIX NSDI 2020, pp. 419–434. https://www.usenix.org/conference/nsdi20/presentation/agache
27. Kata Containers project. https://katacontainers.io/
28. SPDX. *Specifications* (SPDX 3.0; SPDX 2.2.1 published as ISO/IEC 5962:2021). https://spdx.dev/use/specifications/
29. Ecma International. *ECMA-424: CycloneDX Bill of Materials Specification*, 2nd edition, December 2025. https://ecma-international.org/publications-and-standards/standards/ecma-424/
30. OpenSSF SLSA. *SLSA specification v1.2*. https://slsa.dev/spec/
31. Sigstore. *Sigstore overview*. https://docs.sigstore.dev/about/overview/
32. Reproducible Builds project. *Definitions*. https://reproducible-builds.org/docs/definition/
33. OpenSSF SLSA. *Build track basics (v1.2)*. https://slsa.dev/spec/v1.2/build-track-basics
34. Kubernetes documentation. *Verify Signed Kubernetes Artifacts*. https://kubernetes.io/docs/tasks/administer-cluster/verify-signed-artifacts/
35. J. Richer (ed.). *OAuth 2.0 Token Introspection*, RFC 7662, October 2015. https://www.rfc-editor.org/rfc/rfc7662
36. M. Jones et al. *OAuth 2.0 Token Exchange*, RFC 8693, January 2020. https://www.rfc-editor.org/rfc/rfc8693
37. Model Context Protocol. *Specification 2025-06-18 — Authorization*. https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
38. Kubernetes documentation. *Pod Security Standards*. https://kubernetes.io/docs/concepts/security/pod-security-standards/
39. ENISA. "The CRA Single Reporting Platform is launched". https://www.enisa.europa.eu/index.php/news/the-cra-single-reporting-platform-is-launched
40. NIST. *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard*, 13 August 2024. https://csrc.nist.gov/pubs/fips/203/final

### 19 — Privacy, compliance & data sovereignty

Lesson: [`course/02-modern-requirements/19-privacy-compliance-sovereignty.md`](course/02-modern-requirements/19-privacy-compliance-sovereignty.md) · source status: `DRAFT`

1. European Parliament and Council, Regulation (EU) 2016/679 (General Data Protection Regulation), OJ L 119, 4.5.2016. https://eur-lex.europa.eu/eli/reg/2016/679/oj
2. EDPB, Guidelines 4/2019 on Article 25 Data Protection by Design and by Default, version 2.0, adopted 20 October
2020. https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-42019-article-25-data-protection-design-and_en
3. Court of Justice of the EU, Judgment of 16 July 2020, *Data Protection Commissioner v Facebook Ireland and Maximillian Schrems* (Schrems II), C-311/18, ECLI:EU:C:2020:559. https://curia.europa.eu/juris/liste.jsf?num=C-311/18 ; Press Release No 91/20: https://curia.europa.eu/jcms/upload/docs/application/pdf/2020-07/cp200091en.pdf
4. EDPB, Recommendations 01/2020 on measures that supplement transfer tools to ensure compliance with the EU level of protection of personal data, version 2.0, adopted 18 June 2021. https://www.edpb.europa.eu/our-work-tools/our-documents/recommendations/recommendations-012020-measures-supplement-transfer_en
5. European Commission, Implementing Decision (EU) 2023/1795 of 10 July 2023 on the adequate level of protection of personal data under the EU–US Data Privacy Framework. https://eur-lex.europa.eu/eli/dec_impl/2023/1795/oj
6. General Court of the EU, Judgment of 3 September 2025, *Latombe v Commission*, T-553/23, ECLI:EU:T:2025:831. https://curia.europa.eu/juris/liste.jsf?num=T-553/23
7. Appeal brought on 31 October 2025 by Philippe Latombe, Case C-703/25 P, OJ C, 22.12.2025. https://eur-lex.europa.eu/eli/C/2025/6610/oj
8. European Commission, Report on the first periodic review of the functioning of the adequacy decision on the EU–US Data Privacy Framework, 9 October 2024. https://commission.europa.eu/document/25695177-8073-4ce3-bf81-eb816dc6b468_en
9. EDPB, "1.2 billion euro fine for Facebook as a result of EDPB binding decision", 22 May 2023. https://www.edpb.europa.eu/node/6052_en
10. European Parliament and Council, Regulation (EU) 2023/2854 (Data Act), OJ L, 22.12.2023 — Art. 29, 32, 50. https://eur-lex.europa.eu/eli/reg/2023/2854/oj
11. European Parliament and Council, Regulation (EU) 2024/1689 (Artificial Intelligence Act), OJ L, 12.7.2024 — Art. 4, 5, 10, 12, 19, 26, 113. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
12. European Parliament and Council, Regulation (EU) 2026/1744 of 8 July 2026 amending Regulations (EU) 2024/1689, (EU) 2018/1139 and (EU) 2023/1230 (Digital Omnibus on AI), OJ L, 24.7.2026. https://eur-lex.europa.eu/eli/reg/2026/1744/oj
13. European Parliament, Legislative Train Schedule, "Digital Omnibus Regulation Proposal", procedure 2025/0360(COD), page updated 25 October 2026. https://www.europarl.europa.eu/legislative-train/theme-a-new-plan-for-europe-s-sustainable-prosperity-and-competitiveness/file-digital-package
14. EDPB, 2025 Coordinated Enforcement Action: Implementation of the right to erasure by controllers, adopted 10 February 2026. https://www.edpb.europa.eu/system/files/2026-02/edpb_cef-report_2025_right-to-erasure_en.pdf
15. Court of Justice of the EU, Judgment of 4 September 2025, *EDPS v SRB*, C-413/23 P, ECLI:EU:C:2025:645. https://curia.europa.eu/juris/liste.jsf?num=C-413/23
16. EDPB, Opinion 28/2024 on certain data protection aspects related to the processing of personal data in the context of AI models, December 2024. https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en
17. NIST, SP 800-88 Rev. 2, *Guidelines for Media Sanitization*, September 2025. https://csrc.nist.gov/pubs/sp/800/88/r2/final
18. Amazon Web Services, AWS KMS Developer Guide, "Delete an AWS KMS key". https://docs.aws.amazon.com/kms/latest/developerguide/deleting-keys.html
19. Google Cloud, "Data deletion on Google Cloud". https://docs.cloud.google.com/docs/security/deletion
20. Apache Kafka 4.2 documentation, Topic Configs (`retention.ms`, `delete.retention.ms`, `cleanup.policy`, `max.compaction.lag.ms`). https://kafka.apache.org/42/configuration/topic-configs/
21. S. A. Crosby and D. S. Wallach, "Efficient Data Structures for Tamper-Evident Logging", USENIX Security 2009. https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf
22. B. Laurie, E. Messeri, R. Stradling, RFC 9162, *Certificate Transparency Version 2.0*, IETF, December 2021. https://www.rfc-editor.org/rfc/rfc9162
23. L. Bourtoule et al., "Machine Unlearning", IEEE Symposium on Security and Privacy 2021 (arXiv:1912.03817). https://arxiv.org/abs/1912.03817
24. N. Carlini et al., "Extracting Training Data from Large Language Models", USENIX Security 2021 (arXiv:2012.07805). https://arxiv.org/abs/2012.07805
25. OpenLineage project (LF AI & Data), OpenLineage specification. https://openlineage.io/
26. European Commission, "Commission advances cloud sovereignty through strategic procurement", 17 April 2026. https://commission.europa.eu/news-and-media/news/commission-advances-cloud-sovereignty-through-strategic-procurement-2026-04-17_en
27. 18 U.S.C. § 2713, Required preservation and disclosure of communications and records (CLOUD Act). https://www.law.cornell.edu/uscode/text/18/2713
28. Nextgov/FCW, "House passes 45-day FISA extension after senators secure declassification deal", April 2026 (news report; perspective only). https://www.nextgov.com/policy/2026/04/house-passes-45-day-fisa-extension-after-senators-secure-declassification-deal/413250/

### 20 — Real-time & streaming systems

Lesson: [`course/02-modern-requirements/20-real-time-streaming.md`](course/02-modern-requirements/20-real-time-streaming.md) · source status: `DRAFT`

1. T. Akidau, R. Bradshaw, C. Chambers, S. Chernyak, R. J. Fernández-Moctezuma, R. Lax, S. McVeety, D. Mills, F. Perry, E. Schmidt, S. Whittle. "The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing." PVLDB 8(12):1792–1803, 2015. https://www.vldb.org/pvldb/vol8/p1792-Akidau.pdf
2. P. Carbone, G. Fóra, S. Ewen, S. Haridi, K. Tzoumas. "Lightweight Asynchronous Snapshots for Distributed Dataflows." arXiv:1506.08603, 2015 (preprint). https://arxiv.org/abs/1506.08603
3. P. Carbone, S. Ewen, G. Fóra, S. Haridi, S. Richter, K. Tzoumas. "State Management in Apache Flink: Consistent Stateful Distributed Stream Processing." PVLDB 10(12):1718–1729, 2017. https://www.vldb.org/pvldb/vol10/p1718-carbone.pdf
4. K. M. Chandy, L. Lamport. "Distributed Snapshots: Determining Global States of Distributed Systems." ACM TOCS 3(1):63–75,
1985. https://www.cs.princeton.edu/courses/archive/fall17/cos418/papers/chandy_lamport.pdf
5. Apache Kafka. "KIP-98 — Exactly Once Delivery and Transactional Messaging." https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging
6. Apache Kafka 4.4 documentation. "Kafka Streams — Core Concepts." https://kafka.apache.org/44/streams/core-concepts/
7. Apache Kafka 4.4 documentation. "Configuring a Streams Application" (`processing.guarantee`, `commit.interval.ms`). https://kafka.apache.org/44/streams/developer-guide/config-streams/
8. Apache Flink 2.3 documentation. "Timely Stream Processing." https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/
9. Apache Flink 2.3 documentation. "Generating Watermarks." https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/event-time/generating_watermarks/
10. Apache Flink 2.3 documentation. "Checkpointing under backpressure." https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/checkpointing_under_backpressure/
11. Apache Flink 2.3 documentation. "Checkpoints vs. Savepoints." https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/checkpoints_vs_savepoints/
12. Apache Flink 2.3 documentation. "Kafka connector" (Kafka Sink fault tolerance). https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/kafka/
13. Apache Flink 2.3 documentation. "Dynamic Tables." https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/sql-table-concepts/dynamic_tables/
14. Y. Mei, Z. Lan, L. Huang, Y. Lei, H. Yin, R. Xia, K. Hu, P. Carbone, V. Kalavri, F. Wang. "Disaggregated State Management in Apache Flink 2.0." PVLDB 18(12), 2025. https://www.vldb.org/pvldb/vol18/p4846-mei.pdf
15. Debezium 3.7 documentation. "Debezium connector for PostgreSQL." https://debezium.io/documentation/reference/stable/connectors/postgresql.html
16. Debezium documentation. "Outbox Event Router." https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html
17. Debezium. "Releases" (3.7 latest stable series; 3.7.1.Final, 2026-11-06). https://debezium.io/releases/
18. PostgreSQL documentation (current). "Server Configuration — Replication" (`max_slot_wal_keep_size`, `idle_replication_slot_timeout`). https://www.postgresql.org/docs/current/runtime-config-replication.html
19. A. Andreakis, I. Papapanagiotou. "DBLog: A Watermark Based Change-Data-Capture Framework." arXiv:2010.12597, 2020 (preprint). https://arxiv.org/abs/2010.12597
20. J. Kreps. "Questioning the Lambda Architecture." O'Reilly Radar, 2014-07-02. https://www.oreilly.com/radar/questioning-the-lambda-architecture/
21. Apache Druid documentation (latest). "Introduction to Apache Druid" / design. https://druid.apache.org/docs/latest/design/
22. Apache Druid documentation (latest). "Apache Kafka ingestion." https://druid.apache.org/docs/latest/ingestion/kafka-ingestion/
23. Apache Pinot documentation. "Stream Ingestion with Upsert." https://docs.pinot.apache.org/build-with-pinot/ingestion/upsert-dedup/upsert
24. ClickHouse documentation. "ReplacingMergeTree." https://clickhouse.com/docs/engines/table-engines/mergetree-family/replacingmergetree
25. ClickHouse documentation. "Kafka table engine." https://clickhouse.com/docs/engines/table-engines/integrations/kafka
26. Feast documentation. "Push source" and "Stream feature view." https://docs.feast.dev/reference/data-sources/push ; https://docs.feast.dev/getting-started/concepts/stream-feature-view
27. Apache Flink. "Downloads" (2.3.0 latest stable, 2026-06-25). https://flink.apache.org/downloads/
28. Apache Kafka. "Downloads" (4.4.0, 2026-10-22). https://kafka.apache.org/community/downloads/
29. Apache Kafka 4.1 documentation. "Upgrading" (4.0 supports only KRaft mode; ZooKeeper mode removed). https://kafka.apache.org/41/getting-started/upgrade/
30. Apache Kafka. "Apache Kafka 4.1.0 Release Announcement" (KIP-932 Queues for Kafka in preview), 2025-09-04. https://kafka.apache.org/blog/2025/09/04/apache-kafka-4.1.0-release-announcement/

## Part III — AI-native systems

### 21 — Anatomy of LLM inference

Lesson: [`course/03-ai-systems/21-llm-inference-anatomy.md`](course/03-ai-systems/21-llm-inference-anatomy.md) · source status: `DRAFT`

1. Qwen Team, *Qwen3-8B model card*, Hugging Face, 2025. https://huggingface.co/Qwen/Qwen3-8B
2. Qwen Team, *Qwen3-8B config.json* (num_hidden_layers 36, num_attention_heads 32, num_key_value_heads 8, head_dim 128, vocab_size 151936). https://huggingface.co/Qwen/Qwen3-8B/blob/main/config.json
3. Qwen Team, *Qwen3-32B model card and config.json* (64 layers, 64 Q / 8 KV heads, 32.8 B parameters). https://huggingface.co/Qwen/Qwen3-32B
4. W. Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention*, SOSP 2023. arXiv:2309.06180. https://arxiv.org/abs/2309.06180
5. vLLM project, *Metrics (design doc)*, docs.vllm.ai. https://docs.vllm.ai/en/latest/design/metrics.html
6. vLLM project, *vllm/benchmarks/serve.py* (TTFT, TPOT, ITL, request_goodput definitions), v0.34.0. https://github.com/vllm-project/vllm/blob/v0.34.0/vllm/benchmarks/serve.py
7. vLLM Team, *vLLM V1: A Major Upgrade to vLLM's Core Architecture*, 2025-01-27. https://vllm.ai/blog/2025-01-27-v1-alpha-release
8. vLLM project, *OpenAI-Compatible Server*. https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
9. vLLM project, *Disaggregated Prefilling (experimental)*, docs/features/disagg_prefill.md, v0.34.0. https://github.com/vllm-project/vllm/blob/v0.34.0/docs/features/disagg_prefill.md
10. vLLM project, *Optimization and Tuning* (preemption, chunked prefill), docs/configuration/optimization.md, v0.34.0; and *Quantization* docs. https://docs.vllm.ai/en/latest/configuration/optimization.html
11. Y. Zhong et al., *DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving*, OSDI 2024. arXiv:2401.09670. https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin
12. P. Patel et al., *Splitwise: Efficient Generative LLM Inference Using Phase Splitting*, ISCA 2024. arXiv:2311.18677. https://arxiv.org/abs/2311.18677
13. R. Sennrich, B. Haddow, A. Birch, *Neural Machine Translation of Rare Words with Subword Units*, ACL 2016. arXiv:1508.07909. https://arxiv.org/abs/1508.07909
14. A. Agrawal et al., *Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve*, OSDI 2024. arXiv:2403.02310. https://www.usenix.org/conference/osdi24/presentation/agrawal
15. S. Williams, A. Waterman, D. Patterson, *Roofline: An Insightful Visual Performance Model for Multicore Architectures*, Communications of the ACM 52(4), 2009. https://doi.org/10.1145/1498765.1498785
16. N. Shazeer, *Fast Transformer Decoding: One Write-Head is All You Need*, 2019. arXiv:1911.02150. https://arxiv.org/abs/1911.02150
17. J. Ainslie et al., *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*, EMNLP 2023. arXiv:2305.13245. https://arxiv.org/abs/2305.13245
18. A. Grattafiori et al. (Llama Team, Meta), *The Llama 3 Herd of Models*, arXiv:2407.21783, 2024 (Table 3: layers, heads, KV heads). https://arxiv.org/abs/2407.21783
19. WHATWG, *HTML Living Standard — Server-sent events*. https://html.spec.whatwg.org/multipage/server-sent-events.html
20. J. Dean, L. A. Barroso, *The Tail at Scale*, Communications of the ACM 56(2), 2013. https://doi.org/10.1145/2408776.2408794
21. G.-I. Yu et al., *Orca: A Distributed Serving System for Transformer-Based Generative Models*, OSDI 2022. https://www.usenix.org/conference/osdi22/presentation/yu
22. ggml-org, *llama.cpp server README* ("Continuous batching", `--parallel`, `--cont-batching`). https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
23. NVIDIA, *H100 Tensor Core GPU — product specifications*. https://www.nvidia.com/en-us/data-center/h100/
24. NVIDIA, *H200 Tensor Core GPU — specifications* (141 GB, 4.8 TB/s; marked preliminary). https://www.nvidia.com/en-us/data-center/h200/
25. AMD, *Instinct MI300X accelerator — specifications* (192 GB HBM3, 5.3 TB/s, 1.3 PFLOPs FP16). https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html
26. Qwen Team, *Qwen2.5-0.5B-Instruct model card* (0.49 B parameters, 24 layers, 14 Q / 2 KV heads). https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
27. J. Lin et al., *AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration*, MLSys 2024 (Best Paper). arXiv:2306.00978. https://arxiv.org/abs/2306.00978
28. E. Frantar et al., *GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers*, ICLR 2023. arXiv:2210.17323. https://arxiv.org/abs/2210.17323
29. OpenAI, *gpt-oss-120b config.json* (num_local_experts 128, num_experts_per_tok 4, sliding_window 128). https://huggingface.co/openai/gpt-oss-120b/blob/main/config.json
30. A. Agrawal et al., *SARATHI: Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills*, 2023. arXiv:2308.16369 (preprint). https://arxiv.org/abs/2308.16369
31. vLLM project, *Speculative Decoding*. https://docs.vllm.ai/en/latest/features/speculative_decoding/
32. vLLM project, *Release v0.34.0* (2026-11-16): default block size 64, extensible KV cache on by default. https://github.com/vllm-project/vllm/releases/tag/v0.34.0

### 22 — Serving LLMs at scale

Lesson: [`course/03-ai-systems/22-serving-llms-at-scale.md`](course/03-ai-systems/22-serving-llms-at-scale.md) · source status: `DRAFT`

1. Qwen Team, *Qwen3-32B model card and config.json*, Hugging Face. https://huggingface.co/Qwen/Qwen3-32B
2. vLLM Team, *vLLM V1: A Major Upgrade to vLLM's Core Architecture*, 2025-01-27. https://vllm.ai/blog/2025-01-27-v1-alpha-release
3. vLLM project, *GitHub releases v0.8.0 (V1 default), v0.9.2 (priority scheduling in V1; last version with V0 intact), v0.11.0 (V0 removed)*. https://github.com/vllm-project/vllm/releases
4. vLLM project, *Release v0.34.0*, 2026-11-16. https://github.com/vllm-project/vllm/releases/tag/v0.34.0
5. Y. Zhong et al., *DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving*, OSDI 2024. arXiv:2401.09670. https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin
6. P. Patel et al., *Splitwise: Efficient Generative LLM Inference Using Phase Splitting*, ISCA 2024. arXiv:2311.18677. https://www.microsoft.com/en-us/research/publication/splitwise-efficient-generative-llm-inference-using-phase-splitting/
7. R. Qin et al., *Mooncake: Trading More Storage for Less Computation — A KVCache-centric Architecture for Serving LLM Chatbot*, FAST 2025 (Best Paper). arXiv:2407.00079. https://www.usenix.org/conference/fast25/presentation/qin
8. vLLM project, *Disaggregated Prefilling (experimental)*, v0.34.0. https://github.com/vllm-project/vllm/blob/v0.34.0/docs/features/disagg_prefill.md
9. NVIDIA, *Dynamo — README* (v1.6.2, 2026-11-05). https://github.com/ai-dynamo/dynamo
10. llm-d project, *README and releases* (v1.0.0, 2026-10-20; CNCF Sandbox since 2026-03). https://github.com/llm-d/llm-d
11. Kubernetes SIG Network, *Gateway API Inference Extension — README; release v1.0.0 (2025-09-09, InferencePool v1); latest v1.6.2*. https://github.com/kubernetes-sigs/gateway-api-inference-extension
12. KServe project, *README* (CNCF incubating; v0.21.0, 2026-09-25). https://github.com/kserve/kserve
13. Hugging Face, *text-generation-inference README* (maintenance mode; repository archived; v3.3.7, 2025-12-19). https://github.com/huggingface/text-generation-inference
14. W. Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention*, SOSP 2023. arXiv:2309.06180. https://arxiv.org/abs/2309.06180
15. G.-I. Yu, J. S. Jeong, G.-W. Kim, S. Kim, B.-G. Chun, *Orca: A Distributed Serving System for Transformer-Based Generative Models*, OSDI 2022. https://www.usenix.org/conference/osdi22/presentation/yu
16. vLLM project, *Optimization and Tuning* (preemption, chunked prefill), v0.34.0. https://docs.vllm.ai/en/latest/configuration/optimization.html
17. vLLM project, *Automatic Prefix Caching (design)*. https://docs.vllm.ai/en/latest/design/prefix_caching.html
18. L. Zheng et al., *SGLang: Efficient Execution of Structured Language Model Programs*, NeurIPS 2024. arXiv:2312.07104. https://proceedings.neurips.cc/paper_files/paper/2024/hash/724be4472168f31ba1c9ac630f15dec8-Abstract-Conference.html
19. A. Agrawal et al., *Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve*, OSDI 2024. arXiv:2403.02310. https://www.usenix.org/conference/osdi24/presentation/agrawal
20. vLLM project, *Architecture Overview* (V1 process architecture), v0.34.0. https://docs.vllm.ai/en/latest/design/arch_overview.html
21. vLLM project, *OpenAI-Compatible Server*. https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
22. vLLM project, *Structured Outputs*, v0.34.0. https://docs.vllm.ai/en/latest/features/structured_outputs.html
23. L. Chen et al., *Punica: Multi-Tenant LoRA Serving*, MLSys 2024. arXiv:2310.18547. https://proceedings.mlsys.org/paper_files/paper/2024/hash/054de805fcceb78a201f5e9d53c85908-Abstract-Conference.html
24. Y. Sheng et al., *S-LoRA: Serving Thousands of Concurrent LoRA Adapters*, 2023. arXiv:2311.03285. https://arxiv.org/abs/2311.03285
25. vLLM project, *LoRA Adapters*, v0.34.0. https://docs.vllm.ai/en/latest/features/lora.html
26. vLLM project, *Metrics (design doc)*. https://docs.vllm.ai/en/latest/design/metrics.html
27. NVIDIA, *NIXL — NVIDIA Inference Xfer Library, README* (v1.5.2, 2026-10-29). https://github.com/ai-dynamo/nixl
28. LMCache project, *README*. https://github.com/LMCache/LMCache
29. NVIDIA, *H100 Tensor Core GPU — product specifications*. https://www.nvidia.com/en-us/data-center/h100/
30. Y. Leviathan, M. Kalman, Y. Matias, *Fast Inference from Transformers via Speculative Decoding*, ICML 2023. arXiv:2211.17192. https://arxiv.org/abs/2211.17192
31. vLLM project, *Speculative Decoding*. https://docs.vllm.ai/en/latest/features/speculative_decoding/
32. SGLang project, *README* (v0.5.23, 2026-11-02). https://github.com/sgl-project/sglang
33. NVIDIA, *TensorRT-LLM README* (v1.4.0rc4, 2026-11-18). https://github.com/NVIDIA/TensorRT-LLM
34. ggml-org, *llama.cpp server README*. https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
35. vLLM project, *production-stack README* (vllm-stack-0.1.14, 2026-11-07). https://github.com/vllm-project/production-stack
36. vLLM project, *Parallelism and Scaling*, v0.34.0. https://docs.vllm.ai/en/latest/serving/parallelism_scaling.html
37. vLLM project, *Quantization* (supported methods; LLM Compressor; NVFP4), v0.34.0. https://docs.vllm.ai/en/latest/features/quantization/
38. J. Lin et al., *AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration*, MLSys 2024 (Best Paper). arXiv:2306.00978. https://arxiv.org/abs/2306.00978
39. E. Frantar, S. Ashkboos, T. Hoefler, D. Alistarh, *GPTQ*, ICLR 2023. arXiv:2210.17323. https://arxiv.org/abs/2210.17323
40. vLLM project, *Quantized KV Cache*, v0.34.0. https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache.html
41. Y. Li, F. Wei, C. Zhang, H. Zhang, *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty*, 2024. arXiv:2401.15077. https://arxiv.org/abs/2401.15077
42. Y. Li et al., *EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test*, 2025. arXiv:2503.01840 (preprint). https://arxiv.org/abs/2503.01840
43. vLLM project, *Loading models with Run:ai Model Streamer*, v0.34.0. https://docs.vllm.ai/en/latest/models/extensions/runai_model_streamer.html
44. vLLM project, *Sleep Mode*, v0.34.0. https://docs.vllm.ai/en/latest/features/sleep_mode.html
45. Ollama project, *GitHub releases* (v0.40.16, 2026-11-09). https://github.com/ollama/ollama/releases

### 23 — GPU & accelerator infrastructure

Lesson: [`course/03-ai-systems/23-gpu-infrastructure.md`](course/03-ai-systems/23-gpu-infrastructure.md) · source status: `DRAFT`

1. NVIDIA, *H100 Tensor Core GPU — product specifications* (80 GB, 3.35 TB/s, sparsity footnote, NVLink 900 GB/s, PCIe Gen5 128 GB/s, MIG up to 7). https://www.nvidia.com/en-us/data-center/h100/
2. NVIDIA, *H200 Tensor Core GPU — specifications* (141 GB, 4.8 TB/s; preliminary). https://www.nvidia.com/en-us/data-center/h200/
3. NVIDIA, *DGX B200 — specifications* (8 GPUs, 1,440 GB, 64 TB/s, FP8 72 PFLOPS sparse, NVLink 14.4 TB/s, ConnectX-7 400 Gb/s, ~14.3 kW). https://www.nvidia.com/en-us/data-center/dgx-b200/
4. NVIDIA, *GB200 NVL72 — specifications* (72 GPUs, 13.4 TB HBM3E, 576 TB/s, 130 TB/s NVLink, liquid-cooled). https://www.nvidia.com/en-us/data-center/gb200-nvl72/
5. AMD, *Instinct MI300X — specifications* (192 GB, 5.3 TB/s, 1.3 PFLOPs FP16, 750 W). https://www.amd.com/en/products/accelerators/instinct/mi300/mi300x.html
6. AMD, *Instinct MI355X — specifications* (288 GB, 8 TB/s, 2.5 PFLOPs FP16, 1,400 W). https://www.amd.com/en/products/accelerators/instinct/mi350/mi355x.html
7. Google Cloud, *TPU7x (Ironwood)* documentation (192 GiB, 7,380 GB/s, 2,307 BF16 / 4,614 FP8 TFLOPS, 9,216 chips per pod). https://docs.cloud.google.com/tpu/docs/tpu7x
8. AWS, *AWS Trainium* product page (Trainium3: 144 GB HBM3e, 4.9 TB/s, UltraServers up to 144 chips). https://aws.amazon.com/ai/machine-learning/trainium/
9. Kubernetes, *Kubernetes v1.34: DRA has graduated to GA*, 2025-09-01; and *Dynamic Resource Allocation* concept page. https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/ ; https://kubernetes.io/docs/concepts/scheduling-eviction/dynamic-resource-allocation/
10. Kubernetes, *Gang Scheduling* concept page (beta since v1.37, disabled by default; CompositePodGroup alpha in v1.37). https://kubernetes.io/docs/concepts/scheduling-eviction/gang-scheduling/
11. PyTorch, *torch.cuda.utilization* ("percent of time over the past sample period during which one or more kernels was executing on the GPU as given by nvidia-smi"). https://docs.pytorch.org/docs/stable/generated/torch.cuda.utilization.html
12. Kubernetes SIGs, *Kueue README* (v0.20.7, 2026-11-19). https://github.com/kubernetes-sigs/kueue
13. Volcano project, *README* (CNCF incubating; v1.16.0, 2026-10-14). https://github.com/volcano-sh/volcano
14. SchedMD / Slinky project, *slurm-operator README* (v1.3.0, 2026-11-19). https://github.com/SlinkyProject/slurm-operator
15. NVIDIA, *NVIDIA Acquires Open-Source Workload Management Provider SchedMD*, 2025-12-15. https://blogs.nvidia.com/blog/nvidia-acquires-schedmd/
16. A. Grattafiori et al. (Llama Team, Meta), *The Llama 3 Herd of Models*, arXiv:2407.21783, 2024 (Table 3; §3.3.4 reliability, Table 5). https://arxiv.org/abs/2407.21783
17. T. Dao et al., *FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness*, NeurIPS 2022. arXiv:2205.14135. https://arxiv.org/abs/2205.14135
18. NVIDIA, *Quantum-X800 InfiniBand platform* (144 ports of 800 Gb/s). https://www.nvidia.com/en-us/networking/products/infiniband/quantum-x800/
19. Ultra Ethernet Consortium, *UEC Specification 1.0* (2025-06-11) and Linux Foundation press release. https://ultraethernet.org/specification ; https://www.linuxfoundation.org/press/uec-launches-spec-1.0
20. NVIDIA, *GPU Operator overview* and releases (v26.7.3, 2026-11-17). https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/latest/overview.html ; https://github.com/NVIDIA/gpu-operator/releases
21. Kubernetes, *GitHub releases* (v1.37.2, v1.36.6, v1.35.10 on 2026-10-28). https://github.com/kubernetes/kubernetes/releases
22. Kubernetes SIGs / NVIDIA, *DRA Driver for NVIDIA GPUs README* (v0.5.1, 2026-10-12). https://github.com/kubernetes-sigs/dra-driver-nvidia-gpu
23. NVIDIA, *MIG User Guide — Introduction*. https://docs.nvidia.com/datacenter/tesla/mig-user-guide/introduction.html
24. NVIDIA, *k8s-device-plugin README* (time-slicing, MPS, MIG strategies; v0.20.2). https://github.com/NVIDIA/k8s-device-plugin
25. NVIDIA, *MIG User Guide — Supported MIG Profiles* (H100 80GB). https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-mig-profiles.html
26. NVIDIA, *DCGM User Guide — Feature Overview* (profiling metrics). https://docs.nvidia.com/datacenter/dcgm/latest/user-guide/feature-overview.html
27. NVIDIA, *dcgm-exporter releases* (4.9.0, 2026-11-06). https://github.com/NVIDIA/dcgm-exporter/releases
28. vLLM project, *Parallelism and Scaling*, v0.34.0. https://docs.vllm.ai/en/latest/serving/parallelism_scaling.html
29. NVIDIA, *Xid Errors — Analyzing Xid Errors with the Xid Catalog*. https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html
30. vLLM project, *Release v0.34.0* (ROCm 10.0 images; quantisation changes). https://github.com/vllm-project/vllm/releases/tag/v0.34.0
31. SGLang project, *README* (hardware platforms). https://github.com/sgl-project/sglang
32. llm-d project, *README* (adopters and AMD MI300X results). https://github.com/llm-d/llm-d
33. S. Rajbhandari, J. Rasley, O. Ruwase, Y. He, *ZeRO: Memory Optimizations Toward Training Trillion Parameter Models*, SC 2020. arXiv:1910.02054 ("2Ψ + 2Ψ + KΨ = 16Ψ bytes", K = 12 for mixed-precision Adam). https://arxiv.org/abs/1910.02054

### 24 — Retrieval & vector systems

Lesson: [`course/03-ai-systems/24-retrieval-vector-systems.md`](course/03-ai-systems/24-retrieval-vector-systems.md) · source status: `DRAFT`

1. Lewis, P. et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." NeurIPS 2020. arXiv:2005.11401. https://arxiv.org/abs/2005.11401
2. Malkov, Yu. A., Yashunin, D. A. "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs." arXiv:1603.09320 (2016); IEEE TPAMI 42(4), 2020 (online 2018), doi:10.1109/TPAMI.2018.2889473. https://arxiv.org/abs/1603.09320
3. Jégou, H., Douze, M., Schmid, C. "Product Quantization for Nearest Neighbor Search." IEEE TPAMI 33(1), 2011. doi:10.1109/TPAMI.2010.57
4. Subramanya, S. J., Devvrit, F., Simhadri, H. V., Krishnaswamy, R., Kadekodi, R. "DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node." NeurIPS 2019. https://papers.nips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html
5. Kusupati, A. et al. "Matryoshka Representation Learning." NeurIPS 2022. arXiv:2205.13147. https://arxiv.org/abs/2205.13147
6. Guo, R. et al. "Accelerating Large-Scale Inference with Anisotropic Vector Quantization." ICML 2020. arXiv:1908.10396; code: https://github.com/google-research/google-research/tree/master/scann
7. Robertson, S., Zaragoza, H. "The Probabilistic Relevance Framework: BM25 and Beyond." Foundations and Trends in IR 3(4), 2009. doi:10.1561/1500000019
8. Cormack, G. V., Clarke, C. L. A., Büttcher, S. "Reciprocal rank fusion outperforms Condorcet and individual rank learning methods." SIGIR 2009. doi:10.1145/1571941.1572114
9. Gollapudi, S. et al. "Filtered-DiskANN: Graph Algorithms for Approximate Nearest Neighbor Search with Filters." ACM Web Conference 2023. doi:10.1145/3543507.3583552
10. Patel, L., Kraft, P., Guestrin, C., Zaharia, M. "ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data." SIGMOD 2024. arXiv:2403.04871. https://arxiv.org/abs/2403.04871
11. Liu, N. F. et al. "Lost in the Middle: How Language Models Use Long Contexts." TACL 2024. arXiv:2307.03172. https://arxiv.org/abs/2307.03172
12. Hsieh, C.-P. et al. "RULER: What's the Real Context Size of Your Long-Context Language Models?" arXiv:2404.06654 (2024). https://arxiv.org/abs/2404.06654
13. Xu, P. et al. "Retrieval meets Long Context Large Language Models." ICLR 2024. arXiv:2310.03025. https://arxiv.org/abs/2310.03025
14. Aumüller, M., Bernhardsson, E., Faithfull, A. "ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms." arXiv:1807.05614; https://ann-benchmarks.com
15. hnswlib maintainers. "HNSW algorithm parameters" (ALGO_PARAMS.md). https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md
16. pgvector maintainers. pgvector README, v0.8.7. https://github.com/pgvector/pgvector
17. Qdrant. "Filtering" and "Indexing" documentation (v1.20). https://qdrant.tech/documentation/concepts/filtering/ ; https://qdrant.tech/documentation/manage-data/indexing/
18. Milvus. "Index" documentation (v3.0.x). https://milvus.io/docs/index.md
19. Weaviate. "Hybrid search" concepts. https://docs.weaviate.io/weaviate/concepts/search/hybrid-search
20. OpenSearch. "Methods and engines" (k-NN vector). https://docs.opensearch.org/latest/mappings/supported-field-types/knn-methods-engines/
21. Elastic. "dense_vector field type" reference (index_options defaults by version). https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector
22. Nomic AI. "nomic-embed-text-v1.5" model card (Matryoshka dimensions, task prefixes). https://huggingface.co/nomic-ai/nomic-embed-text-v1.5
23. sentence-transformers. "all-MiniLM-L6-v2" model card (384 dimensions, 256 word-piece limit). https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
24. Nogueira, R., Cho, K. "Passage Re-ranking with BERT." arXiv:1901.04085 (2019). https://arxiv.org/abs/1901.04085
25. Khattab, O., Zaharia, M. "ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT." SIGIR 2020. arXiv:2004.12832
26. Anthropic. "Introducing Contextual Retrieval" (vendor engineering blog, 2024). https://www.anthropic.com/news/contextual-retrieval
27. LanceDB documentation. https://docs.lancedb.com/
28. Douze, M. et al. "The Faiss library." arXiv:2401.08281 (2024). https://arxiv.org/abs/2401.08281
29. Edge, D. et al. "From Local to Global: A Graph RAG Approach to Query-Focused Summarization." arXiv:2404.16130 (2024). https://arxiv.org/abs/2404.16130
30. Järvelin, K., Kekäläinen, J. "Cumulated gain-based evaluation of IR techniques." ACM TOIS 20(4), 2002. doi:10.1145/582415.582418
31. Thakur, N. et al. "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models." NeurIPS 2021 Datasets & Benchmarks. arXiv:2104.08663
32. Muennighoff, N. et al. "MTEB: Massive Text Embedding Benchmark." EACL 2023. arXiv:2210.07316
33. Es, S., James, J., Espinosa-Anke, L., Schockaert, S. "Ragas: Automated Evaluation of Retrieval Augmented Generation." EACL 2024 (demo). arXiv:2309.15217. https://arxiv.org/abs/2309.15217
34. ragas maintainers. "Available metrics" (ragas v0.4.4). https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/
35. Microsoft. GraphRAG (v3.3.0). https://github.com/microsoft/graphrag ; https://microsoft.github.io/graphrag/
36. Weaviate. "Multi-tenancy" and "Vector indexing" docs. https://docs.weaviate.io/weaviate/manage-collections/multi-tenancy ; https://docs.weaviate.io/weaviate/concepts/vector-index

### 25 — Agentic systems

Lesson: [`course/03-ai-systems/25-agentic-systems.md`](course/03-ai-systems/25-agentic-systems.md) · source status: `DRAFT`

1. Yao, S. et al. "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023. arXiv:2210.03629. https://arxiv.org/abs/2210.03629
2. Schick, T. et al. "Toolformer: Language Models Can Teach Themselves to Use Tools." NeurIPS 2023. arXiv:2302.04761. https://arxiv.org/abs/2302.04761
3. Model Context Protocol. "Versioning" (current revision 2026-07-28). https://modelcontextprotocol.io/specification/versioning
4. Model Context Protocol. Specification, revision 2026-07-28 (server features: tools, resources, prompts). https://modelcontextprotocol.io/specification/2026-07-28 ; https://modelcontextprotocol.io/specification/2026-07-28/server/tools
5. MCP maintainers. "MCP 2026-07-28" release post (stateless core, Tasks extension, deprecations, authorization changes). https://blog.modelcontextprotocol.io/posts/2026-07-28/
6. Linux Foundation. "Linux Foundation Announces the Formation of the Agentic AI Foundation" (press release, 9 Dec 2025). https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
7. A2A project. Releases v1.0.0 (2026-03-12), v1.0.1 (2026-05-28). https://github.com/a2aproject/A2A/releases
8. A2A project. Documentation and "Key concepts". https://a2a-protocol.org/latest/ ; https://a2a-protocol.org/latest/topics/key-concepts/ ; specification https://a2a-protocol.org/latest/specification/
9. OpenTelemetry. GenAI semantic conventions (agent spans, execute_tool, MCP), status Development. https://github.com/open-telemetry/semantic-conventions-genai
10. LangChain. LangGraph "Persistence" and "Interrupts" docs (LangGraph 1.2.x). https://docs.langchain.com/oss/python/langgraph/persistence ; https://docs.langchain.com/oss/python/langgraph/interrupts
11. Temporal. "Workflow Execution" and "Understanding Temporal". https://docs.temporal.io/workflow-execution ; https://docs.temporal.io/evaluate/understanding-temporal
12. Yao, S., Shinn, N., Razavi, P., Narasimhan, K. "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains." arXiv:2406.12045 (2024). https://arxiv.org/abs/2406.12045
13. Jimenez, C. E. et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" ICLR 2024. arXiv:2310.06770. https://arxiv.org/abs/2310.06770
14. Princeton NLP / SWE-bench team. "SWE-bench Verified" dataset card (500 human-validated tasks). https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified ; leaderboard https://www.swebench.com/
15. gVisor documentation. https://gvisor.dev/docs/
16. Agache, A. et al. "Firecracker: Lightweight Virtualization for Serverless Applications." NSDI 2020. https://www.usenix.org/conference/nsdi20/presentation/agache
17. Greshake, K. et al. "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." AISec 2023. arXiv:2302.12173. https://arxiv.org/abs/2302.12173
18. Debenedetti, E. et al. "Defeating Prompt Injections by Design" (CaMeL). arXiv:2503.18813 (2025). https://arxiv.org/abs/2503.18813
19. Debenedetti, E. et al. "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents." NeurIPS 2024 Datasets & Benchmarks. arXiv:2406.13352
20. Anthropic. "Building effective agents" (engineering blog, Dec 2024; perspective). https://www.anthropic.com/engineering/building-effective-agents
21. Packer, C. et al. "MemGPT: Towards LLMs as Operating Systems." arXiv:2310.08560 (2023). https://arxiv.org/abs/2310.08560
22. Park, J. S. et al. "Generative Agents: Interactive Simulacra of Human Behavior." UIST 2023. arXiv:2304.03442
23. OWASP GenAI Security Project. "LLM06:2025 Excessive Agency." https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
24. Firecracker project site (stated startup time, memory overhead, creation rate). https://firecracker-microvm.github.io/
25. Willison, S. "The lethal trifecta for AI agents" (blog, 16 Jun 2025; perspective). https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
26. Mialon, G. et al. "GAIA: a benchmark for General AI Assistants." arXiv:2311.12983 (2023). https://arxiv.org/abs/2311.12983
27. Liu, X. et al. "AgentBench: Evaluating LLMs as Agents." ICLR 2024. arXiv:2308.03688
28. Zhou, S. et al. "WebArena: A Realistic Web Environment for Building Autonomous Agents." arXiv:2307.13854 (2023). https://arxiv.org/abs/2307.13854
29. Kong. "AI Gateway" documentation (LLM, MCP and A2A traffic). https://developer.konghq.com/ai-gateway/
30. Agent Router (formerly Envoy AI Gateway), README, v1.3.0. https://github.com/theagentrouter/agent-router
31. Linux Foundation. "A2A protocol surpasses 150 organizations…" (press release, Apr 2026). https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year

### 26 — LLM gateways & LLMOps

Lesson: [`course/03-ai-systems/26-llm-gateways-llmops.md`](course/03-ai-systems/26-llm-gateways-llmops.md) · source status: `DRAFT`

1. vLLM project. "OpenAI-Compatible Server." https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
2. BerriAI. LiteLLM releases (v1.108.12 LTS image `docker.litellm.ai/berriai/litellm:v1.108.12-lts`). https://github.com/BerriAI/litellm/releases ; Docker quick start https://docs.litellm.ai/docs/proxy/docker_quick_start
3. Agent Router (formerly Envoy AI Gateway). README and docs, v1.3.0 (2026-11-18). https://github.com/theagentrouter/agent-router ; https://theagentrouter.ai/docs/
4. Kong. "AI Gateway" documentation (AI Semantic Cache, AI Rate Limiting Advanced, AI Prompt Guard, AI Semantic Prompt Guard, MCP). https://developer.konghq.com/ai-gateway/
5. Kubernetes SIG Network. Gateway API Inference Extension docs (InferencePool v1, GA since v1.0.0; Endpoint Picker); releases (v1.6.2, 2026-09-17). https://gateway-api-inference-extension.sigs.k8s.io/ ; https://gateway-api-inference-extension.sigs.k8s.io/api-types/inferencepool/ ; https://github.com/kubernetes-sigs/gateway-api-inference-extension/releases
6. LiteLLM. "Security Update: Suspected Supply Chain Incident" (24 Mar 2026). https://docs.litellm.ai/blog/security-update-march-2026
7. OpenTelemetry. Semantic conventions v1.42.0 release notes (GenAI conventions moved to a dedicated repository). https://github.com/open-telemetry/semantic-conventions/releases/tag/v1.42.0
8. OpenTelemetry. GenAI semantic conventions (spans, metrics, agent and MCP conventions; status Development). https://github.com/open-telemetry/semantic-conventions-genai
9. Zheng, L. et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023 Datasets & Benchmarks. arXiv:2306.05685. https://arxiv.org/abs/2306.05685
10. LiteLLM. "Router — load balancing, routing strategies, cooldowns." https://docs.litellm.ai/docs/routing
11. Ong, I. et al. "RouteLLM: Learning to Route LLMs with Preference Data." arXiv:2406.18665 (2024). https://arxiv.org/abs/2406.18665
12. Chen, L., Zaharia, M., Zou, J. "FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance." arXiv:2305.05176 (2023). https://arxiv.org/abs/2305.05176
13. LiteLLM. "Proxy — fallbacks, retries, timeouts, cooldowns" (reliability). https://docs.litellm.ai/docs/proxy/reliability
14. LiteLLM. "Users / virtual keys: budgets and rate limits" (tpm_limit, rpm_limit, max_parallel_requests, max_budget). https://docs.litellm.ai/docs/proxy/users
15. nginx. "ngx_http_proxy_module: proxy_buffering, X-Accel-Buffering." https://nginx.org/en/docs/http/ngx_http_proxy_module.html
16. Bang, F. "GPTCache: An Open-Source Semantic Cache for LLM Applications Enabling Faster Answers and Cost Savings." NLP-OSS 2023. https://aclanthology.org/2023.nlposs-1.24/
17. LiteLLM. "Caching" (cache types including redis-semantic, qdrant-semantic, valkey-semantic). https://docs.litellm.ai/docs/proxy/caching

### 27 — ML platforms & data for AI

Lesson: [`course/03-ai-systems/27-ml-platforms.md`](course/03-ai-systems/27-ml-platforms.md) · source status: `DRAFT`

1. D. Sculley et al., "Hidden Technical Debt in Machine Learning Systems," NeurIPS 28, 2015. https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems
2. M. Zinkevich, "Rules of Machine Learning: Best Practices for ML Engineering," Google for Developers. https://developers.google.com/machine-learning/guides/rules-of-ml
3. Feast documentation, "Push vs Pull Model." https://docs.feast.dev/getting-started/architecture/push-vs-pull-model
4. Feast documentation, "Point-in-time joins." https://docs.feast.dev/getting-started/concepts/point-in-time-joins
5. J. Hermann and M. Del Balso, "Meet Michelangelo: Uber's Machine Learning Platform," Uber Engineering, 2017. https://www.uber.com/blog/michelangelo-machine-learning-platform/
6. feast-dev/feast, GitHub releases (v0.68.0, 2026-11-10). https://github.com/feast-dev/feast/releases
7. MLflow documentation, "MLflow Model Registry," and GitHub releases (3.18.0). https://mlflow.org/docs/latest/ml/model-registry/ ; https://github.com/mlflow/mlflow/releases
8. Feast documentation, "Feature view." https://docs.feast.dev/getting-started/concepts/feature-view
9. E. J. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models," arXiv:2106.09685, 2021. https://arxiv.org/abs/2106.09685
10. T. Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs," arXiv:2305.14314, 2023. https://arxiv.org/abs/2305.14314
11. P. Covington, J. Adams, E. Sargin, "Deep Neural Networks for YouTube Recommendations," RecSys 2016. https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/
12. X. Yi et al., "Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations," RecSys 2019. https://research.google/pubs/sampling-bias-corrected-neural-modeling-for-large-corpus-item-recommendations/
13. N. Polyzotis, M. Zinkevich, S. Roy, E. Breck, S. Whang, "Data Validation for Machine Learning," MLSys 2019. https://proceedings.mlsys.org/paper_files/paper/2019/hash/928f1160e52192e3e0017fb63ab65391-Abstract.html
14. Llama Team, AI @ Meta (A. Grattafiori et al.), "The Llama 3 Herd of Models," arXiv:2407.21783, 2024, §3.3.4. https://arxiv.org/abs/2407.21783
15. J. Lu et al., "Learning under Concept Drift: A Review," IEEE TKDE 31(12), 2018; arXiv:2004.05785. https://arxiv.org/abs/2004.05785
16. S. Rabanser, S. Günnemann, Z. C. Lipton, "Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift," NeurIPS 2019; arXiv:1810.11953. https://arxiv.org/abs/1810.11953
17. Linux Foundation / PyTorch Foundation, "PyTorch Foundation Welcomes Ray to Deliver a Unified Open Source AI Compute Stack," 2025-10-22. https://pytorch.org/blog/pytorch-foundation-welcomes-ray-to-deliver-a-unified-open-source-ai-compute-stack/
18. Kubeflow, "Kubeflow AI reference platform 26.03" and "Kubeflow Trainer v2.2" release blog. https://www.kubeflow.org/docs/kubeflow-platform/releases/kubeflow-26.03 ; https://blog.kubeflow.org/kubeflow-trainer-v2.2-release/
19. CNCF, "KServe becomes a CNCF incubating project," 2025-11-11. https://www.cncf.io/blog/2025/11/11/kserve-becomes-a-cncf-incubating-project/
20. Bitol, "Open Data Contract Standard (ODCS)." https://bitol-io.github.io/open-data-contract-standard/latest/
21. S. Rajbhandari, J. Rasley, O. Ruwase, Y. He, "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models," arXiv:1910.02054, 2019. https://arxiv.org/abs/1910.02054
22. J. W. Young, "A first order approximation to the optimum checkpoint interval," Communications of the ACM 17(9):530–531, 1974. https://doi.org/10.1145/361147.361115
23. PyTorch documentation, "Distributed Checkpoint – torch.distributed.checkpoint" (2.15). https://docs.pytorch.org/docs/stable/distributed.checkpoint.html
24. Ray documentation, "Overview." https://docs.ray.io/en/latest/ray-overview/index.html
25. Y. Zhao et al., "PyTorch FSDP: Experiences on Scaling Fully Sharded Data Parallel," arXiv:2304.11277, 2023. https://arxiv.org/abs/2304.11277
26. M. Shoeybi et al., "Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism," arXiv:1909.08053, 2019. https://arxiv.org/abs/1909.08053
27. Y. Huang et al., "GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism," arXiv:1811.06965, 2018. https://arxiv.org/abs/1811.06965
28. Z. Liu et al., "Monolith: Real Time Recommendation System With Collisionless Embedding Table," ORSUM@ACM RecSys 2022; arXiv:2209.07663. https://arxiv.org/abs/2209.07663

### 28 — Trust, safety & governance for AI systems

Lesson: [`course/03-ai-systems/28-ai-trust-safety-governance.md`](course/03-ai-systems/28-ai-trust-safety-governance.md) · source status: `DRAFT`

1. OWASP GenAI Security Project, "Top 10 for LLM Applications 2025." https://genai.owasp.org/llm-top-10/
2. OWASP GenAI Security Project, "OWASP Top 10 for Agentic Applications for 2026," 2025-12-09. https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
3. S. Willison, "The lethal trifecta for AI agents: private data, untrusted content, and external communication," 2025-06-16. https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/ *(blog; perspective)*
4. Regulation (EU) 2024/1689 (Artificial Intelligence Act), OJ L, 12.7.2024. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
5. Regulation (EU) 2026/1744 of 8 July 2026 (Digital Omnibus on AI), OJ L, 24.7.2026. https://eur-lex.europa.eu/eli/reg/2026/1744/oj
6. E. Debenedetti et al., "Defeating Prompt Injections by Design," arXiv:2503.18813, 2025 (preprint). https://arxiv.org/abs/2503.18813
7. L. Beurer-Kellner et al., "Design Patterns for Securing LLM Agents against Prompt Injections," arXiv:2506.08837, 2025 (preprint). https://arxiv.org/abs/2506.08837
8. K. Greshake et al., "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," arXiv:2302.12173, 2023. https://arxiv.org/abs/2302.12173
9. A. Wei, N. Haghtalab, J. Steinhardt, "Jailbroken: How Does LLM Safety Training Fail?," arXiv:2307.02483,
2023. https://arxiv.org/abs/2307.02483
10. A. Zou et al., "Universal and Transferable Adversarial Attacks on Aligned Language Models," arXiv:2307.15043, 2023. https://arxiv.org/abs/2307.15043
11. H. Inan et al., "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations," arXiv:2312.06674, 2023. https://arxiv.org/abs/2312.06674
12. T. Rebedea et al., "NeMo Guardrails: A Toolkit for Controllable and Safe LLM Applications with Programmable Rails," arXiv:2310.10501, 2023. https://arxiv.org/abs/2310.10501
13. Presidio documentation (Data Privacy Stack). https://presidio.dataprivacystack.org/
14. C2PA, "C2PA Technical Specification" v2.2, §§1.2, 1.3, 2.4.2, 9.1. https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html
15. C2PA Specifications site (current version listing 2.5). https://spec.c2pa.org/specifications/
16. Hugging Face Hub documentation, "Pickle Scanning." https://huggingface.co/docs/hub/security-pickle
17. OpenSSF, "Launch of Model Signing v1.0: OpenSSF AI/ML Working Group Secures the Machine Learning Supply Chain," 2025-04-04. https://openssf.org/blog/2025/04/04/launch-of-model-signing-v1-0-openssf-ai-ml-working-group-secures-the-machine-learning-supply-chain/
18. sigstore/model-transparency (model_signing library and CLI). https://github.com/sigstore/model-transparency
19. M. Mitchell et al., "Model Cards for Model Reporting," FAT* 2019; arXiv:1810.03993. https://arxiv.org/abs/1810.03993
20. T. Gebru et al., "Datasheets for Datasets," arXiv:1803.09010, 2018 (rev. 2021). https://arxiv.org/abs/1803.09010
21. NIST, "AI Risk Management Framework" (AI RMF 1.0, NIST AI 100-1, 2023-01-26). https://www.nist.gov/itl/ai-risk-management-framework
22. NIST, "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile," NIST AI 600-1, 2024-07-26. https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf

## Part IV — Case studies

### C01 — URL shortener + distributed rate limiter

Lesson: [`course/04-case-studies/C01-url-shortener-rate-limiter.md`](course/04-case-studies/C01-url-shortener-rate-limiter.md) · source status: `DRAFT`

1. R. Fielding, M. Nottingham, J. Reschke (eds.), "HTTP Semantics," RFC 9110, June 2022 — §15.4.2 (301), §15.4.3 (302), §15.4.8 (307), §15.4.9 (308), §10.2.3 (Retry-After). https://www.rfc-editor.org/rfc/rfc9110
2. P. Tarjan, "Scaling your API with rate limiters," Stripe blog, 2017-03-30. https://stripe.com/blog/rate-limiters
3. Envoy project, "Global rate limiting" (architecture overview; local token bucket + global service). https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/other_features/global_rate_limiting
4. Cloudflare, "How we built rate limiting capable of scaling to millions of domains," 2017-06-07. https://blog.cloudflare.com/counting-things-a-lot-of-different-things/
5. IETF httpapi WG, "RateLimit header fields for HTTP," draft-ietf-httpapi-ratelimit-headers-11, 2026-05-23 (Internet-Draft). https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/
6. M. Nottingham, R. Fielding, "Additional HTTP Status Codes," RFC 6585, April 2012 (status 429). https://www.rfc-editor.org/rfc/rfc6585
7. IETF httpapi WG, "The Idempotency-Key HTTP Header Field," draft-ietf-httpapi-idempotency-key-header-08, 2026-10-22 (Internet-Draft). https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
8. Twitter, "Snowflake" README (2010 release; 41-bit time, 10-bit machine, 12-bit sequence). https://github.com/twitter-archive/snowflake/tree/snowflake-2010
9. Redis documentation, "INCR — Pattern: rate limiter" (race between INCR and EXPIRE; Lua fix). https://redis.io/docs/latest/commands/incr/
10. Google, "Safe Browsing" (v4 and v5 APIs; non-commercial use only; commercial use via Web Risk). https://developers.google.com/safe-browsing
11. M. Elhemali et al., "Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service," USENIX ATC 2022 — §4 global admission control with token buckets. https://www.usenix.org/conference/atc22/presentation/elhemali
12. Google Cloud, "Web Risk overview" (Lookup API vs Update API with local hashed lists). https://docs.cloud.google.com/web-risk/docs/overview
13. Cloudflare, "Rate limiting rules" (counting characteristics incl. JA3/JA4; per-data-center counter scope). https://developers.cloudflare.com/waf/rate-limiting-rules/

### C02 — News feed / timeline

Lesson: [`course/04-case-studies/C02-news-feed.md`](course/04-case-studies/C02-news-feed.md) · source status: `DRAFT`

1. A. Silberstein, J. Terrace, B. F. Cooper, R. Ramakrishnan, "Feeding Frenzy: Selectively Materializing Users' Event Feeds," SIGMOD 2010. https://sns.cs.princeton.edu/assets/papers/2010-sigmod-silberstein.pdf (DOI 10.1145/1807167.1807257)
2. P. Covington, J. Adams, E. Sargin, "Deep Neural Networks for YouTube Recommendations," RecSys 2016 (two-stage candidate generation + ranking). https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/
3. N. Bronson et al., "TAO: Facebook's Distributed Data Store for the Social Graph," USENIX ATC 2013. https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson
4. A. Lada, M. Wang, T. Yan, "How machine learning powers Facebook's News Feed ranking algorithm," Engineering at Meta, 2021-01-26. https://engineering.fb.com/2021/01/26/core-infra/news-feed-ranking/
5. X Corp., `twitter/the-algorithm`, Home Mixer README (stages; "~6000 features"). https://github.com/twitter/the-algorithm/blob/main/home-mixer/README.md
6. xAI / X Corp., `xai-org/x-algorithm` README, "X For You Feed Algorithm" (Thunder, Phoenix retrieval and ranking, candidate isolation, hash-based embeddings; notable updates through 2026-10-26). https://github.com/xai-org/x-algorithm
7. Regulation (EU) 2022/2065 (Digital Services Act), Art. 38 "Recommender systems"; obligation also restated in the Commission's answer to parliamentary question E-003424/2023. https://eur-lex.europa.eu/eli/reg/2022/2065/oj and https://www.europarl.europa.eu/doceo/document/E-9-2023-003424-ASW_EN.html

### C03 — Chat & presence

Lesson: [`course/04-case-studies/C03-chat-presence.md`](course/04-case-studies/C03-chat-presence.md) · source status: `DRAFT`

1. S. Vishnevskiy, "How Discord Stores Billions of Messages," Discord blog, 2017-01-13. https://discord.com/blog/how-discord-stores-billions-of-messages
2. B. Ingram, "How Discord Stores Trillions of Messages," Discord blog, 2023-03-06. https://discord.com/blog/how-discord-stores-trillions-of-messages
3. S. Vishnevskiy, "How Discord Scaled Elixir to 5,000,000 Concurrent Users," Discord blog, 2017-07-06. https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users
4. S. Thangudu, "Real-time Messaging," Slack Engineering, 2023-04-11. https://slack.engineering/real-time-messaging/
5. R. Barnes et al., "The Messaging Layer Security (MLS) Protocol," RFC 9420, July 2023. https://www.rfc-editor.org/rfc/rfc9420
6. B. Beurdouche et al., "The Messaging Layer Security (MLS) Architecture," RFC 9750, April 2025 — §5.2 ordering and Delivery Service consistency. https://www.rfc-editor.org/rfc/rfc9750
7. I. Fette, A. Melnikov, "The WebSocket Protocol," RFC 6455, December 2011. https://www.rfc-editor.org/rfc/rfc6455
8. Meta, "Building Private Processing for AI tools on WhatsApp," Engineering at Meta, 2025-04-29. https://engineering.fb.com/2025/04/29/security/whatsapp-private-processing-ai-tools/
9. T. Van Pelt, "RCS Encryption: A Leap Towards Secure and Interoperable Messaging," GSMA Newsroom, 2025-03-14. https://www.gsma.com/newsroom/article/rcs-encryption-a-leap-towards-secure-and-interoperable-messaging/
10. Signal, "Specifications" (XEdDSA, X3DH, PQXDH, Double Ratchet, Sesame, ML-KEM Braid). https://signal.org/docs/
11. M. Thomson, C. A. Wood, "Oblivious HTTP," RFC 9458, January 2024. https://www.rfc-editor.org/rfc/rfc9458

### C04 — Video upload, transcoding & streaming

Lesson: [`course/04-case-studies/C04-video-streaming.md`](course/04-case-studies/C04-video-streaming.md) · source status: `DRAFT`

1. Netflix Technology Blog, "Per-Title Encode Optimization," 2015-12-14. https://netflixtechblog.com/per-title-encode-optimization-7e99442b62a2
2. I. Katsavounidis, "Dynamic optimizer — a perceptual video encoding optimization framework," Netflix Technology Blog, 2018-03-05. https://netflixtechblog.com/dynamic-optimizer-a-perceptual-video-encoding-optimization-framework-e19f1e3a277f
3. Netflix, "Open Connect" (embedded appliances in ISP networks, IXP interconnection; 1,000+ ISP partners). https://openconnect.netflix.com/en/
4. Netflix, VMAF — Video Multi-Method Assessment Fusion (open-source repository). https://github.com/Netflix/vmaf
5. R. Pantos, W. May, "HTTP Live Streaming," RFC 8216, August 2017 (Informational). https://www.rfc-editor.org/rfc/rfc8216
6. A. Radford et al., "Robust Speech Recognition via Large-Scale Weak Supervision," arXiv:2212.04356, 2022 (preprint). https://arxiv.org/abs/2212.04356
7. Amazon Web Services, "Uploading and copying objects using multipart upload in Amazon S3" (part numbers 1–10,000; ≥ 100 MB recommendation; lifecycle abort; checksums; conditional writes). https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html
8. tus.io, "Resumable upload protocol 1.0.0" (2016-03-25). https://tus.io/protocols/resumable-upload
9. IETF httpbis WG, "Resumable Uploads for HTTP," draft-ietf-httpbis-resumable-upload-15, 2026-11-02 (Internet-Draft). https://datatracker.ietf.org/doc/draft-ietf-httpbis-resumable-upload/
10. P. Ranganathan et al., "Warehouse-Scale Video Acceleration: Co-design and Deployment in the Wild," ASPLOS 2021. https://research.google/pubs/warehouse-scale-video-acceleration-co-design-and-deployment-in-the-wild/
11. Meta, "MSVP: Meta's first ASIC for video transcoding," 2023-05-18. https://ai.meta.com/blog/meta-scalable-video-processor-MSVP/
12. Netflix Technology Blog, "AV1 — Now Powering 30% of Netflix Streaming," 2025-12-01 (snapshot 2025-11-13). https://netflixtechblog.com/av1-now-powering-30-of-netflix-streaming-02f592242d80
13. Netflix Technology Blog, "Bringing AV1 Streaming to Netflix Members' TVs," 2021-11-09. https://netflixtechblog.com/bringing-av1-streaming-to-netflix-members-tvs-b7fc88e42320
14. Alliance for Open Media, "Alliance for Open Media Releases AV2 Codec," press release, June 2026. https://aomedia.org/press%20releases/Alliance-for-Open-Media-Releases-AV2-Codec/
15. Directive (EU) 2019/882 (European Accessibility Act) — measures apply from 28 June 2025. https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0882
16. European Commission, "European Accessibility Act" (products and services covered, incl. access to audiovisual media services). https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/union-equality-strategy-rights-persons-disabilities-2021-2030/european-accessibility-act_en

### C05 — Ride-hailing & proximity search

Lesson: [`course/04-case-studies/C05-ride-hailing-proximity.md`](course/04-case-studies/C05-ride-hailing-proximity.md) · source status: `DRAFT`

1. I. Brodsky, "H3: Uber's Hexagonal Hierarchical Spatial Index," Uber Engineering blog, 2018-06-27. https://www.uber.com/blog/h3/
2. H3 project, "Tables of Cell Statistics Across Resolutions." https://h3geo.org/docs/core-library/restable/
3. H3 project, "Overview of the H3 Geospatial Indexing System" (122 base cells; 12 pentagons per resolution; version 4.x) and "Indexing" (aperture 7; exact logical containment). https://h3geo.org/docs/core-library/overview and https://h3geo.org/docs/highlights/indexing/
4. S2 Geometry, "S2 Cells" developer guide (cube faces, Hilbert curve, levels 0–30, 64-bit cell IDs). http://s2geometry.io/devguide/s2cell_hierarchy
5. Uber Engineering, "DeepETA: How Uber Predicts Arrival Times Using Deep Learning," 2022-02-10. https://www.uber.com/blog/deepeta-how-uber-predicts-arrival-times/
6. Redis documentation, "GEOSEARCH" (since 6.2.0; O(N + log M); 52-bit geohash scores). https://redis.io/docs/latest/commands/geosearch/
7. H3 project, "Grid traversal functions" (`gridDisk`, `gridRing`, pentagon behavior). https://h3geo.org/docs/api/traversal
8. Uber, H3 source repository. https://github.com/uber/h3

### C06 — Payments & ledger

Lesson: [`course/04-case-studies/C06-payments-ledger.md`](course/04-case-studies/C06-payments-ledger.md) · source status: `DRAFT`

1. Stripe, "Idempotent requests," API reference. https://docs.stripe.com/api/idempotent_requests
2. B. Leach, "Designing robust and predictable APIs with idempotency," Stripe blog, 2017-02-22. https://stripe.com/blog/idempotency
3. J. Chew, "Avoiding Double Payments in a Distributed Payments System," The Airbnb Tech Blog, 2019-04-16. https://medium.com/airbnb-engineering/avoiding-double-payments-in-a-distributed-payments-system-2981f6b070bb
4. Ł. Strzałkowski, "Books, an immutable double-entry accounting database service," Square Developer blog, 2019-10-16. https://developer.squareup.com/blog/books-an-immutable-double-entry-accounting-database-service/
5. TigerBeetle, "Debit / Credit" concepts documentation. https://docs.tigerbeetle.com/concepts/debit-credit/
6. K. Devarajaiah, "How LedgerStore Supports Trillions of Indexes at Uber," Uber Engineering blog, 2024-04-04. https://www.uber.com/us/en/blog/how-ledgerstore-supports-trillions-of-indexes/
7. Regulation (EU) 2024/886 of 13 March 2024 on instant credit transfers in euro (Arts. 5a–5d). https://eur-lex.europa.eu/eli/reg/2024/886/oj/eng
8. Board of Governors of the Federal Reserve System, "FedNow Service" (went live July 20, 2023; 24x7x365). https://www.federalreserve.gov/paymentsystems/fednow_about.htm
9. Council of the EU, "Payment services: Council and Parliament agree to step up the fight against fraud and increase transparency," press release, 2025-11-27 (verified via search index; page blocked automated fetch). https://www.consilium.europa.eu/en/press/press-releases/2025/11/27/payment-services-council-and-parliament-agree-to-step-up-the-fight-against-fraud-and-increase-transparency/
10. IETF httpapi WG, "The Idempotency-Key HTTP Header Field," draft-ietf-httpapi-idempotency-key-header-08, 2026-10-22 (Internet-Draft). https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
11. European Parliament, Legislative Train Schedule, "Revision of EU rules on payment services" (status "close to adoption", updated 2026-10-25). https://www.europarl.europa.eu/legislative-train/theme-an-economy-that-works-for-people/file-revision-of-eu-rules-on-payment-services
12. PCI Security Standards Council, Document Library (PCI DSS v4.0.1). https://www.pcisecuritystandards.org/document_library/

### C07 — Distributed key-value store (Dynamo-style)

Lesson: [`course/04-case-studies/C07-distributed-kv-store.md`](course/04-case-studies/C07-distributed-kv-store.md) · source status: `DRAFT`

1. G. DeCandia et al., "Dynamo: Amazon's Highly Available Key-value Store," SOSP 2007. https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
2. M. Elhemali et al., "Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service," USENIX ATC 2022. https://www.usenix.org/conference/atc22/presentation/elhemali (PDF: https://www.usenix.org/system/files/atc22-elhemali.pdf)
3. Apache Cassandra documentation, "Dynamo" architecture page (5.0 docs: vnodes, NetworkTopologyStrategy, consistency levels, hints, read repair, Merkle-tree repair, gossip, phi accrual, LWW). https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html
4. Apache Cassandra documentation, "Storage engine" (commit log sync modes, memtables, SSTables, Bloom filters, compaction). https://cassandra.apache.org/doc/latest/cassandra/architecture/storage-engine.html
5. Apache Cassandra documentation, "Tombstones" (gc_grace_seconds default 864,000 s; zombie data). https://cassandra.apache.org/doc/latest/cassandra/managing/operating/compaction/tombstones.html
6. D. Ongaro, J. Ousterhout, "In Search of an Understandable Consensus Algorithm (Extended Version)" (Raft), USENIX ATC 2014. https://raft.github.io/
7. TiKV documentation, "Architecture overview" (Regions as Raft groups, Placement Driver, RocksDB). https://tikv.org/docs/latest/reference/architecture/overview/
8. Cockroach Labs, "Replication Layer" (Raft per range, leaseholders, leader leases). https://docs.cockroachlabs.com/docs/stable/architecture/replication-layer
9. ScyllaDB documentation, "Data Distribution with Tablets" (tablets by default; load balancing; Raft-based consistent topology). https://docs.scylladb.com/manual/stable/architecture/tablets.html
10. Apache Cassandra, "CEP-21: Transactional Cluster Metadata" (state: Accepted). https://cwiki.apache.org/confluence/display/CASSANDRA/CEP-21%3A+Transactional+Cluster+Metadata
11. Apache Cassandra, Downloads (latest GA 5.0.9, 2026-08-07). https://cassandra.apache.org/_/download.html
12. J. Zhou et al., "FoundationDB: A Distributed Unbundled Transactional Key Value Store," SIGMOD 2021. https://www.foundationdb.org/files/fdb-paper.pdf
13. SlateDB project home page. https://slatedb.io/ (source: https://github.com/slatedb/slatedb)
14. turbopuffer, "Architecture" documentation (vendor-reported latencies). https://turbopuffer.com/docs/architecture
15. R. Artoul, "Kafka is dead, long live Kafka," WarpStream blog, 2023-07-25 (vendor-reported latencies). https://www.warpstream.com/blog/kafka-is-dead-long-live-kafka
16. Amazon Web Services, "Amazon S3 now supports conditional writes," 2024-08-20. https://aws.amazon.com/about-aws/whats-new/2024/08/amazon-s3-conditional-writes/
17. Amazon Web Services, "Amazon S3 Express One Zone" (single-digit-millisecond latency; up to 10× faster than S3 Standard). https://aws.amazon.com/s3/storage-classes/express-one-zone/

### C08 — Web crawler & search engine

Lesson: [`course/04-case-studies/C08-web-crawler-search.md`](course/04-case-studies/C08-web-crawler-search.md) · source status: `DRAFT`

1. Common Crawl, "June 2026 Crawl Archive Now Available" (2.10 B pages, 354.59 TiB uncompressed). https://commoncrawl.org/blog/june-2026-crawl-archive-now-available
2. M. Koster, G. Illyes, H. Zeller, L. Sassman, "Robots Exclusion Protocol," RFC 9309, September 2022. https://www.rfc-editor.org/rfc/rfc9309.html
3. A. Heydon, M. Najork, "Mercator: A scalable, extensible Web crawler," *World Wide Web* 2(4), 1999. https://doi.org/10.1023/A:1019213109274
4. M. S. Charikar, "Similarity estimation techniques from rounding algorithms," STOC 2002. https://doi.org/10.1145/509907.509965
5. G. S. Manku, A. Jain, A. Das Sarma, "Detecting near-duplicates for web crawling," WWW 2007. https://doi.org/10.1145/1242572.1242592
6. C. D. Manning, P. Raghavan, H. Schütze, *Introduction to Information Retrieval*, Cambridge University Press, 2008, ch. 4 "Index construction." https://nlp.stanford.edu/IR-book/
7. S. Robertson, H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in IR* 3(4), 2009. https://doi.org/10.1561/1500000019
8. S. Brin, L. Page, "The anatomy of a large-scale hypertextual Web search engine," *Computer Networks and ISDN Systems* 30, 1998. https://doi.org/10.1016/S0169-7552(98)00110-X
9. J. Cho, H. Garcia-Molina, "Estimating frequency of change," *ACM Transactions on Internet Technology* 3(3), 2003. https://doi.org/10.1145/857166.857170
10. OpenAI, "Overview of OpenAI Crawlers." https://developers.openai.com/api/docs/bots
11. Google Search Central, "Google's common crawlers" (Google-Extended). https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers
12. Anthropic, "Does Anthropic crawl data from the web, and how can site owners block the crawler?" https://support.claude.com/en/articles/8896518-does-anthropic-crawl-the-web
13. Common Crawl, "CCBot." https://commoncrawl.org/ccbot
14. IETF, AI Preferences (aipref) working group: charter and documents (draft-ietf-aipref-vocab, draft-ietf-aipref-attach). https://datatracker.ietf.org/wg/aipref/about/
15. G. V. Cormack, C. L. A. Clarke, S. Büttcher, "Reciprocal rank fusion outperforms Condorcet and individual rank learning methods," SIGIR 2009. https://doi.org/10.1145/1571941.1572114
16. J. Cho, H. Garcia-Molina, "Synchronizing a database to improve freshness," SIGMOD 2000. https://doi.org/10.1145/342009.335391

### C09 — ChatGPT-style LLM chat service

Lesson: [`course/04-case-studies/C09-llm-chat-service.md`](course/04-case-studies/C09-llm-chat-service.md) · source status: `DRAFT`

1. W. Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention," SOSP 2023. https://arxiv.org/abs/2309.06180
2. G.-I. Yu, J. S. Jeong et al., "Orca: A Distributed Serving System for Transformer-Based Generative Models," OSDI 2022. https://www.usenix.org/conference/osdi22/presentation/yu
3. vLLM project, "Automatic Prefix Caching" (design doc: block hashing, LRU eviction, cache salt). https://docs.vllm.ai/en/latest/design/prefix_caching.html
4. vLLM project, "Optimization and Tuning" (chunked prefill default in V1, `max_num_batched_tokens`, preemption by recompute). https://docs.vllm.ai/en/latest/configuration/optimization.html
5. WHATWG, HTML Living Standard, §9.2 "Server-sent events." https://html.spec.whatwg.org/multipage/server-sent-events.html
6. NGINX, "Module ngx_http_proxy_module" (`proxy_buffering`, `X-Accel-Buffering`, `proxy_read_timeout`). https://nginx.org/en/docs/http/ngx_http_proxy_module.html
7. vLLM team, "vLLM V1: A Major Upgrade to vLLM's Core Architecture," 2025-01-27 (prefix caching on by default, < 1 % overhead at 0 % hit rate). https://vllm.ai/blog/2025-01-27-v1-alpha-release
8. vLLM project, "Automatic Prefix Caching" (feature guide: target workloads; prefill-only benefit). https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html
9. Kubernetes SIG Network, Gateway API Inference Extension (InferencePool, endpoint picker). https://gateway-api-inference-extension.sigs.k8s.io/
10. llm-d project, "Intelligent inference scheduling with llm-d" (blog, vendor-reported results). https://llm-d.ai/blog/intelligent-inference-scheduling-with-llm-d
11. Y. Zhong et al., "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving," OSDI 2024. https://arxiv.org/abs/2401.09670
12. Meta, Llama 3.3 70B Instruct model configuration (80 layers, 8 KV heads, head dim 128), via a public mirror of `config.json`. https://huggingface.co/unsloth/Llama-3.3-70B-Instruct/blob/main/config.json
13. NVIDIA, "H100 Tensor Core GPU" data sheet (80 GB, 3.35 TB/s, FP8 3,958 TFLOPS with sparsity, up to 700 W, SXM). https://www.nvidia.com/en-us/data-center/h100/
14. P. Patel et al., "Splitwise: Efficient Generative LLM Inference Using Phase Splitting," ISCA 2024; preprint arXiv:2311.18677. https://arxiv.org/abs/2311.18677
15. vLLM project, "Disaggregated Prefilling (experimental)" (KV connectors). https://docs.vllm.ai/en/latest/features/disagg_prefill.html
16. H. Inan et al., "Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations," arXiv:2312.06674 (preprint), 2023. https://arxiv.org/abs/2312.06674
17. vLLM project, "Metrics" design doc (metric names). https://docs.vllm.ai/en/latest/design/metrics.html
18. vLLM project, "Sleep Mode." https://docs.vllm.ai/en/latest/features/sleep_mode.html
19. Regulation (EU) 2016/679 (GDPR), Chapter V, transfers of personal data to third countries. https://eur-lex.europa.eu/eli/reg/2016/679/oj
20. vLLM releases on PyPI (v0.33.0 uploaded 2026-11-02, v0.34.0 uploaded 2026-11-16). https://pypi.org/project/vllm/#history
21. Regulation (EU) 2024/1689 (AI Act), Art. 113 application dates. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
22. Council of the EU adoption of the Digital Omnibus on AI (June 2026), as summarised by Gibson Dunn, "EU AI Act Omnibus Agreement — Postponed High-Risk Deadlines and Other Key Changes" (secondary source; check the Official Journal text). https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/
23. L. Zheng et al., "SGLang: Efficient Execution of Structured Language Model Programs," arXiv:2312.07104 (preprint). https://arxiv.org/abs/2312.07104

### C10 — Enterprise RAG assistant

Lesson: [`course/04-case-studies/C10-enterprise-rag-assistant.md`](course/04-case-studies/C10-enterprise-rag-assistant.md) · source status: `DRAFT`

1. Qdrant, "Indexing" documentation (filterable HNSW, payload index cardinality, tenant index). https://qdrant.tech/documentation/concepts/indexing/
2. pgvector README (filtering with approximate indexes, `hnsw.ef_search` default 40, iterative index scans since 0.8.0; v0.8.7 current). https://github.com/pgvector/pgvector
3. G. V. Cormack, C. L. A. Clarke, S. Büttcher, "Reciprocal rank fusion outperforms Condorcet and individual rank learning methods," SIGIR 2009. https://doi.org/10.1145/1571941.1572114
4. S. Es, J. James, L. Espinosa-Anke, S. Schockaert, "Ragas: Automated Evaluation of Retrieval Augmented Generation," arXiv:2309.15217 (preprint). https://arxiv.org/abs/2309.15217
5. K. Greshake et al., "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection," arXiv:2302.12173 (preprint), 2023. https://arxiv.org/abs/2302.12173
6. OWASP GenAI Security Project, "LLM01:2025 Prompt Injection." https://genai.owasp.org/llmrisk/llm01-prompt-injection/
7. Model Context Protocol, Specification (version 2026-07-28), "Security and Trust & Safety." https://modelcontextprotocol.io/specification/latest
8. J. X. Morris, V. Kuleshov, V. Shmatikov, A. M. Rush, "Text Embeddings Reveal (Almost) As Much As Text," EMNLP 2023; arXiv:2310.06816. https://arxiv.org/abs/2310.06816
9. Regulation (EU) 2016/679 (GDPR), Chapter V. https://eur-lex.europa.eu/eli/reg/2016/679/oj
10. Regulation (EU) 2024/1689 (AI Act), Art. 50 and Art. 113. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
11. Gibson Dunn, "EU AI Act Omnibus Agreement — Postponed High-Risk Deadlines and Other Key Changes" (secondary; check the Official Journal text). https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/

### C11 — AI coding-agent platform

Lesson: [`course/04-case-studies/C11-coding-agent-platform.md`](course/04-case-studies/C11-coding-agent-platform.md) · source status: `DRAFT`

1. gVisor documentation, "What is gVisor?" (Sentry, runsc, performance and compatibility trade-offs). https://gvisor.dev/docs/
2. A. Agache et al., "Firecracker: Lightweight Virtualization for Serverless Applications," NSDI 2020. https://www.usenix.org/conference/nsdi20/presentation/agache
3. Firecracker project, "Snapshot support" documentation. https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md
4. Git documentation, "Partial Clone." https://git-scm.com/docs/partial-clone
5. Git documentation, "git-sparse-checkout." https://git-scm.com/docs/git-sparse-checkout
6. Model Context Protocol, Specification version 2026-07-28 (overview, security and trust & safety, extensions). https://modelcontextprotocol.io/specification/latest
7. Model Context Protocol, Specification 2026-07-28, "Authorization." https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
8. OWASP GenAI Security Project, "LLM01:2025 Prompt Injection." https://genai.owasp.org/llmrisk/llm01-prompt-injection/
9. Temporal documentation, "Event History" and "Workflow Execution." https://docs.temporal.io/encyclopedia/event-history
10. OpenTelemetry, Generative AI semantic conventions repository (status: Development). https://github.com/open-telemetry/semantic-conventions-genai
11. C. E. Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?," ICLR 2024; arXiv:2310.06770. https://arxiv.org/abs/2310.06770
12. SWE-bench, "SWE-bench Verified" (500 human-validated instances, with OpenAI, August 2024). https://swebench.com/verified

### C12 — Real-time fraud detection (and recommendations)

Lesson: [`course/04-case-studies/C12-realtime-fraud-recsys.md`](course/04-case-studies/C12-realtime-fraud-recsys.md) · source status: `DRAFT`

1. M. Zinkevich, "Rules of Machine Learning: Best Practices for ML Engineering," Google for Developers (Rule #29). https://developers.google.com/machine-learning/guides/rules-of-ml
2. A. Dal Pozzolo, G. Boracchi, O. Caelen, C. Alippi, G. Bontempi, "Credit Card Fraud Detection: A Realistic Modeling and a Novel Learning Strategy," IEEE Transactions on Neural Networks and Learning Systems 29(8): 3784–3797, 2018. https://doi.org/10.1109/TNNLS.2017.2736643 (open-access copy: https://re.public.polimi.it/bitstream/11311/1044896/1/08038008.pdf)
3. Apache Flink documentation (v2.3), "Windows." https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/
4. Stripe documentation, "Radar rules." https://docs.stripe.com/radar/rules
5. P. Covington, J. Adams, E. Sargin, "Deep Neural Networks for YouTube Recommendations," RecSys 2016. https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/
6. X. Yi et al., "Sampling-Bias-Corrected Neural Modeling for Large Corpus Item Recommendations," RecSys 2019. https://research.google/pubs/sampling-bias-corrected-neural-modeling-for-large-corpus-item-recommendations/
7. D. Sculley et al., "Hidden Technical Debt in Machine Learning Systems," NeurIPS 2015. https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems
8. S. Lundberg, S.-I. Lee, "A Unified Approach to Interpreting Model Predictions," NIPS 2017; arXiv:1705.07874. https://arxiv.org/abs/1705.07874
9. Regulation (EU) 2016/679 (GDPR), Article 22. https://eur-lex.europa.eu/eli/reg/2016/679/oj
10. Regulation (EU) 2024/1689 (AI Act), Annex III, point 5(b). https://eur-lex.europa.eu/eli/reg/2024/1689/oj
11. Feast documentation, "Point-in-time joins" and "Feature view." https://docs.feast.dev/getting-started/concepts/point-in-time-joins ; https://docs.feast.dev/getting-started/concepts/feature-view
12. feast-dev/feast, GitHub releases. https://github.com/feast-dev/feast/releases

### C13 — Telemetry & observability platform for a GPU/HPC cluster

Lesson: [`course/04-case-studies/C13-gpu-cluster-telemetry.md`](course/04-case-studies/C13-gpu-cluster-telemetry.md) · source status: `DRAFT`

1. T. Pelkonen et al., "Gorilla: A Fast, Scalable, In-Memory Time Series Database," PVLDB 8(12), 2015. https://www.vldb.org/pvldb/vol8/p1816-teller.pdf
2. Prometheus documentation (3.16), "Storage." https://prometheus.io/docs/prometheus/latest/storage/
3. NVIDIA, "DCGM Exporter" (GPU telemetry documentation: `-c` collection interval default 30000 ms; `-k` Kubernetes pod mapping). https://docs.nvidia.com/datacenter/cloud-native/gpu-telemetry/latest/dcgm-exporter.html
4. A. Borghesi, C. Di Santi, M. Molan, M. Seyedkazemi Ardebili, A. Mauri, M. Guarrasi, et al., "M100 ExaData: a data collection campaign on the CINECA's Marconi100 Tier-0 supercomputer," Scientific Data, 2023. https://doi.org/10.1038/s41597-023-02174-3 (full text via Europe PMC PMC10193329; accessed 2026-11)
5. A. Agelastos et al., "The Lightweight Distributed Metric Service: A Scalable Infrastructure for Continuous Monitoring of Large Scale Computing Systems and Applications," SC14, 2014. https://doi.org/10.1109/SC.2014.18 (metadata accessed 2026-11)
6. A. Bartolini, F. Beneventi, A. Borghesi, D. Cesarini, A. Libri, L. Benini, et al., "Paving the Way Toward Energy-Aware and Automated Datacentre," ICPP Workshops 2019. https://doi.org/10.1145/3339186.3339215 (abstract accessed 2026-11)
7. EEESlab, "examon" (GitHub repository). https://github.com/EEESlab/examon
8. NVIDIA, dcgm-exporter `etc/default-counters.csv` (main branch). https://github.com/NVIDIA/dcgm-exporter/blob/main/etc/default-counters.csv
9. Thanos documentation, "Compactor" (downsampling and retention). https://thanos.io/tip/components/compact.md/
10. Grafana Labs, "Grafana Mimir documentation." https://grafana.com/docs/mimir/latest/
11. VictoriaMetrics documentation, "Single-node VictoriaMetrics" (push protocols; Enterprise downsampling). https://docs.victoriametrics.com/victoriametrics/single-server-victoriametrics/
12. ClickHouse documentation, "Manage data with TTL." https://clickhouse.com/docs/guides/developer/ttl
13. Tiger Data (TimescaleDB) documentation, "About continuous aggregates." https://www.tigerdata.com/docs/use-timescale/latest/continuous-aggregates/about-continuous-aggregates
14. Llama Team, AI @ Meta, "The Llama 3 Herd of Models," arXiv:2407.21783, 2024, §3.3 (infrastructure and reliability). https://arxiv.org/abs/2407.21783
15. S. Cui et al., "Story of Two GPUs: Characterizing the Resilience of Hopper H100 and Ampere A100 GPUs," arXiv:2503.11901, 2025 (preprint; related DOI 10.1145/3712285.3759821). https://arxiv.org/abs/2503.11901
16. G. Ostrouchov, D. Maxwell, R. A. Ashraf, C. Engelmann, M. Shankar, J. H. Rogers, "GPU Lifetimes on Titan Supercomputer: Survival Analysis and Reliability," SC20, 2020. https://doi.org/10.1109/SC41405.2020.00045 (abstract accessed 2026-11)
17. D. Tiwari et al., "Understanding GPU errors on large-scale HPC systems and the implications for system design and operation," HPCA 2015. https://doi.org/10.1109/HPCA.2015.7056044 (metadata accessed 2026-11)
18. NVIDIA, "XID Errors: Analyzing Xid Errors with the Xid Catalog." https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html
19. SchedMD, "acct_gather.conf" (Slurm energy plugins). https://slurm.schedmd.com/acct_gather.conf.html

### C14 — Global flash sale

Lesson: [`course/04-case-studies/C14-global-flash-sale.md`](course/04-case-studies/C14-global-flash-sale.md) · source status: `DRAFT`

1. Redis, "DECR" command documentation. https://redis.io/docs/latest/commands/decr/
2. Redis, "Scripting with Lua" (atomic script execution). https://redis.io/docs/latest/develop/programmability/eval-intro/
3. Redis, "Redis replication" (asynchronous by default; `WAIT` does not make Redis CP; acknowledged writes can be lost during failover). https://redis.io/docs/latest/operate/oss_and_stack/management/replication/
4. Cloudflare, "Waiting Room — Queueing methods" (FIFO, Random, Passthrough, Reject). https://developers.cloudflare.com/waiting-room/reference/queueing-methods/
5. Stripe, "Idempotent requests" API reference. https://docs.stripe.com/api/idempotent_requests
6. J. Jena, S. Dalal, D. Tishkin, "The Idempotency-Key HTTP Header Field," draft-ietf-httpapi-idempotency-key-header-08 (Internet-Draft, work in progress), October 2026. https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
7. Agentic Commerce Protocol (OpenAI and Stripe), specification site. https://agenticcommerce.dev/
8. Google Cloud, "Announcing Agent Payments Protocol (AP2)," September 2025; protocol site https://ap2-protocol.org/. https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol

## Part V — Interview track

### I01 — The interview playbook: CLARIFY → QUANTIFY → SKETCH → DEEPEN → STRESS → WRAP

Lesson: [`course/05-interview/I01-interview-playbook.md`](course/05-interview/I01-interview-playbook.md) · source status: `DRAFT`

1. Meta Careers, *Preparing for your Software Engineering Interview at Meta*, published 2016-06-27, updated 2022-10-06. https://www.metacareers.com/blog/preparing-for-your-software-engineering-interview-at-meta/
2. Amazon, *SDE III/Sr. SDE Interview Prep* (redirects from amazon.jobs to atoz.amazon). https://amazon.jobs/content/en/how-we-hire/sde-iii-interview-prep
3. S. Virji, J. Youngman, H. Robertson, S. Thorne, D. Rensin, Z. Egyed, with R. Bondi, "Non-Abstract Large System Design", in *The Site Reliability Workbook*, Google/O'Reilly, 2018, ch. 12. https://sre.google/workbook/non-abstract-design/
4. J. Dean, *Designs, Lessons and Advice from Building Large Distributed Systems*, keynote, LADIS 2009. https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf
5. P. Singaraju, *The System Design Interview Gap: What Prep Doesn't Teach*, HackerNoon, 2026-04-02 (opinion piece; used for perspective). https://hackernoon.com/the-system-design-interview-gap-what-prep-doesnt-teach
6. A. A. Balkan, *My review of the System Design book*, 2021-04-29 (opinion; used for perspective). https://ahmet.im/blog/system-design-book-review/

### I02 — Numbers & cheat sheets: latency, throughput, storage, capacity, cost & GPU numbers

Lesson: [`course/05-interview/I02-numbers-cheat-sheets.md`](course/05-interview/I02-numbers-cheat-sheets.md) · source status: `DRAFT`

1. J. Dean, *Designs, Lessons and Advice from Building Large Distributed Systems*, LADIS 2009 keynote ("Numbers Everyone Should Know" slide). https://www.cs.cornell.edu/projects/ladis2009/talks/dean-keynote-ladis2009.pdf
2. P. Norvig, *Teach Yourself Programming in Ten Years* ("Approximate timing for various operations on a typical PC"; table undated; page © 2001–2014). https://norvig.com/21-days.html
3. C. Scott, *Latency Numbers Every Programmer Should Know* (interactive; extrapolation model in page source). https://colin-scott.github.io/personal_website/research/interactive_latency.html
4. J. D. C. Little, "A Proof for the Queuing Formula: L = λW", *Operations Research* 9(3), 1961. https://doi.org/10.1287/opre.9.3.383
5. Redis, *Redis benchmark* (documentation, `redis-benchmark` examples and pitfalls). https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/
6. J. Kreps, *Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)*, LinkedIn Engineering, 2014-04-27. https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines
7. AWS, *Regions and Availability Zones* ("all within 100 km (60 miles) of each other"; synchronous replication between AZs). https://aws.amazon.com/about-aws/global-infrastructure/regions_az/
8. NVIDIA, *H100 Tensor Core GPU* (H100 SXM 80 GB, 3.35 TB/s; H100 NVL 94 GB, 3.9 TB/s; tensor figures with sparsity). https://www.nvidia.com/en-us/data-center/h100/
9. NVIDIA, *H200 Tensor Core GPU* (141 GB, 4.8 TB/s). https://www.nvidia.com/en-us/data-center/h200/
10. A. Grattafiori et al. (Llama Team, Meta), *The Llama 3 Herd of Models*, arXiv:2407.21783, 2024, Table 3. https://arxiv.org/abs/2407.21783
11. NVIDIA, *L4 Tensor Core GPU* (24 GB, 300 GB/s, 72 W; sparsity footnote). https://www.nvidia.com/en-us/data-center/l4/ 11b. NVIDIA, *L40S GPU* (48 GB GDDR6, 864 GB/s, 350 W). https://www.nvidia.com/en-us/data-center/l40s/
12. NVIDIA, *A100 Tensor Core GPU* (80 GB HBM2e; 1,935 GB/s PCIe, 2,039 GB/s SXM). https://www.nvidia.com/en-us/data-center/a100/
13. Meta AI Research, *Faiss wiki: Guidelines to choose an index* (HNSW: "(d * 4 + M * 2 * 4) bytes per vector"). https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index
14. Google, *Understand and count tokens* (Gemini API docs: ≈ 4 characters per token; 100 tokens ≈ 60–80 English words). https://aistudio.google.com/docs/tokens
15. Cloudflare, *R2 pricing* ($0.015/GB-month Standard storage; no egress charges). https://developers.cloudflare.com/r2/pricing/
16. OpenAI, *gpt-oss-120b model card* (117 B total / 5.1 B active parameters; MXFP4 MoE weights; single 80 GB GPU). https://huggingface.co/openai/gpt-oss-120b
17. DeepSeek-AI, *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model*, arXiv:2405.04434, 2024 (MLA; "reduces the KV cache by 93.3%"). https://arxiv.org/abs/2405.04434
18. NVIDIA, *RTX PRO 6000 Blackwell Workstation Edition* (96 GB GDDR7, 1,792 GB/s, 600 W). https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/
19. NVIDIA, *DGX B200* (8 GPUs; 1,440 GB total; 64 TB/s HBM3e; FP8 72 PFLOPS sparse). https://www.nvidia.com/en-us/data-center/dgx-b200/
20. NVIDIA, *GB200 NVL72* (superchip: 372 GB HBM3e, 16 TB/s; rack: 13.4 TB, 576 TB/s). https://www.nvidia.com/en-us/data-center/gb200-nvl72/
21. D. Salvator, R. Bhargava, K. Devleker, *NVIDIA Blackwell Ultra for the Era of AI Reasoning*, NVIDIA Technical Blog, 2025-03-19 ("up to 288 GB of HBM3e memory per GPU"). https://developer.nvidia.com/blog/nvidia-blackwell-ultra-for-the-era-of-ai-reasoning
22. NVIDIA, *GB300 NVL72* (72 Blackwell Ultra GPUs; 20 TB GPU memory; up to 576 TB/s). https://www.nvidia.com/en-us/data-center/gb300-nvl72/
23. NVIDIA, *HGX platform* (HGX B300: 2.1 TB; HGX B200: 1.4 TB; HGX Rubin NVL8: 2 TB HBM4, 130 TB/s). https://www.nvidia.com/en-us/data-center/hgx/
24. J. Kaplan et al., *Scaling Laws for Neural Language Models*, arXiv:2001.08361, 2020 (§2.1: C_forward ≈ 2N + …; C ≈ 6N FLOPs per training token). https://arxiv.org/abs/2001.08361
25. S. Rajbhandari, J. Rasley, O. Ruwase, Y. He, *ZeRO: Memory Optimizations Toward Training Trillion Parameter Models*, arXiv:1910.02054v3, 2020 (2Ψ + 2Ψ + 12Ψ = 16Ψ bytes). https://arxiv.org/abs/1910.02054
26. E. J. Hu et al., *LoRA: Low-Rank Adaptation of Large Language Models*, arXiv:2106.09685, 2021. https://arxiv.org/abs/2106.09685
27. T. Dettmers, A. Pagnoni, A. Holtzman, L. Zettlemoyer, *QLoRA: Efficient Finetuning of Quantized LLMs*, arXiv:2305.14314, 2023. https://arxiv.org/abs/2305.14314
28. vLLM project, *Metrics* (design documentation). https://docs.vllm.ai/en/latest/design/metrics.html; release v0.34.0: https://github.com/vllm-project/vllm/releases/tag/v0.34.0
29. vLLM project, *Engine Arguments* (`--gpu-memory-utilization`). https://docs.vllm.ai/en/latest/configuration/engine_args.html
30. F. Yergeau, *UTF-8, a transformation format of ISO 10646*, RFC 3629, November 2003. https://www.rfc-editor.org/rfc/rfc3629
31. K. Davis, B. Peabody, P. Leach, *Universally Unique IDentifiers (UUIDs)*, RFC 9562, May 2024 (obsoletes RFC 4122). https://www.rfc-editor.org/rfc/rfc9562

### I03 — Question bank & rubrics: 77 questions by category and level, what good looks like, red flags

Lesson: [`course/05-interview/I03-question-bank-rubrics.md`](course/05-interview/I03-question-bank-rubrics.md) · source status: `DRAFT`

1. Meta Careers, *Preparing for your Software Engineering Interview at Meta*, updated 2022-10-06. https://www.metacareers.com/blog/preparing-for-your-software-engineering-interview-at-meta/
2. Amazon, *SDE III/Sr. SDE Interview Prep*. https://amazon.jobs/content/en/how-we-hire/sde-iii-interview-prep
3. S. Virji et al., "Non-Abstract Large System Design", *The Site Reliability Workbook*, ch. 12. https://sre.google/workbook/non-abstract-design/
4. K. Davis, B. Peabody, P. Leach, *Universally Unique IDentifiers (UUIDs)*, RFC 9562, May 2024 (UUIDv7, referenced in CL-14). https://www.rfc-editor.org/rfc/rfc9562

### I04 — ML/LLM system design interviews: how they differ, question bank, worked answers

Lesson: [`course/05-interview/I04-ml-llm-interviews.md`](course/05-interview/I04-ml-llm-interviews.md) · source status: `DRAFT`

1. M. Zinkevich, *Rules of Machine Learning: Best Practices for ML Engineering*, Google for Developers. https://developers.google.com/machine-learning/guides/rules-of-ml
2. D. Sculley et al., *Hidden Technical Debt in Machine Learning Systems*, NeurIPS 2015. https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html
3. L. Zheng et al., *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*, NeurIPS 2023 Datasets and Benchmarks. arXiv:2306.05685. https://arxiv.org/abs/2306.05685
4. N. F. Liu et al., *Lost in the Middle: How Language Models Use Long Contexts*, TACL 2023. arXiv:2307.03172. https://arxiv.org/abs/2307.03172
5. vLLM project, *Metrics* (design documentation; `vllm:time_to_first_token_seconds`, `vllm:inter_token_latency_seconds`, `vllm:kv_cache_usage_perc`, `vllm:num_requests_running`). https://docs.vllm.ai/en/latest/design/metrics.html
6. P. Covington, J. Adams, E. Sargin, *Deep Neural Networks for YouTube Recommendations*, ACM RecSys 2016. https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/
7. S. Rajbhandari, J. Rasley, O. Ruwase, Y. He, *ZeRO: Memory Optimizations Toward Training Trillion Parameter Models*, arXiv:1910.02054. https://arxiv.org/abs/1910.02054
8. E. J. Hu et al., *LoRA: Low-Rank Adaptation of Large Language Models*, arXiv:2106.09685, 2021. https://arxiv.org/abs/2106.09685
9. H. Inan et al., *Llama Guard: LLM-based Input-Output Safeguard for Human-AI Conversations*, arXiv:2312.06674, 2023. https://arxiv.org/abs/2312.06674
10. Meta AI Research, *Faiss wiki: Guidelines to choose an index*. https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index
11. NVIDIA, *H100 Tensor Core GPU*. https://www.nvidia.com/en-us/data-center/h100/
12. NVIDIA, *L4 Tensor Core GPU*. https://www.nvidia.com/en-us/data-center/l4/
13. Yu. A. Malkov, D. A. Yashunin, *Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs*, arXiv:1603.09320. https://arxiv.org/abs/1603.09320
