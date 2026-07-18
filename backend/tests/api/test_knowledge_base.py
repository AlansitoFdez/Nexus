"""Tests for knowledge base entry REST endpoints."""


def test_create_entry_returns_201_with_created_entry(client):
    """POST /knowledge-base/ should create an entry and return it."""
    response = client.post("/knowledge-base/", json={"title": "Título", "content": "Contenido"})

    assert response.status_code == 201
    assert response.json()["title"] == "Título"


def test_get_entry_returns_404_when_not_found(client):
    """GET /knowledge-base/{id} should return 404 when the entry doesn't exist."""
    response = client.get("/knowledge-base/999")

    assert response.status_code == 404