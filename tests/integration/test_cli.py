import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import REAL_REGISTRY, REPO, RegistryCase, make_resource

SRC = str(REPO / "src")


def subprocess_cli(*args, cwd=None, env=None):
    e = dict(os.environ, PYTHONPATH=SRC)
    e.update(env or {})
    p = subprocess.run([sys.executable, "-m", "kieu_open_resources.cli"] + list(args), capture_output=True, text=True, cwd=cwd, env=e)
    return p.returncode, p.stdout, p.stderr


class RealRegistryTest(unittest.TestCase):
    """Runs the shipped CLI against the real, committed registry."""

    def test_registry_is_valid(self):
        code, out, _ = subprocess_cli("validate", "--registry", str(REAL_REGISTRY), "--format", "json")
        self.assertEqual(code, 0, out)
        self.assertGreaterEqual(json.loads(out)["data"]["resource_count"], 3)

    def test_search_inspect_license_compare_roundtrip(self):
        r = str(REAL_REGISTRY)
        code, out, _ = subprocess_cli("search", "discovery", "--type", "skill", "--registry", r, "--format", "json")
        env = json.loads(out)
        self.assertEqual((code, env["contract"], env["ok"]), (0, "kieu-open-resources/v1", True))
        self.assertEqual(env["data"]["results"][0]["id"], "kieu-resource-discovery")
        code, out, _ = subprocess_cli("license-check", "kieu-resource-discovery", "--operation", "use", "--commercial-use", "--registry", r, "--format", "json")
        d = json.loads(out)["data"]
        self.assertEqual(d["decision"], "permitted")
        self.assertFalse(d["usable"], "seeded entries are candidates until a maintainer approves them")
        code, out, _ = subprocess_cli("license-check", "kieu-resource-discovery", "--operation", "training", "--registry", r, "--format", "json")
        self.assertEqual(json.loads(out)["data"]["decision"], "unresolved")
        code, out, _ = subprocess_cli("compare", "kieu-resource-discovery", "kieu-leetcode-video", "--operation", "use", "--registry", r, "--format", "json")
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(out)["data"]["resources"]), 2)

    def test_no_approved_dataset_or_model_is_invented(self):
        code, out, _ = subprocess_cli("search", "--status", "approved", "--type", "dataset", "--registry", str(REAL_REGISTRY), "--format", "json")
        self.assertEqual(json.loads(out)["data"]["total_matches"], 0)

    def test_registry_discovered_from_cwd(self):
        code, out, _ = subprocess_cli("doctor", "--format", "json", cwd=str(REPO / "docs"))
        self.assertEqual(code, 0, out)

    def test_exit_codes_and_error_envelope(self):
        r = ["--registry", str(REAL_REGISTRY), "--format", "json"]
        code, out, _ = subprocess_cli("inspect", "does-not-exist", *r)
        self.assertEqual((code, json.loads(out)["error"]["code"]), (4, "NOT_FOUND"))
        code, out, _ = subprocess_cli("search", "--type", "gadget", *r)
        self.assertEqual((code, json.loads(out)["error"]["code"]), (2, "INVALID_INPUT"))
        code, out, _ = subprocess_cli("doctor", "--registry", "/nonexistent", "--format", "json")
        self.assertEqual((code, json.loads(out)["error"]["code"]), (3, "REGISTRY_NOT_FOUND"))
        code, out, err = subprocess_cli("inspect", "does-not-exist", "--registry", str(REAL_REGISTRY))
        self.assertEqual(code, 4)
        self.assertIn("NOT_FOUND", err)

    def test_install_skill_into_other_repo(self):
        with tempfile.TemporaryDirectory() as d:
            code, out, _ = subprocess_cli("install-skill", "--project", d, "--format", "json")
            self.assertEqual(code, 0, out)
            canonical = (REPO / "skills/kieu-resource-discovery/SKILL.md").read_bytes()
            for root in (".agents", ".claude"):
                self.assertEqual((Path(d) / root / "skills/kieu-resource-discovery/SKILL.md").read_bytes(), canonical)
                self.assertTrue((Path(d) / root / "skills/kieu-resource-discovery/references/states-and-boundaries.md").is_file())
            code, _, _ = subprocess_cli("install-skill", "--project", d)  # idempotent
            self.assertEqual(code, 0)
            (Path(d) / ".claude/skills/kieu-resource-discovery/SKILL.md").write_text("local edit")
            code, out, _ = subprocess_cli("install-skill", "--project", d, "--format", "json")
            self.assertEqual(code, 6)


class SkillContractTest(unittest.TestCase):
    def test_entrypoints_resolve_to_canonical(self):
        canon = (REPO / "skills/kieu-resource-discovery/SKILL.md").read_bytes()
        for rel in (".agents/skills", ".claude/skills", "src/kieu_open_resources/skills"):
            self.assertEqual((REPO / rel / "kieu-resource-discovery/SKILL.md").read_bytes(), canon, rel)

    def test_frontmatter(self):
        text = (REPO / "skills/kieu-resource-discovery/SKILL.md").read_text()
        head = text.split("---")[1]
        self.assertIn("name: kieu-resource-discovery", head)
        desc = [l for l in head.splitlines() if l.startswith("description:")][0][len("description:"):].strip()
        self.assertTrue(0 < len(desc) <= 1024)

    def test_leetcode_skill_untouched(self):
        self.assertTrue((REPO / "skills/kieu-leetcode-video/SKILL.md").is_file())
        self.assertIn("skills/kieu-leetcode-video/SKILL.md", (REPO / ".agents/skills/kieu-leetcode-video/SKILL.md").read_text())


class VietnameseQAScenarioTest(RegistryCase):
    """No eligible real dataset exists: the correct behaviour is an honest empty result + candidate review."""

    resources = [make_resource("kieu-leetcode-video", rtype="skill", status="candidate")]

    def test_no_result_then_candidate_workflow(self):
        code, env = self.cli("search", "vietnamese document", "--type", "dataset", "--status", "approved", "--task", "question-answering", "--language", "vi")
        self.assertEqual((code, env["data"]["total_matches"]), (0, 0))
        cand = make_resource("example-vi-docqa", status="candidate")
        cand.pop("approval")
        cand["license"] = {"id": "unknown", "status": "unknown", "evidence": []}
        cand["usage_rights"] = {}
        cand["submission"] = {"submitted_by": "agent:test", "use_cases": ["baseline"], "known_risks": ["license unknown"]}
        f = Path(self.tmp.name) / "cand.json"
        f.write_text(json.dumps(cand))
        code, env = self.cli("submit-candidate", str(f))
        self.assertEqual((code, env["data"]["status"]), (0, "candidate"))
        code, env = self.cli("search", "vietnamese", "--type", "dataset", "--status", "approved")
        self.assertEqual(env["data"]["total_matches"], 0)
        code, env = self.cli("manifest", "add", "example-vi-docqa", "--project", str(self.project))
        self.assertEqual((code, env["error"]["code"]), (4, "NOT_FOUND"))  # candidates are not selectable at all
        code, env = self.cli("manifest", "validate", "--project", str(self.project))
        self.assertEqual(env["data"]["entries"], 0)


class ApprovedFlowTest(RegistryCase):
    resources = [make_resource("vi-docs"), make_resource("vi-docs-2", description="second"), make_resource("vi-model", rtype="model", languages=["vi"], tasks=["question-answering"])]

    def test_end_to_end(self):
        c, env = self.cli("search", "--type", "dataset", "--task", "question-answering", "--language", "vi", "--status", "approved")
        self.assertEqual([r["id"] for r in env["data"]["results"]], ["vi-docs", "vi-docs-2"])
        c, env = self.cli("license-check", "vi-docs", "--operation", "fine-tuning", "--commercial-use")
        self.assertEqual(env["data"]["decision"], "unresolved")
        c, env = self.cli("preview", "vi-docs", "--limit", "2")
        self.assertEqual(env["data"]["returned"], 2)
        c, env = self.cli("quickstart", "vi-docs")
        self.assertEqual(c, 0)
        c, env = self.cli("manifest", "add", "vi-docs", "--project", str(self.project), "--operation", "inference", "--rationale", "fits",
                          "--alternative", "vi-docs-2")
        self.assertEqual(c, 0, env)
        lock = json.loads((self.project / "kieu-resources.lock.json").read_text())
        self.assertEqual(lock["resources"][0]["id"], "vi-docs")
        c, env = self.cli("manifest", "validate", "--project", str(self.project))
        self.assertEqual((c, env["data"]["ok"]), (0, True))
        c, env = self.cli("history", "vi-docs")
        self.assertEqual(c, 0)
        c, env = self.cli("review", "vi-docs", "--to", "deprecated", "--reviewer", "m", "--evidence-ref", "https://example.org/x", "--claim", "c")
        self.assertEqual((c, env["error"]["code"]), (6, "WRITE_REFUSED"))
        c, env = self.cli("review", "vi-docs", "--to", "deprecated", "--reviewer", "m", "--evidence-ref", "https://example.org/x", "--claim", "c", "--confirm")
        self.assertEqual(c, 0, env)
        c, env = self.cli("manifest", "validate", "--project", str(self.project))
        self.assertEqual(c, 6)
        self.assertFalse(env["data"]["ok"])


if __name__ == "__main__":
    unittest.main()
