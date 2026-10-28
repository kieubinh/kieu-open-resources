import json
import unittest

from helpers import RegistryCase, clone, make_resource, write_registry
from kieu_open_resources import ResourceRegistry
from kieu_open_resources.errors import KieuError
from kieu_open_resources.schema import can_transition, validate_resource


def errors(r):
    return [i for i in validate_resource(r) if i["severity"] == "error"]


class SchemaTest(unittest.TestCase):
    def test_valid_resource(self):
        self.assertEqual(errors(make_resource()), [])

    def test_missing_required_metadata(self):
        r = make_resource()
        del r["source"]["revision"], r["maintainer"]
        paths = {i["path"] for i in errors(r)}
        self.assertIn("$.source.revision", paths)
        self.assertIn("$.maintainer", paths)

    def test_unknown_field_and_type_rejected(self):
        self.assertTrue(errors(make_resource(surprise=1)))
        self.assertTrue(errors(make_resource(type="gadget")))

    def test_urls_and_versions(self):
        r = make_resource()
        r["source"]["url"] = "http://user:pw@example.org/x"
        r["source"]["revision"] = "not a hex!"
        self.assertEqual({i["path"] for i in errors(r)}, {"$.source.url", "$.source.revision"})
        r["source"].update(url="https://example.org/x", revision="zzzz", revision_type="commit")
        self.assertIn("$.source.revision", {i["path"] for i in errors(r)})

    def test_approved_needs_license_evidence_and_review_history(self):
        r = make_resource()
        r["license"]["status"] = "unverified"
        r["license"]["evidence"] = []
        self.assertGreaterEqual(len(errors(r)), 2)
        r = make_resource()
        r["approval"]["history"] = []
        self.assertTrue(any("review history" in i["message"] for i in errors(r)))

    def test_review_requires_evidence(self):
        r = make_resource()
        r["approval"]["history"][0]["evidence"] = []
        self.assertTrue(errors(r))

    def test_unsupported_transition_rejected(self):
        r = make_resource(status="approved")
        r["approval"]["history"] = [{"from": "candidate", "to": "approved", "date": "2026-01-02", "reviewer": "x",
                                      "evidence": [{"url": "https://example.org/e", "claim": "c"}]}]
        self.assertTrue(any("unsupported transition" in i["message"] for i in errors(r)))
        self.assertFalse(can_transition("deprecated", "approved"))
        self.assertTrue(can_transition("under_review", "approved"))

    def test_history_must_end_at_status(self):
        r = make_resource(status="approved")
        r["approval"]["status"] = "restricted"
        self.assertTrue(errors(r))

    def test_dataset_details_validated(self):
        r = make_resource()
        r["details"]["size_bytes"] = -1
        r["details"]["preview"]["sample_rows"] = [{"a": 1}] * 21
        self.assertEqual(len(errors(r)), 2)


class RegistryTest(RegistryCase):
    resources = [make_resource("a-one"), make_resource("b-two")]

    def test_load_and_get(self):
        reg = ResourceRegistry(self.root)
        self.assertEqual([r["id"] for r in reg.list()], ["a-one", "b-two"])
        with self.assertRaises(KieuError) as cm:
            reg.get("nope")
        self.assertEqual(cm.exception.code, "NOT_FOUND")

    def test_empty_registry(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            write_registry(d, [])
            self.assertEqual(ResourceRegistry(d).list(), [])
            self.assertTrue(ResourceRegistry(d).validate()["ok"])

    def test_duplicate_id_detected(self):
        (self.root / "resources" / "tools").mkdir(exist_ok=True)
        dup = make_resource("a-one", rtype="tool")
        (self.root / "resources" / "tools" / "a-one.json").write_text(json.dumps(dup))
        rep = ResourceRegistry(self.root).validate()
        self.assertFalse(rep["ok"])
        self.assertTrue(any("duplicate id" in e["message"] for e in rep["errors"]))

    def test_corrupted_metadata_blocks_strict_load(self):
        (self.root / "resources" / "datasets" / "bad.json").write_text("{not json")
        with self.assertRaises(KieuError) as cm:
            ResourceRegistry(self.root).list()
        self.assertEqual(cm.exception.code, "REGISTRY_INVALID")

    def test_filename_and_directory_must_match(self):
        r = make_resource("c-three")
        (self.root / "resources" / "models").mkdir(exist_ok=True)
        (self.root / "resources" / "models" / "wrong.json").write_text(json.dumps(r))
        msgs = " ".join(e["message"] for e in ResourceRegistry(self.root).validate()["errors"])
        self.assertIn("filename must be", msgs)
        self.assertIn("belongs in datasets/", msgs)

    def test_missing_registry(self):
        with self.assertRaises(KieuError) as cm:
            ResourceRegistry.locate(explicit="/nonexistent/registry")
        self.assertEqual(cm.exception.code, "REGISTRY_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
