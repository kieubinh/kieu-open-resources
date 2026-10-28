"""Authenticated HTTP API and small catalogue UI over the shared Registry."""

import hmac
import json
import os
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .registry import Registry, ResourceError

_CALLS = defaultdict(deque)


def dispatch(registry, operation, args, actor="reader"):
    if operation == "search_resources":
        if "approved" in args:
            raise ResourceError("INVALID_INPUT", "approval status cannot be overridden")
        return registry.search(**args)
    if operation == "get_resource":
        return registry.get(args["resource_id"])
    if operation == "list_collections":
        return registry.collections()
    if operation == "get_quick_start":
        return registry.quickstart(args["resource_id"])
    if operation == "preview_dataset":
        return registry.preview(args["resource_id"], args.get("limit", 3))
    if operation == "check_usage_rights":
        return registry.rights(args["resource_id"], args["operation"])
    if operation == "compare_resources":
        return registry.compare(args["resource_ids"], args.get("operation"))
    if operation == "get_resource_history":
        return registry.history(args["resource_id"])
    if operation == "generate_manifest":
        return registry.manifest(args["resource_ids"], args["project"], args["operation"])
    if operation == "submit_candidate":
        return registry.submit_candidate(args["resource"], actor)
    if operation == "save_resource_manifest":
        return registry.save_manifest(args["manifest"], actor)
    if operation == "submit_evaluation":
        return registry.submit_evaluation(args["resource_id"], args["finding"], actor)
    if operation == "sync_github_source":
        return registry.sync_github(args["resource_id"], actor)
    raise ResourceError("UNKNOWN_OPERATION", "unknown operation", 404)


class Handler(BaseHTTPRequestHandler):
    registry = None
    tokens = None
    audit_path = None
    rate_limit = 60

    def log_message(self, *_args):
        return

    def _send(self, status, value):
        body = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth(self, write=False):
        supplied = self.headers.get("Authorization", "")
        if not supplied.startswith("Bearer "):
            raise ResourceError("AUTH_REQUIRED", "Bearer credential required", 401)
        token = supplied[7:]
        for known, identity in self.tokens.items():
            if hmac.compare_digest(known, token):
                scope = identity["scope"] if isinstance(identity, dict) else identity
                actor = identity["id"] if isinstance(identity, dict) else scope
                self._actor = actor
                if write and scope != "write":
                    raise ResourceError("FORBIDDEN", "write credential required", 403)
                now = time.monotonic()
                calls = _CALLS[known]
                while calls and calls[0] < now - 60:
                    calls.popleft()
                if len(calls) >= self.rate_limit:
                    raise ResourceError("RATE_LIMITED", "request rate exceeded", 429)
                calls.append(now)
                return actor
        raise ResourceError("AUTH_REQUIRED", "invalid credential", 401)

    def _audit(self, operation, actor, status):
        event = {"time": time.time(), "operation": operation, "actor": actor, "status": status}
        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event) + "\n")
        except OSError as exc:
            raise ResourceError("AUDIT_UNAVAILABLE", "audit log unavailable", 503) from exc

    def _handle(self):
        path = urlsplit(self.path)
        if path.path == "/health":
            return self._send(200, {"ok": True})
        if path.path == "/":
            page = (Path(__file__).parent / "catalogue.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return
        if path.path != "/v1/operations" or self.command != "POST":
            raise ResourceError("NOT_FOUND", "route not found", 404)
        length = int(self.headers.get("Content-Length", "0"))
        if length < 2 or length > 65536:
            raise ResourceError("INVALID_INPUT", "request size must be 2 to 65536 bytes")
        try:
            payload = json.loads(self.rfile.read(length))
        except ValueError as exc:
            raise ResourceError("INVALID_INPUT", "invalid JSON") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("operation"), str) or not isinstance(payload.get("arguments", {}), dict):
            raise ResourceError("INVALID_INPUT", "operation and object arguments required")
        operation, args = payload["operation"], payload.get("arguments", {})
        self._operation = operation
        write = operation in {"submit_candidate", "save_resource_manifest", "submit_evaluation", "sync_github_source"}
        actor = self._auth(write)
        # Protected writes fail closed if auditing is unavailable.
        if write:
            self._audit(operation, actor, "attempt")
        try:
            result = dispatch(self.registry, operation, args, actor)
        except KeyError as exc:
            raise ResourceError("INVALID_INPUT", f"missing argument: {exc.args[0]}") from exc
        self._audit(operation, actor, "ok")
        self._send(200, {"ok": True, "value": result})

    def do_GET(self):
        try:
            self._handle()
        except ResourceError as exc:
            self._send(exc.status, {"ok": False, "error": exc.as_dict()})

    def do_POST(self):
        self._operation = "request"
        self._actor = "unknown"
        try:
            self._handle()
        except ResourceError as exc:
            try:
                self._audit(self._operation, self._actor, exc.code)
            except ResourceError:
                pass
            self._send(exc.status, {"ok": False, "error": exc.as_dict()})
        except (TypeError, ValueError) as exc:
            self._send(400, {"ok": False, "error": {"code": "INVALID_INPUT", "message": str(exc)}})


def main():
    path = os.environ.get("KIEU_RESOURCE_REGISTRY")
    read = os.environ.get("KIEU_RESOURCE_READ_TOKEN")
    write = os.environ.get("KIEU_RESOURCE_WRITE_TOKEN")
    configured = os.environ.get("KIEU_RESOURCE_CREDENTIALS")
    if not path:
        raise SystemExit("Set KIEU_RESOURCE_REGISTRY")
    if configured:
        try:
            tokens = json.loads(configured)
        except ValueError as exc:
            raise SystemExit("KIEU_RESOURCE_CREDENTIALS must be JSON") from exc
        if not isinstance(tokens, dict) or not tokens or any(not isinstance(token, str) or len(token) < 24 or not isinstance(value, dict) or value.get("scope") not in {"read", "write"} or not isinstance(value.get("id"), str) for token, value in tokens.items()):
            raise SystemExit("KIEU_RESOURCE_CREDENTIALS must map long tokens to id/scope objects")
    else:
        if not read or not write or read == write:
            raise SystemExit("Set distinct READ_TOKEN and WRITE_TOKEN, or KIEU_RESOURCE_CREDENTIALS")
        tokens = {read: {"id": "default-reader", "scope": "read"}, write: {"id": "default-writer", "scope": "write"}}
    Handler.registry = Registry(path)
    Handler.tokens = tokens
    Handler.audit_path = Path(os.environ.get("KIEU_RESOURCE_AUDIT", path + ".audit.jsonl"))
    Handler.rate_limit = int(os.environ.get("KIEU_RESOURCE_RATE_LIMIT", "60"))
    host = os.environ.get("KIEU_RESOURCE_HOST", "127.0.0.1")
    port = int(os.environ.get("KIEU_RESOURCE_PORT", "8765"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
