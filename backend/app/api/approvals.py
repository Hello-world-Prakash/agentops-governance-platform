from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.audit_repository import list_approvals, list_pending_approvals, update_approval_status
from app.database.db import get_db
from app.schemas.approval_schema import ApprovalDecisionRequest, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/pending", response_model=list[ApprovalResponse])
def pending_approvals(db: Session = Depends(get_db)):
    return list_pending_approvals(db)


@router.get("", response_model=list[ApprovalResponse])
def approvals(status: str | None = None, db: Session = Depends(get_db)):
    return list_approvals(db, status=status)


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve(approval_id: int, request: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    row = update_approval_status(db, approval_id, "approved", request.reviewer_name, request.decision_comment)
    if row is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return row


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
def reject(approval_id: int, request: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    row = update_approval_status(db, approval_id, "rejected", request.reviewer_name, request.decision_comment)
    if row is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return row


@router.post("/{approval_id}/manual-review", response_model=ApprovalResponse)
def manual_review(approval_id: int, request: ApprovalDecisionRequest, db: Session = Depends(get_db)):
    row = update_approval_status(db, approval_id, "sent_to_manual_review", request.reviewer_name, request.decision_comment)
    if row is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return row
