# Registry schema and governance

One JSON file per resource: `registry/resources/<type-dir>/<id>.json` (`datasets models frameworks tools skills agents templates assets benchmarks`). Filename must equal `id`; directory must match `type`. Validation lives in `schema.py` and is the only definition.

## Fields (schema_version 1)

| Group | Fields |
|---|---|
| Identity | `id` (`^[a-z0-9][a-z0-9._-]{1,63}$`), `name`, `description`, `type` |
| Discovery | `categories`, `tags`, `keywords`, `tasks`, `languages`, `platforms`, `runtimes`, `projects`, `related` |
| Source | `source.{url (https), provider, repository, revision, revision_type: commit\|tag\|version\|snapshot}`, `revisions[]` (last must equal `source.revision`) |
| Dates / ownership | `dates.added`, `dates.last_verified`, `maintainer`, `provenance` |
| Docs | `documentation[]`, `quickstart[{title, steps, verified, evidence}]`, `requirements{install, access, integration_difficulty}` |
| Rights | `license.{id, status: verified\|unverified\|unknown, evidence[], conflicts[]}`, `usage_rights{operation: permitted\|conditional\|prohibited\|unknown}`, `restrictions[]` |
| Governance | `approval.{status, history[]}`, `validation.status`, `evaluation_refs[]`, `limitations[]` |
| Type extensions | `details` — checked for `dataset` (modalities, configurations, splits, schema, size_bytes, download, streaming, access, pii_risk, preview, quality_findings, prior_projects, benchmark_results) and `model` (modalities, parameters_b, context_length, hardware); other types are free-form objects |

Operations: `use research inference commercial-use redistribution modification training fine-tuning`.

## Lifecycle

```
draft → candidate → under_review → approved ⇄ restricted
                         ↓              ↓
                     rejected       deprecated (terminal)
```
Allowed: draft→{candidate,rejected}; candidate→{under_review,rejected}; under_review→{approved,restricted,rejected,candidate}; approved→{restricted,deprecated,under_review}; restricted→{under_review,deprecated,rejected}; rejected→candidate. Every step needs a history entry with `reviewer`, `date` and documented `evidence`; history must be contiguous and end at the current status. Approval additionally requires a verified license with evidence and a `last_verified` date. Conflicting license evidence (an evidence `license_id` differing from `license.id`, or listed `license.conflicts`) always resolves to *unresolved*.

## Changing the registry

* Agents and contributors: `submit-candidate` writes only `registry/candidates/<id>.json` with status `candidate`; text is scanned for prompt-injection and the flags are stored for the reviewer.
* Maintainers: promote by pull request (move the file into `resources/`, add review history), or use `kieu-open-resources review <id> --to <status> --reviewer … --evidence-ref … --confirm` for transitions on existing entries; each decision is appended to `registry/reviews/<id>.jsonl`.
* The seeded `kieu-*` skill entries are `candidate`: they describe this repository's own skills with MIT evidence from `LICENSE`, but no human has recorded an approval review. Their `source.revision` pins the commit at seeding time; update it when the skill changes.
