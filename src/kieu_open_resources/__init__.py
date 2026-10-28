"""Kieu Open Resources core SDK.

One implementation of registry loading, validation, search, license checks,
comparison, history, manifests and candidate handling. The CLI (and later MCP
and web interfaces) are thin callers of this package.
"""

__version__ = "0.2.0"
CONTRACT = "kieu-open-resources/v1"

from .candidates import CandidateSubmission, ReviewWorkflow  # noqa: E402
from .discovery import ResourceDiscovery  # noqa: E402
from .errors import KieuError  # noqa: E402
from .evaluation import EvaluationRepository, ResourceHistory  # noqa: E402
from .licensing import ResourceLicenseChecker  # noqa: E402
from .manifest import ResourceManifest  # noqa: E402
from .registry import ResourceRegistry  # noqa: E402
from .search import ResourceSearch  # noqa: E402

__all__ = [
    "CandidateSubmission", "EvaluationRepository", "KieuError", "ResourceDiscovery", "ResourceHistory",
    "ResourceLicenseChecker", "ResourceManifest", "ResourceRegistry", "ResourceSearch", "ReviewWorkflow",
]
