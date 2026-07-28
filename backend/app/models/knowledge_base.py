from sqlalchemy import Column, Integer, String, Text, DateTime, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import func
from app.database import Base


class KnowledgeBaseEntry(Base):
    """A reference document used by the knowledge base search node."""

    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    search_vector = Column(
        TSVECTOR,
        Computed(
            "to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(content, ''))",
            persisted=True,
        ),
    )