from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from app.database.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_request = Column(Text, nullable=False)
    agent_name = Column(String, nullable=False)
    action_requested = Column(String, nullable=False)
    agent_output = Column(Text, nullable=False)
    governance_decision = Column(String, nullable=False)
    policy_reasons = Column(Text, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    prompt_injection_detected = Column(Boolean, default=False)
    approval_status = Column(String, nullable=False)
    final_status = Column(String, nullable=False)


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, index=True, nullable=False)
    action_requested = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    reviewer_name = Column(String, nullable=True)
    decision_comment = Column(Text, nullable=True)


class EvaluationTestCase(Base):
    __tablename__ = "evaluation_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, index=True, nullable=False)
    input_payload = Column(Text, nullable=False)
    expected_governance_decision = Column(String, nullable=False)
    expected_risk_level = Column(String, nullable=False)
    expected_prompt_injection_detected = Column(Boolean, default=False, nullable=False)
    expected_pii_masking_applied = Column(Boolean, default=False, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_type = Column(String, index=True, nullable=False)
    status = Column(String, default="running", nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    total_tests = Column(Integer, default=0, nullable=False)
    passed_tests = Column(Integer, default=0, nullable=False)
    failed_tests = Column(Integer, default=0, nullable=False)
    critical_failure_count = Column(Integer, default=0, nullable=False)


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, index=True, nullable=False)
    test_case_id = Column(Integer, nullable=True)
    scenario_id = Column(Integer, nullable=True)
    test_case_name = Column(String, nullable=False)
    category = Column(String, index=True, nullable=False)
    input_prompt = Column(Text, nullable=False)
    expected_governance_decision = Column(String, nullable=False)
    actual_governance_decision = Column(String, nullable=False)
    expected_risk_level = Column(String, nullable=False)
    actual_risk_level = Column(String, nullable=False)
    expected_prompt_injection_detected = Column(Boolean, default=False, nullable=False)
    actual_prompt_injection_detected = Column(Boolean, default=False, nullable=False)
    expected_pii_masking_applied = Column(Boolean, default=False, nullable=False)
    actual_pii_masking_applied = Column(Boolean, default=False, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(Text, nullable=False)
    trace_id = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RedTeamScenario(Base):
    __tablename__ = "red_team_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, index=True, nullable=False)
    input_prompt = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    expected_governance_decision = Column(String, nullable=False)
    expected_risk_level = Column(String, nullable=False)
    expected_prompt_injection_detected = Column(Boolean, default=True, nullable=False)
    expected_pii_masking_applied = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
