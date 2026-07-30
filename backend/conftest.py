"""Shared pytest fixtures for the test suite."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.ticket import Ticket
from app.models.approval import Approval

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"


@pytest.fixture
def db_session():
    """Provides a database session backed by a real, isolated test database.

    Creates all tables before the test runs and drops them afterwards,
    so each test starts from a clean, known state.
    """
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    TestSessionLocal = sessionmaker(bind=engine)
    session = TestSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)