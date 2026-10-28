"""EvaluationRepository and ResourceHistory.

Four kinds of evidence are kept apart: raw evidence files (referenced by
checksum), structured metadata (the record), human review (``verification``)
and AI summaries (``ai_summary``). An AI summary can never be verified, and a
record is only ``verified`` with a named human reviewer plus checksummed raw
evidence.
"""

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from .errors import KieuError
from .registry import atomic_write_json, read_json_file
from .schema import ID_RE, SHA256_RE, _Check, is_date, is_safe_relpath

VERIFICATION_STATES = ("unverified", "verified", "rejected")
EVAL_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,95}$")
REQUIRED_OBJECTS = ("configuration", "environment", "hardware", "metrics")


def validate_evaluation(rec):
    c = _Check()
    if not isinstance(rec, dict):
        c.error("$", "evaluation must be an object")
        return c.issues
    eid = c.string(rec, "id", "$", 96)
    if eid and not EVAL_ID_RE.match(eid):
        c.error("$.id", "must match " + EVAL_ID_RE.pattern)
    rid = c.string(rec, "resource_id", "$", 64)
    if rid and not ID_RE.match(rid):
        c.error("$.resource_id", "invalid resource id")
    c.string(rec, "resource_revision", "$", 128)
    ts = c.string(rec, "timestamp", "$", 40)
    if ts:
        try:
            datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            c.error("$.timestamp", "must be an ISO 8601 timestamp")
    c.string(rec, "project", "$", 200)
    c.string(rec, "task", "$", 500)
    c.string(rec, "methodology", "$", 4000)
    for key in REQUIRED_OBJECTS:
        c.obj(rec, key, "$")
    metrics = rec.get("metrics", {})
    if isinstance(metrics, dict):
        if not metrics:
            c.error("$.metrics", "must contain at least one measured metric")
        for k, v in metrics.items():
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                c.error("$.metrics." + k, "must be a number")
    for key in ("quality_findings", "known_failures"):
        c.strings(rec, key, "$")
    ev = rec.get("raw_evidence", [])
    if not isinstance(ev, list):
        c.error("$.raw_evidence", "must be a list")
        ev = []
    for i, e in enumerate(ev):
        p = "$.raw_evidence[%d]" % i
        if not isinstance(e, dict):
            c.error(p, "must be an object")
            continue
        if ("path" in e) == ("url" in e):
            c.error(p, "needs exactly one of path or url")
        elif "path" in e and not is_safe_relpath(e["path"]):
            c.error(p + ".path", "must be a safe relative path")
        elif "url" in e:
            c.url(e["url"], p + ".url")
        if not isinstance(e.get("sha256"), str) or not SHA256_RE.match(e["sha256"]):
            c.error(p + ".sha256", "must be a lowercase sha256 hex digest")
    ver = c.obj(rec, "verification", "$")
    state = c.choice(ver, "status", "$.verification", VERIFICATION_STATES) if ver else None
    if state == "verified":
        if not ver.get("reviewer"):
            c.error("$.verification.reviewer", "verified records require a human reviewer")
        if not is_date(ver.get("reviewed_at")):
            c.error("$.verification.reviewed_at", "verified records require a review date")
        if not ev:
            c.error("$.raw_evidence", "verified records require checksummed raw evidence")
    summary = rec.get("ai_summary")
    if summary is not None:
        if not isinstance(summary, dict) or not isinstance(summary.get("text"), str):
            c.error("$.ai_summary", "must be an object with text")
        elif summary.get("verified"):
            c.error("$.ai_summary.verified", "AI-generated summaries can never be marked verified")
    return c.issues


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class EvaluationRepository:
    def __init__(self, registry):
        self.registry = registry

    def _dir(self, resource_id):
        if not ID_RE.match(resource_id):
            raise KieuError("INVALID_INPUT", "invalid resource id")
        return self.registry.root / "evaluations" / resource_id

    def list(self, resource_id, include_unverified=True):
        d = self._dir(resource_id)
        out = []
        if d.is_dir():
            for f in sorted(d.glob("*.json")):
                rec = read_json_file(f, self.registry.root)
                issues = [i for i in validate_evaluation(rec) if i["severity"] == "error"]
                if issues:
                    raise KieuError("REGISTRY_INVALID", "invalid evaluation %s: %s" % (f.name, issues[0]["message"]))
                if include_unverified or rec["verification"]["status"] == "verified":
                    out.append(rec)
        return out

    def verify_evidence(self, record):
        """Check local raw-evidence files against recorded checksums."""
        base = self._dir(record["resource_id"]).resolve()
        results = []
        for e in record.get("raw_evidence", []):
            if "path" not in e:
                results.append({"ref": e["url"], "status": "remote-not-checked"})
                continue
            p = (base / e["path"]).resolve()
            if not p.is_relative_to(base) or not p.is_file():
                results.append({"ref": e["path"], "status": "missing"})
            else:
                results.append({"ref": e["path"], "status": "ok" if sha256_file(p) == e["sha256"] else "checksum-mismatch"})
        return results

    def submit(self, record):
        """Store an evaluation as unverified. Verification is a separate, reviewed edit."""
        rec = dict(record)
        ver = rec.get("verification") or {}
        if ver.get("status") == "verified":
            raise KieuError("POLICY_BLOCKED", "submissions are stored unverified; verification requires a reviewed change")
        rec["verification"] = {"status": "unverified"}
        issues = [i for i in validate_evaluation(rec) if i["severity"] == "error"]
        if issues:
            raise KieuError("INVALID_INPUT", "invalid evaluation: %s %s" % (issues[0]["path"], issues[0]["message"]), {"issues": issues})
        res = self.registry.get(rec["resource_id"])
        if rec["resource_revision"] != res["source"]["revision"] and rec["resource_revision"] not in [r.get("revision") for r in res.get("revisions", [])]:
            raise KieuError("INVALID_INPUT", "resource_revision does not match any known revision of the resource")
        path = self._dir(rec["resource_id"]) / (rec["id"] + ".json")
        atomic_write_json(path, rec, exclusive=True)
        return {"id": rec["id"], "resource_id": rec["resource_id"], "status": "unverified", "path": path.relative_to(self.registry.root).as_posix()}


class ResourceHistory:
    def __init__(self, registry):
        self.registry = registry
        self.evaluations = EvaluationRepository(registry)

    def get(self, resource_id):
        r = self.registry.get(resource_id)
        evals = self.evaluations.list(resource_id)
        return {
            "id": r["id"],
            "current_revision": r["source"]["revision"],
            "revisions": r.get("revisions", []),
            "approval_history": r["approval"].get("history", []),
            "evaluations": [{"id": e["id"], "timestamp": e["timestamp"], "project": e["project"], "task": e["task"],
                             "resource_revision": e["resource_revision"], "metrics": e["metrics"],
                             "verification": e["verification"]["status"]} for e in evals],
            "evaluation_note": "Unverified evaluations are leads, not evidence of quality.",
        }
