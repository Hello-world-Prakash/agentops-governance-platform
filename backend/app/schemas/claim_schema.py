from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ClaimReviewRequest(BaseModel):
    customer_id: str
    claim_text: str
    claim_type: str
    claim_amount: float = Field(ge=0)


class ClaimIntakeOutput(BaseModel):
    claim_id: str
    customer_id: str
    incident_type: str
    claim_amount: float
    extracted_facts: Dict[str, Any]
    missing_documents: List[str]
    confidence_score: float


class PolicyEvidence(BaseModel):
    relevant_policy_clauses: List[str]
    exclusions: List[str]
    deductible: float
    coverage_limit: float
    confidence_score: float


class FraudRiskOutput(BaseModel):
    fraud_score: float
    fraud_level: str
    fraud_reasons: List[str]


class ClaimDecisionOutput(BaseModel):
    recommended_action: str
    reasoning: str
    confidence_score: float
    evidence: List[str]


class ClaimReviewResponse(BaseModel):
    trace_id: str
    claim: ClaimIntakeOutput
    policy: PolicyEvidence
    fraud: FraudRiskOutput
    recommendation: ClaimDecisionOutput
    governance: Dict[str, Any]
    approval_id: Optional[int] = None

