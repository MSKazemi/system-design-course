"""Property tests for shardsim (stdlib unittest). Run: python3 -m unittest -v test_shardsim"""
import unittest

import shardsim as s


class TestPartitioners(unittest.TestCase):
    KEYS = s.keys(20_000)

    def test_deterministic(self):
        for scheme in ("modulo", "ring", "rendezvous", "jump"):
            a = s.make(scheme, s.node_names(7))
            b = s.make(scheme, s.node_names(7))
            self.assertEqual([a.locate(k) for k in self.KEYS[:500]], [b.locate(k) for k in self.KEYS[:500]])

    def test_modulo_moves_most_keys(self):
        # Growing 10 -> 11 under modulo keeps a key only if h%10 == h%11: about 1/11 of keys stay.
        self.assertGreater(s.moved_fraction("modulo", self.KEYS, 10, 11), 0.85)

    def test_consistent_schemes_move_about_one_over_n_plus_one(self):
        ideal = 1 / 11
        for scheme in ("ring", "rendezvous", "jump"):
            f = s.moved_fraction(scheme, self.KEYS, 10, 11, vnodes=128)
            self.assertLess(abs(f - ideal), 0.03, f"{scheme} moved {f:.3f}, ideal {ideal:.3f}")

    def test_monotone_only_to_new_node(self):
        # Consistent schemes: a key that moves must move to the NEW node (monotonicity, Karger et al.).
        for scheme in ("ring", "rendezvous", "jump"):
            a, b = s.make(scheme, s.node_names(10)), s.make(scheme, s.node_names(11))
            for k in self.KEYS[:5000]:
                if a.locate(k) != b.locate(k):
                    self.assertEqual(b.locate(k), "node-10", scheme)

    def test_vnodes_improve_balance(self):
        nodes = s.node_names(10)
        one = s.load_stats(s.Ring(nodes, 1), self.KEYS)["max_over_mean"]
        many = s.load_stats(s.Ring(nodes, 256), self.KEYS)["max_over_mean"]
        self.assertLess(many, one)
        self.assertLess(many, 1.25)

    def test_jump_known_range(self):
        for k in range(1000):
            self.assertTrue(0 <= s.jump_hash(k, 13) < 13)
        self.assertEqual(s.jump_hash(12345, 1), 0)

    def test_salting_reduces_hottest_node(self):
        nodes = s.node_names(10)
        ring = s.Ring(nodes, 64)
        ks = s.keys(5000, "item")
        w = s.zipf_weights(len(ks), 1.1)
        base = s.load_stats(ring, ks, w)["max_over_mean"]
        sk, sw = [], []
        for r, (k, x) in enumerate(zip(ks, w)):
            if r < 10:
                for i in range(16):
                    sk.append(f"{k}#{i}")
                    sw.append(x / 16)
            else:
                sk.append(k)
                sw.append(x)
        self.assertLess(s.load_stats(ring, sk, sw)["max_over_mean"], base)


if __name__ == "__main__":
    unittest.main()
