from app.llm.local_llm import call_ollama
from app.schemas.claim_schema import ClaimDecisionOutput, ClaimIntakeOutput, FraudRiskOutput, PolicyEvidence


def recommend_claim_action(claim: ClaimIntakeOutput, policy: PolicyEvidence, fraud: FraudRiskOutput) -> ClaimDecisionOutput:
    evidence = list(policy.relevant_policy_clauses)
    if claim.missing_documents:
        action = "request_more_documents"
        base_reasoning = f"Missing required documents: {', '.join(claim.missing_documents)}."
        confidence = 0.78
    elif fraud.fraud_score > 0.7:
        action = "escalate"
        base_reasoning = "Fraud risk is high, so the claim should be manually reviewed."
        confidence = 0.8
    elif claim.claim_amount <= policy.coverage_limit:
        action = "recommend_approve"
        base_reasoning = "Claim amount appears within coverage limit and required evidence is present."
        confidence = 0.84
    else:
        action = "recommend_deny"
        base_reasoning = "Claim amount exceeds the deterministic policy coverage limit."
        confidence = 0.82

    llm_reasoning = call_ollama(
        prompt=f"Explain this deterministic recommendation briefly for an audit reviewer: {base_reasoning}",
        system="You explain deterministic reasoning only. Do not approve, deny, score risk, or override policy.",
    )
    return ClaimDecisionOutput(
        recommended_action=action,
        reasoning=llm_reasoning or base_reasoning,
        confidence_score=confidence,
        evidence=evidence,
    )

