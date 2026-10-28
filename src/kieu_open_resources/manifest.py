"""ResourceManifest: project-level ``kieu-resources.lock.json``.

Writes are local to the project directory and never touch the registry.
"""

import json
import os
import tempfile
from datetime import date
from pathlib import Path

from . import __version__
from .errors import KieuError
from .licensing import ResourceLicenseChecker
from .schema import SHA256_RE, STATUSES

LOCK_NAME = "kieu-resources.lock.json"
BLOCKING_NOW = ("rejected", "deprecated", "restricted")


class ResourceManifest:
    def __init__(self, registry, project_dir):
        self.registry = registry
        self.licenses = ResourceLicenseChecker()
        p = Path(project_dir)
        if not p.is_dir():
            raise KieuError("INVALID_INPUT", "project directory does not exist: %s" % project_dir)
        self.project_dir = p.resolve()
        self.path = self.project_dir / LOCK_NAME

    def _safe_path(self):
        if self.path.is_symlink() and not self.path.resolve().is_relative_to(self.project_dir):
            raise KieuError("PATH_UNSAFE", "%s is a symlink leaving the project directory" % LOCK_NAME)

    def load(self):
        self._safe_path()
        if not self.path.exists():
            return {"schema_version": 1, "project": self.project_dir.name, "generated_by": "kieu-open-resources " + __version__, "resources": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise KieuError("INVALID_INPUT", "cannot parse %s: %s" % (LOCK_NAME, exc)) from exc
        if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("resources"), list):
            raise KieuError("INVALID_INPUT", "%s has an unsupported structure" % LOCK_NAME)
        return data

    def _write(self, data):
        self._safe_path()
        fd, tmp = tempfile.mkstemp(dir=str(self.project_dir), prefix=".lock-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, str(self.path))
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def add(self, resource_id, operations=("use",), commercial_use=False, rationale=None, alternatives=None,
            integration_method=None, environment=None, artifact_sha256=None, evaluations=None, allow_unapproved=False, today=None):
        r = self.registry.get(resource_id)
        status = r["approval"]["status"]
        if status != "approved" and not (allow_unapproved and status in ("candidate", "under_review", "draft")):
            raise KieuError("POLICY_BLOCKED", "resource status is '%s'; only approved resources can be selected%s" % (
                status, " (--allow-unapproved covers candidate/under_review/draft only)" if allow_unapproved else ""))
        if artifact_sha256 and not SHA256_RE.match(artifact_sha256):
            raise KieuError("INVALID_INPUT", "artifact_sha256 must be a lowercase sha256 hex digest")
        alternatives = list(alternatives or [])
        for alt in alternatives:
            self.registry.get(alt)
        decisions = []
        for op in operations:
            check = self.licenses.check(r, op, commercial_use)
            if check["decision"] != "permitted":
                raise KieuError("POLICY_BLOCKED", "%s is %s for %s: %s" % (resource_id, check["decision"], op, "; ".join(check["reasons"])),
                                {"license_check": check})
            decisions.append({"operation": op, "commercial_use": bool(commercial_use), "decision": check["decision"]})
        known_evals = {e["id"] for e in self._evals(resource_id)}
        for e in evaluations or []:
            if e not in known_evals:
                raise KieuError("INVALID_INPUT", "unknown evaluation id '%s' for %s" % (e, resource_id))
        entry = {
            "id": r["id"], "type": r["type"], "name": r["name"],
            "version": r["source"]["revision"], "revision_type": r["source"]["revision_type"],
            "source_url": r["source"]["url"],
            "license": {"id": r["license"]["id"], "status": r["license"]["status"]},
            "usage_restrictions": list(r.get("restrictions", [])),
            "intended_use": decisions,
            "approval_status_at_selection": status,
            "selection_rationale": rationale or "",
            "alternatives_considered": alternatives,
            "integration_method": integration_method or "",
            "expected_environment": environment or "",
            "artifact_sha256": artifact_sha256 or None,
            "date_verified": r["dates"].get("last_verified"),
            "evaluation_evidence": list(evaluations or []),
            "selected_at": (today or date.today()).isoformat(),
        }
        data = self.load()
        data["resources"] = sorted([x for x in data["resources"] if x.get("id") != resource_id] + [entry], key=lambda x: x["id"])
        self._write(data)
        warnings = [] if status == "approved" else ["selected resource is '%s', not approved; re-run validate after review" % status]
        return {"path": str(self.path), "entry": entry, "warnings": warnings}

    def remove(self, resource_id):
        data = self.load()
        before = len(data["resources"])
        data["resources"] = [x for x in data["resources"] if x.get("id") != resource_id]
        if len(data["resources"]) == before:
            raise KieuError("NOT_FOUND", "%s is not in the manifest" % resource_id)
        self._write(data)
        return {"path": str(self.path), "removed": resource_id}

    def show(self):
        return self.load()

    def validate(self):
        """Re-check every manifest entry against the current registry."""
        data = self.load()
        errors, warnings = [], []
        for e in data["resources"]:
            rid = e.get("id")
            try:
                r = self.registry.get(rid)
            except KieuError:
                errors.append({"id": rid, "message": "resource no longer exists in the registry"})
                continue
            if e.get("version") != r["source"]["revision"]:
                warnings.append({"id": rid, "message": "pinned version %s differs from registry revision %s" % (e.get("version"), r["source"]["revision"])})
            if (e.get("license") or {}).get("id") != r["license"]["id"]:
                errors.append({"id": rid, "message": "license changed from %s to %s" % ((e.get("license") or {}).get("id"), r["license"]["id"])})
            status = r["approval"]["status"]
            if status in BLOCKING_NOW:
                errors.append({"id": rid, "message": "resource is now '%s'" % status})
            elif status != "approved":
                warnings.append({"id": rid, "message": "resource is '%s', not approved" % status})
            for use in e.get("intended_use", []):
                try:
                    check = self.licenses.check(r, use.get("operation"), use.get("commercial_use", False))
                except KieuError as exc:
                    errors.append({"id": rid, "message": exc.message})
                    continue
                if check["decision"] != "permitted":
                    errors.append({"id": rid, "message": "%s is now %s" % (use.get("operation"), check["decision"])})
            if not e.get("selection_rationale"):
                warnings.append({"id": rid, "message": "no selection rationale recorded"})
            if e.get("approval_status_at_selection") not in STATUSES:
                errors.append({"id": rid, "message": "invalid approval_status_at_selection"})
        return {"ok": not errors, "entries": len(data["resources"]), "errors": errors, "warnings": warnings}

    def _evals(self, resource_id):
        from .evaluation import EvaluationRepository
        return EvaluationRepository(self.registry).list(resource_id)
