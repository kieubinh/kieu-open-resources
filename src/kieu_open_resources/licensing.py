"""ResourceLicenseChecker: operation-specific usage-rights decisions.

Approval and license eligibility are separate questions. ``decision`` answers
"do documented rights allow this operation?"; ``usable`` additionally requires
approved status. Unknown, unverified or conflicting rights are never permission.
"""

from .errors import KieuError
from .schema import OPERATIONS, license_conflicts


class ResourceLicenseChecker:
    def check(self, resource, operation, commercial_use=False):
        if operation not in OPERATIONS:
            raise KieuError("INVALID_INPUT", "unknown operation '%s'; expected one of: %s" % (operation, ", ".join(OPERATIONS)))
        lic = resource.get("license", {})
        rights = resource.get("usage_rights", {})
        required = [operation] + (["commercial-use"] if commercial_use and operation != "commercial-use" else [])
        perms = {op: rights.get(op, "unknown") for op in required}
        conflicts = license_conflicts(resource)
        reasons = []
        for op, perm in perms.items():
            if perm == "prohibited":
                reasons.append("%s is prohibited" % op)
        if reasons:
            decision = "prohibited"
        else:
            if conflicts:
                reasons.append("conflicting license information")
            if lic.get("status") != "verified":
                reasons.append("license status is '%s', not verified" % lic.get("status", "unknown"))
            for op, perm in perms.items():
                if perm == "unknown":
                    reasons.append("rights for %s are unknown" % op)
            if reasons:
                decision = "unresolved"
            elif any(p == "conditional" for p in perms.values()):
                decision = "conditional"
                reasons.append("permitted only under documented conditions; see restrictions")
            else:
                decision = "permitted"
                reasons.append("documented as permitted with verified license evidence")
        status = resource["approval"]["status"]
        return {
            "id": resource["id"],
            "operation": operation,
            "commercial_use": bool(commercial_use),
            "decision": decision,
            "approval_status": status,
            "usable": decision == "permitted" and status == "approved",
            "license": {"id": lic.get("id"), "status": lic.get("status")},
            "rights": perms,
            "reasons": reasons,
            "conflicts": conflicts,
            "restrictions": list(resource.get("restrictions", [])),
            "evidence": list(lic.get("evidence", [])),
            "note": "Registry assessment of documented terms, not legal advice. Re-read the original terms before relying on it.",
        }
