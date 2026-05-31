from app.governance.policy_engine import evaluate_policy


def test_deny_claim_requires_human_approval():
    result = evaluate_policy("claim_decision_agent", "deny_claim", {"claim_amount": 1000, "confidence_score": 0.9})
    assert result["decision"] == "human_approval_required"


def test_low_confidence_requires_manual_review():
    result = evaluate_policy("claim_decision_agent", "recommend_approve", {"claim_amount": 1000, "confidence_score": 0.6})
    assert result["decision"] == "manual_review_required"


def test_high_claim_amount_requires_approval():
    result = evaluate_policy("claim_decision_agent", "recommend_approve", {"claim_amount": 6000, "confidence_score": 0.9})
    assert result["decision"] == "human_approval_required"
