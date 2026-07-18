"""Tests for ticket REST endpoints using a real, isolated test database."""


def test_create_ticket_returns_201_with_created_ticket(client):
    response = client.post("/tickets/", json={"original_text": "no carga la página de inicio"})
    assert response.status_code == 201
    data = response.json()
    assert data["original_text"] == "no carga la página de inicio"
    assert data["escalated"] is False
    assert data["node_history"] == []


def test_get_ticket_returns_404_when_not_found(client):
    response = client.get("/tickets/999")
    assert response.status_code == 404


def test_patch_ticket_updates_only_provided_fields(client):
    create_response = client.post("/tickets/", json={"original_text": "no puedo subir archivos"})
    ticket_id = create_response.json()["id"]

    client.patch(f"/tickets/{ticket_id}", json={"diagnosis": "límite de tamaño excedido"})
    response = client.patch(f"/tickets/{ticket_id}", json={"classification": "bug"})

    data = response.json()
    assert data["classification"] == "bug"
    assert data["diagnosis"] == "límite de tamaño excedido"


def test_patch_ticket_returns_404_when_not_found(client):
    response = client.patch("/tickets/999", json={"classification": "bug"})
    assert response.status_code == 404