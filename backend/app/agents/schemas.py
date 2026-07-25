"""Pydantic schema for the classifier node's structured LLM output.

Unlike app/schemas/ (API request/response validation) or TicketState
(internal graph processing), this schema validates the boundary
between an external, non-deterministic system (the LLM's response)
and the rest of the pipeline — the LLM's output isn't guaranteed to
match this shape just because we asked nicely; Pydantic enforces it.
"""

from typing import Literal
from pydantic import BaseModel, Field


class TicketClassification(BaseModel):
    """Structured classification produced by the classifier node."""

    category: Literal["bug", "usage_question", "configuration", "urgent"] = Field(
        description="The type of support issue described in the ticket."
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="How urgently this ticket needs to be addressed."
    )
    confidence: float = Field(
        ge=0, le=1, description="The model's confidence in this classification, from 0 to 1."
    )

class DiagnosisOutput(BaseModel):
    """Structured diagnosis produced by the diagnosis node."""

    probable_cause: str = Field(description="The most likely root cause of the issue.")
    proposed_solution: str = Field(description="A concrete solution or next step to resolve it.")
    confidence: float = Field(ge=0, le=1, description="Confidence in this diagnosis, from 0 to 1.")
    actions_required: list[str] | None = Field(
        default=None,
        description="High-impact actions requiring human approval before execution. Use an empty list or omit this field entirely if none are needed.",
    )