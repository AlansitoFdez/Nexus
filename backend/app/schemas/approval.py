from datetime import datetime
from pydantic import BaseModel

class ApprovalCreate(BaseModel):
    ticket_id: int
    proposed_action: str


class ApprovalResponse(BaseModel):
    id: int
    ticket_id: int
    proposed_action: str
    status: str
    decided_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True