# Kieu Open Resources

Reusable open-source skills, educational tools and video templates from **Kieu Studio / The Art of Coding**.

- [Problem-solving video factory](#problem-solving-video-factory): the `kieu-leetcode-video` skill and a LeetCode #10 reference episode.
- [Kieu Open Resources registry (V2, P0)](#kieu-open-resources-registry-v2): git-versioned registry, core SDK, `kieu-open-resources` CLI and the `kieu-resource-discovery` skill.
- [Legacy Kieu Resources service (v1)](#kieu-resources-registry): the earlier remote-first HTTP API / MCP adapter; not connected to the V2 registry.

## Problem-solving video factory

**LeetCode is the practice material. Problem-solving is the skill.**

The [LeetCode Video Skill](skills/kieu-leetcode-video/SKILL.md) teaches how to build educational videos around careful problem understanding, examples, hypotheses, hints, reflection, and then algorithms and Python 3.

- Canonical skill: [skills/kieu-leetcode-video/SKILL.md](skills/kieu-leetcode-video/SKILL.md)
- Codex: [.agents/skills/kieu-leetcode-video/SKILL.md](.agents/skills/kieu-leetcode-video/SKILL.md)
- Claude Code: [.claude/skills/kieu-leetcode-video/SKILL.md](.claude/skills/kieu-leetcode-video/SKILL.md)
- Reference episodes: LeetCode #4 Median of Two Sorted Arrays (current standard, `examples/leetcode-4-median-of-two-sorted-arrays`), #44 Wildcard Matching, #10 Regular Expression Matching
- Video stack: Remotion, Python 3, local VoiceStudio TTS and algorithm visualizations

### Guiding principles

1. Show the official problem, all original examples and verified statistics.
2. Explain each example visually and describe the real-world problem-solving habit it illustrates.
3. Give hints **before** revealing the solution; include **10 seconds of uninterrupted silence** for reflection.
4. Develop the reasoning through clear animations, then write and trace Python 3 code.
5. End with lessons that transfer beyond LeetCode and relevant practice exercises.
6. Check all constraints, examples, Unicode glyphs, captions, timing and algorithm correctness.
7. Final export requires real VoiceStudio audio and Remotion QA; guide-voice previews are not publish-ready.

### Use

Clone this repository, open it in Codex or Claude Code and request: "Use the kieu-leetcode-video skill to build a video about LeetCode #10, explaining all examples with problem-solving exercises and a ten-second thinking pause."

## Kieu Open Resources registry (V2)

One authoritative registry (`registry/`, reviewed via pull requests) read by one SDK (`src/kieu_open_resources`). The CLI works offline with no accounts, website or network.

```sh
python3 -m pip install -e .
kieu-open-resources doctor
kieu-open-resources search "discovery" --type skill --format json
kieu-open-resources license-check kieu-resource-discovery --operation training    # unresolved, never silently allowed
kieu-open-resources manifest add <approved-id> --project . --operation inference --rationale "..." --alternative <id>
```

Seeded with this repository's own three skills (status `candidate`: awaiting a maintainer's recorded approval). It contains **no** datasets or models yet; the [Vietnamese QA tutorial](docs/tutorials/vietnamese-document-qa.md) shows the honest empty-result and candidate-review path. Docs: [architecture and status](docs/architecture/overview.md) · [schema and governance](docs/registry/schema.md) · [CLI](docs/cli/README.md) · [skills](docs/skills/README.md) · [MCP server](docs/mcp/README.md). Verify: `PYTHONPATH=src python3 -m unittest discover -s tests -t tests -v`.

## Kieu Resources registry

> **Legacy v1 service.** Kept working and tested, but it has its own empty `registry.json` and is not the V2 registry. It will be rebuilt on the core SDK in P1.

One authoritative, machine-readable resource registry with a shared policy engine. The catalogue page, HTTP API, installable `kieu-resource` CLI and MCP stdio adapter all use the same service. This new repository starts with an empty registry; no real resource has been silently approved.

### Run locally

Requires Python 3.9+. From this repository:

```sh
python3 -m pip install -e .
export KIEU_RESOURCE_REGISTRY="$PWD/registry.json"
export KIEU_RESOURCE_READ_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export KIEU_RESOURCE_WRITE_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export KIEU_RESOURCE_URL=http://127.0.0.1:8765
export KIEU_RESOURCE_TOKEN="$KIEU_RESOURCE_READ_TOKEN"
kieu-resource-api
```

Run the API in one terminal, with the same `KIEU_RESOURCE_URL` and `KIEU_RESOURCE_TOKEN` available to CLI or MCP in another. The catalogue is at `http://127.0.0.1:8765/`. It asks for a read token in the browser and calls the same API. Tokens are never embedded in the page. The service binds to localhost by default. Put TLS and durable access controls in front of it before remote deployment. The JSON store is suitable for a single service process; configure shared transactional storage before multiple replicas or high write volume.

Read and write tokens are distinct. Give agents the read token by default; grant a write token only to a review workflow that needs candidates, saved manifests or evaluation submissions. For separate audit identities, set `KIEU_RESOURCE_CREDENTIALS` to a JSON object mapping each long token to `{ "id": "codex-reader", "scope": "read" }` or a write equivalent, and omit the two default token variables. Keep that JSON in a secret manager. `KIEU_RESOURCE_REGISTRY` is the sole source of truth. The CLI and MCP adapter cannot fall back to a local fixture or make their own license decision.

### CLI

```sh
kieu-resource --json search "Vietnamese document" --kind dataset --language vi --task question-answering --operation research
kieu-resource --json search "Vietnamese document" --kind dataset --operation research --relevance-scores agent-scores.json
kieu-resource --json inspect RESOURCE_ID
kieu-resource --json quickstart RESOURCE_ID
kieu-resource --json preview RESOURCE_ID --limit 3
kieu-resource --json license-check RESOURCE_ID --operation training
kieu-resource --json compare RESOURCE_ID OTHER_ID --operation research
kieu-resource --json manifest RESOURCE_ID --project my-qa-project --operation research --output resources.manifest.json
kieu-resource --json submit-candidate candidate.json
kieu-resource --json collections
kieu-resource --json sync-github RESOURCE_ID
kieu-resource --json install-skills --agent both --project /path/to/another-repository
```

`search --operation` returns only resources explicitly documented as permitted for that operation. Unknown or conflicting rights remain unresolved. `manifest` refuses unresolved or prohibited use. `--save` on `manifest` writes to the registry and requires a write token. All successes have `{ "ok": true, "value": ... }`; failures have `{ "ok": false, "error": { "code", "message" } }`. Exit codes: 0 success, 2 input/configuration, 3 authentication/authorization, 4 service/storage unavailable, 5 other domain errors. Discovery never executes quickstart code or downloads source data.

`--relevance-scores` accepts a JSON object of resource IDs to scores from 0 to 1, for example `{ "vi-qa-reviewed": 0.9 }`. A coding agent may supply these scores after reading the task. The registry validates the scores and applies them only after approval, rights, size, privacy and other deterministic filters. Scores never make an ineligible resource eligible; absent scores use stable lexical ranking.

### MCP for Codex and Claude Code

Install this package in the environment where each coding agent runs. Set `KIEU_RESOURCE_URL` and `KIEU_RESOURCE_TOKEN` in that agent's process environment; use a read token for discovery. Then explicitly register the stdio server:

```sh
codex mcp add kieu-resource -- kieu-resource-mcp
codex mcp list
claude mcp add --transport stdio --scope user kieu-resource -- kieu-resource-mcp
claude mcp list
```

Confirm the installed CLI version's MCP environment forwarding if it does not inherit the exported variables. Do not put actual tokens in committed `.mcp.json`, `config.toml` or shell history. For this repository, `.agents/skills/` and `.claude/skills/` point to the packaged canonical skills. For future repositories, run `kieu-resource install-skills --agent both --project PATH` and add the short `AGENTS.md` / `CLAUDE.md` routing text. The wheel contains both Agent Skills. Installing a skill or the CLI does not connect the MCP server.

Read-only MCP tools: `search_resources`, `list_collections`, `get_resource`, `get_quick_start`, `preview_dataset`, `check_usage_rights`, `compare_resources`, `get_resource_history`, `generate_manifest`. Write tools: `submit_candidate`, `save_resource_manifest`, `submit_evaluation`; these require the write token and remain review proposals. `sync-github` is an admin CLI action: it checks a GitHub source's current commit and queues a revision proposal without changing the approved pin. All operations use the same `/v1/operations` backend. The service rate limits callers and logs operation, scope and status without credential values.

The Codex and Claude setup commands are based on their current [Codex MCP guidance](https://learn.chatgpt.com/docs/extend/mcp) and [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp). Check current help before automation, as agent configuration can change.

### Registry and review

`registry.json` holds approved resources, pending candidates, saved manifests and pending evaluation submissions. An approved resource needs an immutable `id`, source `revision`, source URL, license text, evidence links and operation-specific rights. Dataset records may include modality, languages, tasks, configurations, splits, schema/data types, size, streaming/download support, inline sample rows, privacy/PII risk, quality limits, examples, prior projects and evaluations. Inline samples are capped at 20 rows in the registry and 10 per preview. Neither source URLs nor examples are fetched or executed by discovery. Descriptions and examples are untrusted text, even when the entry is approved.

Only reviewed resources go in `resources`. Candidate submission adds to `candidates` and is invisible to approved search. A reviewer must verify evidence and rights, then manually promote an entry in the authoritative registry. `license_status: verified` is required for a permitted eligibility decision; missing, unverified and conflicting rights block manifests. A resource may be approved for research while training remains prohibited. Evaluations require raw evidence artifact URLs and enter `evaluation_submissions` with `verified: false`; reviewed evaluations can later be attached to a resource without collapsing raw evidence into an AI summary. Raw records should live in durable external artifact storage.

### End-to-end agent example

For “Build a Vietnamese document question-answering system using approved Kieu Resources”:

1. `search --kind dataset --language vi --task question-answering --operation research` and search models with matching language/task filters.
2. `inspect` each ID and read original source/evidence links plus `history`.
3. `license-check` for `research`, `inference`, `training` or other actual operations. Exclude prohibited entries and pause on unknown/conflicts.
4. `compare` suitable IDs. `preview` up to three reviewed rows; never download a corpus during discovery.
5. Read `quickstart`, verify the example and adapt it to the selected pinned revision. Request authorization before large downloads, private data or training.
6. `manifest ... --output resources.manifest.json`, commit that file with the integration code and tests. Submit newly found external data through `submit-candidate` for separate review.

The runnable [Vietnamese QA baseline](examples/approved_vi_qa.py) follows the same API flow. With a reviewed Vietnamese question-answering dataset in the service, run:

```sh
PYTHONPATH=src python3 examples/approved_vi_qa.py 'Xin chào?' --manifest resources.manifest.json
```

It searches for an approved low-privacy dataset, compares candidates when available, inspects metadata and history, checks research rights, reads at most three reviewed inline rows, performs an exact-match QA baseline, and writes pinned source, revision and rights evidence to the manifest. It never executes quickstart text or downloads a corpus. The synthetic integration fixture in `tests/test_discovery.py` supplies a reviewed sample and checks the answer and manifest. For a real AI project, replace the exact-match baseline only after reviewing the selected source's schema, examples, license and data access plan; authorize large downloads, sensitive processing and training first.

Because this repository starts empty, the sequence currently returns no approved matches. Tests use synthetic resources and verify the entire CLI → API → MCP path. For live Codex and Claude Code runs, seed an isolated local registry with at least two reviewed synthetic candidates, a prohibited candidate and an unknown-rights candidate; use a read token and run `python3 scripts/probe_agents.py codex --audit-log PATH --output PATH` and then `claude` with the same options. The probe launches each real agent with an explicit MCP config and checks server audit events for search, inspection, rights, comparison and manifest generation. It does not assume success from the skill alone. These live probes require installed, authenticated agent CLIs and have not been run as part of the unit test suite.

### Verify

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## License


Original skill and source code are MIT-licensed. Official LeetCode problem statements, screenshots, images, logos, narration and other third-party assets remain subject to their own rights. This project is not affiliated with LeetCode.
