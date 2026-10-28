"""CandidateSubmission and ReviewWorkflow.

Submissions only create ``registry/candidates/<id>.json`` with status
``candidate``. They never touch ``registry/resources``. Promotion to the
authoritative registry is a reviewed pull request; ``ReviewWorkflow`` applies
an explicit, evidenced status transition to an existing authoritative entry and
appends to an audit trail.
"""

import json
from datetime import date
from pathlib import Path

from . import sanitize
from .errors import KieuError
from .registry import atomic_write_json, read_json_file
from .schema import (ID_RE, SCHEMA_VERSION, TYPE_DIRS, can_transition, is_date, validate_resource)

SUBMISSION_KEYS = ("submitted_by", "use_cases", "known_risks", "submission_provenance")


class CandidateSubmission:
    def __init__(self, registry):
        self.registry = registry

    def normalize(self, data, today=None):
        if not isinstance(data, dict):
            raise KieuError("INVALID_INPUT", "candidate must be a JSON object")
        today = (today or date.today()).isoformat()
        res = dict(data)
        sub = res.pop("submission", {}) or {}
        if not isinstance(sub, dict):
            raise KieuError("INVALID_INPUT", "submission must be an object")
        requested = (res.get("approval") or {}).get("status")
        if requested not in (None, "draft", "candidate"):
            raise KieuError("POLICY_BLOCKED", "candidates cannot arrive as '%s'; approval is granted only by explicit review" % requested)
        res["approval"] = {"status": "candidate", "history": []}
        res.setdefault("schema_version", SCHEMA_VERSION)
        res.setdefault("dates", {})
        if isinstance(res["dates"], dict):
            res["dates"].setdefault("added", today)
        res.setdefault("usage_rights", {})
        res["validation"] = {"status": "not_run"}
        res.setdefault("license", {"id": "unknown", "status": "unknown", "evidence": []})
        res["license"].setdefault("evidence", [])
        return res, sub

    def submit(self, data, today=None):
        res, sub = self.normalize(data, today)
        issues = [i for i in validate_resource(res) if i["severity"] == "error"]
        if issues:
            raise KieuError("INVALID_INPUT", "candidate failed validation: %s %s" % (issues[0]["path"], issues[0]["message"]), {"issues": issues})
        for k in ("submitted_by", "use_cases", "known_risks"):
            if not sub.get(k):
                raise KieuError("INVALID_INPUT", "submission.%s is required (who proposed it, why, and known risks)" % k)
        for k in sub:
            if k not in SUBMISSION_KEYS:
                raise KieuError("INVALID_INPUT", "unknown submission field '%s'" % k)
        rid = res["id"]
        if rid in self.registry.load():
            raise KieuError("CONFLICT", "id already exists in the authoritative registry: %s" % rid)
        record = {"submission": dict(sub, submitted_on=(today or date.today()).isoformat(),
                                     injection_flags=sanitize.scan_resource(res)),
                  "resource": res}
        path = self.registry.root / "candidates" / (rid + ".json")
        atomic_write_json(path, record, exclusive=True)
        return {"id": rid, "status": "candidate", "path": path.relative_to(self.registry.root).as_posix(),
                "injection_flags": record["submission"]["injection_flags"],
                "next_step": "A maintainer reviews this file and promotes it by pull request. It is invisible to approved search."}

    def list(self):
        d = self.registry.root / "candidates"
        return [read_json_file(f, self.registry.root) for f in sorted(d.glob("*.json"))] if d.is_dir() else []


class ReviewWorkflow:
    def __init__(self, registry):
        self.registry = registry

    def apply(self, resource_id, to_status, reviewer, evidence, note="", confirm=False, today=None):
        if not confirm:
            raise KieuError("WRITE_REFUSED", "review changes registry state; pass --confirm to proceed")
        r = json.loads(json.dumps(self.registry.get(resource_id)))
        old = r["approval"]["status"]
        if not can_transition(old, to_status):
            raise KieuError("INVALID_TRANSITION", "unsupported transition %s -> %s" % (old, to_status))
        if not reviewer or not isinstance(reviewer, str):
            raise KieuError("INVALID_INPUT", "reviewer is required")
        if not evidence:
            raise KieuError("INVALID_INPUT", "documented evidence is required for every review decision")
        today = (today or date.today()).isoformat()
        entry = {"from": old, "to": to_status, "date": today, "reviewer": reviewer, "evidence": evidence}
        if note:
            entry["note"] = note
        r["approval"]["history"].append(entry)
        r["approval"]["status"] = to_status
        issues = [i for i in validate_resource(r) if i["severity"] == "error"]
        if issues:
            raise KieuError("POLICY_BLOCKED", "transition would leave an invalid resource: %s %s" % (issues[0]["path"], issues[0]["message"]), {"issues": issues})
        atomic_write_json(self.registry.resource_path(r), r)
        audit = self.registry.root / "reviews" / (resource_id + ".jsonl")
        audit.parent.mkdir(parents=True, exist_ok=True)
        with open(audit, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(entry, resource_id=resource_id), ensure_ascii=False) + "\n")
        return {"id": resource_id, "from": old, "to": to_status, "reviewer": reviewer, "audit_log": audit.relative_to(self.registry.root).as_posix()}
