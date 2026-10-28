"""Opt-in LIVE probe: runs the real `claude` CLI against the V2 MCP server.

Builds a throwaway registry (copy of registry/ plus clearly synthetic fixtures), a throwaway project with the
discovery skill installed, then asks Claude Code a realistic task WITHOUT naming the skill or any tool.
Records every tool call from the stream-json transcript and checks observable behaviour. Costs model tokens;
never part of the unit test suite. Synthetic fixtures live only in the temp dir and are never committed.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests"))
from helpers import make_resource, write_registry  # noqa: E402

PROMPT = ("Build a Vietnamese document question-answering baseline for a commercial product. Use approved resources from the "
          "Kieu Open Resources registry: pick one dataset for evaluation and one model for inference, say which candidates you "
          "rejected and why, and record your selections in this project. Do not download anything or run training.")


def fixtures():
    out = []
    def add(rid, rtype="dataset", status="approved", desc="SYNTHETIC FIXTURE for a live probe. Not a real resource.", **kw):
        r = make_resource(rid, rtype, status, description=desc, **kw)
        out.append(r)
        return r
    add("syn-vi-docqa-open")
    add("syn-vi-docqa-nc", **{"usage_rights": {"use": "permitted", "research": "permitted", "commercial-use": "prohibited", "inference": "permitted"}})
    add("syn-vi-docqa-conflict", **{"license": {"id": "CC-BY-4.0", "status": "verified", "evidence": [
        {"url": "https://example.org/a", "claim": "card: CC-BY-4.0", "license_id": "CC-BY-4.0"},
        {"url": "https://example.org/b", "claim": "repo: CC-BY-NC-4.0", "license_id": "CC-BY-NC-4.0"}]}})
    add("syn-vi-docqa-unknown", **{"usage_rights": {}})
    add("syn-vi-llm-small", "model", tasks=["question-answering"], tags=["llm", "vietnamese"])
    add("syn-vi-llm-restricted", "model", "restricted", tasks=["question-answering"], tags=["llm", "vietnamese"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--timeout", type=int, default=420)
    ap.add_argument("--model")
    a = ap.parse_args()
    if not shutil.which("claude"):
        sys.exit("claude CLI not found")
    work = Path(tempfile.mkdtemp(prefix="kieu-probe-"))
    reg, proj, audit = work / "registry", work / "project", work / "audit.jsonl"
    shutil.copytree(REPO / "registry", reg)
    write_registry(reg, fixtures())
    proj.mkdir()
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    subprocess.run([sys.executable, "-m", "kieu_open_resources.cli", "install-skill", "--project", str(proj), "--agent", "claude"], check=True, env=env, capture_output=True)
    cfg = work / "mcp.json"
    cfg.write_text(json.dumps({"mcpServers": {"kieu": {"command": sys.executable, "args": [
        "-m", "kieu_open_resources.mcp", "--registry", str(reg), "--allow-writes", "--project-root", str(proj), "--audit-log", str(audit)],
        "env": {"PYTHONPATH": str(REPO / "src")}}}}))
    cmd = ["claude", "-p", PROMPT, "--output-format", "stream-json", "--verbose", "--mcp-config", str(cfg), "--strict-mcp-config",
           "--allowedTools", "mcp__kieu", "Skill", "--disallowedTools", "Bash", "Write", "Edit", "WebFetch", "WebSearch", "--max-turns", "25"]
    if a.model:
        cmd += ["--model", a.model]
    p = subprocess.run(cmd, cwd=str(proj), capture_output=True, text=True, timeout=a.timeout, stdin=subprocess.DEVNULL)
    calls, final, skill_use = [], "", False
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for blk in ev["message"].get("content", []):
                if blk.get("type") == "tool_use":
                    calls.append({"tool": blk["name"], "input": blk["input"]})
                    if blk["name"] == "Skill":
                        skill_use = True
        if ev.get("type") == "result":
            final = ev.get("result", "")
    if p.returncode != 0 and (not calls) and ("Not logged in" in final or "login" in final.lower()):
        a.output.write_text(json.dumps({"status": "NOT_RUN", "reason": final, "workdir": str(work)}, indent=2))
        sys.exit("NOT_RUN: claude CLI is not authenticated in this environment (%s). Run `claude` once interactively / `/login`, then retry." % final.strip())
    mcp_calls = [c["tool"].replace("mcp__kieu__", "") for c in calls if c["tool"].startswith("mcp__kieu__")]
    audit_tools = [json.loads(l)["tool"] for l in audit.read_text().splitlines()] if audit.exists() else []
    lock = proj / "kieu-resources.lock.json"
    manifest = json.loads(lock.read_text()) if lock.exists() else None
    picked = [r["id"] for r in (manifest or {}).get("resources", [])]
    checks = {
        "searched_registry": "search_resources" in mcp_calls,
        "searched_before_other_tools": bool(mcp_calls) and mcp_calls[0] == "search_resources",
        "checked_usage_rights": "check_usage_rights" in mcp_calls,
        "compared": "compare_resources" in mcp_calls,
        "inspected": "get_resource" in mcp_calls,
        "manifest_written": manifest is not None,
        "manifest_only_eligible": manifest is not None and set(picked) <= {"syn-vi-docqa-open", "syn-vi-llm-small"},
        "rejected_resources_not_in_manifest": not ({"syn-vi-docqa-nc", "syn-vi-docqa-conflict", "syn-vi-docqa-unknown", "syn-vi-llm-restricted"} & set(picked)),
        "used_skill_tool": skill_use,
        "audit_log_matches_calls": audit_tools == mcp_calls,
    }
    report = {"exit_code": p.returncode, "prompt": PROMPT, "tool_calls": calls, "mcp_call_sequence": mcp_calls, "audit_sequence": audit_tools,
              "manifest": manifest, "checks": checks, "final_answer": final, "stderr_tail": p.stderr[-800:], "workdir": str(work)}
    a.output.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({"checks": checks, "mcp_call_sequence": mcp_calls, "picked": picked}, indent=2))


if __name__ == "__main__":
    main()
