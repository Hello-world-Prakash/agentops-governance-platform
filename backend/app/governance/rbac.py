from typing import Dict, List


ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "Admin": ["manage_policies", "manage_users", "manage_agents", "submit_claims", "review_claims", "approve_high_risk", "view_audit_logs", "view_dashboard"],
    "Claims Adjuster": ["submit_claims", "review_claims", "view_dashboard"],
    "Risk Reviewer": ["approve_high_risk", "review_claims", "view_audit_logs", "view_dashboard"],
    "Auditor": ["view_audit_logs", "view_dashboard"],
    "Read-only Viewer": ["view_dashboard"],
}


def has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])

