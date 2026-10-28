"""Canonical resource schema, lifecycle rules and validation.

This module is the single definition of what a valid registry entry is.
Everything is plain data and stdlib so it runs anywhere with no network.
"""

import re
from datetime import date
from urllib.parse import urlparse

SCHEMA_VERSION = 1

RESOURCE_TYPES = ("dataset", "model", "framework", "tool", "skill", "agent", "template", "asset", "benchmark")
TYPE_DIRS = {
    "dataset": "datasets", "model": "models", "framework": "frameworks", "tool": "tools", "skill": "skills",
    "agent": "agents", "template": "templates", "asset": "assets", "benchmark": "benchmarks",
}
STATUSES = ("draft", "candidate", "under_review", "approved", "restricted", "rejected", "deprecated")
# Lifecycle: any other transition is rejected. Approval always passes through
# under_review so there is an explicit, recorded review step.
TRANSITIONS = {
    "draft": {"candidate", "rejected"},
    "candidate": {"under_review", "rejected"},
    "under_review": {"approved", "restricted", "rejected", "candidate"},
    "approved": {"restricted", "deprecated", "under_review"},
    "restricted": {"under_review", "deprecated", "rejected"},
    "rejected": {"candidate"},
    "deprecated": set(),
}
OPERATIONS = ("use", "research", "inference", "commercial-use", "redistribution", "modification", "training", "fine-tuning")
RIGHTS = ("permitted", "conditional", "prohibited", "unknown")
LICENSE_STATUSES = ("verified", "unverified", "unknown")
REVISION_TYPES = ("commit", "tag", "version", "snapshot")
ACCESS_LEVELS = ("open", "gated", "authenticated", "private")
PII_RISKS = ("none", "low", "moderate", "high", "unknown")
VALIDATION_STATES = ("not_run", "passed", "failed")

ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
REVISION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+/-]{0,127}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,64}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

TOP_LEVEL_KEYS = {
    "schema_version", "id", "name", "description", "type", "categories", "tags", "tasks", "languages", "keywords",
    "source", "dates", "maintainer", "documentation", "quickstart", "requirements", "platforms", "runtimes",
    "license", "usage_rights", "restrictions", "approval", "validation", "provenance", "revisions",
    "evaluation_refs", "limitations", "related", "projects", "details",
}


def is_date(value):
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def is_https_url(value):
    if not isinstance(value, str) or not value or len(value) > 2000 or any(c.isspace() for c in value):
        return False
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and parsed.username is None and parsed.password is None


def is_safe_relpath(value):
    """A repo-relative path that cannot escape its root."""
    if not isinstance(value, str) or not value or len(value) > 500 or "\x00" in value or "\\" in value:
        return False
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        return False
    return ".." not in value.split("/")


def can_transition(old, new):
    return new in TRANSITIONS.get(old, set())


class _Check:
    def __init__(self):
        self.issues = []

    def error(self, path, message):
        self.issues.append({"severity": "error", "path": path, "message": message})

    def warn(self, path, message):
        self.issues.append({"severity": "warning", "path": path, "message": message})

    def string(self, obj, key, path, maximum=2000, required=True):
        value = obj.get(key)
        if value is None:
            if required:
                self.error(path + "." + key, "required")
            return None
        if not isinstance(value, str) or not value.strip() or len(value) > maximum:
            self.error(path + "." + key, "must be a non-empty string of at most %d characters" % maximum)
            return None
        return value

    def strings(self, obj, key, path, maximum=100, required=False):
        value = obj.get(key)
        if value is None:
            if required:
                self.error(path + "." + key, "required")
            return []
        if (not isinstance(value, list) or len(value) > maximum
                or any(not isinstance(v, str) or not v.strip() or len(v) > 500 for v in value)):
            self.error(path + "." + key, "must be a list of at most %d non-empty strings" % maximum)
            return []
        return value

    def obj(self, parent, key, path, required=True):
        value = parent.get(key)
        if value is None:
            if required:
                self.error(path + "." + key, "required")
            return {}
        if not isinstance(value, dict):
            self.error(path + "." + key, "must be an object")
            return {}
        return value

    def choice(self, obj, key, path, allowed, required=True):
        value = obj.get(key)
        if value is None:
            if required:
                self.error(path + "." + key, "required")
            return None
        if value not in allowed:
            self.error(path + "." + key, "must be one of: " + ", ".join(allowed))
            return None
        return value

    def url(self, value, path):
        if not is_https_url(value):
            self.error(path, "must be an https URL without credentials")
            return False
        return True

    def date(self, obj, key, path, required=True):
        value = obj.get(key)
        if value is None:
            if required:
                self.error(path + "." + key, "required")
            return None
        if not is_date(value):
            self.error(path + "." + key, "must be an ISO date (YYYY-MM-DD)")
            return None
        return value

    def evidence(self, items, path, allow_license_id=False):
        if not isinstance(items, list) or len(items) > 50:
            self.error(path, "must be a list of at most 50 evidence objects")
            return
        for i, ev in enumerate(items):
            p = "%s[%d]" % (path, i)
            if not isinstance(ev, dict):
                self.error(p, "must be an object")
                continue
            self.string(ev, "claim", p, 2000)
            has_url, has_path = "url" in ev, "path" in ev
            if has_url == has_path:
                self.error(p, "needs exactly one of url or path")
            elif has_url:
                self.url(ev["url"], p + ".url")
            elif not is_safe_relpath(ev["path"]):
                self.error(p + ".path", "must be a safe repository-relative path")
            if allow_license_id and "license_id" in ev and not isinstance(ev["license_id"], str):
                self.error(p + ".license_id", "must be a string")


def license_conflicts(resource):
    """License identifiers asserted by evidence that disagree with the declared license."""
    lic = resource.get("license") or {}
    declared = str(lic.get("id", "")).strip().casefold()
    found = []
    for ev in lic.get("evidence", []) or []:
        asserted = ev.get("license_id") if isinstance(ev, dict) else None
        if isinstance(asserted, str) and asserted.strip().casefold() != declared:
            found.append("evidence asserts '%s' but license.id is '%s'" % (asserted, lic.get("id")))
    for note in lic.get("conflicts", []) or []:
        found.append(str(note))
    return found


def validate_resource(data):
    """Return a list of issues ({severity, path, message}); empty means valid."""
    c = _Check()
    if not isinstance(data, dict):
        c.error("$", "resource must be an object")
        return c.issues
    for key in sorted(set(data) - TOP_LEVEL_KEYS):
        c.error("$." + key, "unknown field")
    if data.get("schema_version") != SCHEMA_VERSION:
        c.error("$.schema_version", "must be %d" % SCHEMA_VERSION)
    rid = c.string(data, "id", "$", 64)
    if rid and not ID_RE.match(rid):
        c.error("$.id", "must match " + ID_RE.pattern)
    c.string(data, "name", "$", 200)
    c.string(data, "description", "$", 4000)
    rtype = c.choice(data, "type", "$", RESOURCE_TYPES)
    for key in ("categories", "tags", "tasks", "languages", "keywords", "platforms", "runtimes", "limitations", "related", "projects", "restrictions", "evaluation_refs", "documentation"):
        c.strings(data, key, "$")
    for i, link in enumerate(data.get("documentation", []) if isinstance(data.get("documentation"), list) else []):
        c.url(link, "$.documentation[%d]" % i)
    c.string(data, "maintainer", "$", 200)

    source = c.obj(data, "source", "$")
    if source:
        if c.url(source.get("url"), "$.source.url") is False and "url" not in source:
            pass
        c.string(source, "provider", "$.source", 200)
        c.string(source, "repository", "$.source", 500, required=False)
        rev = c.string(source, "revision", "$.source", 128)
        rtype_rev = c.choice(source, "revision_type", "$.source", REVISION_TYPES)
        if rev and not REVISION_RE.match(rev):
            c.error("$.source.revision", "is not a valid version identifier")
        if rev and rtype_rev == "commit" and not COMMIT_RE.match(rev):
            c.error("$.source.revision", "commit revisions must be 7-64 lowercase hex characters")

    dates = c.obj(data, "dates", "$")
    if dates:
        c.date(dates, "added", "$.dates")
        c.date(dates, "last_verified", "$.dates", required=False)

    lic = c.obj(data, "license", "$")
    lic_status = None
    if lic:
        c.string(lic, "id", "$.license", 100)
        lic_status = c.choice(lic, "status", "$.license", LICENSE_STATUSES)
        c.evidence(lic.get("evidence", []), "$.license.evidence", allow_license_id=True)
        c.strings(lic, "conflicts", "$.license")
    rights = c.obj(data, "usage_rights", "$", required=False)
    for op, value in rights.items():
        if op not in OPERATIONS:
            c.error("$.usage_rights." + op, "unknown operation")
        elif value not in RIGHTS:
            c.error("$.usage_rights." + op, "must be one of: " + ", ".join(RIGHTS))

    approval = c.obj(data, "approval", "$")
    status = None
    if approval:
        status = c.choice(approval, "status", "$.approval", STATUSES)
        _check_history(c, approval.get("history", []), status)
    validation = c.obj(data, "validation", "$", required=False)
    if validation:
        c.choice(validation, "status", "$.validation", VALIDATION_STATES)

    prov = c.obj(data, "provenance", "$", required=False)
    if prov:
        for k in prov:
            if not isinstance(prov[k], (str, list)):
                c.error("$.provenance." + k, "must be a string or list")

    qs = data.get("quickstart", [])
    if not isinstance(qs, list) or len(qs) > 20:
        c.error("$.quickstart", "must be a list of at most 20 entries")
    else:
        for i, q in enumerate(qs):
            p = "$.quickstart[%d]" % i
            if not isinstance(q, dict):
                c.error(p, "must be an object")
                continue
            c.string(q, "title", p, 200)
            c.strings(q, "steps", p, 50, required=True)
            if not isinstance(q.get("verified", False), bool):
                c.error(p + ".verified", "must be boolean")
            if q.get("verified") and not q.get("evidence"):
                c.error(p + ".evidence", "verified quickstarts require evidence")
            c.evidence(q.get("evidence", []), p + ".evidence")
    reqs = data.get("requirements", {})
    if not isinstance(reqs, dict):
        c.error("$.requirements", "must be an object")
    elif "access" in reqs and reqs["access"] not in ACCESS_LEVELS:
        c.error("$.requirements.access", "must be one of: " + ", ".join(ACCESS_LEVELS))

    revisions = data.get("revisions", [])
    if not isinstance(revisions, list):
        c.error("$.revisions", "must be a list")
    else:
        for i, r in enumerate(revisions):
            p = "$.revisions[%d]" % i
            if not isinstance(r, dict):
                c.error(p, "must be an object")
                continue
            rv = c.string(r, "revision", p, 128)
            if rv and not REVISION_RE.match(rv):
                c.error(p + ".revision", "is not a valid version identifier")
            c.date(r, "date", p)
        if revisions and source and isinstance(revisions[-1], dict) and revisions[-1].get("revision") != source.get("revision"):
            c.error("$.revisions", "last revision must equal source.revision")

    if rtype == "dataset":
        _check_dataset(c, c.obj(data, "details", "$", required=False))
    elif rtype == "model":
        _check_model(c, c.obj(data, "details", "$", required=False))
    elif "details" in data and not isinstance(data["details"], dict):
        c.error("$.details", "must be an object")

    if status == "approved":
        if lic_status != "verified":
            c.error("$.license.status", "approved resources require verified license status")
        if not (lic.get("evidence") if lic else None):
            c.error("$.license.evidence", "approved resources require license evidence")
        if not (dates and dates.get("last_verified")):
            c.error("$.dates.last_verified", "approved resources require a last verification date")
    if license_conflicts(data) and status == "approved":
        c.warn("$.license", "conflicting license information: " + "; ".join(license_conflicts(data)))
    return c.issues


def _check_history(c, history, status):
    path = "$.approval.history"
    if not isinstance(history, list):
        c.error(path, "must be a list")
        return
    prev = None
    for i, h in enumerate(history):
        p = "%s[%d]" % (path, i)
        if not isinstance(h, dict):
            c.error(p, "must be an object")
            continue
        old = c.choice(h, "from", p, STATUSES)
        new = c.choice(h, "to", p, STATUSES)
        c.date(h, "date", p)
        c.string(h, "reviewer", p, 200)
        c.evidence(h.get("evidence", []), p + ".evidence")
        if not h.get("evidence"):
            c.error(p + ".evidence", "every review decision requires documented evidence")
        if old and new:
            if not can_transition(old, new):
                c.error(p, "unsupported transition %s -> %s" % (old, new))
            if prev is not None and old != prev:
                c.error(p, "history is not contiguous: expected from=%s" % prev)
            prev = new
    if status in STATUSES:
        if status in ("draft", "candidate") and not history:
            return
        if not history:
            c.error(path, "status '%s' requires a recorded review history" % status)
        elif prev != status:
            c.error(path, "last history entry (%s) does not match status (%s)" % (prev, status))


def _check_dataset(c, d):
    p = "$.details"
    c.strings(d, "modalities", p)
    c.strings(d, "configurations", p)
    c.strings(d, "splits", p)
    c.strings(d, "quality_findings", p)
    c.strings(d, "prior_projects", p)
    c.strings(d, "benchmark_results", p)
    if "size_bytes" in d and (not isinstance(d["size_bytes"], int) or isinstance(d["size_bytes"], bool) or d["size_bytes"] < 0):
        c.error(p + ".size_bytes", "must be a non-negative integer")
    for flag in ("download", "streaming"):
        if flag in d and not isinstance(d[flag], bool):
            c.error("%s.%s" % (p, flag), "must be boolean")
    if "schema" in d and not isinstance(d["schema"], dict):
        c.error(p + ".schema", "must be an object mapping fields to types")
    if "access" in d and d["access"] not in ACCESS_LEVELS:
        c.error(p + ".access", "must be one of: " + ", ".join(ACCESS_LEVELS))
    if "pii_risk" in d and d["pii_risk"] not in PII_RISKS:
        c.error(p + ".pii_risk", "must be one of: " + ", ".join(PII_RISKS))
    preview = d.get("preview", {})
    if not isinstance(preview, dict):
        c.error(p + ".preview", "must be an object")
        return
    if "allowed" in preview and not isinstance(preview["allowed"], bool):
        c.error(p + ".preview.allowed", "must be boolean")
    rows = preview.get("sample_rows", [])
    if not isinstance(rows, list) or len(rows) > 20 or any(not isinstance(r, dict) for r in rows):
        c.error(p + ".preview.sample_rows", "must be at most 20 inline row objects")
    elif any(len(str(r)) > 4096 for r in rows):
        c.error(p + ".preview.sample_rows", "rows must be at most 4096 characters each")


def _check_model(c, d):
    p = "$.details"
    c.strings(d, "modalities", p)
    if "parameters_b" in d and (not isinstance(d["parameters_b"], (int, float)) or isinstance(d["parameters_b"], bool) or d["parameters_b"] <= 0):
        c.error(p + ".parameters_b", "must be a positive number (billions)")
    if "context_length" in d and (not isinstance(d["context_length"], int) or d["context_length"] <= 0):
        c.error(p + ".context_length", "must be a positive integer")
    if "hardware" in d and not isinstance(d["hardware"], dict):
        c.error(p + ".hardware", "must be an object")
