"""Tests for application settings loading and validation."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_loads_with_all_required_env_vars(monkeypatch):
    """Settings should build successfully when all required vars are present."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5434/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    monkeypatch.setenv("MCP_SERVER_URL", "http://localhost:8001")
    monkeypatch.setenv("MCP_API_KEY", "fake-mcp-key")

    settings = Settings()

    assert settings.DATABASE_URL == "postgresql://user:pass@localhost:5434/test"
    assert settings.ENVIRONMENT == "development"


def test_settings_fails_when_required_var_is_missing(monkeypatch):
    """Settings should raise a validation error if a required var is absent."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5434/test")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("MCP_SERVER_URL", "http://localhost:8001")
    monkeypatch.setenv("MCP_API_KEY", "fake-mcp-key")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)