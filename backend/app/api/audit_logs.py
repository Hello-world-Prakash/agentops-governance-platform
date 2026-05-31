import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.audit_repository import get_audit_by_trace_id, list_audit_logs
from app.database.db import get_db

router = APIRouter(prefix="/audit-logs", tags=["audit"])


def _serialize(row):
    return {
        "id": row.id,
        "trace_id": row.trace_id,
        "timestamp": row.timestamp,
        "user_request": json.loads(row.user_request),
        "agent_name": row.agent_name,
        "action_requested": row.action_requested,
        "agent_output": json.loads(row.agent_output),
        "governance_decision": row.governance_decision,
        "policy_reasons": json.loads(row.policy_reasons),
        "risk_score": row.risk_score,
        "risk_level": row.risk_level,
        "prompt_injection_detected": row.prompt_injection_detected,
        "approval_status": row.approval_status,
        "final_status": row.final_status,
    }


@router.get("")
def audit_logs(db: Session = Depends(get_db)):
    return [_serialize(row) for row in list_audit_logs(db)]


@router.get("/{trace_id}")
def audit_log(trace_id: str, db: Session = Depends(get_db)):
    row = get_audit_by_trace_id(db, trace_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return _serialize(row)

