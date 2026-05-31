from fastapi import APIRouter

from app.governance.policy_engine import list_agent_policies

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
def get_agents():
    return {"agents": [{"name": name, "allowed_actions": actions} for name, actions in list_agent_policies().items()]}

