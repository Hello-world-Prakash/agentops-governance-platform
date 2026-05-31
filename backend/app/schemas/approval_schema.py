from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trace_id: str
    action_requested: str
    status: str
    created_at: datetime
