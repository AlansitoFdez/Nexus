"""SQLAlchemy model for support tickets.

A Ticket starts with only the user's original text. The rest of its
fields (classification, diagnosis, proposed_response, etc.) are filled
in progressively by the LangGraph agent pipeline as it processes the
ticket, not at creation time.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Ticket(Base):
    """A support ticket processed by the multi-agent graph.

    Attributes:
        node_history: Ordered list of node names the ticket has passed
            through in the LangGraph pipeline, used for traceability.
        approvals: Human approval requests associated with this ticket.
    """

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    classification = Column(String(50), nullable=True)
    diagnosis = Column(Text, nullable=True)
    proposed_response = Column(Text, nullable=True)
    escalated = Column(Boolean, server_default=sa.text("false"), nullable=False)
    node_history = Column(JSONB, server_default=sa.text("'[]'::jsonb"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    approvals = relationship("Approval", back_populates="ticket")