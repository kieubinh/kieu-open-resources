"""kieu-open-resources command line interface.

A thin layer over the Core SDK. No network access is performed by any command.
JSON output is a versioned envelope: {"contract", "ok", "command", "data"|"error"}.
Exit codes: 0 ok, 1 unexpected, 2 usage/input, 3 registry missing/invalid,
4 not found, 5 policy blocked/unsupported, 6 conflict/refused write.
"""

import argparse
import json
import sys
from pathlib import Path

from . import CONTRACT, __version__
from .candidates import CandidateSubmission, ReviewWorkflow
from .discovery import ResourceDiscovery
from .errors import EXIT_OK, EXIT_UNEXPECTED, EXIT_USAGE, KieuError
from .evaluation import EvaluationRepository, ResourceHistory
from .licensing import ResourceLicenseChecker
from .manifest import ResourceManifest
from .registry import MAX_FILE_BYTES, ResourceRegistry
from .schema import OPERATIONS, RESOURCE_TYPES, STATUSES
from .search import ResourceSearch


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise KieuError("INVALID_INPUT", message)


def _common():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("--registry", help="registry directory (default: $KIEU_OPEN_RESOURCES_REGISTRY or nearest ./registry)")
    p.add_argument("--offline", action="store_true", help="accepted for clarity; this CLI never uses the network")
    return p


def build_parser():
    common = _common()
    p = _Parser(prog="kieu-open-resources", description="Discover, evaluate and record trusted resources.")
    p.add_argument("--version", action="version", version="kieu-open-resources " + __version__)
    sub = p.add_subparsers(dest="command", required=True, parser_class=_Parser)

    s = sub.add_parser("search", parents=[common], help="deterministic resource search")
    s.add_argument("query", nargs="?", default="")
    s.add_argument("--type", choices=RESOURCE_TYPES)
    s.add_argument("--category")
    s.add_argument("--task")
    s.add_argument("--language")
    s.add_argument("--status", action="append", choices=STATUSES, help="repeatable; default excludes rejected/deprecated")
    s.add_argument("--operation", choices=OPERATIONS, help="keep only resources whose rights permit this operation")
    s.add_argument("--commercial-use", action="store_true")
    s.add_argument("--modality")
    s.add_argument("--runtime")
    s.add_argument("--provider")
    s.add_argument("--project")
    s.add_argument("--max-params-b", type=float)
    s.add_argument("--max-size-bytes", type=int)
    s.add_argument("--verified-within-days", type=int)
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--explain-excluded", action="store_true")
    s.add_argument("--relevance-scores", type=Path, help="JSON {id: 0..1} from an agent; applies only after hard filters")

    for name, helptext in (("inspect", "full metadata, provenance and evidence"), ("quickstart", "verified integration steps (never executed)"),
                           ("history", "revisions, approvals and evaluations")):
        c = sub.add_parser(name, parents=[common], help=helptext)
        c.add_argument("resource_id")
    pv = sub.add_parser("preview", parents=[common], help="bounded sample of a permitted dataset")
    pv.add_argument("resource_id")
    pv.add_argument("--limit", type=int, default=3)
    lc = sub.add_parser("license-check", parents=[common], help="usage rights for a specific operation")
    lc.add_argument("resource_id")
    lc.add_argument("--operation", required=True, choices=OPERATIONS)
    lc.add_argument("--commercial-use", action="store_true")
    cp = sub.add_parser("compare", parents=[common], help="structured comparison")
    cp.add_argument("resource_ids", nargs="+")
    cp.add_argument("--operation", choices=OPERATIONS)
    cp.add_argument("--commercial-use", action="store_true")
    cp.add_argument("--task")
    cp.add_argument("--language")

    m = sub.add_parser("manifest", help="project resource manifest (kieu-resources.lock.json)")
    msub = m.add_subparsers(dest="action", required=True, parser_class=_Parser)
    ma = msub.add_parser("add", parents=[common])
    ma.add_argument("resource_id")
    ma.add_argument("--project", default=".")
    ma.add_argument("--operation", action="append", choices=OPERATIONS, help="intended operation(s); default: use")
    ma.add_argument("--commercial-use", action="store_true")
    ma.add_argument("--rationale")
    ma.add_argument("--alternative", action="append", default=[])
    ma.add_argument("--integration-method")
    ma.add_argument("--environment")
    ma.add_argument("--artifact-sha256")
    ma.add_argument("--evaluation", action="append", default=[])
    ma.add_argument("--allow-unapproved", action="store_true", help="allow candidate/under_review resources; recorded in the manifest")
    for n in ("show", "validate"):
        x = msub.add_parser(n, parents=[common])
        x.add_argument("--project", default=".")
    mr = msub.add_parser("remove", parents=[common])
    mr.add_argument("resource_id")
    mr.add_argument("--project", default=".")

    sc = sub.add_parser("submit-candidate", parents=[common], help="propose a resource for review (writes registry/candidates only)")
    sc.add_argument("file")
    se = sub.add_parser("submit-evaluation", parents=[common], help="store an unverified evaluation record")
    se.add_argument("file")
    rv = sub.add_parser("review", parents=[common], help="PRIVILEGED: record an explicit review decision on an authoritative entry")
    rv.add_argument("resource_id")
    rv.add_argument("--to", required=True, choices=STATUSES)
    rv.add_argument("--reviewer", required=True)
    rv.add_argument("--evidence-ref", action="append", default=[], help="https URL or registry-relative path (repeatable)")
    rv.add_argument("--claim", default="", help="what the evidence shows")
    rv.add_argument("--note", default="")
    rv.add_argument("--confirm", action="store_true")

    sub.add_parser("validate", parents=[common], help="validate the whole registry")
    sub.add_parser("doctor", parents=[common], help="check configuration")
    ik = sub.add_parser("install-skill", parents=[common], help="copy the packaged discovery skill into another repository")
    ik.add_argument("--project", default=".")
    ik.add_argument("--agent", choices=("codex", "claude", "both"), default="both")
    return p


def _read_input_json(path):
    f = Path(path)
    try:
        if f.stat().st_size > MAX_FILE_BYTES:
            raise KieuError("INVALID_INPUT", "input file too large")
        return json.loads(f.read_text(encoding="utf-8"))
    except OSError as exc:
        raise KieuError("INVALID_INPUT", "cannot read %s: %s" % (path, exc)) from exc
    except ValueError as exc:
        raise KieuError("INVALID_INPUT", "%s is not valid JSON: %s" % (path, exc)) from exc


def skills_dir():
    return Path(__file__).parent / "skills"


def install_skill(project, agent):
    src = skills_dir() / "kieu-resource-discovery"
    if not (src / "SKILL.md").is_file():
        raise KieuError("NOT_FOUND", "packaged skill not found")
    proj = Path(project)
    if not proj.is_dir():
        raise KieuError("INVALID_INPUT", "project directory does not exist")
    roots = {"codex": [".agents"], "claude": [".claude"], "both": [".agents", ".claude"]}[agent]
    files = [f for f in sorted(src.rglob("*")) if f.is_file()]
    plan = []
    for root in roots:
        for f in files:
            target = proj / root / "skills" / "kieu-resource-discovery" / f.relative_to(src)
            if target.exists() and target.read_bytes() != f.read_bytes():
                raise KieuError("CONFLICT", "refusing to overwrite differing file: %s" % target)
            plan.append((f, target))
    written = []
    for f, target in plan:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(f.read_bytes())
            written.append(str(target))
    return {"installed": written, "note": "Copies are generated from the packaged canonical skill; re-run after upgrading the package."}


def run(args):
    c = args.command
    if c == "install-skill":
        return install_skill(args.project, args.agent)
    registry = ResourceRegistry.locate(args.registry)
    if c == "doctor":
        return doctor(registry)
    if c == "validate":
        return registry.validate()
    if c == "search":
        scores = _read_input_json(args.relevance_scores) if args.relevance_scores else None
        return ResourceSearch(registry).search(
            query=args.query, type=args.type, category=args.category, task=args.task, language=args.language,
            statuses=args.status, operation=args.operation, commercial_use=args.commercial_use, modality=args.modality,
            runtime=args.runtime, provider=args.provider, max_params_b=args.max_params_b, max_size_bytes=args.max_size_bytes,
            verified_within_days=args.verified_within_days, project=args.project, limit=args.limit,
            include_excluded=args.explain_excluded, relevance_scores=scores)
    disc = ResourceDiscovery(registry)
    if c == "inspect":
        return disc.inspect(args.resource_id)
    if c == "quickstart":
        return disc.quickstart(args.resource_id)
    if c == "preview":
        return disc.preview(args.resource_id, args.limit)
    if c == "history":
        return ResourceHistory(registry).get(args.resource_id)
    if c == "license-check":
        return ResourceLicenseChecker().check(registry.get(args.resource_id), args.operation, args.commercial_use)
    if c == "compare":
        return disc.compare(args.resource_ids, args.operation, args.commercial_use, args.task, args.language)
    if c == "manifest":
        mf = ResourceManifest(registry, args.project)
        if args.action == "add":
            return mf.add(args.resource_id, tuple(args.operation or ["use"]), args.commercial_use, args.rationale, args.alternative,
                          args.integration_method, args.environment, args.artifact_sha256, args.evaluation, args.allow_unapproved)
        if args.action == "remove":
            return mf.remove(args.resource_id)
        return mf.show() if args.action == "show" else mf.validate()
    if c == "submit-candidate":
        return CandidateSubmission(registry).submit(_read_input_json(args.file))
    if c == "submit-evaluation":
        return EvaluationRepository(registry).submit(_read_input_json(args.file))
    if c == "review":
        evidence = [({"url": r} if r.startswith("https://") else {"path": r}) for r in args.evidence_ref]
        for e in evidence:
            e["claim"] = args.claim or "review evidence"
        return ReviewWorkflow(registry).apply(args.resource_id, args.to, args.reviewer, evidence, args.note, args.confirm)
    raise KieuError("INVALID_INPUT", "unknown command")


def doctor(registry):
    checks = [{"check": "python", "ok": sys.version_info >= (3, 9), "detail": sys.version.split()[0]},
              {"check": "registry-root", "ok": True, "detail": str(registry.root)}]
    report = registry.validate()
    checks.append({"check": "registry-valid", "ok": report["ok"], "detail": "%d resources, %d errors, %d warnings" % (
        report["resource_count"], len(report["errors"]), len(report["warnings"]))})
    checks.append({"check": "packaged-skill", "ok": (skills_dir() / "kieu-resource-discovery" / "SKILL.md").is_file(), "detail": str(skills_dir())})
    checks.append({"check": "network", "ok": True, "detail": "not used: all operations are local"})
    out = {"ok": all(x["ok"] for x in checks), "version": __version__, "checks": checks}
    if report["ok"]:
        out["counts"] = registry.counts()
    return out


# ---- rendering -------------------------------------------------------------

def render_text(command, data):
    if command == "search":
        lines = ["%d match(es), showing %d" % (data["total_matches"], len(data["results"]))]
        for r in data["results"]:
            lines.append("  %-34s %-10s %-12s score=%s  %s" % (r["id"], r["type"], r["status"], r["score"], r["name"]))
        for x in data.get("excluded", []):
            lines.append("  excluded %s: %s" % (x["id"], "; ".join(x["reasons"])))
        return "\n".join(lines)
    if command == "license-check":
        lines = ["%s -> %s for %s%s (approval: %s, usable: %s)" % (
            data["id"], data["decision"].upper(), data["operation"], " + commercial use" if data["commercial_use"] else "",
            data["approval_status"], data["usable"])]
        lines += ["  - " + r for r in data["reasons"]] + ["  restriction: " + r for r in data["restrictions"]]
        return "\n".join(lines)
    if command == "inspect":
        r = data["resource"]
        lines = ["%s  (%s)  %s" % (r["id"], r["type"], r["name"]), "  status:   %s" % r["approval"]["status"],
                 "  source:   %s @ %s" % (r["source"]["url"], r["source"]["revision"]),
                 "  license:  %s (%s)" % (r["license"]["id"], r["license"]["status"]),
                 "  verified: %s" % r["dates"].get("last_verified", "never"), "  " + r["description"]]
        if data["injection_flags"]:
            lines.append("  WARNING suspicious content flags: " + ", ".join(data["injection_flags"]))
        lines.append("  note: " + data["untrusted_content_notice"])
        return "\n".join(lines)
    if command == "validate":
        lines = ["%s: %d resources, %d errors, %d warnings" % ("OK" if data["ok"] else "INVALID", data["resource_count"], len(data["errors"]), len(data["warnings"]))]
        lines += ["  %s %s %s: %s" % (i["severity"].upper(), i["file"], i["path"], i["message"]) for i in data["errors"] + data["warnings"]]
        return "\n".join(lines)
    if command == "doctor":
        return "\n".join(["%s %-16s %s" % ("ok " if x["ok"] else "FAIL", x["check"], x["detail"]) for x in data["checks"]])
    return json.dumps(data, ensure_ascii=False, indent=2)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    fmt = "json" if "--format" in argv and argv[argv.index("--format") + 1:argv.index("--format") + 2] == ["json"] else "text"
    command = next((a for a in argv if not a.startswith("-")), "")
    try:
        args = build_parser().parse_args(argv)
        fmt, command = args.format if hasattr(args, "format") else fmt, args.command
        data = run(args)
        if fmt == "json":
            print(json.dumps({"contract": CONTRACT, "ok": True, "command": command, "data": data}, ensure_ascii=False))
        else:
            print(render_text(command, data))
        # validate/doctor/manifest validate report failure through the exit code
        failed = isinstance(data, dict) and data.get("ok") is False
        return 3 if failed and command in ("validate", "doctor") else 6 if failed else EXIT_OK
    except KieuError as exc:
        if fmt == "json":
            print(json.dumps({"contract": CONTRACT, "ok": False, "command": command, "error": exc.as_dict()}, ensure_ascii=False))
        else:
            print("error [%s]: %s" % (exc.code, exc.message), file=sys.stderr)
        return exc.exit_code
    except SystemExit as exc:  # argparse --help / --version
        return exc.code if isinstance(exc.code, int) else EXIT_OK
    except Exception as exc:  # pragma: no cover - defensive
        print("unexpected error: %s" % exc, file=sys.stderr)
        return EXIT_UNEXPECTED


if __name__ == "__main__":
    raise SystemExit(main())
