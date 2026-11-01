#!/usr/bin/env python3
"""Generate src/data/trace.json — every number the video animates comes from real execution.

* The greedy trace is captured by running ``Solution.isMatch`` under ``sys.settrace``,
  i.e. the exact function whose source is shown on screen.
* The DP table, call tree, blow-up counts and the failing greedy come from ``oracles.py``.

Run:  python3 scripts/build_trace.py          (writes src/data/trace.json)
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from oracles import dp_table, greedy_no_backtrack, naive_calls, naive_tree, regex_oracle  # noqa: E402
from solution import Solution  # noqa: E402

OFFICIAL = [  # LeetCode #44 official examples (source: problem page, 28 Oct 2026)
    {"id": 1, "s": "aa", "p": "a", "expected": False},
    {"id": 2, "s": "aa", "p": "*", "expected": True},
    {"id": 3, "s": "cb", "p": "?a", "expected": False},
]
MAIN_EXAMPLE = {"s": "adceb", "p": "*a*b"}  # extra example, from the LeetCode discussion tab test-cases
TREE_EXAMPLE = {"s": "aaa", "p": "*a*b"}
FIELDS = ("i", "j", "star", "mark")


def source_block():
    """Return (lines, first_line_number) of the ``class Solution`` block in solution.py."""
    text = (HERE / "solution.py").read_text(encoding="utf-8").splitlines()
    start = next(k for k, line in enumerate(text) if line.startswith("class Solution"))
    return text[start:], start + 1


def trace_function(fn, s, p, first_line):
    """Run fn(s, p) under sys.settrace; return (result, steps).

    A step is recorded *before* each source line executes, with the locals at that moment.
    """
    steps = []
    target = fn.__code__

    def local_tracer(frame, event, arg):
        if event == "line":
            lv = frame.f_locals
            steps.append({"line": frame.f_lineno - first_line, **{k: lv.get(k) for k in FIELDS}})
        elif event == "return":
            lv = frame.f_locals
            steps.append({"line": -1, "ret": bool(arg), **{k: lv.get(k) for k in FIELDS}})
        return local_tracer

    def global_tracer(frame, event, arg):
        return local_tracer if frame.f_code is target else None

    sys.settrace(global_tracer)
    try:
        result = fn(s, p)
    finally:
        sys.settrace(None)
    return result, steps


def line_index(lines, needle, nth=0):
    hits = [k for k, line in enumerate(lines) if line.strip() == needle]
    if len(hits) <= nth:
        raise SystemExit(f"solution.py changed: cannot find line {needle!r}")
    return hits[nth]


def derive_events(lines, steps):
    """Collapse the line trace into one event per loop iteration (plus trailing / return)."""
    L = {
        "while": line_index(lines, "while i < len(s):"),
        "match": line_index(lines, "i += 1"),
        "star": line_index(lines, "star = j"),
        "back": line_index(lines, "mark += 1"),
        "fail": line_index(lines, "return False"),
        "trail_while": line_index(lines, 'while j < len(p) and p[j] == "*":'),
        "ret": line_index(lines, "return j == len(p)"),
    }
    # `j += 1` occurs three times; the last one is the trailing-star skip.
    j_hits = [k for k, line in enumerate(lines) if line.strip() == "j += 1"]
    L["trail_step"] = j_hits[-1]
    kinds = {L["match"]: "match", L["star"]: "star", L["back"]: "backtrack", L["fail"]: "fail", L["trail_step"]: "trailing"}
    events = []
    for k, step in enumerate(steps):
        kind = kinds.get(step["line"])
        if kind is None:
            continue
        after = step
        for nxt in steps[k + 1:]:
            if nxt["line"] in (L["while"], L["trail_while"], L["ret"]) or nxt["line"] == -1:
                after = nxt
                break
        events.append({"kind": kind, "step": k, "line": step["line"],
                       "before": {f: step[f] for f in FIELDS},
                       "after": {f: after[f] for f in FIELDS}})
    return events, L


def summarise(s, p, lines, first_line):
    result, steps = trace_function(Solution().isMatch, s, p, first_line)
    events, _ = derive_events(lines, steps)
    return {"s": s, "p": p, "result": result, "steps": steps, "events": events}


def nobt_events(s, p):
    """Walk the wrong greedy (star never revisited) and record each decision."""
    i = j = 0
    out = []
    while i < len(s):
        before = {"i": i, "j": j}
        if j < len(p) and (p[j] == s[i] or p[j] == "?"):
            i, j = i + 1, j + 1
            out.append({"kind": "match", "before": before, "after": {"i": i, "j": j}})
        elif j < len(p) and p[j] == "*":
            j += 1
            out.append({"kind": "star-empty", "before": before, "after": {"i": i, "j": j}})
        else:
            out.append({"kind": "fail", "before": before, "after": before})
            return False, out
    while j < len(p) and p[j] == "*":
        j += 1
    return j == len(p), out


def build():
    """Return the complete trace dictionary (deterministic; no timestamps)."""
    lines, first_line = source_block()
    data = {
        "source": {"lines": lines, "firstLine": first_line,
                   "lineOf": {"while": line_index(lines, "while i < len(s):"),
                              "match": line_index(lines, "i += 1"),
                              "star": line_index(lines, "star = j"),
                              "back": line_index(lines, "mark += 1"),
                              "fail": line_index(lines, "return False"),
                              "trailWhile": line_index(lines, 'while j < len(p) and p[j] == "*":'),
                              "ret": line_index(lines, "return j == len(p)")}},
        "official": [],
        "main": summarise(MAIN_EXAMPLE["s"], MAIN_EXAMPLE["p"], lines, first_line),
    }
    for ex in OFFICIAL:
        row = summarise(ex["s"], ex["p"], lines, first_line)
        row.update({"id": ex["id"], "expected": ex["expected"]})
        row["matches_expected"] = row["result"] == ex["expected"]
        row["dp"] = dp_table(ex["s"], ex["p"])
        data["official"].append(row)

    data["main"]["dp"] = dp_table(MAIN_EXAMPLE["s"], MAIN_EXAMPLE["p"])
    data["main"]["regex"] = regex_oracle(MAIN_EXAMPLE["s"], MAIN_EXAMPLE["p"])
    nobt_result, nobt = nobt_events(MAIN_EXAMPLE["s"], MAIN_EXAMPLE["p"])
    data["noBacktrack"] = {"s": MAIN_EXAMPLE["s"], "p": MAIN_EXAMPLE["p"], "result": nobt_result,
                           "correct": data["main"]["result"], "events": nobt,
                           "agrees_with_function": greedy_no_backtrack(MAIN_EXAMPLE["s"], MAIN_EXAMPLE["p"]) == nobt_result}

    nodes = naive_tree(TREE_EXAMPLE["s"], TREE_EXAMPLE["p"])
    seen = Counter()
    for node in nodes:
        key = (node["i"], node["j"])
        seen[key] += 1
        node["repeat"] = seen[key] > 1
    totals = Counter((n["i"], n["j"]) for n in nodes)
    for node in nodes:
        node["dup"] = totals[(node["i"], node["j"])] > 1
    data["tree"] = {"s": TREE_EXAMPLE["s"], "p": TREE_EXAMPLE["p"], "nodes": nodes,
                    "calls": naive_calls(TREE_EXAMPLE["s"], TREE_EXAMPLE["p"])[1],
                    "distinctStates": len(totals)}
    data["blowup"] = {"n": 20, "pattern": "'*a' × k + 'b'", "rows": [
        {"k": k, "calls": naive_calls("a" * 20, "*a" * k + "b")[1]} for k in range(1, 7)]}
    return data


def main():
    data = build()
    out = ROOT / "src/data/trace.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("wrote", out.relative_to(ROOT), "main steps:", len(data["main"]["steps"]),
          "events:", [e["kind"] for e in data["main"]["events"]])
    print("tree nodes", len(data["tree"]["nodes"]), "distinct", data["tree"]["distinctStates"],
          "blowup", [r["calls"] for r in data["blowup"]["rows"]])


if __name__ == "__main__":
    main()
