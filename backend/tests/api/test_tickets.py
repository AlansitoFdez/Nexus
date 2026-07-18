"""Tests for ticket REST endpoints using a real, isolated test database."""

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


client = TestClient(app)


def test_create_ticket_returns_201_with_created_ticket():
    """POST /tickets/ should create a ticket and return it with defaults."""
    response = client.post("/tickets/", json={"original_text": "no carga la página de inicio"})

    assert response.status_code == 201
    data = response.json()
    assert data["original_text"] == "no carga la página de inicio"
    assert data["escalated"] is False
    assert data["node_history"] == []


def test_get_ticket_returns_404_when_not_found():
    """GET /tickets/{id} should return 404 when the ticket doesn't exist."""
    response = client.get("/tickets/999")

    assert response.status_code == 404


def test_patch_ticket_updates_only_provided_fields():
    """PATCH /tickets/{id} should update only the fields sent in the payload."""
    create_response = client.post("/tickets/", json={"original_text": "no puedo subir archivos"})
    ticket_id = create_response.json()["id"]

    client.patch(f"/tickets/{ticket_id}", json={"diagnosis": "límite de tamaño excedido"})
    response = client.patch(f"/tickets/{ticket_id}", json={"classification": "bug"})

    data = response.json()
    assert data["classification"] == "bug"
    assert data["diagnosis"] == "límite de tamaño excedido"


def test_patch_ticket_returns_404_when_not_found():
    """PATCH /tickets/{id} should return 404 when the ticket doesn't exist."""
    response = client.patch("/tickets/999", json={"classification": "bug"})

    assert response.status_code == 404