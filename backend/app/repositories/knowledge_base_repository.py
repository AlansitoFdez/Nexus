from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.knowledge_base import KnowledgeBaseEntry
from app.schemas.knowledge_base import KnowledgeBaseEntryCreate


class KnowledgeBaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: KnowledgeBaseEntryCreate) -> KnowledgeBaseEntry:
        entry = KnowledgeBaseEntry(**data.model_dump())
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_by_id(self, entry_id: int) -> KnowledgeBaseEntry | None:
        return self.db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.id == entry_id).first()

    def get_all(self) -> list[KnowledgeBaseEntry]:
        return self.db.query(KnowledgeBaseEntry).all()

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Full-text search ranked by relevance against search_vector.

        Uses plainto_tsquery, not to_tsquery: plainto_tsquery treats the
        input as plain text and ignores tsquery operators (&, |, !),
        so a raw ticket text (which may contain arbitrary punctuation)
        can't accidentally break or manipulate the query syntax.
        """
        sql = text("""
            SELECT id, title, content, category,
                   ts_rank(search_vector, plainto_tsquery('spanish', :query)) AS relevance_score
            FROM knowledge_base
            WHERE search_vector @@ plainto_tsquery('spanish', :query)
            ORDER BY relevance_score DESC
            LIMIT :limit
        """)
        rows = self.db.execute(sql, {"query": query, "limit": limit}).mappings().all()
        return [dict(row) for row in rows]