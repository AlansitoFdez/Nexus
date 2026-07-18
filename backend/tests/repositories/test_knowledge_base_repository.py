"""Tests for KnowledgeBaseRepository database operations."""

from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseEntryCreate


def test_create_persists_a_new_entry(db_session):
    """create() should save a new entry with the given data."""
    repo = KnowledgeBaseRepository(db_session)

    entry = repo.create(KnowledgeBaseEntryCreate(title="Cómo resetear contraseña", content="Pasos..."))

    assert entry.id is not None
    assert entry.title == "Cómo resetear contraseña"
    assert entry.category is None


def test_get_by_id_returns_none_when_entry_does_not_exist(db_session):
    """get_by_id() should return None when no entry matches the given ID."""
    repo = KnowledgeBaseRepository(db_session)

    result = repo.get_by_id(999)

    assert result is None


def test_get_all_returns_every_entry(db_session):
    """get_all() should return all persisted entries."""
    repo = KnowledgeBaseRepository(db_session)
    repo.create(KnowledgeBaseEntryCreate(title="Entrada uno", content="..."))
    repo.create(KnowledgeBaseEntryCreate(title="Entrada dos", content="..."))

    entries = repo.get_all()

    assert len(entries) == 2