#!/usr/bin/env python3
"""SYSDESIGN-16 lab: a transparent cost model for three architectures of "Lumen".

Python 3.10+ standard library only. No network access, no cloud account, no cost.

The model answers four questions a designer must be able to answer before launch:
  1. What does each architecture cost per month, broken down by cost driver?
  2. What is the unit cost (per 1M requests, per tenant, per 1k LLM tokens)?
  3. Where is the break-even between pay-per-use (serverless) and provisioned capacity?
  4. Which assumption moves the answer most (sensitivity)?

Every price is either a PUBLIC LIST PRICE (AWS us-east-1, read from the public AWS Price
List API on 2026-11-19/20, see PRICES[...].source) or an explicit, labelled ASSUMPTION.
List prices change; re-check them before using any number in a real decision. Discounts,
free tiers, taxes, support plans and negotiated rates are deliberately ignored unless a
labelled assumption says otherwise.

Usage:
  python3 cost_model.py                 # baseline report
  python3 cost_model.py --requests 300e6
  python3 cost_model.py --sweep         # break-even sweep over traffic
  python3 cost_model.py --sensitivity   # one-at-a-time sensitivity
  python3 cost_model.py --llm           # cost per 1k tokens, self-hosted GPU vs API
  python3 cost_model.py --json          # machine-readable baseline
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict, dataclass, field, replace

HOURS_PER_MONTH = 730.0  # AWS convention for monthly estimates (8,760 h / 12)
DAYS_PER_MONTH = HOURS_PER_MONTH / 24.0
SECONDS_PER_MONTH = HOURS_PER_MONTH * 3600.0

PRICE_LIST = "AWS Price List API, region us-east-1, https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/"


@dataclass(frozen=True)
class Price:
    value: float
    unit: str
    kind: str  # "list-price" or "assumption"
    source: str


PRICES: dict[str, Price] = {
    # --- compute (list prices, Linux, shared tenancy, On-Demand) ---
    "vm_hour": Price(0.2016, "USD per instance-hour (m7i.xlarge, 4 vCPU, 16 GiB)", "list-price",
                     PRICE_LIST + "AmazonEC2 (accessed 2026-11-20)"),
    "gpu_hour": Price(0.8048, "USD per instance-hour (g6.xlarge, 1x NVIDIA L4)", "list-price",
                      PRICE_LIST + "AmazonEC2 (accessed 2026-11-20)"),
    "lambda_gb_s": Price(0.0000166667, "USD per GB-second (x86, first 6B GB-s/month)", "list-price",
                         PRICE_LIST + "AWSLambda (accessed 2026-11-19)"),
    "lambda_request": Price(0.20 / 1e6, "USD per request", "list-price",
                            PRICE_LIST + "AWSLambda (accessed 2026-11-19)"),
    "apigw_http_request": Price(1.00 / 1e6, "USD per request (HTTP API, first 300M/month)", "list-price",
                                PRICE_LIST + "AmazonApiGateway (accessed 2026-11-19)"),
    "alb_hour": Price(0.0225, "USD per ALB-hour", "list-price", PRICE_LIST + "AWSELB (accessed 2026-11-19)"),
    "alb_lcu_hour": Price(0.008, "USD per LCU-hour", "list-price", PRICE_LIST + "AWSELB (accessed 2026-11-19)"),
    # --- storage and network (list prices) ---
    "s3_standard_gb_month": Price(0.023, "USD per GB-month (first 50 TB)", "list-price",
                                  PRICE_LIST + "AmazonS3 (accessed 2026-11-19)"),
    "s3_ia_gb_month": Price(0.0125, "USD per GB-month (Standard-IA)", "list-price",
                            PRICE_LIST + "AmazonS3 (accessed 2026-11-19)"),
    "s3_glacier_ir_gb_month": Price(0.004, "USD per GB-month (Glacier Instant Retrieval)", "list-price",
                                    PRICE_LIST + "AmazonS3 (accessed 2026-11-19)"),
    "cross_az_gb": Price(0.01, "USD per GB, each direction, between AZs", "list-price",
                         PRICE_LIST + "AWSDataTransfer (accessed 2026-11-19)"),
    # Internet egress tiers: (upper bound in GB, USD per GB). 100 GB/month free allowance below.
    "egress_free_gb": Price(100.0, "GB per month free, aggregated across services", "list-price",
                            "https://aws.amazon.com/s3/pricing/ (accessed 2026-11-19)"),
    # --- assumptions (NOT list prices; change them and watch the answer move) ---
    "savings_plan_discount": Price(0.30, "fraction off On-Demand for committed baseline", "assumption",
                                   "Assumption. AWS states Compute Savings Plans save 'up to 66%' "
                                   "(https://aws.amazon.com/savingsplans/compute-pricing/). For scale: the "
                                   "1-year No Upfront Standard Reserved Instance list rate for m7i.xlarge "
                                   "is $0.13336/h, 34% below On-Demand (AmazonEC2 price list, 2026-11-20)."),
    "spot_discount": Price(0.60, "fraction off On-Demand for spot capacity", "assumption",
                           "Assumption. AWS states 'up to 90%' (https://aws.amazon.com/ec2/spot/); spot "
                           "prices vary by pool and over time."),
    "llm_api_usd_per_1k_tokens": Price(0.0010, "USD per 1k tokens (blended input+output)", "assumption",
                                       "Hypothetical vendor price. Replace with a real quote."),
    "gpu_tokens_per_s": Price(1500.0, "aggregate tokens/s one GPU sustains at full batch", "assumption",
                              "Hypothetical throughput for a small model with continuous batching; "
                              "measure it (see lab L22) before trusting any per-token number."),
}

EGRESS_TIERS = [  # (tier size in GB, USD per GB), us-east-1 to internet, after the free allowance
    (10 * 1024, 0.09),
    (40 * 1024, 0.085),
    (100 * 1024, 0.07),
    (math.inf, 0.05),
]

# Hourly load shape (UTC hours 0..23), relative units. ASSUMPTION: one dominant region,
# quiet night, two daytime humps. It is normalised to mean 1.0 below.
DIURNAL_SHAPE = [0.30, 0.25, 0.22, 0.20, 0.22, 0.30, 0.50, 0.80, 1.20, 1.50, 1.60, 1.60,
                 1.50, 1.50, 1.60, 1.70, 1.70, 1.60, 1.40, 1.20, 1.00, 0.80, 0.60, 0.40]


def p(name: str) -> float:
    return PRICES[name].value


@dataclass(frozen=True)
class Workload:
    """Lumen's API tier. Every field is an assumption you are expected to change."""

    requests_per_month: float = 300e6
    cpu_ms_per_request: float = 50.0      # on-CPU time per request in the VM design
    wall_ms_per_request: float = 120.0    # wall-clock duration (includes I/O wait) -> serverless bill
    lambda_memory_gb: float = 1.0
    vcpus_per_vm: int = 4                  # m7i.xlarge
    target_cpu_utilisation: float = 0.60   # headroom for latency SLO
    min_vms: int = 3                       # one per AZ for N+1 across three AZs
    autoscale_headroom: float = 1.15       # extra capacity because scaling lags demand
    spot_share_of_burst: float = 0.70      # share of burst instance-hours on spot
    response_kb: float = 30.0              # internet egress per request
    internal_kb: float = 10.0              # service-to-datastore bytes per request
    cross_az_share: float = 2.0 / 3.0      # share of internal bytes crossing an AZ (3 AZs, uniform)
    stored_gb: float = 10_000.0            # documents + embeddings + backups
    hot_share: float = 0.20                # share of stored bytes read in the last 30 days
    tenants: int = 200
    tenant_zipf_s: float = 1.1


def diurnal_factors() -> list[float]:
    mean = sum(DIURNAL_SHAPE) / len(DIURNAL_SHAPE)
    return [x / mean for x in DIURNAL_SHAPE]


def egress_cost(gb: float, free_gb: float | None = None) -> float:
    """Tiered internet egress after a free allowance."""
    free = p("egress_free_gb") if free_gb is None else free_gb
    remaining = max(0.0, gb - free)
    cost = 0.0
    for size, rate in EGRESS_TIERS:
        take = min(remaining, size)
        cost += take * rate
        remaining -= take
        if remaining <= 0:
            break
    return cost


def vms_needed(rps: float, w: Workload, headroom: float = 1.0) -> int:
    capacity_rps_per_vm = w.vcpus_per_vm * w.target_cpu_utilisation / (w.cpu_ms_per_request / 1000.0)
    return max(w.min_vms, math.ceil(rps * headroom / capacity_rps_per_vm))


def alb_cost(w: Workload) -> float:
    # LCU is billed on the highest dimension; this model uses processed bytes only
    # (1 LCU = 1 GB/hour for EC2 targets) and states the simplification.
    gb_per_hour = w.requests_per_month * (w.response_kb + 1.0) / 1e6 / HOURS_PER_MONTH
    lcu_hours = max(gb_per_hour, 0.0) * HOURS_PER_MONTH
    return p("alb_hour") * HOURS_PER_MONTH + p("alb_lcu_hour") * lcu_hours


def shared_costs(w: Workload) -> dict[str, float]:
    """Costs that do not depend on the compute architecture."""
    egress_gb = w.requests_per_month * w.response_kb / 1e6
    cross_az_gb = w.requests_per_month * w.internal_kb * w.cross_az_share / 1e6
    return {
        "egress": egress_cost(egress_gb),
        # billed on both sides of the AZ boundary, so 2x per GB moved
        "cross_az": 2 * cross_az_gb * p("cross_az_gb"),
        "storage": w.stored_gb * p("s3_standard_gb_month"),
    }


def arch_fixed_fleet(w: Workload) -> dict[str, float]:
    """A. Fixed fleet sized for peak, On-Demand, behind an ALB."""
    avg_rps = w.requests_per_month / SECONDS_PER_MONTH
    peak_rps = avg_rps * max(diurnal_factors())
    n = vms_needed(peak_rps, w)
    return {"compute": n * HOURS_PER_MONTH * p("vm_hour"), "load_balancer": alb_cost(w),
            "_instances": float(n)}


def arch_autoscaled_mixed(w: Workload) -> dict[str, float]:
    """B. Autoscaled fleet: committed baseline (Savings Plan) + burst mostly on spot."""
    avg_rps = w.requests_per_month / SECONDS_PER_MONTH
    hourly = [vms_needed(avg_rps * f, w, w.autoscale_headroom) for f in diurnal_factors()]
    baseline = min(hourly)
    burst_instance_hours = sum(n - baseline for n in hourly) * DAYS_PER_MONTH
    od = p("vm_hour")
    committed = baseline * HOURS_PER_MONTH * od * (1 - p("savings_plan_discount"))
    spot = burst_instance_hours * w.spot_share_of_burst * od * (1 - p("spot_discount"))
    on_demand = burst_instance_hours * (1 - w.spot_share_of_burst) * od
    return {"compute": committed + spot + on_demand, "load_balancer": alb_cost(w),
            "_baseline_instances": float(baseline), "_peak_instances": float(max(hourly))}


def arch_serverless(w: Workload) -> dict[str, float]:
    """C. Functions + HTTP API gateway; billed per request and per GB-second of wall-clock."""
    gb_seconds = w.requests_per_month * w.lambda_memory_gb * w.wall_ms_per_request / 1000.0
    return {
        "compute": gb_seconds * p("lambda_gb_s") + w.requests_per_month * p("lambda_request"),
        "load_balancer": w.requests_per_month * p("apigw_http_request"),  # the API gateway plays this role
    }


ARCHITECTURES = {
    "A fixed fleet (on-demand, sized for peak)": arch_fixed_fleet,
    "B autoscaled (savings plan + spot burst)": arch_autoscaled_mixed,
    "C serverless (functions + API gateway)": arch_serverless,
}


def evaluate(w: Workload) -> dict[str, dict[str, float]]:
    common = shared_costs(w)
    out: dict[str, dict[str, float]] = {}
    for name, fn in ARCHITECTURES.items():
        parts = fn(w)
        row = {k: v for k, v in parts.items() if not k.startswith("_")}
        row.update(common)
        row["total"] = sum(row.values())
        row["per_1M_requests"] = row["total"] / (w.requests_per_month / 1e6)
        row.update({k: v for k, v in parts.items() if k.startswith("_")})
        out[name] = row
    return out


def tiered_storage_cost(w: Workload) -> dict[str, float]:
    """Storage experiment: everything in Standard vs lifecycle tiering of cold bytes."""
    all_standard = w.stored_gb * p("s3_standard_gb_month")
    cold = w.stored_gb * (1 - w.hot_share)
    to_ia = w.stored_gb * w.hot_share * p("s3_standard_gb_month") + cold * p("s3_ia_gb_month")
    to_gir = w.stored_gb * w.hot_share * p("s3_standard_gb_month") + cold * p("s3_glacier_ir_gb_month")
    return {"all Standard": all_standard, "cold -> Standard-IA": to_ia,
            "cold -> Glacier Instant Retrieval": to_gir}


def zipf_weights(n: int, s: float) -> list[float]:
    raw = [1.0 / (k ** s) for k in range(1, n + 1)]
    total = sum(raw)
    return [x / total for x in raw]


def tenant_unit_costs(w: Workload, arch: str) -> dict[str, dict[str, float]]:
    """Cost per tenant under two allocation policies for shared/fixed cost."""
    row = evaluate(w)[arch]
    weights = zipf_weights(w.tenants, w.tenant_zipf_s)
    variable = row["egress"] + row["cross_az"]
    if arch.startswith("C"):
        variable += row["compute"] + row["load_balancer"]
        fixed = row["storage"]
    else:
        fixed = row["compute"] + row["load_balancer"] + row["storage"]
    picks = {"largest tenant": 0, "median tenant": w.tenants // 2, "smallest tenant": w.tenants - 1}
    result = {}
    for label, i in picks.items():
        proportional = (variable + fixed) * weights[i]
        even_fixed = variable * weights[i] + fixed / w.tenants
        result[label] = {
            "share_of_requests": weights[i],
            "proportional": proportional,
            "fixed_split_evenly": even_fixed,
        }
    return result


def llm_cost_per_1k_tokens(utilisation: float) -> float:
    tokens_per_hour = p("gpu_tokens_per_s") * 3600.0 * utilisation
    return p("gpu_hour") / (tokens_per_hour / 1000.0)


def money(x: float) -> str:
    return f"${x:,.2f}"


def print_report(w: Workload) -> None:
    res = evaluate(w)
    print(f"Lumen API tier: {w.requests_per_month/1e6:,.0f}M requests/month "
          f"(avg {w.requests_per_month/SECONDS_PER_MONTH:,.1f} req/s, "
          f"peak/avg {max(diurnal_factors()):.2f})")
    print("All figures USD per month; list prices us-east-1 + labelled assumptions.\n")
    cols = ["compute", "load_balancer", "egress", "cross_az", "storage", "total", "per_1M_requests"]
    print(f"{'architecture':44}" + "".join(f"{c:>17}" for c in cols))
    for name, row in res.items():
        print(f"{name:44}" + "".join(f"{money(row[c]):>17}" for c in cols))
    a = res["A fixed fleet (on-demand, sized for peak)"]
    b = res["B autoscaled (savings plan + spot burst)"]
    print(f"\nA runs {a['_instances']:.0f} VMs all month; B runs {b['_baseline_instances']:.0f} committed "
          f"VMs and bursts to {b['_peak_instances']:.0f}.")
    print("\nStorage tiering experiment (same bytes, different classes; retrieval fees ignored):")
    for k, v in tiered_storage_cost(w).items():
        print(f"  {k:36}{money(v):>12}")
    print("\nCost per tenant, architecture B, two allocation policies for fixed cost:")
    for k, v in tenant_unit_costs(w, "B autoscaled (savings plan + spot burst)").items():
        print(f"  {k:16} share {v['share_of_requests']*100:6.2f}%   proportional {money(v['proportional']):>10}"
              f"   fixed split evenly {money(v['fixed_split_evenly']):>10}")


def print_sweep(w: Workload) -> None:
    print("Compute + front door only (shared costs excluded), USD per month:")
    print(f"{'req/month':>14}{'A fixed':>14}{'B autoscaled':>14}{'C serverless':>14}   cheapest")
    volumes = [1e6, 3e6, 10e6, 30e6, 60e6, 100e6, 300e6, 1e9, 3e9]
    for v in volumes:
        wv = replace(w, requests_per_month=v)
        res = evaluate(wv)
        vals = {n[0]: r["compute"] + r["load_balancer"] for n, r in zip(res.keys(), res.values())}
        best = min(vals, key=vals.get)
        print(f"{v:>14,.0f}{money(vals['A']):>14}{money(vals['B']):>14}{money(vals['C']):>14}   {best}")
    be = break_even_requests(w)
    if be is None:
        print("\nNo crossover between B and C in the searched range.")
    else:
        print(f"\nServerless (C) stops being cheaper than autoscaled VMs (B) at about "
              f"{be/1e6:,.0f}M requests/month ({be/SECONDS_PER_MONTH:,.0f} req/s average).")


def break_even_requests(w: Workload, lo: float = 1e5, hi: float = 1e10) -> float | None:
    """Bisection on log scale for the volume where C (serverless) costs the same as B."""
    def diff(v: float) -> float:
        res = evaluate(replace(w, requests_per_month=v))
        b = res["B autoscaled (savings plan + spot burst)"]
        c = res["C serverless (functions + API gateway)"]
        return (c["compute"] + c["load_balancer"]) - (b["compute"] + b["load_balancer"])
    if diff(lo) > 0 or diff(hi) < 0:
        return None
    for _ in range(80):
        mid = math.sqrt(lo * hi)
        if diff(mid) > 0:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)


def print_sensitivity(w: Workload) -> None:
    base = evaluate(w)
    arch_b = "B autoscaled (savings plan + spot burst)"
    arch_c = "C serverless (functions + API gateway)"
    print("One-at-a-time sensitivity: change one assumption, total USD/month for B and C.")
    cases = [
        ("baseline", w),
        ("wall-clock 120 -> 300 ms (slow dependency)", replace(w, wall_ms_per_request=300.0)),
        ("cpu 50 -> 25 ms (optimised code)", replace(w, cpu_ms_per_request=25.0)),
        ("response 30 -> 300 KB (images inline)", replace(w, response_kb=300.0)),
        ("internal 10 -> 100 KB (chatty services)", replace(w, internal_kb=100.0)),
        ("target util 0.60 -> 0.40 (stricter SLO)", replace(w, target_cpu_utilisation=0.40)),
        ("no spot (spot share 0)", replace(w, spot_share_of_burst=0.0)),
    ]
    print(f"{'case':46}{'B total':>14}{'C total':>14}{'B vs base':>11}{'C vs base':>11}")
    b0, c0 = base[arch_b]["total"], base[arch_c]["total"]
    for label, wv in cases:
        r = evaluate(wv)
        b, c = r[arch_b]["total"], r[arch_c]["total"]
        print(f"{label:46}{money(b):>14}{money(c):>14}{(b/b0-1)*100:>+10.0f}%{(c/c0-1)*100:>+10.0f}%")


def print_llm() -> None:
    print("Self-hosted GPU cost per 1k tokens vs utilisation (g6.xlarge On-Demand list price,")
    print(f"ASSUMED {p('gpu_tokens_per_s'):,.0f} tokens/s at full batch). API price ASSUMED "
          f"${p('llm_api_usd_per_1k_tokens'):.4f} per 1k tokens (hypothetical).")
    print(f"{'utilisation':>12}{'USD per 1k tokens':>20}{'vs API':>10}")
    for u in (0.05, 0.10, 0.25, 0.50, 0.75, 0.90):
        c = llm_cost_per_1k_tokens(u)
        print(f"{u*100:>11.0f}%{c:>20.5f}{c/p('llm_api_usd_per_1k_tokens'):>9.2f}x")
    be_u = p("gpu_hour") / (p("gpu_tokens_per_s") * 3.6 * p("llm_api_usd_per_1k_tokens"))
    print(f"\nBreak-even utilisation (self-hosted = API): {be_u*100:.1f}% of the GPU's sustained throughput.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--requests", type=float, help="requests per month (default 300e6)")
    ap.add_argument("--sweep", action="store_true", help="break-even sweep over traffic volume")
    ap.add_argument("--sensitivity", action="store_true", help="one-at-a-time sensitivity table")
    ap.add_argument("--llm", action="store_true", help="cost per 1k tokens, GPU vs API")
    ap.add_argument("--json", action="store_true", help="print baseline results as JSON")
    ap.add_argument("--prices", action="store_true", help="list every price and assumption with its source")
    args = ap.parse_args(argv)

    w = Workload() if args.requests is None else Workload(requests_per_month=args.requests)
    if args.prices:
        for k, v in PRICES.items():
            print(f"{k:28} {v.value:<14g} [{v.kind}] {v.unit}\n{'':28} source: {v.source}")
        return 0
    if args.json:
        json.dump({"workload": asdict(w), "results": evaluate(w),
                   "prices": {k: asdict(v) for k, v in PRICES.items()}}, sys.stdout, indent=2)
        print()
        return 0
    if args.sweep:
        print_sweep(w)
    elif args.sensitivity:
        print_sensitivity(w)
    elif args.llm:
        print_llm()
    else:
        print_report(w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
