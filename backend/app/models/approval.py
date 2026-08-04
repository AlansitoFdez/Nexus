"""SQLAlchemy model for human approval requests.

An Approval represents an action proposed by the agent pipeline that
requires human sign-off before execution (human-in-the-loop) — in this
domain, specifically whether to post the analysis findings as a comment
on the real PR (post_to_pr). Always linked to the AnalysisRequest that
generated it.
"""

from sqlalchemy import CheckConstraint, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import sqlalchemy as sa
from app.database import Base


class Approval(Base):
    """A pending, approved or rejected action awaiting human review.

    Attributes:
        status: One of "pending", "approved" or "rejected". Always
            starts as "pending" when created — and stays "pending"
            while claimed_at is set, since claiming a decision and
            deciding it are separate concepts (see claimed_at below).
        claimed_at: Set atomically by POST /approvals/{id}/decision the
            moment a decision is accepted, before resume_analysis is
            even scheduled — not by human_approval_node, and not the
            same thing as the decision itself. Without this, two
            concurrent POSTs against the same approval_id could both
            read status="pending" before either had written anything,
            since the real status write only happens later, when the
            graph actually wakes up and resumes. The endpoint claims
            the approval with a single atomic UPDATE ... WHERE
            status='pending' AND claimed_at IS NULL — whichever request
            actually flips this column wins the race; the other gets 0
            rows affected and a 409.
        analysis_request: The AnalysisRequest this approval was generated for.
    """

    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_request_id = Column(Integer, ForeignKey("analysis_requests.id"), nullable=False, index=True)
    proposed_action = Column(Text, nullable=False)
    status = Column(String(20), server_default=sa.text("'pending'"), nullable=False)
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis_request = relationship("AnalysisRequest", back_populates="approvals")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_approvals_valid_status",
        ),
    )