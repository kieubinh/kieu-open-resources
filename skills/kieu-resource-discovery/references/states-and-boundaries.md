# States, approval boundaries and exit codes

## Resource states an agent must keep apart

| State | Meaning | Evidence |
|---|---|---|
| discovered | appeared in a search result | search output |
| eligible | passed hard filters and `license-check` = `permitted` for the real operation | `license-check` JSON |
| approved | registry `approval.status` is `approved` after an evidenced review | `history` approval entries |
| selected | chosen for this project with a rationale | `kieu-resources.lock.json` entry |
| integrated | code or config actually uses the pinned revision | project diff and tests |
| evaluated | an evaluation record exists (`verified` only with human review + checksummed raw evidence) | `history` evaluations |

Approval and license eligibility are independent: an approved resource may still be unusable for training; a permitted license on a `candidate` is still only a lead.

## Lifecycle

`draft → candidate → under_review → approved | restricted | rejected`; `approved → restricted | deprecated | under_review`. Anything else is rejected by the validator.

## Operations needing explicit user approval

Downloads beyond the bounded preview, running unverified or risk-flagged quickstart steps, gated or authenticated sources, private data leaving the machine, paid/GPU jobs, training or fine-tuning, any registry-changing write.

## CLI exit codes

0 ok · 1 unexpected · 2 invalid input · 3 registry missing/invalid · 4 not found · 5 policy blocked / unsupported · 6 conflict or refused write.
JSON envelope: `{"contract":"kieu-open-resources/v1","ok":bool,"command":str,"data"|"error"}`.
