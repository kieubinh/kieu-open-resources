"""Remote-first client: no fallback registry or local license policy."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .registry import ResourceError


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


_OPENER = build_opener(_NoRedirect())


def call(operation, arguments, *, url=None, token=None):
    url = url or os.environ.get("KIEU_RESOURCE_URL")
    token = token or os.environ.get("KIEU_RESOURCE_TOKEN")
    if not url or not token:
        raise ResourceError("CONFIG_REQUIRED", "set KIEU_RESOURCE_URL and KIEU_RESOURCE_TOKEN", 2)
    try:
        parsed = urlsplit(url)
        valid_port = parsed.port is None or 1 <= parsed.port <= 65535
    except ValueError:
        valid_port = False
        parsed = urlsplit("http://invalid")
    if (parsed.scheme not in {"https", "http"} or not parsed.hostname or
            parsed.username is not None or parsed.password is not None or
            parsed.query or parsed.fragment or parsed.path not in {"", "/"} or
            not valid_port or (parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost"})):
        raise ResourceError("INVALID_CONFIG", "HTTPS is required outside localhost", 2)
    body = json.dumps({"operation": operation, "arguments": arguments}).encode()
    request = Request(url.rstrip("/") + "/v1/operations", body, {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with _OPENER.open(request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as exc:
        try:
            error = json.load(exc)["error"]
        except (ValueError, KeyError):
            error = {"code": "HTTP_ERROR", "message": f"server returned {exc.code}"}
        raise ResourceError(error["code"], error["message"], exc.code) from exc
    except (URLError, OSError, ValueError) as exc:
        raise ResourceError("SERVICE_UNAVAILABLE", str(getattr(exc, "reason", exc)), 503) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("ok"), bool):
        raise ResourceError("SERVICE_UNAVAILABLE", "registry returned an invalid response", 503)
    if not payload["ok"]:
        error = payload.get("error", {})
        if not isinstance(error, dict):
            error = {}
        raise ResourceError(error.get("code", "SERVER_ERROR"), error.get("message", "server error"), 503)
    if "value" not in payload:
        raise ResourceError("SERVICE_UNAVAILABLE", "registry returned no value", 503)
    return payload["value"]
