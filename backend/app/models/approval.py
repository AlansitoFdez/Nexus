"""SQLAlchemy model for human approval requests.

An Approval represents an action proposed by the agent pipeline that
requires human sign-off before execution (human-in-the-loop) — in this
domain, specifically whether to post the analysis findings as a comment
on the real PR (post_to_pr). Always linked to the AnalysisRequest that
generated it.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sqlalchemy as sa
from app.database import Base


class Approval(Base):
    """A pending, approved or rejected action awaiting human review.

    Attributes:
        status: One of "pending", "approved" or "rejected". Always
            starts as "pending" when created.
        analysis_request: The AnalysisRequest this approval was generated for.
    """

    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_request_id = Column(Integer, ForeignKey("analysis_requests.id"), nullable=False, index=True)
    proposed_action = Column(Text, nullable=False)
    status = Column(String(20), server_default=sa.text("'pending'"), nullable=False)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis_request = relationship("AnalysisRequest", back_populates="approvals")