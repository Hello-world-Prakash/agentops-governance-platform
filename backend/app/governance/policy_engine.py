from typing import Dict, List


AGENT_POLICIES: Dict[str, List[str]] = {
    "claims_intake_agent": ["extract_claim_facts", "summarize_claim"],
    "policy_retrieval_agent": ["retrieve_policy_evidence", "summarize_policy_clause"],
    "fraud_risk_agent": ["calculate_fraud_risk", "flag_suspicious_claim"],
    "claim_decision_agent": ["recommend_approve", "recommend_deny", "request_more_documents", "escalate"],
}

BLOCKED_ACTIONS = {"approve_claim", "deny_claim", "confirm_fraud", "delete_audit_logs"}


def evaluate_policy(agent_name: str, action_requested: str, context: Dict[str, object]) -> Dict[str, object]:
    reasons: List[str] = []
    decision = "approved"

    if action_requested in BLOCKED_ACTIONS and action_requested not in {"approve_claim", "deny_claim"}:
        return {"decision": "blocked", "reasons": [f"{action_requested} is a blocked action"]}

    allowed_actions = AGENT_POLICIES.get(agent_name, [])
    if action_requested not in allowed_actions:
        if action_requested in {"approve_claim", "deny_claim"}:
            reasons.append(f"{action_requested} requires human approval and cannot be finalized by an agent")
            decision = "human_approval_required"
        else:
            return {"decision": "blocked", "reasons": [f"{agent_name} is not allowed to perform {action_requested}"]}

    claim_amount = float(context.get("claim_amount", 0) or 0)
    confidence_score = float(context.get("confidence_score", 1) or 1)
    fraud_score = float(context.get("fraud_score", 0) or 0)

    if action_requested == "deny_claim":
        decision = "human_approval_required"
        reasons.append("Final claim denial requires human approval")
    if action_requested in {"approve_claim", "recommend_approve"} and claim_amount > 5000:
        decision = "human_approval_required"
        reasons.append("Claims above 5000 require human approval before approval")
    if confidence_score < 0.75:
        decision = "manual_review_required"
        reasons.append("Confidence score below 0.75 requires manual review")
    if fraud_score > 0.7:
        decision = "manual_review_required"
        reasons.append("Fraud score above 0.7 requires manual review")

    return {"decision": decision, "reasons": reasons or ["Policy checks passed"]}


def list_agent_policies() -> Dict[str, List[str]]:
    return AGENT_POLICIES
