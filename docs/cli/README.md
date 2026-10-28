# CLI reference: `kieu-open-resources`

Install: `pip install -e .` (Python ≥ 3.9, no third-party dependencies). Registry: `--registry PATH`, else `$KIEU_OPEN_RESOURCES_REGISTRY`, else the nearest `registry/` above the working directory. No command uses the network, so `--offline` is accepted but redundant.

| Command | Purpose | Writes |
|---|---|---|
| `search [QUERY] [--type --category --task --language --status* --operation --commercial-use --modality --runtime --provider --project --max-params-b --max-size-bytes --verified-within-days --limit --explain-excluded --relevance-scores FILE]` | deterministic filter + lexical score; `--explain-excluded` lists why others were dropped | – |
| `inspect ID` | full metadata, validation issues, injection flags, evaluation counts | – |
| `quickstart ID` | steps with `verified` and `risk_flags`; never executed | – |
| `preview ID [--limit 1-10]` | bounded reviewed sample; blocked unless approved, open access, not high-PII, preview enabled | – |
| `license-check ID --operation OP [--commercial-use]` | `permitted / conditional / unresolved / prohibited` plus `usable` (also requires approved) | – |
| `compare ID ID… [--operation --commercial-use --task --language]` | objective side-by-side; `ai_generated_judgments` is always empty | – |
| `history ID` | revisions, approval history, evaluations | – |
| `manifest add\|show\|validate\|remove` | project `kieu-resources.lock.json` | project dir only |
| `submit-candidate FILE` / `submit-evaluation FILE` | proposals (candidate / unverified) | `registry/candidates`, `registry/evaluations` |
| `review ID --to STATUS --reviewer … --evidence-ref … --claim … --confirm` | maintainer-only, evidenced transition | resource file + audit log |
| `validate`, `doctor` | registry validation, configuration check | – |
| `install-skill [--project --agent codex\|claude\|both]` | copy packaged discovery skill into another repo | `.agents/`, `.claude/` |

`--format json` gives `{"contract":"kieu-open-resources/v1","ok":…,"command":…,"data"|"error":{code,message}}`. Exit codes: 0 ok · 1 unexpected · 2 invalid input · 3 registry missing/invalid (also `validate`/`doctor` failure) · 4 not found · 5 policy blocked/unsupported · 6 conflict, refused write, or failed `manifest validate`.

`search` hides `rejected` and `deprecated` by default; use `--status approved` when you need selectable resources. `--relevance-scores` accepts `{id: 0..1}` from an agent: it re-orders results that already passed every hard filter and never adds one.
