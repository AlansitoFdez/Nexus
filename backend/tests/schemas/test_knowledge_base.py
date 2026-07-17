"""Tests for KnowledgeBaseEntry Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.knowledge_base import KnowledgeBaseEntryCreate


def test_entry_create_accepts_valid_data_without_category():
    """category should default to None when not provided."""
    entry = KnowledgeBaseEntryCreate(title="Cómo resetear tu contraseña", content="Pasos para...")

    assert entry.title == "Cómo resetear tu contraseña"
    assert entry.category is None


def test_entry_create_fails_without_title():
    """title is required and creation should fail without it."""
    with pytest.raises(ValidationError):
        KnowledgeBaseEntryCreate(content="Pasos para...")


def test_entry_create_fails_without_content():
    """content is required and creation should fail without it."""
    with pytest.raises(ValidationError):
        KnowledgeBaseEntryCreate(title="Cómo resetear tu contraseña")