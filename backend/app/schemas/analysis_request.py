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
    pr_number: int | None = None

    @model_validator(mode="after")
    def check_exactly_one_source(self) -> "AnalysisRequestCreate":
        if self.source_type == "github_repo":
            if self.repo_url is None or self.pasted_code is not None:
                raise ValueError("source_type='github_repo' requires repo_url and no pasted_code")
        else:
            if self.pasted_code is None or self.repo_url is not None:
                raise ValueError("source_type='pasted_code' requires pasted_code and no repo_url")
        return self

    @model_validator(mode="after")
    def check_post_to_pr_requires_github_repo_and_pr_number(self) -> "AnalysisRequestCreate":
        """post_to_pr=True means "publish the report as a comment on a
        real PR" — that only makes sense when the code actually
        reviewed came from that PR's repo (source_type="github_repo")
        and we know which PR (pr_number). A pasted_code analysis has no
        associated PR to comment on; allowing post_to_pr there would
        let the tool post a comment that doesn't describe the code the
        reader thinks it does.
        """
        if self.post_to_pr and (self.source_type != "github_repo" or self.pr_number is None):
            raise ValueError(
                "post_to_pr=True requires source_type='github_repo' and pr_number to be set"
            )
        return self


class AnalysisRequestResponse(BaseModel):
    """Full representation of an analysis request returned by the API."""

    id: int
    source_type: str
    repo_url: str | None
    pasted_code: str | None
    review_request: str
    post_to_pr: bool
    pr_number: int | None
    status: str
    final_report: str | None
    pr_comment_url: str | None
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

    status: Literal["pending", "running", "completed", "completed_with_errors", "failed"] | None = None
    final_report: str | None = None
    pr_comment_url: str | None = None