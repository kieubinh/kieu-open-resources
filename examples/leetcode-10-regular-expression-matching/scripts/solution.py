"""LeetCode #10 — memoized Python 3 solution: O(len(s) × len(p))."""
from functools import cache

class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        @cache
        def dfs(i: int, j: int) -> bool:
            if j == len(p):
                return i == len(s)
            first = i < len(s) and (s[i] == p[j] or p[j] == ".")
            if j + 1 < len(p) and p[j + 1] == "*":
                return dfs(i, j + 2) or (first and dfs(i + 1, j))
            return first and dfs(i + 1, j + 1)
        return dfs(0, 0)
