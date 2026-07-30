"""Pydantic schemas for Finding creation and API responses.

FindingCreate exists for graph nodes (Fase 2.5-2.8) to use when writing
findings via FindingRepository, not for direct API client use — findings
are produced by specialist agents, not submitted by users.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FindingCreate(BaseModel):
    """Payload required to create a new finding."""

    analysis_request_id: int
    specialist: str
    severity: str
    description: str
    file_path: str | None = None
    suggestion: str | None = None


class FindingResponse(BaseModel):
    """Full representation of a finding returned by the API."""

    id: int
    analysis_request_id: int
    specialist: str
    severity: str
    file_path: str | None
    description: str
    suggestion: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)