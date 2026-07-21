"""Shared state that flows through every node of the LangGraph pipeline.

Unlike a SQLAlchemy model (persistence) or a Pydantic schema (API
validation), this state only exists for the lifetime of a single graph
execution — it's the "expediente" that travels node to node. It is
never itself persisted as a whole; individual fields get written to
the Ticket table via TicketUpdate as each node produces them.

Fields annotated with a reducer (operator.add) are written by more
than one node across the pipeline and must accumulate rather than
overwrite; every other field has exactly one writer node and uses the
default overwrite behavior.
"""

import operator
from typing import Annotated, TypedDict


class TicketState(TypedDict):
    ticket_id: int
    original_text: str
    cleaned_text: str | None
    classification: str | None
    kb_documents: list[dict]
    similar_tickets: list[dict]
    diagnosis: str | None
    proposed_response: str | None
    pending_actions: list[dict]
    escalated: bool
    node_history: Annotated[list[str], operator.add]
    error: str | None