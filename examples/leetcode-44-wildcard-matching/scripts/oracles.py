"""Independent reference implementations used to test and illustrate EP03.

Nothing here is imported by solution.py. Each oracle is deliberately a
different algorithm from the greedy solution:

* ``regex_oracle``        — translates the wildcard pattern to a regular expression.
* ``dp_table``            — bottom-up table: dp[i][j] = "s[:i] matches p[:j]".
* ``dp_oracle``           — the last cell of ``dp_table``.
* ``naive_calls``         — exhaustive recursion (no memo) with a call counter.
* ``naive_tree``          — the same recursion, recording the call tree.
* ``greedy_no_backtrack`` — the tempting-but-wrong greedy used as a counter-example.
"""
import re
import sys


def regex_oracle(s, p):
    pattern = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in p)
    return re.fullmatch(pattern, s, re.DOTALL) is not None


REGEX_MAX_STAR_GROUPS = 4


def regex_oracle_bounded(s, p):
    """Regex oracle that returns None when the pattern has too many ``*`` groups.

    Python's backtracking ``re`` is exponential in the number of ``.*`` groups, so patterns with more
    than REGEX_MAX_STAR_GROUPS runs of ``*`` are skipped (the DP oracle still checks them).
    """
    collapsed = re.sub(r"\*+", "*", p)
    if collapsed.count("*") > REGEX_MAX_STAR_GROUPS:
        return None
    return regex_oracle(s, collapsed)


def dp_table(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] and p[j - 1] == "*"
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                dp[i][j] = dp[i - 1][j] or dp[i][j - 1]
            else:
                dp[i][j] = dp[i - 1][j - 1] and (p[j - 1] == "?" or p[j - 1] == s[i - 1])
    return dp


def dp_oracle(s, p):
    return dp_table(s, p)[len(s)][len(p)]


def naive_calls(s, p):
    """Return (answer, number_of_calls) for exhaustive recursion without memoisation."""
    calls = [0]
    sys.setrecursionlimit(10000)

    def go(i, j):
        calls[0] += 1
        if j == len(p):
            return i == len(s)
        if p[j] == "*":
            return go(i, j + 1) or (i < len(s) and go(i + 1, j))
        return i < len(s) and (p[j] == "?" or p[j] == s[i]) and go(i + 1, j + 1)

    return go(0, 0), calls[0]


def naive_tree(s, p):
    """Exhaustive recursion call tree as a list of node dicts; node 0 is the root.

    The recursion mirrors ``naive_calls`` exactly (same short-circuit order), so
    ``len(naive_tree(s, p)) == naive_calls(s, p)[1]`` — a property the tests check.
    """
    nodes = []

    def build(i, j, how):
        node = {"id": len(nodes), "i": i, "j": j, "how": how, "children": [], "result": None}
        nodes.append(node)
        if j == len(p):
            node["result"] = i == len(s)
            node["why"] = "end" if node["result"] else "leftover"
            return node
        if p[j] == "*":
            first = build(i, j + 1, "skip")
            node["children"].append(first["id"])
            if first["result"]:
                node["result"] = True
                return node
            if i < len(s):
                second = build(i + 1, j, "eat")
                node["children"].append(second["id"])
                node["result"] = second["result"]
            else:
                node["result"] = False
            return node
        if i < len(s) and (p[j] == "?" or p[j] == s[i]):
            child = build(i + 1, j + 1, "match")
            node["children"].append(child["id"])
            node["result"] = child["result"]
        else:
            node["result"] = False
            node["why"] = "mismatch" if i < len(s) else "no-char"
        return node

    build(0, 0, "root")
    return nodes


def greedy_no_backtrack(s, p):
    """Wrong on purpose: a star swallows nothing and is never revisited."""
    i = j = 0
    while i < len(s):
        if j < len(p) and (p[j] == s[i] or p[j] == "?"):
            i += 1
            j += 1
        elif j < len(p) and p[j] == "*":
            j += 1
        else:
            return False
    while j < len(p) and p[j] == "*":
        j += 1
    return j == len(p)
