"""Shared synthetic fixtures. Fixtures are test data only; none are registry content."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from kieu_open_resources import cli
from kieu_open_resources.schema import TYPE_DIRS

REPO = Path(__file__).resolve().parents[1]
REAL_REGISTRY = REPO / "registry"
REVIEW = {"from": "under_review", "to": "approved", "date": "2026-01-02", "reviewer": "test-reviewer",
          "evidence": [{"url": "https://example.org/review", "claim": "synthetic review"}]}
RIGHTS_OK = {"use": "permitted", "research": "permitted", "inference": "permitted", "commercial-use": "permitted",
             "training": "prohibited", "fine-tuning": "unknown", "redistribution": "conditional"}


def make_resource(rid="vi-docs", rtype="dataset", status="approved", **over):
    r = {
        "schema_version": 1, "id": rid, "name": "Synthetic %s" % rid, "description": "Synthetic test resource for Vietnamese document QA.",
        "type": rtype, "categories": ["nlp"], "tags": ["qa", "vietnamese"], "tasks": ["question-answering"], "languages": ["vi"],
        "keywords": [], "source": {"url": "https://example.org/" + rid, "provider": "example", "revision": "abc1234", "revision_type": "commit"},
        "dates": {"added": "2026-01-01", "last_verified": "2026-01-02"}, "maintainer": "tests",
        "documentation": ["https://example.org/docs"], "quickstart": [{"title": "Load", "steps": ["print('hi')"], "verified": False}],
        "requirements": {"access": "open"}, "platforms": ["linux"], "runtimes": ["python"],
        "license": {"id": "CC-BY-4.0", "status": "verified", "evidence": [{"url": "https://example.org/license", "claim": "card says CC-BY-4.0", "license_id": "CC-BY-4.0"}]},
        "usage_rights": dict(RIGHTS_OK), "restrictions": ["attribution required"],
        "approval": {"status": status, "history": []}, "validation": {"status": "not_run"},
        "provenance": {"origin": "synthetic"}, "limitations": ["synthetic"], "related": [], "projects": ["qa-demo"],
        "details": {"modalities": ["text"], "configurations": ["default"], "splits": ["train", "test"], "size_bytes": 1000,
                    "streaming": True, "download": False, "access": "open", "pii_risk": "low",
                    "preview": {"allowed": True, "sample_rows": [{"question": "Xin chào?", "answer": "Chào bạn."}] * 5}},
    }
    if rtype == "model":
        r["details"] = {"modalities": ["text"], "parameters_b": 1.5}
    if rtype not in ("dataset", "model"):
        r.pop("details")
    if status == "under_review":
        r["approval"]["history"] = [dict(REVIEW, **{"from": "candidate", "to": "under_review"})]
    elif status not in ("draft", "candidate"):
        chain = [dict(REVIEW, **{"from": "candidate", "to": "under_review"}), dict(REVIEW)]
        if status != "approved":
            chain.append(dict(REVIEW, **{"from": "approved", "to": status}))
        r["approval"]["history"] = chain
    for k, v in over.items():
        r[k] = v
    return r


def write_registry(root, resources):
    root = Path(root)
    for d in TYPE_DIRS.values():
        (root / "resources" / d).mkdir(parents=True, exist_ok=True)
    for r in resources:
        (root / "resources" / TYPE_DIRS[r["type"]] / (r["id"] + ".json")).write_text(json.dumps(r), encoding="utf-8")
    return root


class RegistryCase(unittest.TestCase):
    resources = ()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "registry"
        write_registry(self.root, self.resources)
        self.project = Path(self.tmp.name) / "project"
        self.project.mkdir()

    def cli(self, *args):
        """Run the CLI in-process; returns (exit_code, parsed_json_or_text)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(args) + ["--registry", str(self.root), "--format", "json"])
        text = out.getvalue()
        return code, (json.loads(text) if text.strip() else {"stderr": err.getvalue()})


def clone(obj):
    return copy.deepcopy(obj)
