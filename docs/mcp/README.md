# MCP

**Status: planned (P1) for the new core.** The legacy `kieu-resource-mcp` adapter (package `kieu_resource`) exists but talks to the legacy HTTP service, not to `registry/`. Do not configure agents against it for registry discovery. P1 will add a stdio server over `kieu_open_resources`, with the same read-only tools as the CLI, schema-validated inputs, output caps and audit logging, plus config examples for Codex and Claude Code and a recorded end-to-end smoke test. Until then agents use the CLI.
