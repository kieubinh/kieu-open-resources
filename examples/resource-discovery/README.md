# Resource discovery quick tour

```sh
pip install -e .
kieu-open-resources doctor
kieu-open-resources search discovery --type skill --format json
kieu-open-resources inspect kieu-resource-discovery
kieu-open-resources license-check kieu-resource-discovery --operation training   # unresolved: rights unknown
kieu-open-resources compare kieu-resource-discovery kieu-leetcode-video --operation use
kieu-open-resources manifest add kieu-resource-discovery --project . --allow-unapproved --rationale "demo"
```
The seeded skills are `candidate`, so selecting them requires `--allow-unapproved` (recorded in the manifest). Remove the demo lock file afterwards: `kieu-open-resources manifest remove kieu-resource-discovery`.
