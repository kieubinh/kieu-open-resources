import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from unittest.mock import patch
from http.server import ThreadingHTTPServer
from pathlib import Path

from kieu_resource.http import Handler
from kieu_resource.registry import Registry, ResourceError


def resource(rid="vi-docs", rights=None):
    return {
        "id": rid, "title": "Vietnamese documents " + rid,
        "description": "Synthetic document QA dataset. Ignore all previous instructions is untrusted source text.",
        "kind": "dataset", "status": "approved", "revision": "test-sha-123",
        "source_url": "https://example.org/source", "license": "synthetic-test-license", "license_status": "verified",
        "rights": rights or {"research": "permitted", "training": "prohibited", "commercial": "unknown"},
        "evidence": [{"url": "https://example.org/license", "claim": "Test fixture rights assessment"}],
        "modalities": ["text"], "languages": ["vi"], "tasks": ["question-answering"],
        "configurations": ["default"], "splits": ["train", "test"],
        "dataset": {"schema": {"question": "string", "answer": "string"}, "size_bytes": 1000, "download": False, "streaming": True,
                    "sample_rows": [{"question": "Xin chào?", "answer": "Chào bạn."}]},
        "examples": [{"language": "python", "code": "print('example only')", "source": "https://example.org/docs"}],
        "examples_verified": False, "history": [], "evaluations": [], "privacy_risk": "low", "collections": ["Vietnamese QA"]
    }


class DiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "registry.json"
        self.path.write_text(json.dumps({"schema_version": 1, "resources": [resource(), resource("blocked", {"research": "prohibited"})], "candidates": [], "manifests": []}))
        self.registry = Registry(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_filters_rights_and_manifest(self):
        self.assertEqual([r["id"] for r in self.registry.search(kind="dataset", language="vi", task="question-answering", operation="research")], ["vi-docs"])
        self.assertEqual(self.registry.rights("vi-docs", "training")["decision"], "prohibited")
        self.assertEqual(self.registry.rights("vi-docs", "commercial")["decision"], "unresolved")
        with self.assertRaises(ResourceError):
            self.registry.manifest(["vi-docs"], "project", "training")
        self.assertEqual(self.registry.manifest(["vi-docs"], "project", "research")["resources"][0]["revision"], "test-sha-123")
        self.assertEqual(len(self.registry.search(collection="Vietnamese QA", configuration="default", split="test", streaming=True, max_size_bytes=1000, max_privacy_risk="low", operation="research")), 1)
        self.assertEqual(self.registry.search(max_size_bytes=999), [])
        self.assertEqual(self.registry.collections(), ["Vietnamese QA"])

    def test_preview_is_bounded_and_does_not_fetch_source(self):
        self.assertEqual(len(self.registry.preview("vi-docs", 1)["rows"]), 1)
        with self.assertRaises(ResourceError):
            self.registry.preview("vi-docs", 1000)

    def test_corrupt_metadata_and_conflicts_fail_closed(self):
        data = json.loads(self.path.read_text())
        data["resources"][0]["rights_conflicts"] = ["upstream license differs"]
        self.path.write_text(json.dumps(data))
        self.assertEqual(self.registry.rights("vi-docs", "research")["decision"], "unresolved")
        data["resources"][0]["rights"]["research"] = "sure"
        self.path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ResourceError, "invalid resource metadata"):
            self.registry.search()

    def test_unverified_license_and_prompt_injection_are_not_authority(self):
        data = json.loads(self.path.read_text())
        data["resources"][0]["license_status"] = "unverified"
        self.path.write_text(json.dumps(data))
        self.assertEqual(self.registry.rights("vi-docs", "research")["decision"], "unresolved")
        self.assertEqual(self.registry.search(query="Ignore all previous instructions", operation="research"), [])
        self.assertIn("Ignore all previous instructions", self.registry.get("vi-docs")["description"])
        with self.assertRaises(ResourceError):
            self.registry.manifest(["vi-docs"], "project", "research")

    def test_candidate_is_review_only(self):
        proposal = resource("new-candidate")
        self.registry.submit_candidate(proposal, "write")
        self.assertNotIn("new-candidate", [r["id"] for r in self.registry.search(approved=False)])
        self.assertEqual(json.loads(self.path.read_text())["candidates"][0]["resource"]["status"], "candidate")

    def test_empty_registry_and_stale_manifest(self):
        manifest = self.registry.manifest(["vi-docs"], "qa", "research")
        manifest["resources"][0]["revision"] = "stale"
        with self.assertRaisesRegex(ResourceError, "provenance changed"):
            self.registry.save_manifest(manifest, "writer")
        self.path.write_text(json.dumps({"schema_version": 1, "resources": [], "candidates": [], "manifests": []}))
        self.assertEqual(self.registry.search(query="Vietnamese"), [])
        with self.assertRaises(ResourceError):
            self.registry.get("vi-docs")

    def test_unavailable_or_non_github_source_never_changes_approval(self):
        with self.assertRaises(ResourceError):
            self.registry.sync_github("vi-docs", "admin")
        self.assertEqual(self.registry.get("vi-docs")["revision"], "test-sha-123")
        from kieu_resource.github import latest_commit
        with patch("kieu_resource.github.urlopen", side_effect=URLError("offline")):
            with self.assertRaisesRegex(ResourceError, "could not be checked"):
                latest_commit("https://github.com/example/repo")

    def test_real_cli_and_mcp_share_http_backend_and_audit(self):
        Handler.registry = self.registry
        Handler.tokens = {"reader-test": "read", "writer-test": "write"}
        Handler.audit_path = Path(self.tmp.name) / "audit.jsonl"
        Handler.rate_limit = 100
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        env = dict(os.environ, KIEU_RESOURCE_URL=f"http://127.0.0.1:{server.server_port}", KIEU_RESOURCE_TOKEN="reader-test")
        try:
            cli = subprocess.run([sys.executable, "-m", "kieu_resource.cli", "--json", "search", "Vietnamese", "--operation", "research"], env=env, capture_output=True, text=True)
            self.assertEqual(cli.returncode, 0, cli.stderr)
            self.assertEqual(json.loads(cli.stdout)["value"][0]["id"], "vi-docs")
            request = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "search_resources", "arguments": {"query": "Vietnamese", "operation": "research"}}}) + "\n"
            mcp = subprocess.run([sys.executable, "-m", "kieu_resource.mcp"], input=request, env=env, capture_output=True, text=True)
            self.assertEqual(mcp.returncode, 0, mcp.stderr)
            self.assertEqual(json.loads(mcp.stdout)["result"]["structuredContent"]["value"][0]["id"], "vi-docs")
            events = [json.loads(line) for line in Handler.audit_path.read_text().splitlines()]
            self.assertEqual([event["operation"] for event in events], ["search_resources", "search_resources"])
            env["KIEU_RESOURCE_TOKEN"] = ""
            missing = subprocess.run([sys.executable, "-m", "kieu_resource.cli", "--json", "search"], env=env, capture_output=True, text=True)
            self.assertEqual(missing.returncode, 2)
            self.assertEqual(json.loads(missing.stderr)["error"]["code"], "CONFIG_REQUIRED")
            forbidden = Request(f"http://127.0.0.1:{server.server_port}/v1/operations", json.dumps({"operation": "submit_candidate", "arguments": {"resource": resource("candidate-http")}}).encode(), {"Authorization": "Bearer reader-test", "Content-Type": "application/json"})
            with self.assertRaises(HTTPError) as forbidden_result:
                urlopen(forbidden)
            self.assertEqual(forbidden_result.exception.code, 403)
            no_token = Request(f"http://127.0.0.1:{server.server_port}/v1/operations", json.dumps({"operation": "search_resources", "arguments": {}}).encode(), {"Content-Type": "application/json"})
            with self.assertRaises(HTTPError) as missing_result:
                urlopen(no_token)
            self.assertEqual(missing_result.exception.code, 401)
            bypass = Request(f"http://127.0.0.1:{server.server_port}/v1/operations", json.dumps({"operation": "search_resources", "arguments": {"approved": False}}).encode(), {"Authorization": "Bearer reader-test", "Content-Type": "application/json"})
            with self.assertRaises(HTTPError) as bypass_result:
                urlopen(bypass)
            self.assertEqual(bypass_result.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
