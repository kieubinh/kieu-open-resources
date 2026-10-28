"""ResourceSearch: deterministic filtering plus simple lexical scoring.

Hard filters (type, status, license eligibility, ...) always apply. Scores only
order results that already passed them. Optional external relevance scores may
re-order eligible results but can never add an excluded one.
"""

import re
from datetime import date

from .errors import KieuError
from .licensing import ResourceLicenseChecker
from .schema import OPERATIONS, RESOURCE_TYPES, STATUSES

DEFAULT_STATUSES = ("draft", "candidate", "under_review", "approved", "restricted")


def _norm(values):
    return {str(v).casefold() for v in values or []}


def _terms(query):
    return [t for t in re.split(r"\s+", (query or "").casefold().strip()) if t]


class ResourceSearch:
    def __init__(self, registry):
        self.registry = registry
        self.licenses = ResourceLicenseChecker()

    def search(self, query="", type=None, category=None, task=None, language=None, statuses=None,
               operation=None, commercial_use=False, modality=None, runtime=None, provider=None,
               max_params_b=None, max_size_bytes=None, verified_within_days=None, project=None,
               limit=20, today=None, include_excluded=False, relevance_scores=None):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise KieuError("INVALID_INPUT", "limit must be between 1 and 100")
        if type is not None and type not in RESOURCE_TYPES:
            raise KieuError("INVALID_INPUT", "unsupported resource type '%s'" % type)
        if operation is not None and operation not in OPERATIONS:
            raise KieuError("INVALID_INPUT", "unknown operation '%s'" % operation)
        if commercial_use and operation is None:
            operation = "use"
        statuses = tuple(statuses) if statuses else DEFAULT_STATUSES
        for s in statuses:
            if s not in STATUSES:
                raise KieuError("INVALID_INPUT", "unknown status '%s'" % s)
        if not isinstance(query, str) or len(query) > 200:
            raise KieuError("INVALID_INPUT", "query must be a string of at most 200 characters")
        if relevance_scores is not None:
            if (not isinstance(relevance_scores, dict) or len(relevance_scores) > 100 or
                    any(not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1 for v in relevance_scores.values())):
                raise KieuError("INVALID_INPUT", "relevance_scores must map ids to numbers from 0 to 1")
        today = today or date.today()
        terms = _terms(query)
        results, excluded = [], []
        for r in self.registry.list():
            why = []
            status = r["approval"]["status"]
            details = r.get("details", {})
            if type and r["type"] != type:
                why.append("type is %s" % r["type"])
            if status not in statuses:
                why.append("status is %s" % status)
            if category and category.casefold() not in _norm(r.get("categories")):
                why.append("category not matched")
            if task and task.casefold() not in _norm(r.get("tasks")):
                why.append("task not matched")
            if language and language.casefold() not in _norm(r.get("languages")):
                why.append("language not matched")
            if modality and modality.casefold() not in _norm(details.get("modalities")):
                why.append("modality not matched")
            if runtime and runtime.casefold() not in _norm(r.get("runtimes")):
                why.append("runtime not matched")
            if provider and provider.casefold() != r["source"]["provider"].casefold():
                why.append("provider is %s" % r["source"]["provider"])
            if project and project.casefold() not in _norm(r.get("projects")):
                why.append("not marked compatible with project '%s'" % project)
            if max_params_b is not None and not (isinstance(details.get("parameters_b"), (int, float)) and details["parameters_b"] <= max_params_b):
                why.append("model size unknown or above limit")
            if max_size_bytes is not None and not (isinstance(details.get("size_bytes"), int) and details["size_bytes"] <= max_size_bytes):
                why.append("dataset size unknown or above limit")
            if verified_within_days is not None:
                lv = r["dates"].get("last_verified")
                if not lv or (today - date.fromisoformat(lv)).days > verified_within_days:
                    why.append("not verified within %d days" % verified_within_days)
            license_info = None
            if operation:
                license_info = self.licenses.check(r, operation, commercial_use)
                if license_info["decision"] != "permitted":
                    why.append("license decision for %s is %s" % (operation, license_info["decision"]))
            score, matched = self._score(r, terms)
            if terms and score == 0:
                why.append("query terms not matched")
            if why:
                if include_excluded:
                    excluded.append({"id": r["id"], "reasons": why})
                continue
            item = {
                "id": r["id"], "name": r["name"], "type": r["type"], "status": status,
                "revision": r["source"]["revision"], "score": score, "matched": matched,
                "eligibility": ["passed all hard filters"] + (["license %s for %s" % (license_info["decision"], operation)] if license_info else []),
            }
            if relevance_scores is not None:
                item["external_relevance"] = relevance_scores.get(r["id"])
            results.append(item)
        results.sort(key=lambda x: (-(x.get("external_relevance") or 0), -x["score"], x["id"]))
        out = {"total_matches": len(results), "limit": limit, "results": results[:limit]}
        if include_excluded:
            out["excluded"] = sorted(excluded, key=lambda x: x["id"])
        return out

    @staticmethod
    def _score(resource, terms):
        if not terms:
            return 0, []
        fields = [
            ("name", 5, [resource["name"], resource["id"]]),
            ("tags", 3, resource.get("tags", []) + resource.get("keywords", [])),
            ("tasks", 3, resource.get("tasks", [])),
            ("categories", 2, resource.get("categories", [])),
            ("description", 1, [resource["description"]]),
        ]
        total, matched = 0, set()
        for term in terms:
            hit = False
            for label, weight, texts in fields:
                if any(term in t.casefold() for t in texts):
                    total += weight
                    matched.add(label)
                    hit = True
            if not hit:
                return 0, []  # AND semantics: every term must match somewhere
        return total, sorted(matched)
