"""Structured errors shared by every interface (SDK, CLI, future MCP/web)."""

EXIT_OK = 0
EXIT_UNEXPECTED = 1
EXIT_USAGE = 2
EXIT_REGISTRY = 3
EXIT_NOT_FOUND = 4
EXIT_POLICY = 5
EXIT_CONFLICT = 6

_EXIT = {
    "INVALID_INPUT": EXIT_USAGE,
    "PATH_UNSAFE": EXIT_USAGE,
    "REGISTRY_NOT_FOUND": EXIT_REGISTRY,
    "REGISTRY_INVALID": EXIT_REGISTRY,
    "NOT_FOUND": EXIT_NOT_FOUND,
    "POLICY_BLOCKED": EXIT_POLICY,
    "UNSUPPORTED": EXIT_POLICY,
    "CONFLICT": EXIT_CONFLICT,
    "WRITE_REFUSED": EXIT_CONFLICT,
    "INVALID_TRANSITION": EXIT_CONFLICT,
}


class KieuError(Exception):
    """An expected, reportable failure with a stable machine-readable code."""

    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    @property
    def exit_code(self):
        return _EXIT.get(self.code, EXIT_UNEXPECTED)

    def as_dict(self):
        out = {"code": self.code, "message": self.message}
        if self.details:
            out["details"] = self.details
        return out
