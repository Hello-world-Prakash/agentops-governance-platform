from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trace_id: str
    timestamp: datetime
    user_request: Dict[str, Any]
    agent_name: str
    action_requested: str
    agent_output: Dict[str, Any]
    governance_decision: str
    policy_reasons: List[str]
    risk_score: float
    risk_level: str
    prompt_injection_detected: bool
    approval_status: str
    final_status: str
