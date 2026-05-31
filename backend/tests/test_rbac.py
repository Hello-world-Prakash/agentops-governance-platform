from app.governance.rbac import has_permission


def test_rbac_blocks_unauthorized_actions():
    assert has_permission("Auditor", "approve_high_risk") is False
    assert has_permission("Read-only Viewer", "submit_claims") is False
    assert has_permission("Claims Adjuster", "approve_high_risk") is False
    assert has_permission("Risk Reviewer", "approve_high_risk") is True
    assert has_permission("Admin", "manage_agents") is True

