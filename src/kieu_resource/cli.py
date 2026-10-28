"""Installable kieu-resource command line interface."""

import argparse
import json
import sys
from pathlib import Path

from .client import call
from .registry import ResourceError


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ResourceError("INVALID_INPUT", message)


def parser():
    p = _Parser(prog="kieu-resource")
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("search")
    s.add_argument("query", nargs="?", default="")
    for name in ("kind", "language", "task", "modality", "collection", "configuration", "split", "operation", "max-privacy-risk"):
        s.add_argument("--" + name)
    s.add_argument("--streaming", action="store_true", default=None)
    s.add_argument("--max-size-bytes", type=int)
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--relevance-scores", type=Path, help="JSON map of agent relevance scores; eligibility filters still apply")
    for name in ("inspect", "quickstart", "preview", "license-check", "history"):
        cmd = sub.add_parser(name)
        cmd.add_argument("resource_id")
        if name == "preview":
            cmd.add_argument("--limit", type=int, default=3)
        if name == "license-check":
            cmd.add_argument("--operation", required=True)
    c = sub.add_parser("compare")
    c.add_argument("resource_ids", nargs="+")
    c.add_argument("--operation")
    m = sub.add_parser("manifest")
    m.add_argument("resource_ids", nargs="+")
    m.add_argument("--project", required=True)
    m.add_argument("--operation", required=True)
    m.add_argument("--output", help="write project manifest to this path")
    m.add_argument("--save", action="store_true", help="save manifest in registry; requires write credential")
    candidate = sub.add_parser("submit-candidate")
    candidate.add_argument("file", help="JSON resource proposal")
    sub.add_parser("collections")
    sync = sub.add_parser("sync-github")
    sync.add_argument("resource_id")
    install = sub.add_parser("install-skills", help="copy packaged skills into an agent project")
    install.add_argument("--agent", choices=("codex", "claude", "both"), default="both")
    install.add_argument("--project", type=Path, default=Path.cwd())
    return p


def install_skills(project, agent):
    source = Path(__file__).parent / "skills"
    targets = {"codex": ".agents", "claude": ".claude"}
    selected = targets if agent == "both" else {agent: targets[agent]}
    installed = []
    try:
        for folder in selected.values():
            for name in ("kieu-resource-discovery", "kieu-model-builder"):
                content = (source / name / "SKILL.md").read_bytes()
                target = Path(project) / folder / "skills" / name / "SKILL.md"
                if target.exists():
                    if target.read_bytes() != content:
                        raise ResourceError("CONFLICT", f"skill already exists with different content: {target}", 409)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
                installed.append(str(target))
    except OSError as exc:
        raise ResourceError("FILE_ERROR", f"cannot install skills: {exc}") from exc
    return {"installed": installed}


def run(args):
    c = args.command
    if c == "install-skills":
        return install_skills(args.project, args.agent)
    if c == "search":
        payload = {k: v for k, v in vars(args).items() if k in {"query", "kind", "language", "task", "modality", "collection", "configuration", "split", "streaming", "max_size_bytes", "max_privacy_risk", "operation", "limit"} and v is not None}
        if args.relevance_scores:
            try:
                payload["relevance_scores"] = json.loads(args.relevance_scores.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                raise ResourceError("INVALID_INPUT", f"relevance scores file: {exc}") from exc
        return call("search_resources", payload)
    if c == "collections":
        return call("list_collections", {})
    if c == "sync-github":
        return call("sync_github_source", {"resource_id": args.resource_id})
    if c in {"inspect", "quickstart", "preview", "license-check", "history"}:
        operation = {"inspect": "get_resource", "quickstart": "get_quick_start", "preview": "preview_dataset", "license-check": "check_usage_rights", "history": "get_resource_history"}[c]
        extra = {"limit": args.limit} if c == "preview" else {"operation": args.operation} if c == "license-check" else {}
        return call(operation, {"resource_id": args.resource_id, **extra})
    if c == "compare":
        return call("compare_resources", {"resource_ids": args.resource_ids, "operation": args.operation})
    if c == "manifest":
        result = call("generate_manifest", {"resource_ids": args.resource_ids, "project": args.project, "operation": args.operation})
        if args.save:
            result = call("save_resource_manifest", {"manifest": result})
        if args.output:
            Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    if c == "submit-candidate":
        try:
            resource = json.loads(Path(args.file).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ResourceError("INVALID_INPUT", f"candidate file: {exc}") from exc
        return call("submit_candidate", {"resource": resource})
    raise ResourceError("INVALID_INPUT", "unknown command")


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        result = run(args)
        print(json.dumps({"ok": True, "value": result}, ensure_ascii=False, indent=2 if not args.json else None))
        return 0
    except ResourceError as exc:
        print(json.dumps({"ok": False, "error": exc.as_dict()}, ensure_ascii=False), file=sys.stderr)
        return 2 if exc.code in {"CONFIG_REQUIRED", "INVALID_CONFIG", "INVALID_INPUT"} else 3 if exc.code in {"AUTH_REQUIRED", "FORBIDDEN"} else 4 if exc.code in {"SERVICE_UNAVAILABLE", "AUDIT_UNAVAILABLE", "CORRUPT_REGISTRY"} else 5


if __name__ == "__main__":
    raise SystemExit(main())
