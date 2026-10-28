import unittest
from datetime import date

from helpers import RegistryCase, clone, make_resource
from kieu_open_resources import ResourceDiscovery, ResourceLicenseChecker, ResourceRegistry, ResourceSearch
from kieu_open_resources.errors import KieuError


def conflicted():
    r = make_resource("conflict")
    r["license"]["evidence"].append({"url": "https://example.org/other", "claim": "repo says MIT", "license_id": "MIT"})
    return r


class LicenseTest(unittest.TestCase):
    check = ResourceLicenseChecker().check

    def test_permitted(self):
        d = self.check(make_resource(), "inference", commercial_use=True)
        self.assertEqual((d["decision"], d["usable"]), ("permitted", True))

    def test_prohibited_training(self):
        self.assertEqual(self.check(make_resource(), "training")["decision"], "prohibited")

    def test_unknown_is_unresolved_not_permission(self):
        d = self.check(make_resource(), "fine-tuning")
        self.assertEqual(d["decision"], "unresolved")
        self.assertFalse(d["usable"])

    def test_conditional(self):
        self.assertEqual(self.check(make_resource(), "redistribution")["decision"], "conditional")

    def test_conflicting_license_unresolved(self):
        d = self.check(conflicted(), "use")
        self.assertEqual(d["decision"], "unresolved")
        self.assertTrue(d["conflicts"])

    def test_unverified_license_unresolved(self):
        r = make_resource()
        r["license"]["status"] = "unverified"
        self.assertEqual(self.check(r, "use")["decision"], "unresolved")

    def test_commercial_flag_adds_requirement(self):
        r = make_resource()
        r["usage_rights"]["commercial-use"] = "prohibited"
        self.assertEqual(self.check(r, "use", commercial_use=True)["decision"], "prohibited")
        self.assertEqual(self.check(r, "use")["decision"], "permitted")

    def test_permitted_license_but_not_approved_is_not_usable(self):
        r = make_resource(status="under_review")
        d = self.check(r, "use")
        self.assertEqual((d["decision"], d["usable"]), ("permitted", False))

    def test_unknown_operation(self):
        with self.assertRaises(KieuError):
            self.check(make_resource(), "teleport")


class SearchCompareTest(RegistryCase):
    resources = [
        make_resource("vi-qa-a"),
        make_resource("vi-qa-b", description="Another Vietnamese set", tasks=["summarization"]),
        make_resource("en-model", rtype="model", languages=["en"], tasks=["question-answering"], tags=["llm"]),
        make_resource("old-set", status="deprecated", **{"dates": {"added": "2020-01-01", "last_verified": "2020-01-01"}}),
        conflicted(),
    ]

    def setUp(self):
        super().setUp()
        self.reg = ResourceRegistry(self.root)
        self.s = ResourceSearch(self.reg)

    def ids(self, **kw):
        return [r["id"] for r in self.s.search(**kw)["results"]]

    def test_filters(self):
        self.assertEqual(self.ids(type="model"), ["en-model"])
        self.assertEqual(self.ids(language="vi", task="question-answering", statuses=["approved"]), ["conflict", "vi-qa-a"])
        self.assertEqual(self.ids(type="dataset", operation="training"), [])

    def test_default_excludes_deprecated(self):
        self.assertNotIn("old-set", self.ids())
        self.assertIn("old-set", self.ids(statuses=["deprecated"]))

    def test_operation_filter_excludes_conflicts_and_unknown(self):
        got = self.ids(operation="inference")
        self.assertIn("vi-qa-a", got)
        self.assertNotIn("conflict", got)
        self.assertEqual(self.ids(operation="fine-tuning"), [])

    def test_exclusion_reasons(self):
        out = self.s.search(operation="training", type="dataset", include_excluded=True)
        reasons = {x["id"]: x["reasons"] for x in out["excluded"]}
        self.assertTrue(any("prohibited" in r for r in reasons["vi-qa-a"]))
        self.assertTrue(any("type is model" in r for r in reasons["en-model"]))

    def test_deterministic_order_and_text(self):
        a = self.s.search(query="vietnamese")
        self.assertEqual(a, self.s.search(query="vietnamese"))
        self.assertTrue(a["results"])
        self.assertEqual(self.ids(query="zzz-nothing"), [])

    def test_freshness_and_limits(self):
        self.assertNotIn("old-set", self.ids(statuses=["deprecated", "approved"], verified_within_days=30, today=date(2026, 1, 10)))
        self.assertEqual(self.s.search(limit=1)["limit"], 1)
        with self.assertRaises(KieuError):
            self.s.search(limit=0)
        with self.assertRaises(KieuError):
            self.s.search(type="gadget")

    def test_size_filters(self):
        self.assertIn("vi-qa-a", self.ids(max_size_bytes=5000))
        self.assertEqual(self.ids(max_size_bytes=10), [])
        self.assertEqual(self.ids(max_params_b=2), ["en-model"])

    def test_external_scores_reorder_but_never_add(self):
        scores = {"vi-qa-b": 1.0, "old-set": 1.0}
        got = self.s.search(statuses=["approved"], relevance_scores=scores)["results"]
        self.assertEqual(got[0]["id"], "vi-qa-b")
        self.assertNotIn("old-set", [r["id"] for r in got])
        with self.assertRaises(KieuError):
            self.s.search(relevance_scores={"x": 5})

    def test_compare(self):
        d = ResourceDiscovery(self.reg).compare(["vi-qa-a", "vi-qa-b"], operation="inference", task="question-answering")
        self.assertEqual(d["usable_for_operation"], ["vi-qa-a", "vi-qa-b"])
        self.assertEqual(d["ai_generated_judgments"], [])
        self.assertEqual([r["suitability"]["task_match"] for r in d["resources"]], [True, False])
        for bad in (["vi-qa-a"], ["vi-qa-a", "vi-qa-a"], ["vi-qa-a", "missing"]):
            with self.assertRaises(KieuError):
                ResourceDiscovery(self.reg).compare(bad)


if __name__ == "__main__":
    unittest.main()
