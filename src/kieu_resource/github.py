"""Bounded, review-only GitHub source revision synchronization."""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from .registry import ResourceError


def latest_commit(source_url, ref=None):
    parsed = urlparse(source_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ResourceError("UNSUPPORTED", "source is not a GitHub repository")
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2 or not all(re.fullmatch(r"[A-Za-z0-9_.-]+", x) for x in parts[:2]):
        raise ResourceError("INVALID_METADATA", "invalid GitHub repository URL")
    owner, repo = parts[:2]
    repo = repo.removesuffix(".git")
    if ref and (not isinstance(ref, str) or len(ref) > 100 or not re.fullmatch(r"[A-Za-z0-9_./-]+", ref)):
        raise ResourceError("INVALID_METADATA", "invalid GitHub ref")
    path = f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}/commits"
    if ref:
        path += "/" + quote(ref, safe="")
    else:
        path += "?per_page=1"
    request = Request(path, headers={"Accept": "application/vnd.github+json", "User-Agent": "kieu-resource/0.1"})
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read(65537)
    except (HTTPError, URLError) as exc:
        raise ResourceError("SOURCE_UNAVAILABLE", "GitHub revision could not be checked", 503) from exc
    if len(raw) > 65536:
        raise ResourceError("SOURCE_UNAVAILABLE", "GitHub response too large", 503)
    try:
        data = json.loads(raw)
        commit = data[0] if isinstance(data, list) else data
        sha = commit["sha"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise ResourceError("SOURCE_UNAVAILABLE", "GitHub returned invalid revision metadata", 503) from exc
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ResourceError("SOURCE_UNAVAILABLE", "GitHub returned an invalid commit SHA", 503)
    return sha
