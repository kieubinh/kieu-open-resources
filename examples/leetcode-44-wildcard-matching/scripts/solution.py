"""LeetCode #44 — Wildcard Matching. Python 3 greedy two-pointer solution.

Time: O(len(s) * len(p)) worst case, close to O(len(s) + len(p)) on typical input.
Extra space: O(1).

The class below is exactly what the episode shows on screen. Keep line count
and wording stable: the execution trace in src/data/trace.json is produced by
running this very function (see scripts/trace.py).
"""


class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        i = j = 0
        star = -1
        mark = 0
        while i < len(s):
            if j < len(p) and (p[j] == s[i] or p[j] == "?"):
                i += 1
                j += 1
            elif j < len(p) and p[j] == "*":
                star = j
                mark = i
                j += 1
            elif star != -1:
                mark += 1
                i = mark
                j = star + 1
            else:
                return False
        while j < len(p) and p[j] == "*":
            j += 1
        return j == len(p)
