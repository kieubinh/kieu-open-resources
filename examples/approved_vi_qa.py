"""Small retrieval baseline over reviewed inline samples, not a production corpus loader."""

import argparse
import json
import sys
from pathlib import Path

from kieu_resource.client import call
from kieu_resource.registry import ResourceError


def run(question, manifest_path):
    matches = call("search_resources", {
        "kind": "dataset", "language": "vi", "task": "question-answering",
        "operation": "research", "max_privacy_risk": "low", "limit": 10,
    })
    if not matches:
        raise ResourceError("NOT_FOUND", "no approved eligible Vietnamese QA dataset", 404)
    if len(matches) > 1:
        call("compare_resources", {"resource_ids": [item["id"] for item in matches[:10]], "operation": "research"})
    resource_id = matches[0]["id"]
    metadata = call("get_resource", {"resource_id": resource_id})
    call("get_resource_history", {"resource_id": resource_id})
    usage = call("check_usage_rights", {"resource_id": resource_id, "operation": "research"})
    if usage["decision"] != "permitted":
        raise ResourceError("RIGHTS_UNRESOLVED", "selected dataset is not eligible for research", 422)
    sample = call("preview_dataset", {"resource_id": resource_id, "limit": 3})
    manifest = call("generate_manifest", {"resource_ids": [resource_id], "project": "approved-vi-qa-baseline", "operation": "research"})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    answer = next((row.get("answer") for row in sample["rows"] if row.get("question", "").casefold() == question.casefold()), None)
    return {"answer": answer, "resource_id": resource_id, "revision": metadata["revision"], "manifest": str(manifest_path), "scope": "reviewed inline sample only"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--manifest", type=Path, default=Path("resources.manifest.json"))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.question, args.manifest), ensure_ascii=False))
        return 0
    except (ResourceError, OSError) as exc:
        error = exc.as_dict() if isinstance(exc, ResourceError) else {"code": "FILE_ERROR", "message": str(exc)}
        print(json.dumps({"ok": False, "error": error}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
