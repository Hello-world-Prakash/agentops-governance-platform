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
