"""Pydantic schemas for analysis request creation and API responses."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.finding import FindingResponse


class AnalysisRequestCreate(BaseModel):
    """Payload required to create a new code analysis request.

    Exactly one of repo_url/pasted_code must be provided, matching
    source_type — enforced here as an early, friendly error, on top of
    the CheckConstraint enforced at the database level as the real
    guarantee (see ck_analysis_requests_exactly_one_source).
    """

    source_type: Literal["github_repo", "pasted_code"]
    repo_url: str | None = None
    pasted_code: str | None = None
    review_request: str
    post_to_pr: bool = False

    @model_validator(mode="after")
    def check_exactly_one_source(self) -> "AnalysisRequestCreate":
        if self.source_type == "github_repo":
            if self.repo_url is None or self.pasted_code is not None:
                raise ValueError("source_type='github_repo' requires repo_url and no pasted_code")
        else:
            if self.pasted_code is None or self.repo_url is not None:
                raise ValueError("source_type='pasted_code' requires pasted_code and no repo_url")
        return self


class AnalysisRequestResponse(BaseModel):
    """Full representation of an analysis request returned by the API."""

    id: int
    source_type: str
    repo_url: str | None
    pasted_code: str | None
    review_request: str
    post_to_pr: bool
    status: str
    findings: list[FindingResponse]
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AnalysisRequestUpdate(BaseModel):
    """Payload for partially updating an existing analysis request.

    Used internally by graph nodes as they progress an analysis (e.g.
    router_node moving status to "running"), not meant for direct
    client-side use beyond perhaps cancelling a request.
    """

    status: Literal["pending", "running", "completed", "failed"] | None = None