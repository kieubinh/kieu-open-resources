"""Remote-first client: no fallback registry or local license policy."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .registry import ResourceError


def call(operation, arguments, *, url=None, token=None):
    url = url or os.environ.get("KIEU_RESOURCE_URL")
    token = token or os.environ.get("KIEU_RESOURCE_TOKEN")
    if not url or not token:
        raise ResourceError("CONFIG_REQUIRED", "set KIEU_RESOURCE_URL and KIEU_RESOURCE_TOKEN", 2)
    if not url.startswith(("https://", "http://127.0.0.1:", "http://localhost:")):
        raise ResourceError("INVALID_CONFIG", "HTTPS is required outside localhost", 2)
    body = json.dumps({"operation": operation, "arguments": arguments}).encode()
    request = Request(url.rstrip("/") + "/v1/operations", body, {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
    except HTTPError as exc:
        try:
            error = json.load(exc)["error"]
        except (ValueError, KeyError):
            error = {"code": "HTTP_ERROR", "message": f"server returned {exc.code}"}
        raise ResourceError(error["code"], error["message"], exc.code) from exc
    except URLError as exc:
        raise ResourceError("SERVICE_UNAVAILABLE", str(exc.reason), 503) from exc
    if not payload.get("ok"):
        error = payload.get("error", {})
        raise ResourceError(error.get("code", "SERVER_ERROR"), error.get("message", "server error"), 503)
    return payload["value"]
