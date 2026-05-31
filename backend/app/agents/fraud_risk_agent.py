from typing import List

from app.schemas.claim_schema import ClaimIntakeOutput, FraudRiskOutput


def calculate_fraud_risk(claim: ClaimIntakeOutput) -> FraudRiskOutput:
    score = 0.1
    reasons: List[str] = []
    summary = str(claim.extracted_facts.get("summary", "")).lower()

    if claim.claim_amount > 7500:
        score += 0.25
        reasons.append("Claim amount is materially high")
    if "urgent" in summary or "cash" in summary:
        score += 0.2
        reasons.append("Unusual urgency or cash language")
    if len(claim.missing_documents) >= 2:
        score += 0.25
        reasons.append("Multiple key documents missing")

    fraud_score = min(round(score, 2), 1.0)
    if fraud_score > 0.7:
        level = "high"
    elif fraud_score > 0.4:
        level = "medium"
    else:
        level = "low"

    return FraudRiskOutput(fraud_score=fraud_score, fraud_level=level, fraud_reasons=reasons or ["No major fraud indicators"])

