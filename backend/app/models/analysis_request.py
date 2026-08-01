"""SQLAlchemy model for a code analysis request.

An AnalysisRequest starts with only the source (a GitHub repo URL or
pasted code — never both) and the user's free-text review request.
The rest of the pipeline (router, specialists, synthesizer) fills in
status and produces Finding rows as it processes the request.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, CheckConstraint
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisRequest(Base):
    """A code review request processed by the multi-agent graph.

    Attributes:
        source_type: Discriminates which of repo_url/pasted_code is
            populated for this request.
        review_request: The user's free-text description of what to
            check (e.g. "seguridad y rendimiento"), interpreted by the
            router node to decide which specialists to run.
        findings: All Finding rows produced by specialists for this
            request.
    """

    __tablename__ = "analysis_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(20), nullable=False)
    repo_url = Column(String(500), nullable=True)
    pasted_code = Column(Text, nullable=True)
    review_request = Column(Text, nullable=False)
    status = Column(String(30), server_default=sa.text("'pending'"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    post_to_pr = Column(Boolean, server_default=sa.text("false"), nullable=False)
    final_report = Column(Text, nullable=True)

    findings = relationship("Finding", back_populates="analysis_request")
    approvals = relationship("Approval", back_populates="analysis_request")

    __table_args__ = (
        CheckConstraint(
            "(source_type = 'github_repo' AND repo_url IS NOT NULL AND pasted_code IS NULL) OR "
            "(source_type = 'pasted_code' AND pasted_code IS NOT NULL AND repo_url IS NULL)",
            name="ck_analysis_requests_exactly_one_source",
        ),
    )