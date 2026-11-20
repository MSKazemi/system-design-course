#!/usr/bin/env python3
"""Predict mean and p99 time-in-system for the lab service before you measure it.

Two textbook single-server models (WORKERS=1, exponential service time, mean S):

  M/M/1  Poisson (random) arrivals.  Time in system is exponential with rate (mu - lambda):
         mean W = 1/(mu - lambda),  p99 = ln(100)/(mu - lambda).
  D/M/1  Evenly spaced arrivals (what k6's constant-arrival-rate executor produces).
         Time in system is exponential with rate mu(1 - sigma), where sigma in (0,1) solves
         sigma = exp(-(1 - sigma)/rho):   mean W = 1/(mu(1 - sigma)),  p99 = ln(100)/(mu(1 - sigma)).

Both are G/M/1 results (see Kleinrock, Queueing Systems Vol. 1, 1975). This lab's arrivals are
evenly spaced, so expect measurements near D/M/1. Production traffic is usually burstier than
Poisson, so production queues tend to be worse than both models. Neither model includes network
and HTTP overhead (about 1 ms here).

Usage: python3 predict.py [SERVICE_MS] [rate1 rate2 ...]
       python3 predict.py --measured RATE UTIL [RATE UTIL ...]
The second form uses the utilisation the service itself reported (the SERVER line printed
by sweep.sh), so the prediction uses the service time actually achieved in that run
(time.sleep overshoots slightly, and exponential draws vary from run to run).
"""
import math
import sys


def dm1_sigma(rho: float) -> float:
    # Fixed-point iteration converges for rho < 1.
    s = 0.5
    for _ in range(10_000):
        s_new = math.exp(-(1.0 - s) / rho)
        if abs(s_new - s) < 1e-12:
            break
        s = s_new
    return s


def measured(pairs: list[float]) -> None:
    ln100 = math.log(100)
    print(f"{'rate':>6} {'rho':>6} {'S':>7} | {'M/M/1 mean':>10} {'M/M/1 p99':>10} | {'D/M/1 mean':>10} {'D/M/1 p99':>10}")
    for lam, rho in zip(pairs[0::2], pairs[1::2]):
        s = rho / lam
        mu = 1.0 / s
        if rho >= 1:
            print(f"{lam:6.0f} {rho:6.3f} unstable")
            continue
        r_mm1, r_dm1 = mu - lam, mu * (1 - dm1_sigma(rho))
        print(f"{lam:6.0f} {rho:6.3f} {s*1000:5.2f}ms | {1000/r_mm1:8.1f}ms {1000*ln100/r_mm1:8.1f}ms | "
              f"{1000/r_dm1:8.1f}ms {1000*ln100/r_dm1:8.1f}ms")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--measured":
        measured([float(x) for x in sys.argv[2:]])
        return
    service_ms = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    rates = [float(x) for x in sys.argv[2:]] or [20, 40, 60, 70, 80, 90, 95, 98]
    mu = 1000.0 / service_ms
    print(f"service time {service_ms} ms -> capacity mu = {mu:.0f} req/s\n")
    print(f"{'rate':>6} {'rho':>5} | {'M/M/1 mean':>10} {'M/M/1 p99':>10} | {'D/M/1 mean':>10} {'D/M/1 p99':>10}")
    for lam in rates:
        rho = lam / mu
        if rho >= 1:
            print(f"{lam:6.0f} {rho:5.2f} | {'unstable':>10} {'':>10} | {'unstable':>10}")
            continue
        r_mm1 = mu - lam
        r_dm1 = mu * (1 - dm1_sigma(rho))
        ln100 = math.log(100)
        print(f"{lam:6.0f} {rho:5.2f} | {1000/r_mm1:8.1f}ms {1000*ln100/r_mm1:8.1f}ms | "
              f"{1000/r_dm1:8.1f}ms {1000*ln100/r_dm1:8.1f}ms")


if __name__ == "__main__":
    main()
