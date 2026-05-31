from fastapi import APIRouter

from app.governance.policy_engine import evaluate_policy, list_agent_policies
from app.schemas.policy_schema import PolicyEvaluationRequest

router = APIRouter(prefix="/policies", tags=["policies"])


@router.get("")
def policies():
    return {"agent_policies": list_agent_policies()}


@router.post("/evaluate")
def evaluate(request: PolicyEvaluationRequest):
    return evaluate_policy(request.agent_name, request.action_requested, request.context)

