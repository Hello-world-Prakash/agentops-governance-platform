import re
from typing import Dict, List


SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\bssn\b", re.IGNORECASE),
    re.compile(r"\b\d{16}\b"),
]


def has_sensitive_data(text: str) -> bool:
    return any(pattern.search(text) for pattern in SENSITIVE_PATTERNS)


def calculate_risk(
    action_requested: str,
    claim_amount: float,
    confidence_score: float,
    fraud_score: float,
    text: str,
    policy_ambiguity: bool = False,
) -> Dict[str, object]:
    score = 0.0
    reasons: List[str] = []

    if action_requested in {"recommend_deny", "deny_claim"}:
        score += 0.25
        reasons.append("Denial-related action")
    if claim_amount > 5000:
        score += 0.25
        reasons.append("High claim amount")
    if confidence_score < 0.75:
        score += 0.25
        reasons.append("Low confidence")
    if fraud_score > 0.7:
        score += 0.25
        reasons.append("High fraud risk")
    elif fraud_score > 0.4:
        score += 0.15
        reasons.append("Elevated fraud risk")
    if has_sensitive_data(text):
        score += 0.15
        reasons.append("Sensitive data present")
    if policy_ambiguity:
        score += 0.15
        reasons.append("Policy evidence is ambiguous")

    risk_score = min(round(score, 2), 1.0)
    if risk_score >= 0.85:
        level = "critical"
    elif risk_score >= 0.6:
        level = "high"
    elif risk_score >= 0.3:
        level = "medium"
    else:
        level = "low"

    return {"risk_score": risk_score, "risk_level": level, "risk_reasons": reasons or ["Low deterministic risk"]}

