"""Pydantic schemas for Finding creation and API responses.

FindingCreate exists for graph nodes (Fase 2.5-2.8) to use when writing
findings via FindingRepository, not for direct API client use — findings
are produced by specialist agents, not submitted by users.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class FindingCreate(BaseModel):
    """Payload required to create a new finding.

    specialist/severity are Literals here, matching SpecialistFinding's
    own severity Literal in agents/schemas.py (that inconsistency — a
    free str on the persistence side of a value already constrained to
    4 options on the LLM-output side — was a real gap, Fase 4.2 review).
    Both domains are also enforced by a CheckConstraint at the database
    level (ck_findings_valid_severity) for severity — but not specialist:
    unlike severity, which is a truly fixed set of values, specialist's
    valid values are exactly whichever nodes agents/specialists.SPECIALISTS
    defines, so hardcoding them a second time into a migration would mean
    two places to update — and easy to desync — every time a specialist
    is added. Written by hand instead of derived from SPECIALISTS.keys()
    (unlike RouterDecision.agents_to_run) specifically to avoid app/schemas/
    depending on app/agents/ — no other schema in this package does, and
    agents/ already depends inward on schemas/, not the other way around.
    """

    analysis_request_id: int
    specialist: Literal["security", "performance", "design_patterns", "best_practices"]
    severity: Literal["critical", "high", "medium", "low"]
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
