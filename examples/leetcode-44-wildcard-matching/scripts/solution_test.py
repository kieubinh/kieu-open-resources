"""Algorithm tests for LeetCode #44. Run: python3 -m unittest discover -s scripts -p '*test.py' -v"""
import itertools
import json
import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_trace as ep03_trace  # noqa: E402
from oracles import (dp_oracle, dp_table, greedy_no_backtrack, naive_calls, naive_tree, regex_oracle,  # noqa: E402
                     regex_oracle_bounded)
from solution import Solution  # noqa: E402

ROOT = HERE.parent


class OfficialExamples(unittest.TestCase):
    def test_three_official_examples(self):
        f = Solution().isMatch
        self.assertIs(f("aa", "a"), False)   # Example 1
        self.assertIs(f("aa", "*"), True)    # Example 2
        self.assertIs(f("cb", "?a"), False)  # Example 3


class EdgeCases(unittest.TestCase):
    CASES = [
        ("", "", True), ("", "*", True), ("", "***", True), ("", "?", False), ("a", "", False),
        ("a", "a*", True), ("a", "*a*", True), ("a", "??", False), ("ab", "?*", True),
        ("ab", "*?*?*", True), ("aaaa", "***a", True), ("adceb", "*a*b", True),
        ("acdcb", "a*c?b", False), ("abcabczzzde", "*abc???de*", True), ("aab", "c*a*b", False),
        ("mississippi", "m??*ss*?i*pi", False),
    ]

    def test_edge_cases(self):
        f = Solution().isMatch
        for s, p, expected in self.CASES:
            with self.subTest(s=s, p=p):
                self.assertEqual(f(s, p), expected)

    def test_maximum_length_inputs(self):
        f = Solution().isMatch
        n = 2000
        self.assertTrue(f("a" * n, "*"))
        self.assertTrue(f("a" * n, "?" * n))
        self.assertFalse(f("a" * n, "?" * (n - 1)))
        self.assertFalse(f("a" * n, "*" + "a" * (n // 2 - 1) + "b"))  # greedy worst case (~1M loop iterations)
        self.assertTrue(f("", "*" * n))


class DifferentialTests(unittest.TestCase):
    def test_exhaustive_small_alphabet(self):
        f = Solution().isMatch
        strings = ["".join(t) for n in range(6) for t in itertools.product("ab", repeat=n)]
        patterns = ["".join(t) for n in range(5) for t in itertools.product("ab?*", repeat=n)]
        for s in strings:
            for p in patterns:
                got = f(s, p)
                self.assertEqual(got, regex_oracle(s, p), (s, p))
                self.assertEqual(got, dp_oracle(s, p), (s, p))

    def test_random_against_two_oracles(self):
        f = Solution().isMatch
        rng = random.Random(4401)
        for _ in range(4000):
            alphabet = rng.choice(["ab", "abc"])
            s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 30)))
            p = "".join(rng.choice(alphabet + "??**") for _ in range(rng.randint(0, 24)))
            got = f(s, p)
            self.assertEqual(got, dp_oracle(s, p), (s, p))
            via_regex = regex_oracle_bounded(s, p)  # None when the pattern would make `re` exponential
            if via_regex is not None:
                self.assertEqual(got, via_regex, (s, p))


class TeachingClaims(unittest.TestCase):
    """Every claim the video makes about the 'wrong' approaches must be reproducible."""

    def test_greedy_without_backtracking_is_wrong(self):
        self.assertTrue(Solution().isMatch("adceb", "*a*b"))
        self.assertFalse(greedy_no_backtrack("adceb", "*a*b"))

    def test_call_tree_matches_call_counter(self):
        for s, p in [("aaa", "*a*b"), ("aa", "*"), ("adceb", "*a*b"), ("", "***")]:
            self.assertEqual(len(naive_tree(s, p)), naive_calls(s, p)[1])
            self.assertEqual(naive_tree(s, p)[0]["result"], naive_calls(s, p)[0])

    def test_recursion_blows_up_with_more_stars(self):
        calls = [naive_calls("a" * 20, "*a" * k + "b")[1] for k in range(1, 7)]
        self.assertEqual(calls, sorted(calls))
        self.assertGreater(calls[-1], 100 * calls[0])

    def test_tree_example_has_repeated_states(self):
        nodes = naive_tree("aaa", "*a*b")
        states = [(n["i"], n["j"]) for n in nodes]
        self.assertLess(len(set(states)), len(states))

    def test_dp_table_shape_and_corner(self):
        table = dp_table("adceb", "*a*b")
        self.assertEqual((len(table), len(table[0])), (6, 5))
        self.assertTrue(table[0][0] and table[0][1] and not table[0][2])
        self.assertTrue(table[5][4])


class SourceForDisplay(unittest.TestCase):
    def test_source_fits_on_screen(self):
        lines, _ = ep03_trace.source_block()
        self.assertLessEqual(len(lines), 24)
        self.assertLessEqual(max(len(line) for line in lines), 60)
        self.assertTrue(all("\t" not in line for line in lines))


class TraceFileIsFresh(unittest.TestCase):
    def test_trace_json_matches_real_execution(self):
        stored = json.loads((ROOT / "src/data/trace.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, json.loads(json.dumps(ep03_trace.build())),
                         "src/data/trace.json is stale — run python3 scripts/build_trace.py")

    def test_trace_official_rows(self):
        stored = json.loads((ROOT / "src/data/trace.json").read_text(encoding="utf-8"))
        self.assertEqual([r["s"] + "|" + r["p"] for r in stored["official"]], ["aa|a", "aa|*", "cb|?a"])
        self.assertTrue(all(r["matches_expected"] for r in stored["official"]))
        self.assertEqual([r["expected"] for r in stored["official"]], [False, True, False])


class VerificationFile(unittest.TestCase):
    def test_verification_report_is_clean(self):
        v = json.loads((ROOT / "src/data/verification.json").read_text(encoding="utf-8"))
        self.assertTrue(all(r["pass"] for r in v["official"]))
        self.assertEqual(v["edge"]["failures"], [])
        self.assertEqual(v["exhaustive"]["mismatches"], 0)
        self.assertEqual(v["random"]["mismatches"], 0)
        self.assertTrue(v["worst"]["agrees"])
        strings = sum(2 ** n for n in range(v["exhaustive"]["max_s"] + 1))
        patterns = sum(4 ** n for n in range(v["exhaustive"]["max_p"] + 1))
        self.assertEqual(v["exhaustive"]["cases"], strings * patterns)
        self.assertEqual(v["max_cells_for_constraints"], 2001 * 2001)


if __name__ == "__main__":
    unittest.main()
