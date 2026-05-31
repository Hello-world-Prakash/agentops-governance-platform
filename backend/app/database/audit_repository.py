import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models import Approval, AuditLog
from app.events.event_bus import publish_trace_event
from app.governance.pii_detector import mask_pii


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
    masked_user_request = mask_pii(user_request)
    masked_agent_output = mask_pii(agent_output)
    row = AuditLog(
        trace_id=trace_id,
        user_request=json.dumps(masked_user_request),
        agent_name=agent_name,
        action_requested=action_requested,
        agent_output=json.dumps(masked_agent_output),
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
    publish_trace_event(
        trace_id,
        "audit_log_created",
        {
            "agent_name": agent_name,
            "action_requested": action_requested,
            "governance_decision": row.governance_decision,
            "risk_score": row.risk_score,
            "risk_level": row.risk_level,
            "approval_status": row.approval_status,
            "final_status": row.final_status,
        },
    )
    return row


def create_approval(db: Session, trace_id: str, action_requested: str) -> Approval:
    row = Approval(trace_id=trace_id, action_requested=action_requested, status="pending")
    db.add(row)
    db.commit()
    db.refresh(row)
    publish_trace_event(trace_id, "approval_created", {"approval_id": row.id, "action_requested": action_requested, "status": row.status})
    return row


def list_audit_logs(db: Session) -> List[AuditLog]:
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()


def get_audit_by_trace_id(db: Session, trace_id: str) -> Optional[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.trace_id == trace_id).first()


def list_pending_approvals(db: Session) -> List[Approval]:
    return db.query(Approval).filter(Approval.status == "pending").all()


def list_approvals(db: Session, status: Optional[str] = None) -> List[Approval]:
    query = db.query(Approval)
    if status:
        query = query.filter(Approval.status == status)
    return query.order_by(Approval.created_at.desc()).all()


def update_approval_status(db: Session, approval_id: int, status: str, reviewer_name: str, decision_comment: str) -> Optional[Approval]:
    row = db.query(Approval).filter(Approval.id == approval_id).first()
    if row is None:
        return None
    row.status = status
    row.reviewer_name = reviewer_name
    row.decision_comment = decision_comment
    row.decided_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    publish_trace_event(
        row.trace_id,
        "approval_decided",
        {
            "approval_id": row.id,
            "status": row.status,
            "reviewer_name": row.reviewer_name,
            "decision_comment": row.decision_comment,
            "decided_at": row.decided_at,
        },
    )
    return row
