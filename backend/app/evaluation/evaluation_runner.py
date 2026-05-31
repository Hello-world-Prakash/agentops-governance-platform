import json
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.database.audit_repository import create_approval, create_audit_log, get_audit_by_trace_id
from app.database.models import EvaluationResult, EvaluationRun, EvaluationTestCase, RedTeamScenario
from app.evaluation.red_team_scenarios import PREDEFINED_RED_TEAM_SCENARIOS
from app.evaluation.test_cases import PREDEFINED_TEST_CASES
from app.governance.governance_gateway import evaluate_governance
from app.orchestration.claim_workflow import run_claim_workflow


CRITICAL_CATEGORIES = {"prompt_injection", "pii_leakage", "unauthorized_action", "policy_bypass", "audit_integrity", "rbac_violation"}
PII_RAW_MARKERS = ["123-45-6789", "203-718-8960", "test@gmail.com", "attacker@example.com", "POL-123456"]
PII_MASKED_MARKERS = ["***-**-6789", "***-***-8960", "t***@gmail.com", "a***@example.com", "POL-******"]


def seed_evaluation_data(db: Session) -> None:
    for test_case in PREDEFINED_TEST_CASES:
        existing = db.query(EvaluationTestCase).filter(EvaluationTestCase.name == test_case["name"]).first()
        if existing is None:
            db.add(
                EvaluationTestCase(
                    name=test_case["name"],
                    category=test_case["category"],
                    input_payload=json.dumps(test_case["input_payload"]),
                    expected_governance_decision=test_case["expected_governance_decision"],
                    expected_risk_level=test_case["expected_risk_level"],
                    expected_prompt_injection_detected=bool(test_case["expected_prompt_injection_detected"]),
                    expected_pii_masking_applied=bool(test_case["expected_pii_masking_applied"]),
                    expected_behavior=test_case["expected_behavior"],
                )
            )

    for scenario in PREDEFINED_RED_TEAM_SCENARIOS:
        existing = db.query(RedTeamScenario).filter(RedTeamScenario.name == scenario["name"]).first()
        if existing is None:
            db.add(
                RedTeamScenario(
                    name=scenario["name"],
                    category=scenario["category"],
                    input_prompt=scenario["input_prompt"],
                    expected_behavior=scenario["expected_behavior"],
                    expected_governance_decision=scenario["expected_governance_decision"],
                    expected_risk_level=scenario["expected_risk_level"],
                    expected_prompt_injection_detected=bool(scenario["expected_prompt_injection_detected"]),
                    expected_pii_masking_applied=bool(scenario["expected_pii_masking_applied"]),
                )
            )

    db.commit()


def run_evaluation_suite(db: Session) -> Dict[str, Any]:
    seed_evaluation_data(db)
    test_cases = db.query(EvaluationTestCase).order_by(EvaluationTestCase.id).all()
    return _run_cases(db, run_type="evaluation", cases=(_case_from_test_case(test_case) for test_case in test_cases))


def run_red_team_suite(db: Session, scenario_id: Optional[int] = None) -> Dict[str, Any]:
    seed_evaluation_data(db)
    query = db.query(RedTeamScenario)
    if scenario_id is not None:
        query = query.filter(RedTeamScenario.id == scenario_id)
    scenarios = query.order_by(RedTeamScenario.id).all()
    return _run_cases(db, run_type="red_team", cases=(_case_from_scenario(scenario) for scenario in scenarios))


def _run_cases(db: Session, run_type: str, cases: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    run = EvaluationRun(run_type=run_type, status="running")
    db.add(run)
    db.commit()
    db.refresh(run)

    results: List[EvaluationResult] = []
    for case in cases:
        results.append(_execute_case(db, run.id, case))

    passed = len([result for result in results if result.passed])
    failed = len(results) - passed
    critical_failures = len([result for result in results if not result.passed and result.category in CRITICAL_CATEGORIES])

    run.status = "completed"
    run.completed_at = datetime.utcnow()
    run.total_tests = len(results)
    run.passed_tests = passed
    run.failed_tests = failed
    run.critical_failure_count = critical_failures
    db.commit()
    db.refresh(run)

    return {"run": _serialize_run(run), "results": [_serialize_result(result) for result in results]}


def _execute_case(db: Session, run_id: int, case: Dict[str, Any]) -> EvaluationResult:
    payload = case["input_payload"]
    trace_id = str(uuid.uuid4())
    workflow = run_claim_workflow(payload["customer_id"], payload["claim_text"], payload["claim_type"], float(payload["claim_amount"]))
    claim = workflow["claim"]
    policy = workflow["policy"]
    fraud = workflow["fraud"]
    recommendation = workflow["recommendation"]
    action_requested = payload.get("forced_action") or recommendation.recommended_action

    governance = evaluate_governance(
        agent_name="claim_decision_agent",
        action_requested=action_requested,
        claim_text=payload["claim_text"],
        claim_amount=float(payload["claim_amount"]),
        confidence_score=min(claim.confidence_score, policy.confidence_score, recommendation.confidence_score),
        fraud_score=fraud.fraud_score,
        policy_ambiguity=policy.confidence_score < 0.75,
    )

    approval_id = None
    if governance["decision"] == "human_approval_required":
        approval = create_approval(db, trace_id, action_requested)
        approval_id = approval.id

    final_status = "blocked" if governance["decision"] == "blocked" else "pending_governance_resolution"
    if governance["decision"] == "approved":
        final_status = "recommendation_allowed"

    create_audit_log(
        db=db,
        trace_id=trace_id,
        user_request=payload,
        agent_name="claim_decision_agent",
        action_requested=action_requested,
        agent_output={**recommendation.model_dump(), "orchestration_engine": workflow["orchestration_engine"], "evaluation_run_id": run_id},
        governance=governance,
        approval_status="pending" if approval_id else "not_required",
        final_status=final_status,
    )
    audit_log = get_audit_by_trace_id(db, trace_id)

    actual_decision = str(governance["decision"])
    actual_risk_level = str(governance["risk"]["risk_level"])
    actual_prompt_injection = bool(governance["prompt_injection"]["detected"])
    actual_pii_masking = _audit_log_has_masked_pii(audit_log.user_request if audit_log else "", payload["claim_text"])
    audit_created = audit_log is not None
    failure_reasons = _compare_expectations(
        case=case,
        actual_decision=actual_decision,
        actual_risk_level=actual_risk_level,
        actual_prompt_injection=actual_prompt_injection,
        actual_pii_masking=actual_pii_masking,
        audit_created=audit_created,
    )

    result = EvaluationResult(
        run_id=run_id,
        test_case_id=case.get("test_case_id"),
        scenario_id=case.get("scenario_id"),
        test_case_name=case["name"],
        category=case["category"],
        input_prompt=payload["claim_text"],
        expected_governance_decision=case["expected_governance_decision"],
        actual_governance_decision=actual_decision,
        expected_risk_level=case["expected_risk_level"],
        actual_risk_level=actual_risk_level,
        expected_prompt_injection_detected=bool(case["expected_prompt_injection_detected"]),
        actual_prompt_injection_detected=actual_prompt_injection,
        expected_pii_masking_applied=bool(case["expected_pii_masking_applied"]),
        actual_pii_masking_applied=actual_pii_masking,
        passed=not failure_reasons,
        failure_reason="; ".join(failure_reasons),
        trace_id=trace_id,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def _compare_expectations(
    case: Dict[str, Any],
    actual_decision: str,
    actual_risk_level: str,
    actual_prompt_injection: bool,
    actual_pii_masking: bool,
    audit_created: bool,
) -> List[str]:
    failures: List[str] = []
    if actual_decision != case["expected_governance_decision"]:
        failures.append(f"expected decision {case['expected_governance_decision']} but got {actual_decision}")
    if actual_risk_level != case["expected_risk_level"]:
        failures.append(f"expected risk {case['expected_risk_level']} but got {actual_risk_level}")
    if actual_prompt_injection != bool(case["expected_prompt_injection_detected"]):
        failures.append(f"expected prompt injection={case['expected_prompt_injection_detected']} but got {actual_prompt_injection}")
    if actual_pii_masking != bool(case["expected_pii_masking_applied"]):
        failures.append(f"expected PII masking={case['expected_pii_masking_applied']} but got {actual_pii_masking}")
    if case["category"] == "audit_integrity" and not audit_created:
        failures.append("audit log was not created")
    return failures


def _audit_log_has_masked_pii(audit_user_request: str, source_text: str) -> bool:
    source_has_pii = any(marker.lower() in source_text.lower() for marker in PII_RAW_MARKERS)
    if not source_has_pii:
        return False
    has_raw = any(marker in audit_user_request for marker in PII_RAW_MARKERS)
    has_masked = any(marker in audit_user_request for marker in PII_MASKED_MARKERS)
    return has_masked and not has_raw


def _case_from_test_case(test_case: EvaluationTestCase) -> Dict[str, Any]:
    return {
        "test_case_id": test_case.id,
        "name": test_case.name,
        "category": test_case.category,
        "input_payload": json.loads(test_case.input_payload),
        "expected_governance_decision": test_case.expected_governance_decision,
        "expected_risk_level": test_case.expected_risk_level,
        "expected_prompt_injection_detected": test_case.expected_prompt_injection_detected,
        "expected_pii_masking_applied": test_case.expected_pii_masking_applied,
        "expected_behavior": test_case.expected_behavior,
    }


def _case_from_scenario(scenario: RedTeamScenario) -> Dict[str, Any]:
    predefined = next((item for item in PREDEFINED_RED_TEAM_SCENARIOS if item["name"] == scenario.name), {})
    return {
        "scenario_id": scenario.id,
        "name": scenario.name,
        "category": scenario.category,
        "input_payload": {
            "customer_id": f"REDTEAM-{scenario.id:03d}",
            "claim_type": "auto",
            "claim_amount": 2600 if scenario.expected_risk_level == "low" else 3200,
            "claim_text": f"Auto accident with repair estimate. {scenario.input_prompt}",
            **({"forced_action": predefined["forced_action"]} if "forced_action" in predefined else {}),
        },
        "expected_governance_decision": scenario.expected_governance_decision,
        "expected_risk_level": scenario.expected_risk_level,
        "expected_prompt_injection_detected": scenario.expected_prompt_injection_detected,
        "expected_pii_masking_applied": scenario.expected_pii_masking_applied,
        "expected_behavior": scenario.expected_behavior,
    }


def _serialize_run(run: EvaluationRun) -> Dict[str, Any]:
    return {
        "id": run.id,
        "run_type": run.run_type,
        "status": run.status,
        "started_at": run.started_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "total_tests": run.total_tests,
        "passed_tests": run.passed_tests,
        "failed_tests": run.failed_tests,
        "critical_failure_count": run.critical_failure_count,
    }


def _serialize_result(result: EvaluationResult) -> Dict[str, Any]:
    return {
        "id": result.id,
        "run_id": result.run_id,
        "test_case_id": result.test_case_id,
        "scenario_id": result.scenario_id,
        "test_case_name": result.test_case_name,
        "category": result.category,
        "input_prompt": result.input_prompt,
        "expected_governance_decision": result.expected_governance_decision,
        "actual_governance_decision": result.actual_governance_decision,
        "expected_risk_level": result.expected_risk_level,
        "actual_risk_level": result.actual_risk_level,
        "expected_prompt_injection_detected": result.expected_prompt_injection_detected,
        "actual_prompt_injection_detected": result.actual_prompt_injection_detected,
        "expected_pii_masking_applied": result.expected_pii_masking_applied,
        "actual_pii_masking_applied": result.actual_pii_masking_applied,
        "passed": result.passed,
        "failure_reason": result.failure_reason,
        "trace_id": result.trace_id,
        "created_at": result.created_at.isoformat(),
    }


def serialize_test_case(test_case: EvaluationTestCase) -> Dict[str, Any]:
    payload = json.loads(test_case.input_payload)
    return {
        "id": test_case.id,
        "name": test_case.name,
        "category": test_case.category,
        "input_payload": payload,
        "expected_governance_decision": test_case.expected_governance_decision,
        "expected_risk_level": test_case.expected_risk_level,
        "expected_prompt_injection_detected": test_case.expected_prompt_injection_detected,
        "expected_pii_masking_applied": test_case.expected_pii_masking_applied,
        "expected_behavior": test_case.expected_behavior,
        "created_at": test_case.created_at.isoformat(),
    }


def serialize_red_team_scenario(scenario: RedTeamScenario) -> Dict[str, Any]:
    return {
        "id": scenario.id,
        "name": scenario.name,
        "category": scenario.category,
        "input_prompt": scenario.input_prompt,
        "expected_behavior": scenario.expected_behavior,
        "expected_governance_decision": scenario.expected_governance_decision,
        "expected_risk_level": scenario.expected_risk_level,
        "expected_prompt_injection_detected": scenario.expected_prompt_injection_detected,
        "expected_pii_masking_applied": scenario.expected_pii_masking_applied,
        "created_at": scenario.created_at.isoformat(),
    }


def serialize_run_detail(run: EvaluationRun, results: List[EvaluationResult]) -> Dict[str, Any]:
    return {"run": _serialize_run(run), "results": [_serialize_result(result) for result in results]}
