#!/usr/bin/env python3
"""Invariant tests for cost_model.py (standard library unittest).

Run:  python3 -m unittest -v test_cost_model.py
These tests check the model's arithmetic and monotonicity, not the prices themselves.
"""

import contextlib
import io
import math
import unittest
from dataclasses import replace

import cost_model as cm


class EgressTests(unittest.TestCase):
    def test_free_allowance(self):
        self.assertEqual(cm.egress_cost(50.0), 0.0)
        self.assertEqual(cm.egress_cost(100.0), 0.0)

    def test_first_tier(self):
        self.assertAlmostEqual(cm.egress_cost(1100.0), 1000 * 0.09)

    def test_tier_boundary(self):
        # 100 free + 10 TiB in tier 1 + 1 GB in tier 2
        gb = 100 + 10 * 1024 + 1
        self.assertAlmostEqual(cm.egress_cost(gb), 10 * 1024 * 0.09 + 0.085)

    def test_monotone_and_concave(self):
        costs = [cm.egress_cost(g) for g in (1e3, 1e4, 1e5, 1e6)]
        self.assertEqual(costs, sorted(costs))
        # average price per GB falls with volume (tiered pricing)
        avg = [c / g for c, g in zip(costs, (1e3, 1e4, 1e5, 1e6))]
        self.assertGreater(avg[1], avg[3])


class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.w = cm.Workload()

    def test_diurnal_profile_normalised(self):
        f = cm.diurnal_factors()
        self.assertEqual(len(f), 24)
        self.assertAlmostEqual(sum(f) / 24, 1.0)
        self.assertGreater(max(f), 1.0)

    def test_totals_are_sum_of_parts(self):
        for row in cm.evaluate(self.w).values():
            parts = sum(row[k] for k in ("compute", "load_balancer", "egress", "cross_az", "storage"))
            self.assertAlmostEqual(row["total"], parts)

    def test_serverless_is_linear_in_requests(self):
        a = cm.arch_serverless(replace(self.w, requests_per_month=1e6))
        b = cm.arch_serverless(replace(self.w, requests_per_month=2e6))
        self.assertAlmostEqual(b["compute"], 2 * a["compute"])
        self.assertAlmostEqual(b["load_balancer"], 2 * a["load_balancer"])

    def test_fixed_fleet_has_floor(self):
        tiny = cm.arch_fixed_fleet(replace(self.w, requests_per_month=1.0))
        self.assertEqual(tiny["_instances"], self.w.min_vms)
        self.assertAlmostEqual(tiny["compute"], self.w.min_vms * cm.HOURS_PER_MONTH * cm.p("vm_hour"))

    def test_autoscaled_never_exceeds_fixed_compute(self):
        for v in (1e6, 1e8, 1e9, 1e10):
            wv = replace(self.w, requests_per_month=v)
            self.assertLessEqual(cm.arch_autoscaled_mixed(wv)["compute"],
                                 cm.arch_fixed_fleet(wv)["compute"] * self.w.autoscale_headroom + 1e-9)

    def test_break_even_exists_and_is_consistent(self):
        be = cm.break_even_requests(self.w)
        self.assertIsNotNone(be)
        below = cm.evaluate(replace(self.w, requests_per_month=be * 0.5))
        above = cm.evaluate(replace(self.w, requests_per_month=be * 2.0))
        key_b, key_c = list(cm.ARCHITECTURES)[1], list(cm.ARCHITECTURES)[2]
        fd = lambda r: r["compute"] + r["load_balancer"]
        self.assertLess(fd(below[key_c]), fd(below[key_b]))
        self.assertGreater(fd(above[key_c]), fd(above[key_b]))

    def test_longer_wall_clock_only_hurts_serverless(self):
        slow = replace(self.w, wall_ms_per_request=self.w.wall_ms_per_request * 2)
        self.assertEqual(cm.arch_fixed_fleet(slow)["compute"], cm.arch_fixed_fleet(self.w)["compute"])
        self.assertGreater(cm.arch_serverless(slow)["compute"], cm.arch_serverless(self.w)["compute"])


class AllocationTests(unittest.TestCase):
    def test_zipf_weights_sum_to_one(self):
        w = cm.zipf_weights(200, 1.1)
        self.assertAlmostEqual(sum(w), 1.0)
        self.assertEqual(w, sorted(w, reverse=True))

    def test_policies_allocate_the_same_total(self):
        w = cm.Workload(tenants=50)
        arch = list(cm.ARCHITECTURES)[1]
        row = cm.evaluate(w)[arch]
        weights = cm.zipf_weights(w.tenants, w.tenant_zipf_s)
        variable = row["egress"] + row["cross_az"]
        fixed = row["compute"] + row["load_balancer"] + row["storage"]
        prop = sum((variable + fixed) * x for x in weights)
        even = sum(variable * x + fixed / w.tenants for x in weights)
        self.assertAlmostEqual(prop, row["total"])
        self.assertAlmostEqual(even, row["total"])

    def test_even_split_raises_small_tenant_cost(self):
        res = cm.tenant_unit_costs(cm.Workload(), list(cm.ARCHITECTURES)[1])
        small = res["smallest tenant"]
        self.assertGreater(small["fixed_split_evenly"], small["proportional"])


class LlmTests(unittest.TestCase):
    def test_cost_per_token_inverse_in_utilisation(self):
        c10, c50 = cm.llm_cost_per_1k_tokens(0.10), cm.llm_cost_per_1k_tokens(0.50)
        self.assertAlmostEqual(c10 / c50, 5.0)

    def test_formula(self):
        expected = cm.p("gpu_hour") / (cm.p("gpu_tokens_per_s") * 3600 / 1000)
        self.assertTrue(math.isclose(cm.llm_cost_per_1k_tokens(1.0), expected))


class PriceMetadataTests(unittest.TestCase):
    def test_every_price_is_labelled(self):
        for name, price in cm.PRICES.items():
            self.assertIn(price.kind, ("list-price", "assumption"), name)
            self.assertTrue(price.source, name)

    def test_cli_runs(self):
        for args in ([], ["--sweep"], ["--sensitivity"], ["--llm"], ["--prices"], ["--json"]):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.assertEqual(cm.main(args), 0)
            self.assertTrue(buf.getvalue().strip(), args)


if __name__ == "__main__":
    unittest.main()
