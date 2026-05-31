import re
from typing import Dict

from app.governance.policy_engine import evaluate_policy
from app.governance.prompt_injection_detector import detect_prompt_injection
from app.governance.risk_scorer import calculate_risk


def mask_sensitive_fields(value: str) -> str:
    value = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "***-**-****", value)
    value = re.sub(r"\b\d{16}\b", "****-****-****-****", value)
    return value


def evaluate_governance(
    agent_name: str,
    action_requested: str,
    claim_text: str,
    claim_amount: float,
    confidence_score: float,
    fraud_score: float,
    policy_ambiguity: bool = False,
) -> Dict[str, object]:
    injection = detect_prompt_injection(claim_text)
    risk = calculate_risk(
        action_requested=action_requested,
        claim_amount=claim_amount,
        confidence_score=confidence_score,
        fraud_score=fraud_score,
        text=claim_text,
        policy_ambiguity=policy_ambiguity,
    )

    if injection["detected"]:
        return {
            "decision": "blocked",
            "policy_reasons": ["Prompt injection detected", *injection["matches"]],
            "risk": risk,
            "prompt_injection": injection,
        }

    policy = evaluate_policy(
        agent_name,
        action_requested,
        {
            "claim_amount": claim_amount,
            "confidence_score": confidence_score,
            "fraud_score": fraud_score,
        },
    )
    return {
        "decision": policy["decision"],
        "policy_reasons": policy["reasons"],
        "risk": risk,
        "prompt_injection": injection,
    }

