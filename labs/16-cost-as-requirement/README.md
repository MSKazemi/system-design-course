# Lab L16 — A cost model for three architectures

Part of [SYSDESIGN-16 Cost as a requirement](../../course/02-modern-requirements/16-cost-as-requirement.md).

## Goal

Build and interrogate a transparent, auditable monthly cost model for the API tier of **Lumen** (the course's
fictional AI knowledge & chat product) under three architectures:

| | Architecture | Billing shape |
|---|---|---|
| A | Fixed fleet of VMs sized for peak, On-Demand, behind a load balancer | pay for capacity, all hours |
| B | Autoscaled fleet: committed baseline (Savings-Plan-style discount) + burst capacity mostly on spot | pay for capacity, tracks demand |
| C | Serverless functions behind an HTTP API gateway | pay per request and per GB-second of wall-clock |

You will find the break-even traffic between pay-per-use and provisioned capacity, see which cost driver
dominates (it is often **not** compute), compute cost per tenant under two allocation policies, and estimate cost
per 1k LLM tokens for a self-hosted GPU as a function of utilisation.

## What you will observe

- Egress can cost more than compute for an API that returns modest payloads.
- Serverless wins at low volume and loses above a crossover; the crossover moves a lot when request wall-clock
  time grows (a slow dependency makes every function-second more expensive, but costs a VM nothing extra).
- A minimum fleet for availability (N+1 across three AZs) sets a cost floor that pay-per-use does not have.
- The allocation policy for shared/fixed cost changes the reported cost of a small tenant by several times.
- Self-hosted GPU cost per token is inversely proportional to utilisation — idle GPUs are the expensive part.

## Prerequisites

- Python **3.10 or newer** (tested with 3.12.3). Standard library only: no `pip install`, no network, no cloud
  account, no credentials.

## Run

```bash
cd labs/16-cost-as-requirement
python3 cost_model.py --prices        # every price/assumption with its source and label
python3 cost_model.py                 # baseline report (300M requests/month)
python3 cost_model.py --sweep         # A vs B vs C across traffic volumes + break-even
python3 cost_model.py --sensitivity   # one-at-a-time sensitivity
python3 cost_model.py --llm           # cost per 1k tokens, self-hosted GPU vs API
python3 cost_model.py --json          # machine-readable baseline
python3 -m unittest -v test_cost_model.py
```

## Where the numbers come from

Every input is a `Price` with a `kind`:

- **`list-price`** — AWS us-east-1 public list prices read from the public AWS Price List API
  (`https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/<offer>/current/us-east-1/index.json`) on 2026-11-19/20:
  m7i.xlarge On-Demand $0.2016/h, g6.xlarge $0.8048/h, Lambda $0.0000166667 per GB-s and $0.20 per 1M requests,
  API Gateway HTTP API $1.00 per 1M requests (first 300M), ALB $0.0225/h + $0.008 per LCU-hour, S3 Standard $0.023,
  Standard-IA $0.0125, Glacier Instant Retrieval $0.004 per GB-month, cross-AZ $0.01/GB each direction, internet
  egress $0.09/GB for the first 10 TB after a 100 GB monthly free allowance. List prices change; re-read them.
- **`assumption`** — labelled guesses you are meant to change: Savings Plan discount (30%), spot discount (60%),
  GPU throughput (1,500 tokens/s), LLM API price ($0.001 per 1k tokens, hypothetical), and every field of
  `Workload` (CPU ms and wall-clock ms per request, response size, tenants, diurnal shape, …).

AWS is used only because its price list is public and machine-readable; the model's structure applies to any
cloud or to on-premises hardware (replace the price table). Ignored on purpose: free tiers other than egress,
taxes, support plans, negotiated discounts, request retries, observability, databases, NAT gateways, and the ALB
LCU dimensions other than processed bytes. Each of these is a valid extension exercise.

## Experiments

1. **Find the dominant driver.** Run the baseline. Rank the five cost columns for architecture B. What fraction of
   the total is compute?
2. **Break-even.** Run `--sweep`. At what monthly volume does serverless stop being cheapest? Convert it to average
   requests per second.
3. **The slow dependency.** Re-run the sweep after editing `wall_ms_per_request` from 120 to 300 in `Workload`.
   How far does the break-even move, and why does architecture A not change at all?
4. **The availability floor.** Set `min_vms = 2`, then `6`. How does the cost of A and B at 1M requests/month
   change? What requirement justifies each value?
5. **Payload diet.** Compare `response_kb = 30` with `response_kb = 8` (compression, pagination). How much does
   each architecture save per month? Compare that saving with switching architecture.
6. **Tenant allocation.** In the baseline output, compare the smallest tenant's cost under "proportional" vs
   "fixed split evenly". Which policy would you show a free-tier tenant, and which would you use for pricing?
7. **GPU utilisation.** Run `--llm`. At what utilisation does the self-hosted GPU match the (hypothetical) API price?
   Change `gpu_tokens_per_s` to half and to double; how does break-even utilisation move?
8. **Extension.** Add a NAT gateway, a managed database, or a second region to `shared_costs()` with list prices you
   look up yourself, each labelled with its source and access date.

## Expected results

Look for these patterns (the exact dollar figures depend on the prices and assumptions in the file):

- In the baseline, internet egress is the largest single line item for B and comparable to compute for A.
- `--sweep` reports one crossover between C and B; C is cheapest at low volumes and B at high volumes.
- `--sensitivity` shows that the wall-clock change moves C only, the CPU and utilisation changes move B only, and
  the payload change moves every architecture.
- `--llm` shows cost per 1k tokens halving each time utilisation doubles.
- All 18 unit tests pass.

## Clean up

Nothing to clean up beyond `rm -rf __pycache__` if Python created one.

## Cost

€0. Runs locally; makes no network calls.

## Test status

**runtime-tested** — 2026-11-20, Ubuntu 24.04.5 LTS (kernel 7.0.0-43-generic), Python 3.12.3.

Observed output summary (default `Workload`, prices as in the file on that date):

- Baseline, 300M requests/month (114.2 req/s average, peak/average 1.72), USD/month totals:
  A fixed fleet $1,897.66 (5 VMs), B autoscaled $1,545.57 (3 committed VMs, bursts to 5), C serverless $2,031.00.
  Egress $801.00 for every architecture; B compute $383.74.
- Storage experiment, 10 TB: all Standard $230.00; cold 80% to Standard-IA $146.00; to Glacier IR $78.00.
- `--sweep`: C cheapest up to 100M requests/month, B cheapest from 300M; reported crossover ≈ 110M
  requests/month (≈ 42 req/s average).
- `--sensitivity`: wall-clock 120→300 ms raises C by 44% and B by 0%; response 30→300 KB raises B by 450% and C by 311%.
- `--llm`: $0.00298 per 1k tokens at 5% utilisation, $0.00030 at 50%; break-even with the hypothetical API price at
  14.9% utilisation.
- `python3 -m unittest -v test_cost_model.py`: `Ran 18 tests … OK`, exit code 0.

## Troubleshooting

- `SyntaxError` on `float | None`: you are on Python < 3.10. Use 3.10+.
- `ModuleNotFoundError: cost_model` when running tests: run them from this directory, and do not pass `-I` to
  Python (isolated mode drops the script directory from `sys.path`).
- Numbers differ from the test-status summary: you changed an assumption or updated a price — that is the point.
  Record the date and source of any price you change.
