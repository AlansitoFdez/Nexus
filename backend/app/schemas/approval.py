"""Pydantic schemas for approval creation and API responses."""

from datetime import datetime
from typing import Literal
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
    """Payload used internally by human_approval_node to persist the
    final status once the graph resumes — not the client-facing decision
    payload (see ApprovalDecision below)."""

    status: str


class ApprovalDecision(BaseModel):
    """Client-facing payload for POST /approvals/{id}/decision.

    Deliberately a closed Literal, not a free-form str like
    ApprovalUpdate.status: the only two decisions a human can make on a
    pending approval are approve or reject — anything else is a client
    bug, and should fail validation before it ever reaches the graph.
    """

    decision: Literal["approved", "rejected"]