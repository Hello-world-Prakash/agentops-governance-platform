import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models import Approval, AuditLog


def create_audit_log(
    db: Session,
    trace_id: str,
    user_request: Dict[str, Any],
    agent_name: str,
    action_requested: str,
    agent_output: Dict[str, Any],
    governance: Dict[str, Any],
    approval_status: str,
    final_status: str,
) -> AuditLog:
    risk = governance["risk"]
    row = AuditLog(
        trace_id=trace_id,
        user_request=json.dumps(user_request),
        agent_name=agent_name,
        action_requested=action_requested,
        agent_output=json.dumps(agent_output),
        governance_decision=str(governance["decision"]),
        policy_reasons=json.dumps(governance["policy_reasons"]),
        risk_score=float(risk["risk_score"]),
        risk_level=str(risk["risk_level"]),
        prompt_injection_detected=bool(governance["prompt_injection"]["detected"]),
        approval_status=approval_status,
        final_status=final_status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_approval(db: Session, trace_id: str, action_requested: str) -> Approval:
    row = Approval(trace_id=trace_id, action_requested=action_requested, status="pending")
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def list_audit_logs(db: Session) -> List[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()


def get_audit_by_trace_id(db: Session, trace_id: str) -> Optional[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.trace_id == trace_id).first()


def list_pending_approvals(db: Session) -> List[Approval]:
    return db.query(Approval).filter(Approval.status == "pending").all()


def update_approval_status(db: Session, approval_id: int, status: str) -> Optional[Approval]:
    row = db.query(Approval).filter(Approval.id == approval_id).first()
    if row is None:
        return None
    row.status = status
    db.commit()
    db.refresh(row)
    return row

