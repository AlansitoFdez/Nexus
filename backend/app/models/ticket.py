from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    classification = Column(String(50), nullable=True)
    diagnosis = Column(Text, nullable=True)
    proposed_response = Column(Text, nullable=True)
    escalated = Column(Boolean, default=False)
    node_history = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())