import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.audit_repository import create_approval, create_audit_log
from app.database.db import get_db
from app.governance.governance_gateway import evaluate_governance
from app.orchestration.claim_workflow import run_claim_workflow
from app.schemas.claim_schema import ClaimReviewRequest, ClaimReviewResponse

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("/review", response_model=ClaimReviewResponse)
def review_claim(request: ClaimReviewRequest, db: Session = Depends(get_db)) -> ClaimReviewResponse:
    trace_id = str(uuid.uuid4())
    workflow = run_claim_workflow(request.customer_id, request.claim_text, request.claim_type, request.claim_amount)
    claim = workflow["claim"]
    policy = workflow["policy"]
    fraud = workflow["fraud"]
    recommendation = workflow["recommendation"]

    governance = evaluate_governance(
        agent_name="claim_decision_agent",
        action_requested=recommendation.recommended_action,
        claim_text=request.claim_text,
        claim_amount=request.claim_amount,
        confidence_score=min(claim.confidence_score, policy.confidence_score, recommendation.confidence_score),
        fraud_score=fraud.fraud_score,
        policy_ambiguity=policy.confidence_score < 0.75,
    )

    approval_id = None
    if governance["decision"] == "human_approval_required":
        approval = create_approval(db, trace_id, recommendation.recommended_action)
        approval_id = approval.id

    final_status = "blocked" if governance["decision"] == "blocked" else "pending_governance_resolution"
    if governance["decision"] == "approved":
        final_status = "recommendation_allowed"

    create_audit_log(
        db=db,
        trace_id=trace_id,
        user_request=request.model_dump(),
        agent_name="claim_decision_agent",
        action_requested=recommendation.recommended_action,
        agent_output={**recommendation.model_dump(), "orchestration_engine": workflow["orchestration_engine"]},
        governance=governance,
        approval_status="pending" if approval_id else "not_required",
        final_status=final_status,
    )

    return ClaimReviewResponse(
        trace_id=trace_id,
        claim=claim,
        policy=policy,
        fraud=fraud,
        recommendation=recommendation,
        governance=governance,
        approval_id=approval_id,
    )
