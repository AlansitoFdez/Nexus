"""SQLAlchemy model for notifications sent to the human support team.

Fase 3.4: persisted so the dashboard (Fase 4) can show a history of
what was notified and when, not just a fire-and-forget log line.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    """A notification sent to the human support team."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=False)
    urgency = Column(String(20), nullable=False)
    channel = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)