#!/usr/bin/env python3
"""Run the differential / edge / worst-case verification and write src/data/verification.json.

The numbers shown in the "Kiểm chứng" scene of the video are read from that file, so the
video can never claim a test that was not run. Re-run after any change to solution.py.

Run:  python3 scripts/run_verification.py
"""
import itertools
import json
import platform
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from oracles import dp_oracle, regex_oracle, regex_oracle_bounded  # noqa: E402
from solution import Solution  # noqa: E402

OFFICIAL = [("aa", "a", False), ("aa", "*", True), ("cb", "?a", False)]
EDGE = [
    ("", "", True), ("", "*", True), ("", "***", True), ("", "?", False), ("a", "", False),
    ("a", "a*", True), ("a", "*a*", True), ("a", "??", False), ("ab", "?*", True),
    ("ab", "*?*?*", True), ("aaaa", "***a", True), ("adceb", "*a*b", True),
    ("acdcb", "a*c?b", False), ("abcabczzzde", "*abc???de*", True), ("aab", "c*a*b", False),
    ("mississippi", "m??*ss*?i*pi", False),
]
EXHAUSTIVE = {"alphabet_s": "ab", "max_s": 6, "alphabet_p": "ab?*", "max_p": 5}
RANDOM = {"seed": 44, "cases": 20000, "max_s": 40, "max_p": 30}
WORST = {"n": 2000}
TYPICAL = {"seed": 4402, "cases": 40, "n": 2000}


def words(alphabet, longest):
    for length in range(longest + 1):
        for tup in itertools.product(alphabet, repeat=length):
            yield "".join(tup)


def count_loop_iterations(s, p):
    """Count executions of the main ``while`` line using the real solution function."""
    target = Solution.isMatch.__code__
    first = target.co_firstlineno
    while_line = None
    for no, text in enumerate((HERE / "solution.py").read_text().splitlines(), 1):
        if text.strip() == "while i < len(s):":
            while_line = no
    hits = [0]

    def local(frame, event, arg):
        if event == "line" and frame.f_lineno == while_line:
            hits[0] += 1
        return local

    def global_(frame, event, arg):
        return local if frame.f_code is target else None

    assert while_line and while_line > first
    sys.settrace(global_)
    try:
        result = Solution().isMatch(s, p)
    finally:
        sys.settrace(None)
    return result, hits[0]


def main():
    f = Solution().isMatch
    out = {"python": platform.python_version(), "platform": platform.platform(terse=True)}
    out["official"] = [{"s": s, "p": p, "expected": e, "actual": f(s, p), "pass": f(s, p) == e} for s, p, e in OFFICIAL]
    out["edge"] = {"cases": len(EDGE), "failures": [[s, p] for s, p, e in EDGE if f(s, p) != e]}

    cases = mismatches = 0
    for s in words(EXHAUSTIVE["alphabet_s"], EXHAUSTIVE["max_s"]):
        for p in words(EXHAUSTIVE["alphabet_p"], EXHAUSTIVE["max_p"]):
            cases += 1
            got = f(s, p)
            if got != regex_oracle(s, p) or got != dp_oracle(s, p):
                mismatches += 1
    out["exhaustive"] = {**EXHAUSTIVE, "cases": cases, "mismatches": mismatches,
                         "oracles": ["regex fullmatch", "2-D DP table"]}

    rng = random.Random(RANDOM["seed"])
    mismatches = regex_checked = 0
    for _ in range(RANDOM["cases"]):
        alphabet = rng.choice(["ab", "abc", "abcd"])
        s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, RANDOM["max_s"])))
        p = "".join(rng.choice(alphabet + "??**") for _ in range(rng.randint(0, RANDOM["max_p"])))
        got = f(s, p)
        via_regex = regex_oracle_bounded(s, p)
        regex_checked += via_regex is not None
        if got != dp_oracle(s, p) or (via_regex is not None and got != via_regex):
            mismatches += 1
    out["random"] = {**RANDOM, "mismatches": mismatches, "regex_checked": regex_checked,
                     "oracles": ["2-D DP table (every case)", "regex fullmatch (patterns with at most 4 star groups)"]}

    n = WORST["n"]
    s, p = "a" * n, "*" + "a" * (n // 2 - 1) + "b"
    started = time.perf_counter()
    answer, iterations = count_loop_iterations(s, p)
    traced_seconds = time.perf_counter() - started
    started = time.perf_counter()
    answer2 = f(s, p)
    seconds = time.perf_counter() - started
    out["worst"] = {"n": n, "s": "'a' × 2000", "p": "'*' + 'a' × 999 + 'b'", "answer": answer2,
                    "agrees": answer == answer2 == dp_oracle(s, p) == regex_oracle(s, p),
                    "loop_iterations": iterations, "seconds": round(seconds, 4),
                    "note": "wall-clock on the machine that ran this script; iterations are exact"}
    # Typical behaviour: random maximum-size inputs (|s| = |p| = 2000), loop iterations per (|s| + |p|).
    rng = random.Random(TYPICAL["seed"])
    ratios = []
    for _ in range(TYPICAL["cases"]):
        s = "".join(rng.choice("ab") for _ in range(TYPICAL["n"]))
        p = "".join(rng.choice("ab?**") for _ in range(TYPICAL["n"]))
        res, iters = count_loop_iterations(s, p)
        assert res == f(s, p)
        ratios.append(iters / (len(s) + len(p)))
    out["typical"] = {**TYPICAL, "mean_iterations_per_char": round(sum(ratios) / len(ratios), 3),
                      "max_iterations_per_char": round(max(ratios), 3)}
    out["dp_cells"] = (n + 1) * (n + 1)
    out["max_cells_for_constraints"] = 2001 * 2001
    path = ROOT / "src/data/verification.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    bad = (not all(r["pass"] for r in out["official"]) or out["edge"]["failures"]
           or out["exhaustive"]["mismatches"] or out["random"]["mismatches"] or not out["worst"]["agrees"])
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
