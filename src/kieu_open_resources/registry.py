"""ResourceRegistry: loads and validates the version-controlled registry.

Layout (root = the ``registry`` directory)::

    resources/<type-dir>/<id>.json   authoritative entries (changed by reviewed PR)
    candidates/<id>.json             proposed entries, never returned as approved
    evaluations/<resource-id>/*.json evaluation records
    reviews/<resource-id>.jsonl      append-only review audit trail
"""

import json
import os
import tempfile
from pathlib import Path

from .errors import KieuError
from .schema import ID_RE, TYPE_DIRS, validate_resource

ENV_REGISTRY = "KIEU_OPEN_RESOURCES_REGISTRY"
MAX_FILE_BYTES = 512 * 1024


def resolve_root(explicit=None, start=None, environ=None):
    """Locate the registry root: explicit path, env var, then walk up from cwd."""
    environ = os.environ if environ is None else environ
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    elif environ.get(ENV_REGISTRY):
        candidates.append(Path(environ[ENV_REGISTRY]))
    else:
        here = Path(start or os.getcwd()).resolve()
        for d in [here] + list(here.parents):
            candidates.append(d)
    for c in candidates:
        for root in (c, c / "registry"):
            if (root / "resources").is_dir():
                return root.resolve()
    raise KieuError("REGISTRY_NOT_FOUND",
                    "no registry found; pass --registry or set %s (expected a directory containing resources/)" % ENV_REGISTRY)


def read_json_file(path, root):
    """Read a bounded JSON file that must resolve inside root."""
    p = Path(path)
    try:
        resolved = p.resolve(strict=True)
    except OSError as exc:
        raise KieuError("NOT_FOUND", "file not found: %s" % p) from exc
    if not resolved.is_relative_to(Path(root).resolve()):
        raise KieuError("PATH_UNSAFE", "path escapes the registry root: %s" % p)
    if not resolved.is_file() or resolved.stat().st_size > MAX_FILE_BYTES:
        raise KieuError("REGISTRY_INVALID", "not a regular file or too large: %s" % p)
    try:
        return json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise KieuError("REGISTRY_INVALID", "cannot parse %s: %s" % (p.name, exc)) from exc


def atomic_write_json(path, data, exclusive=False):
    """Write JSON atomically. With exclusive=True never replace an existing file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if exclusive and path.exists():
        raise KieuError("CONFLICT", "already exists: %s" % path.name)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            os.link(tmp, str(path))  # fails atomically if another writer won the race
            os.unlink(tmp)
        else:
            os.replace(tmp, str(path))
    except FileExistsError as exc:
        raise KieuError("CONFLICT", "already exists: %s" % path.name) from exc
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class ResourceRegistry:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self._cache = None

    @classmethod
    def locate(cls, explicit=None, start=None, environ=None):
        return cls(resolve_root(explicit, start, environ))

    # -- loading -----------------------------------------------------------
    def _scan(self):
        """Return (resources_by_id, issues). Never raises on bad entries."""
        resources, issues, seen = {}, [], {}
        base = self.root / "resources"
        for type_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            if type_dir.name not in TYPE_DIRS.values():
                issues.append(self._issue("error", type_dir.name, "$", "unknown resource directory"))
                continue
            for f in sorted(type_dir.glob("*.json")):
                rel = f.relative_to(self.root).as_posix()
                try:
                    data = read_json_file(f, self.root)
                except KieuError as exc:
                    issues.append(self._issue("error", rel, "$", exc.message))
                    continue
                for i in validate_resource(data):
                    issues.append(self._issue(i["severity"], rel, i["path"], i["message"]))
                if not isinstance(data, dict):
                    continue
                rid = data.get("id")
                if isinstance(rid, str) and ID_RE.match(rid):
                    if f.stem != rid:
                        issues.append(self._issue("error", rel, "$.id", "filename must be %s.json" % rid))
                    expected = TYPE_DIRS.get(data.get("type"))
                    if expected and expected != type_dir.name:
                        issues.append(self._issue("error", rel, "$.type", "type '%s' belongs in %s/" % (data["type"], expected)))
                    if rid in seen:
                        issues.append(self._issue("error", rel, "$.id", "duplicate id (also in %s)" % seen[rid]))
                        continue
                    seen[rid] = rel
                    resources[rid] = data
        for rid, data in resources.items():
            for rel_id in data.get("related", []) if isinstance(data.get("related"), list) else []:
                if rel_id not in resources:
                    issues.append(self._issue("warning", seen[rid], "$.related", "unknown related resource '%s'" % rel_id))
        return resources, issues

    @staticmethod
    def _issue(severity, file, path, message):
        return {"severity": severity, "file": file, "path": path, "message": message}

    def validate(self):
        resources, issues = self._scan()
        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]
        return {"ok": not errors, "resource_count": len(resources), "errors": errors, "warnings": warnings}

    def load(self):
        """Strict load: any invalid authoritative entry makes the whole registry unusable."""
        if self._cache is None:
            resources, issues = self._scan()
            errors = [i for i in issues if i["severity"] == "error"]
            if errors:
                raise KieuError("REGISTRY_INVALID", "registry has %d validation error(s); run 'validate'" % len(errors),
                                {"first_errors": errors[:5]})
            self._cache = resources
        return self._cache

    def list(self):
        return [self.load()[k] for k in sorted(self.load())]

    def get(self, resource_id):
        if not isinstance(resource_id, str) or not ID_RE.match(resource_id):
            raise KieuError("INVALID_INPUT", "invalid resource id")
        try:
            return self.load()[resource_id]
        except KeyError:
            raise KieuError("NOT_FOUND", "resource not found: %s" % resource_id) from None

    def counts(self):
        out = {"by_type": {}, "by_status": {}}
        for r in self.list():
            out["by_type"][r["type"]] = out["by_type"].get(r["type"], 0) + 1
            s = r["approval"]["status"]
            out["by_status"][s] = out["by_status"].get(s, 0) + 1
        return out

    def resource_path(self, resource):
        return self.root / "resources" / TYPE_DIRS[resource["type"]] / (resource["id"] + ".json")
