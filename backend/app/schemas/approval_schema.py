from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecisionRequest(BaseModel):
    reviewer_name: str = Field(min_length=1, max_length=120)
    decision_comment: str = Field(min_length=1, max_length=1000)


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trace_id: str
    action_requested: str
    status: str
    created_at: datetime
    decided_at: Optional[datetime] = None
    reviewer_name: Optional[str] = None
    decision_comment: Optional[str] = None
