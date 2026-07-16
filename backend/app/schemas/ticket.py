from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TicketCreate(BaseModel):
    original_text: str


class TicketResponse(BaseModel):
    id: int
    original_text: str
    cleaned_text: str | None
    classification: str | None
    diagnosis: str | None
    proposed_response: str | None
    escalated: bool
    node_history: list
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)