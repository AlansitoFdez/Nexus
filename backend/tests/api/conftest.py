"""Shared fixtures for API endpoint tests, using an isolated test database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "postgresql://user:password@localhost:5434/nexus_test"

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    """Provides a test-database session in place of the real get_db."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Creates all tables before each test and drops them afterwards."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provides a TestClient bound to the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_websocket_manager():
    from app.api.websocket import manager
    manager.active_connections.clear()
    yield
    manager.active_connections.clear()