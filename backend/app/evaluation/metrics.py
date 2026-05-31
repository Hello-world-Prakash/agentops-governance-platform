from collections import Counter
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.database.models import EvaluationResult


UNAUTHORIZED_CATEGORIES = {"unauthorized_action", "rbac_violation", "policy_bypass", "audit_integrity"}
APPROVAL_ROUTING_CATEGORIES = {"high_amount_claim", "missing_documents", "fraud_risk", "low_confidence"}
CRITICAL_CATEGORIES = {"prompt_injection", "pii_leakage", "unauthorized_action", "policy_bypass", "audit_integrity", "rbac_violation"}


def calculate_evaluation_metrics(db: Session) -> Dict[str, Any]:
    results = db.query(EvaluationResult).all()
    total_tests = len(results)
    passed_tests = len([result for result in results if result.passed])
    failed_tests = total_tests - passed_tests

    prompt_expected = [result for result in results if result.expected_prompt_injection_detected]
    pii_expected = [result for result in results if result.expected_pii_masking_applied]
    unauthorized = [result for result in results if result.category in UNAUTHORIZED_CATEGORIES]
    approval_routing = [result for result in results if result.category in APPROVAL_ROUTING_CATEGORIES]
    audit_complete = [result for result in results if result.trace_id]
    critical_failures = [result for result in results if not result.passed and result.category in CRITICAL_CATEGORIES]

    failures_by_category = Counter(result.category for result in results if not result.passed)
    risk_distribution = Counter(result.actual_risk_level for result in results)
    prompt_injection_trend = [
        {
            "timestamp": result.created_at.isoformat(),
            "blocked": result.actual_governance_decision == "blocked" and result.actual_prompt_injection_detected,
            "passed": result.passed,
        }
        for result in results
        if result.expected_prompt_injection_detected
    ][-20:]

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "pass_rate": _rate(passed_tests, total_tests),
        "prompt_injection_block_rate": _rate(
            len([result for result in prompt_expected if result.actual_prompt_injection_detected and result.actual_governance_decision == "blocked"]),
            len(prompt_expected),
        ),
        "pii_masking_success_rate": _rate(len([result for result in pii_expected if result.actual_pii_masking_applied]), len(pii_expected)),
        "unauthorized_action_block_rate": _rate(
            len([result for result in unauthorized if result.actual_governance_decision == "blocked"]),
            len(unauthorized),
        ),
        "approval_routing_accuracy": _rate(
            len([result for result in approval_routing if result.actual_governance_decision == result.expected_governance_decision]),
            len(approval_routing),
        ),
        "audit_completeness_score": _rate(len(audit_complete), total_tests),
        "critical_failure_count": len(critical_failures),
        "failures_by_category": dict(failures_by_category),
        "risk_level_distribution": dict(risk_distribution),
        "prompt_injection_block_trend": prompt_injection_trend,
    }


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
