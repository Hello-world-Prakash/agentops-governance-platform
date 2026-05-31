import json
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.claim_decision_agent import recommend_claim_action
from app.agents.claims_intake_agent import extract_claim_facts
from app.agents.fraud_risk_agent import calculate_fraud_risk
from app.agents.policy_retrieval_agent import retrieve_policy_evidence
from app.database.audit_repository import create_approval, create_audit_log
from app.database.db import get_db
from app.governance.governance_gateway import evaluate_governance, mask_sensitive_fields
from app.schemas.claim_schema import ClaimReviewRequest, ClaimReviewResponse

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("/review", response_model=ClaimReviewResponse)
def review_claim(request: ClaimReviewRequest, db: Session = Depends(get_db)) -> ClaimReviewResponse:
    trace_id = str(uuid.uuid4())
    claim = extract_claim_facts(request.claim_text, request.claim_amount, request.claim_type, request.customer_id)
    policy = retrieve_policy_evidence(request.claim_type, claim.incident_type)
    fraud = calculate_fraud_risk(claim)
    recommendation = recommend_claim_action(claim, policy, fraud)

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

    masked_request = request.model_dump()
    masked_request["claim_text"] = mask_sensitive_fields(masked_request["claim_text"])
    create_audit_log(
        db=db,
        trace_id=trace_id,
        user_request=masked_request,
        agent_name="claim_decision_agent",
        action_requested=recommendation.recommended_action,
        agent_output=json.loads(recommendation.model_dump_json()),
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

