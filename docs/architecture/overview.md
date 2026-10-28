# Architecture and decisions

```
registry/ (git, reviewed PRs)  →  kieu_open_resources core SDK  →  CLI   MCP (stdio)   web/API (planned)
```

Rules: the git registry is the only source of truth; every interface calls the SDK (`registry`, `schema`, `licensing`, `search`, `discovery`, `evaluation`, `manifest`, `candidates`, `sanitize`); skills describe workflows and hold no registry logic; nothing in P0 touches the network or executes resource content.

## Status (P0)

| Area | State |
|---|---|
| Schema, lifecycle, validation, duplicate/conflict detection | implemented, unit-tested |
| Search, license-check, compare, history, quickstart, preview | implemented, tested |
| Manifest (`kieu-resources.lock.json`) add/validate/remove | implemented, tested |
| Candidate submission, evaluation submission, evidenced review | implemented, tested |
| Discovery skill + Codex/Claude entrypoints + `install-skill` | implemented; **agent behaviour not measured in a live runtime** |
| Local stdio MCP server on the core SDK (read-only default, gated proposal writes, audit log) | implemented, tested over real stdio; **not yet verified in a live Codex/Claude Code session** |
| Dataset preview adapters beyond inline reviewed samples, remote transport | **planned** |
| `kieu-model-builder` rework, AI relevance ranker, baselines | **planned (P2)** |
| Generated SQLite index | not built; not justified by registry size |

## Decisions

1. **Stdlib-only, Python ≥ 3.9.** The target machine only has 3.9.6 and the SDK needs nothing else; code avoids 3.10+ syntax and CI covers 3.9/3.11/3.12. A hand-written validator replaces `jsonschema` to keep installs dependency-free; the cost is no editor JSON Schema (see `registry/schema/README.md`).
2. **JSON files, one per resource.** Diff-friendly PR review and trivial validation; no database.
3. **Legacy `kieu_resource` package kept.** It is a separate, remote-first HTTP/MCP service with an empty registry and 16 passing tests. It is *not* connected to the new registry. To avoid two sources of truth it is frozen and slated to be rebuilt on the core SDK in P1; do not add resources to its `registry.json`.
4. **Candidates are not selectable.** `get`/`manifest` only see `registry/resources`; candidates live in `registry/candidates`.
5. **Approval ≠ eligibility.** `license-check` returns both `decision` and `usable`.
6. **Skills are canonical in `skills/`.** `.agents/skills`, `.claude/skills` and the packaged `src/*/skills` are symlinks; `install-skill` writes generated copies for other repositories.
