from typing import Any, Dict
from pydantic import BaseModel


class PolicyEvaluationRequest(BaseModel):
    agent_name: str
    action_requested: str
    context: Dict[str, Any]
