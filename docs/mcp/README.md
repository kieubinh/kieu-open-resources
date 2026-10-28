# MCP server: `kieu-open-resources-mcp`

Local stdio server over the Core SDK (same logic as the CLI; nothing is reimplemented). No network, no accounts. Agents do **not** discover it automatically: register it explicitly.

## Tools

| Read-only (always) | Writes (only with `--allow-writes`) |
|---|---|
| `search_resources` `get_resource` `get_quick_start` `preview_dataset` `check_usage_rights` `compare_resources` `get_resource_history` `get_resource_evaluations` | `submit_resource_candidate` (review item only) · `submit_evaluation_candidate` (always stored unverified) · `save_project_resource_manifest` (confined to `--project-root`) |

There is no approval tool: approval stays a reviewed registry change. Inputs are validated against each tool's schema (unknown arguments rejected, limits enforced); results over 64 KiB are refused; request lines over 256 KiB are refused; resource text is returned as data with `injection_flags` and an untrusted-content notice; a registry that fails validation makes the server refuse to start. `--audit-log FILE` appends JSONL records of tool, status, argument *names* and resource id (no argument values).

Flags: `--registry PATH` · `--allow-writes` · `--project-root DIR` (default cwd) · `--audit-log FILE` · `--check` (health check: validates the registry, prints JSON, exits 0/3).

## Install for Claude Code

```sh
pip install -e /path/to/kieu-open-resources
kieu-open-resources-mcp --registry /path/to/kieu-open-resources/registry --check
claude mcp add --scope project kieu -- kieu-open-resources-mcp --registry /path/to/kieu-open-resources/registry
claude mcp list
```
Add `--allow-writes --project-root "$PWD" --audit-log ~/.kieu/audit.jsonl` only if the agent should propose candidates or save manifests. Project-scoped servers need a one-time approval in Claude Code.

## Install for Codex

`~/.codex/config.toml` (or `codex mcp add kieu -- kieu-open-resources-mcp --registry /path/to/registry`):
```toml
[mcp_servers.kieu]
command = "kieu-open-resources-mcp"
args = ["--registry", "/path/to/kieu-open-resources/registry"]
```
**Untested:** Codex is not installed on the development machine, so this configuration has not been exercised. Check `codex mcp --help` for your version.

## Verification status

* Implemented and tested: JSON-RPC over a real subprocess (`tests/integration/test_mcp.py`): initialize, tools/list, search → rights → compare → preview → manifest write, audit-log ordering, health check, read-only default, schema validation, path confinement, size caps, no-approval-by-write, injected-text flagging.
* **Not verified: behaviour inside a real Codex or Claude Code session.** `scripts/probe_claude_mcp.py` launches the real `claude` CLI on a realistic Vietnamese QA task against a temp registry (synthetic fixtures: eligible, non-commercial, license-conflict, unknown-rights, restricted) without naming the skill or any tool, then checks the recorded tool calls and manifest. It reports `NOT_RUN` if the CLI is unauthenticated; in the session that built this it was, so it has not yet produced results. Run it from a logged-in terminal: `python3 scripts/probe_claude_mcp.py --output probe.json`.
* Remote transport: not built. Add authentication, authorization and rate limiting before any remote exposure.
