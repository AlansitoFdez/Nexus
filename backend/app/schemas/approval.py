"""Pydantic schemas for approval creation and API responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    """Payload required to create a new approval request."""

    analysis_request_id: int
    proposed_action: str


class ApprovalResponse(BaseModel):
    """Full representation of an approval returned by the API."""

    id: int
    analysis_request_id: int
    proposed_action: str
    status: str
    decided_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApprovalUpdate(BaseModel):
    """Payload for deciding a pending approval."""

    status: str