"""Tests for approval REST endpoints."""


def test_create_approval_returns_201_for_existing_ticket(client):
    """POST /approvals/ should create an approval when the ticket exists."""
    ticket_response = client.post("/tickets/", json={"original_text": "acceso denegado"})
    ticket_id = ticket_response.json()["id"]

    response = client.post("/approvals/", json={"ticket_id": ticket_id, "proposed_action": "resetear permisos"})

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_create_approval_returns_404_when_ticket_does_not_exist(client):
    """POST /approvals/ should return 404 when ticket_id doesn't exist."""
    response = client.post("/approvals/", json={"ticket_id": 999, "proposed_action": "resetear permisos"})

    assert response.status_code == 404