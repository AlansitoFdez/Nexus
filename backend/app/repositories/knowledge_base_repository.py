"""Repository for KnowledgeBaseEntry database operations."""

from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBaseEntry
from app.schemas.knowledge_base import KnowledgeBaseEntryCreate


class KnowledgeBaseRepository:
    """Handles persistence operations for KnowledgeBaseEntry entities."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: KnowledgeBaseEntryCreate) -> KnowledgeBaseEntry:
        """Creates and persists a new knowledge base entry."""
        entry = KnowledgeBaseEntry(**data.model_dump())
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_id(self, entry_id: int) -> KnowledgeBaseEntry | None:
        """Retrieves an entry by its ID, or None if it doesn't exist."""
        return self.db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()

    def get_all(self) -> list[KnowledgeBaseEntry]:
        """Retrieves all knowledge base entries."""
        return self.db.query(KnowledgeBaseEntry).all()