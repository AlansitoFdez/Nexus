"""Pydantic schemas for knowledge base entry creation and API responses."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class KnowledgeBaseEntryCreate(BaseModel):
    """Payload required to create a new knowledge base entry.

    category is optional; entries without one are still valid but
    won't be filtered by category during search.
    """

    title: str
    content: str
    category: str | None = None


class KnowledgeBaseEntryResponse(BaseModel):
    """Full representation of a knowledge base entry returned by the API."""

    id: int
    title: str
    content: str
    category: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)