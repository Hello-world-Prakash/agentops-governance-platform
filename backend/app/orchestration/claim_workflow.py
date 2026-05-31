from typing import Any, Dict, TypedDict

from app.agents.claim_decision_agent import recommend_claim_action
from app.agents.claims_intake_agent import extract_claim_facts
from app.agents.fraud_risk_agent import calculate_fraud_risk
from app.agents.policy_retrieval_agent import retrieve_policy_evidence
from app.schemas.claim_schema import ClaimDecisionOutput, ClaimIntakeOutput, FraudRiskOutput, PolicyEvidence


class ClaimWorkflowState(TypedDict, total=False):
    customer_id: str
    claim_text: str
    claim_type: str
    claim_amount: float
    claim: ClaimIntakeOutput
    policy: PolicyEvidence
    fraud: FraudRiskOutput
    recommendation: ClaimDecisionOutput
    orchestration_engine: str


def _intake_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    state["claim"] = extract_claim_facts(state["claim_text"], state["claim_amount"], state["claim_type"], state["customer_id"])
    return state


def _policy_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    claim = state["claim"]
    state["policy"] = retrieve_policy_evidence(state["claim_type"], claim.incident_type)
    return state


def _fraud_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    state["fraud"] = calculate_fraud_risk(state["claim"])
    return state


def _decision_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    state["recommendation"] = recommend_claim_action(state["claim"], state["policy"], state["fraud"])
    return state


def _run_deterministic_workflow(initial_state: ClaimWorkflowState) -> ClaimWorkflowState:
    state = _intake_node(initial_state)
    state = _policy_node(state)
    state = _fraud_node(state)
    state = _decision_node(state)
    state["orchestration_engine"] = "deterministic"
    return state


def _run_langgraph_workflow(initial_state: ClaimWorkflowState) -> ClaimWorkflowState:
    try:
        from langgraph.graph import END, StateGraph
    except Exception:
        return _run_deterministic_workflow(initial_state)

    workflow = StateGraph(ClaimWorkflowState)
    workflow.add_node("claims_intake", _intake_node)
    workflow.add_node("policy_retrieval", _policy_node)
    workflow.add_node("fraud_risk", _fraud_node)
    workflow.add_node("claim_decision", _decision_node)
    workflow.set_entry_point("claims_intake")
    workflow.add_edge("claims_intake", "policy_retrieval")
    workflow.add_edge("policy_retrieval", "fraud_risk")
    workflow.add_edge("fraud_risk", "claim_decision")
    workflow.add_edge("claim_decision", END)
    result = workflow.compile().invoke(initial_state)
    result["orchestration_engine"] = "langgraph"
    return result


def run_claim_workflow(customer_id: str, claim_text: str, claim_type: str, claim_amount: float) -> Dict[str, Any]:
    initial_state: ClaimWorkflowState = {
        "customer_id": customer_id,
        "claim_text": claim_text,
        "claim_type": claim_type,
        "claim_amount": claim_amount,
    }
    return _run_langgraph_workflow(initial_state)

