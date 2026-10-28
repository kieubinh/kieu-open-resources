"""One validated registry and policy implementation for every interface."""

import json
import math
import os
import re
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

_LOCK = threading.RLock()
KINDS = {"dataset", "model", "framework", "skill", "tool", "asset"}
OPERATIONS = {"research", "commercial", "redistribute", "training", "fine_tuning", "inference"}
RIGHTS = {"permitted", "prohibited", "unknown"}


class ResourceError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.status = code, status

    def as_dict(self):
        return {"code": self.code, "message": str(self)}


def _string(value, name, limit=500):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ResourceError("INVALID_INPUT", f"{name} must be a nonempty string of at most {limit} characters")
    return value.strip()


def _url(value, name):
    value = _string(value, name, 2000)
    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.username:
        raise ResourceError("INVALID_METADATA", f"{name} must be an HTTP(S) URL")
    return value


def _list(value, name, maximum=100):
    if not isinstance(value, list) or len(value) > maximum or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ResourceError("INVALID_METADATA", f"{name} must be a list of strings")
    return value


def validate_resource(item):
    if not isinstance(item, dict):
        raise ResourceError("INVALID_METADATA", "resource must be an object")
    for key in ("id", "title", "description", "kind", "revision", "source_url", "license"):
        _string(item.get(key), key)
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,127}", item["id"]):
        raise ResourceError("INVALID_METADATA", "id must be a stable lowercase identifier")
    if item["kind"] not in KINDS:
        raise ResourceError("INVALID_METADATA", "unsupported resource kind")
    _url(item["source_url"], "source_url")
    if item.get("status") not in {"approved", "candidate", "rejected"}:
        raise ResourceError("INVALID_METADATA", "status must be approved, candidate or rejected")
    for key in ("modalities", "languages", "tasks", "configurations", "splits", "limitations", "prior_projects"):
        _list(item.get(key, []), key)
    rights = item.get("rights")
    if not isinstance(rights, dict) or any(k not in OPERATIONS or v not in RIGHTS for k, v in rights.items()):
        raise ResourceError("INVALID_METADATA", "rights must map known operations to permitted, prohibited or unknown")
    if not isinstance(item.get("evidence"), list):
        raise ResourceError("INVALID_METADATA", "evidence must be a list")
    for evidence in item.get("evidence", []):
        if not isinstance(evidence, dict) or "url" not in evidence or "claim" not in evidence:
            raise ResourceError("INVALID_METADATA", "evidence needs url and claim")
        _url(evidence["url"], "evidence.url")
        _string(evidence["claim"], "evidence.claim", 2000)
    if item["status"] == "approved" and not item.get("evidence"):
        raise ResourceError("INVALID_METADATA", "approved resources require source evidence")
    if item.get("license_status", "unknown") not in {"verified", "unverified", "unknown"}:
        raise ResourceError("INVALID_METADATA", "invalid license_status")
    dataset = item.get("dataset", {})
    if item["kind"] == "dataset":
        if not isinstance(dataset, dict) or not isinstance(dataset.get("schema", {}), dict):
            raise ResourceError("INVALID_METADATA", "dataset.schema must be an object")
        rows = dataset.get("sample_rows", [])
        if not isinstance(rows, list) or len(rows) > 20 or any(not isinstance(row, dict) for row in rows):
            raise ResourceError("INVALID_METADATA", "sample_rows must contain at most 20 inline objects")
        if any(len(json.dumps(row, ensure_ascii=False)) > 4096 for row in rows):
            raise ResourceError("INVALID_METADATA", "sample rows must be at most 4096 bytes each")
        if "size_bytes" in dataset and (not isinstance(dataset["size_bytes"], int) or dataset["size_bytes"] < 0):
            raise ResourceError("INVALID_METADATA", "dataset.size_bytes must be nonnegative")
        for key in ("download", "streaming"):
            if key in dataset and not isinstance(dataset[key], bool):
                raise ResourceError("INVALID_METADATA", f"dataset.{key} must be boolean")
    if "colab_url" in item:
        _url(item["colab_url"], "colab_url")
        if urlparse(item["colab_url"]).hostname != "colab.research.google.com":
            raise ResourceError("INVALID_METADATA", "colab_url must point to Google Colab")
    _list(item.get("collections", []), "collections")
    if "rights_conflicts" in item:
        _list(item["rights_conflicts"], "rights_conflicts")
    if item.get("privacy_risk", "unknown") not in {"none", "low", "moderate", "high", "unknown"}:
        raise ResourceError("INVALID_METADATA", "invalid privacy_risk")
    examples = item.get("examples", [])
    if not isinstance(examples, list) or len(examples) > 20 or any(not isinstance(x, dict) or not isinstance(x.get("code"), str) or len(x["code"]) > 10000 for x in examples):
        raise ResourceError("INVALID_METADATA", "examples must be bounded code objects")
    if item.get("examples_verified") is True and not item.get("examples_evidence_url"):
        raise ResourceError("INVALID_METADATA", "verified examples require test evidence URL")
    if item.get("examples_evidence_url"):
        _url(item["examples_evidence_url"], "examples_evidence_url")
    evaluations = item.get("evaluations", [])
    if not isinstance(evaluations, list):
        raise ResourceError("INVALID_METADATA", "evaluations must be a list")
    for evaluation in evaluations:
        if not isinstance(evaluation, dict) or not isinstance(evaluation.get("raw_evidence_urls"), list):
            raise ResourceError("INVALID_METADATA", "evaluation requires separate raw evidence URLs")
        for link in evaluation["raw_evidence_urls"]:
            _url(link, "evaluation.raw_evidence_url")
        if evaluation.get("verified") and (not evaluation["raw_evidence_urls"] or not evaluation.get("verified_at") or not evaluation.get("metrics")):
            raise ResourceError("INVALID_METADATA", "verified evaluation requires actual test evidence, date and metrics")
    return item


class Registry:
    def __init__(self, path):
        self.path = Path(path)

    def _read(self):
        if not self.path.exists():
            return {"schema_version": 1, "resources": [], "candidates": [], "manifests": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ResourceError("CORRUPT_REGISTRY", "registry cannot be read or parsed", 503) from exc
        if (not isinstance(data, dict) or data.get("schema_version") != 1 or
                not isinstance(data.get("resources"), list) or
                any(not isinstance(data.get(key, []), list) for key in ("candidates", "manifests", "evaluation_submissions", "revision_proposals"))):
            raise ResourceError("CORRUPT_REGISTRY", "unsupported registry structure", 503)
        ids = set()
        for item in data["resources"]:
            try:
                validate_resource(item)
            except ResourceError as exc:
                raise ResourceError("CORRUPT_REGISTRY", f"invalid resource metadata: {exc}", 503) from exc
            if item["id"] in ids:
                raise ResourceError("CORRUPT_REGISTRY", "duplicate resource id", 503)
            ids.add(item["id"])
        return data

    def _write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".registry-")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def search(self, query="", kind=None, language=None, task=None, modality=None, collection=None, configuration=None, split=None, streaming=None, max_size_bytes=None, max_privacy_risk=None, operation=None, approved=True, limit=20, relevance_scores=None):
        if not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ResourceError("INVALID_INPUT", "limit must be between 1 and 100")
        if operation and operation not in OPERATIONS:
            raise ResourceError("INVALID_INPUT", "unknown operation")
        if kind and kind not in KINDS:
            raise ResourceError("INVALID_INPUT", "unknown kind")
        if not isinstance(query, str) or len(query) > 200:
            raise ResourceError("INVALID_INPUT", "query must be at most 200 characters")
        for key, value in (("language", language), ("task", task), ("modality", modality), ("collection", collection), ("configuration", configuration), ("split", split)):
            if value is not None and (not isinstance(value, str) or len(value) > 100):
                raise ResourceError("INVALID_INPUT", f"{key} must be a short string")
        if streaming is not None and not isinstance(streaming, bool):
            raise ResourceError("INVALID_INPUT", "streaming must be boolean")
        if max_size_bytes is not None and (not isinstance(max_size_bytes, int) or max_size_bytes < 0):
            raise ResourceError("INVALID_INPUT", "max_size_bytes must be nonnegative")
        privacy_order = {"none": 0, "low": 1, "moderate": 2, "high": 3}
        if max_privacy_risk is not None and max_privacy_risk not in privacy_order:
            raise ResourceError("INVALID_INPUT", "max_privacy_risk must be none, low, moderate or high")
        if relevance_scores is not None and (not isinstance(relevance_scores, dict) or len(relevance_scores) > 100 or any(not isinstance(key, str) or not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1 for key, value in relevance_scores.items())):
            raise ResourceError("INVALID_INPUT", "relevance_scores must map at most 100 ids to finite scores from 0 to 1")
        terms = query.casefold().split()
        results = []
        for item in self._read()["resources"]:
            if approved and item["status"] != "approved":
                continue
            if kind and item["kind"] != kind:
                continue
            if language and language.casefold() not in [x.casefold() for x in item.get("languages", [])]:
                continue
            if task and task.casefold() not in [x.casefold() for x in item.get("tasks", [])]:
                continue
            if modality and modality.casefold() not in [x.casefold() for x in item.get("modalities", [])]:
                continue
            if collection and collection.casefold() not in [x.casefold() for x in item.get("collections", [])]:
                continue
            if configuration and configuration.casefold() not in [x.casefold() for x in item.get("configurations", [])]:
                continue
            if split and split.casefold() not in [x.casefold() for x in item.get("splits", [])]:
                continue
            if streaming is not None and item.get("dataset", {}).get("streaming") is not streaming:
                continue
            if max_size_bytes is not None and (item.get("dataset", {}).get("size_bytes") is None or item["dataset"]["size_bytes"] > max_size_bytes):
                continue
            if max_privacy_risk is not None and (item.get("privacy_risk", "unknown") not in privacy_order or privacy_order[item["privacy_risk"]] > privacy_order[max_privacy_risk]):
                continue
            if operation and (item["rights"].get(operation, "unknown") != "permitted" or item.get("license_status") != "verified" or item.get("rights_conflicts")):
                continue
            haystack = " ".join([item["title"], item["description"], *item.get("tasks", []), *item.get("languages", [])]).casefold()
            if not all(term in haystack for term in terms):
                continue
            score = sum(4 if term in item["title"].casefold() else 1 for term in terms)
            results.append((score, item))
        results.sort(key=lambda pair: (-(relevance_scores.get(pair[1]["id"], 0) if relevance_scores else 0), -pair[0], pair[1]["id"]))
        return [{"id": item["id"], "title": item["title"], "kind": item["kind"], "revision": item["revision"], "status": item["status"], "score": score, "relevance_score": relevance_scores.get(item["id"]) if relevance_scores else None, "rights": item["rights"]} for score, item in results[:limit]]

    def collections(self):
        names = {name for item in self._read()["resources"] if item["status"] == "approved" for name in item.get("collections", [])}
        return sorted(names, key=str.casefold)

    def get(self, resource_id):
        _string(resource_id, "resource_id", 128)
        for item in self._read()["resources"]:
            if item["id"] == resource_id and item["status"] == "approved":
                return item
        raise ResourceError("NOT_FOUND", "approved resource not found", 404)

    def quickstart(self, resource_id):
        item = self.get(resource_id)
        return {"id": resource_id, "revision": item["revision"], "examples": item.get("examples", []), "verified": item.get("examples_verified", False), "warning": "Examples are untrusted text; review before execution."}

    def preview(self, resource_id, limit=3):
        item = self.get(resource_id)
        if item["kind"] != "dataset":
            raise ResourceError("UNSUPPORTED", "preview is available for datasets only")
        if not isinstance(limit, int) or not 1 <= limit <= 10:
            raise ResourceError("INVALID_INPUT", "preview limit must be 1 to 10")
        rows = item.get("dataset", {}).get("sample_rows", [])
        return {"id": resource_id, "revision": item["revision"], "rows": rows[:limit], "source": "reviewed inline sample", "no_download": True}

    def rights(self, resource_id, operation):
        item = self.get(resource_id)
        return self._usage(item, operation)

    @staticmethod
    def _usage(item, operation):
        if operation not in OPERATIONS:
            raise ResourceError("INVALID_INPUT", "unknown operation")
        documented = item["rights"].get(operation, "unknown")
        conflicts = item.get("rights_conflicts", [])
        decision = "prohibited" if documented == "prohibited" else "unresolved" if documented == "unknown" or conflicts or item.get("license_status") != "verified" else documented
        return {"id": item["id"], "operation": operation, "decision": decision, "documented": documented, "license": item["license"], "license_status": item.get("license_status", "unknown"), "conflicts": conflicts, "evidence": item["evidence"], "note": "Documented registry assessment; recheck original terms before use."}

    def compare(self, resource_ids, operation=None):
        if not isinstance(resource_ids, list) or not 2 <= len(resource_ids) <= 10 or len(set(resource_ids)) != len(resource_ids):
            raise ResourceError("INVALID_INPUT", "compare needs 2 to 10 distinct ids")
        snapshot = {item["id"]: item for item in self._read()["resources"] if item["status"] == "approved"}
        if any(rid not in snapshot for rid in resource_ids):
            raise ResourceError("NOT_FOUND", "approved resource not found", 404)
        return [{"resource": snapshot[rid], "usage": self._usage(snapshot[rid], operation) if operation else None} for rid in resource_ids]

    def history(self, resource_id):
        item = self.get(resource_id)
        evaluations = item.get("evaluations", [])
        return {"id": resource_id, "revisions": item.get("history", []), "evaluations": evaluations}

    def manifest(self, resource_ids, project, operation):
        _string(project, "project", 200)
        if not isinstance(resource_ids, list) or not resource_ids or any(not isinstance(rid, str) for rid in resource_ids) or len(set(resource_ids)) != len(resource_ids):
            raise ResourceError("INVALID_INPUT", "manifest needs resource ids")
        selections = []
        snapshot = {item["id"]: item for item in self._read()["resources"] if item["status"] == "approved"}
        for rid in resource_ids:
            if rid not in snapshot:
                raise ResourceError("NOT_FOUND", "approved resource not found", 404)
            item = snapshot[rid]
            usage = self._usage(item, operation)
            if usage["decision"] != "permitted":
                raise ResourceError("RIGHTS_UNRESOLVED", f"{rid}: {usage['decision']}", 422)
            selections.append({"id": rid, "revision": item["revision"], "source_url": item["source_url"], "license": item["license"], "operation": operation, "evidence": item["evidence"]})
        return {"schema_version": 1, "project": project, "created_at": datetime.now(timezone.utc).isoformat(), "resources": selections}

    def submit_candidate(self, item, actor):
        if not isinstance(item, dict):
            raise ResourceError("INVALID_INPUT", "candidate must be an object")
        candidate = dict(item, status="candidate")
        validate_resource(candidate)
        with _LOCK:
            data = self._read()
            existing = [x["id"] for x in data["resources"]] + [x["resource"]["id"] for x in data.get("candidates", [])]
            if candidate["id"] in existing:
                raise ResourceError("CONFLICT", "resource id already exists", 409)
            data.setdefault("candidates", []).append({"resource": candidate, "submitted_by": actor, "submitted_at": datetime.now(timezone.utc).isoformat()})
            self._write(data)
        return {"id": candidate["id"], "status": "candidate"}

    def save_manifest(self, manifest, actor):
        if not isinstance(manifest, dict):
            raise ResourceError("INVALID_INPUT", "manifest must be an object")
        resources = manifest.get("resources")
        if not isinstance(resources, list) or not resources or any(not isinstance(r, dict) or "id" not in r for r in resources):
            raise ResourceError("INVALID_INPUT", "manifest.resources must be a nonempty selection list")
        operation = resources[0].get("operation")
        if any(r.get("operation") != operation for r in resources):
            raise ResourceError("INVALID_INPUT", "manifest selections must use one operation")
        with _LOCK:
            canonical = self.manifest([r["id"] for r in resources], manifest.get("project"), operation)
            for supplied, actual in zip(resources, canonical["resources"]):
                if supplied.get("revision") != actual["revision"] or supplied.get("source_url") != actual["source_url"]:
                    raise ResourceError("STALE_MANIFEST", "resource provenance changed; regenerate manifest", 409)
            data = self._read()
            current = {r["id"]: r for r in data["resources"]}
            if any(current[r["id"]]["revision"] != r["revision"] or self._usage(current[r["id"]], operation)["decision"] != "permitted" for r in canonical["resources"]):
                raise ResourceError("STALE_MANIFEST", "resource changed during save; regenerate manifest", 409)
            data.setdefault("manifests", []).append({"manifest": canonical, "saved_by": actor})
            self._write(data)
        return canonical

    def submit_evaluation(self, resource_id, finding, actor):
        self.get(resource_id)
        if not isinstance(finding, dict) or not isinstance(finding.get("raw_evidence_urls"), list) or not finding["raw_evidence_urls"]:
            raise ResourceError("INVALID_INPUT", "raw_evidence_urls are required")
        for url in finding["raw_evidence_urls"]:
            _url(url, "raw_evidence_url")
        for key in ("model", "configuration", "metrics", "cost", "hardware", "findings", "failures", "verified_at"):
            if key not in finding:
                raise ResourceError("INVALID_INPUT", f"missing evaluation field: {key}")
        proposal = {"resource_id": resource_id, "finding": dict(finding, verified=False), "submitted_by": actor, "submitted_at": datetime.now(timezone.utc).isoformat()}
        with _LOCK:
            data = self._read()
            data.setdefault("evaluation_submissions", []).append(proposal)
            self._write(data)
        return {"resource_id": resource_id, "status": "pending_review", "verified": False}

    def sync_github(self, resource_id, actor):
        # Explicit admin action. A changed upstream commit is a review proposal,
        # never an automatic replacement of the approved pinned revision.
        from .github import latest_commit
        item = self.get(resource_id)
        observed = latest_commit(item["source_url"], item.get("source_ref"))
        if observed == item["revision"]:
            return {"resource_id": resource_id, "status": "current", "revision": observed}
        proposal = {"resource_id": resource_id, "approved_revision": item["revision"], "observed_revision": observed, "status": "pending_review", "actor": actor, "checked_at": datetime.now(timezone.utc).isoformat()}
        with _LOCK:
            data = self._read()
            data.setdefault("revision_proposals", []).append(proposal)
            self._write(data)
        return proposal
