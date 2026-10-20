import itertools
import json
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from verify import score, canonical, orbit, parse_sequence, verify_object


def xor_correlations(bits):
    """Independent packed-bit Hamming distance formulation."""
    n = len(bits)
    b = int(bits, 2)
    return [(n-k)-2*((b ^ (b >> k)) & ((1 << (n-k))-1)).bit_count()
            for k in range(1, n)]


class VerifyTests(unittest.TestCase):
    def test_known(self):
        self.assertEqual(score("+++++--++-+-+")["E"], 6)
        self.assertEqual(score("1")["F_exact"], "infinity")
        for n in range(2, 25):
            self.assertEqual(score("1"*n)["E"], n*(n-1)*(2*n-1)//6)

    def test_rejection(self):
        for x in ("", "102", "+1-1", [], [True], [1.0], [0], [2], None):
            with self.assertRaises(ValueError):
                parse_sequence(x)
        with self.assertRaises(ValueError):
            verify_object({"sequence": "111", "E": 1})
        with self.assertRaises(ValueError):
            verify_object({"sequence": "111", "N": 2})
        for value in (True, 1.0):
            with self.assertRaises(ValueError):
                verify_object({"sequence": "10", "E": value})

    def test_independent_and_symmetries(self):
        rng = random.Random(101)
        for n in (2, 3, 7, 16, 31, 66, 99, 451, 573):
            s = [rng.choice([-1, 1]) for _ in range(n)]
            v = score(s)
            bits = "".join("1" if x == 1 else "0" for x in s)
            self.assertEqual(v["autocorrelations"], xor_correlations(bits))
            for t in orbit(s):
                self.assertEqual(score(list(t))["E"], v["E"])
                self.assertEqual(canonical(t), v["canonical"])
        # A cyclic rotation is NOT an aperiodic-energy symmetry.
        self.assertNotEqual(score("11110")["E"], score("11101")["E"])

    def test_exhaustive(self):
        # Full enumeration: no symmetry pruning can hide a checker error.
        expected = [0, 1, 1, 2, 2, 7, 3, 8, 12, 13, 5, 10, 6, 19, 15, 24]
        for n, energy in enumerate(expected, 1):
            best = None
            for v in range(1 << n):
                b = format(v, f"0{n}b")
                cs = xor_correlations(b)
                e = sum(x*x for x in cs)
                if n <= 9:
                    self.assertEqual(score(b)["autocorrelations"], cs)
                best = e if best is None else min(best, e)
            self.assertEqual(best, energy, n)
            if n >= 2:
                published = json.loads((ROOT/f"data/witnesses/{n}.json").read_text())
                self.assertEqual(score(published["sequence"])["E"], best)


if __name__ == "__main__":
    unittest.main()
