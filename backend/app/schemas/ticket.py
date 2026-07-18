"""Pydantic schemas for ticket creation and API responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TicketCreate(BaseModel):
    """Payload required to create a new ticket.

    Only the user's original text is required; all other fields are
    filled in later by the agent pipeline, not by the client.
    """

    original_text: str


class TicketResponse(BaseModel):
    """Full representation of a ticket returned by the API.

    Built from a SQLAlchemy Ticket instance (see model_config below),
    including fields the agent pipeline may not have filled in yet.
    """

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


class TicketUpdate(BaseModel):
    """Payload for partially updating an existing ticket.

    Every field is optional: each caller (e.g. a graph node) only
    sends the fields it just computed, leaving the rest untouched.
    """

    cleaned_text: str | None = None
    classification: str | None = None
    diagnosis: str | None = None
    proposed_response: str | None = None
    escalated: bool | None = None
    node_history: list | None = None