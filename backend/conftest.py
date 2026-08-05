"""Shared pytest fixtures for the test suite."""

import pytest

from app.database import Base
from tests.db import engine, TestSessionLocal


@pytest.fixture
def db_session():
    """Provides a database session backed by a real, isolated test database.

    Creates all tables before the test runs and drops them afterwards,
    so each test starts from a clean, known state. engine itself is
    shared (tests/db.py), not rebuilt per test.
    """
    Base.metadata.create_all(bind=engine)

    session = TestSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
