from app.governance.risk_scorer import calculate_risk


def test_risk_scorer_increases_for_sensitive_high_amount_claim():
    result = calculate_risk("recommend_approve", 9000, 0.9, 0.1, "SSN 123-45-6789")
    assert result["risk_score"] >= 0.4
    assert result["risk_level"] in {"medium", "high", "critical"}

