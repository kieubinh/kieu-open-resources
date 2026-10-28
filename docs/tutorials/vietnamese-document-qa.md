# Tutorial: discovering resources for a Vietnamese document QA system

Run it yourself: `examples/vietnamese-document-qa/run_demo.sh` (works on a temporary copy of the registry).

Real output from the current registry:

```
$ kieu-open-resources search "vietnamese document" --type dataset --task question-answering --language vi --status approved
0 match(es), showing 0
$ kieu-open-resources search "vietnamese" --type model --language vi --status approved
0 match(es), showing 0
$ kieu-open-resources submit-candidate examples/vietnamese-document-qa/candidate.example.json
{"id": "example-vi-docqa-dataset", "status": "candidate", "path": "candidates/example-vi-docqa-dataset.json", ...}
$ kieu-open-resources search vietnamese --type dataset --status approved
0 match(es), showing 0
$ kieu-open-resources manifest add example-vi-docqa-dataset --project .
error [NOT_FOUND]: resource not found: example-vi-docqa-dataset      (exit 4)
```

**What this demonstrates, and what it does not.** The registry honestly holds no approved Vietnamese QA dataset or model, so the correct outcome is: report the empty result, search externally, and submit what you find as a *candidate*. A candidate is invisible to approved search and cannot be put in a manifest. Steps 5–11 of the full scenario (preview, license comparison of real alternatives, integration code, evaluation records) are exercised against synthetic fixtures in `tests/integration/test_cli.py::ApprovedFlowTest`, not against real datasets. No live Codex or Claude Code run has been performed.

Once a maintainer approves a real entry the flow is: `search … --status approved` → `inspect` → `license-check --operation training|fine-tuning|inference` → `compare` → `preview --limit 3` → `quickstart` → `manifest add … --rationale … --alternative …` → commit `kieu-resources.lock.json`.
