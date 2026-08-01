"""Tests for approval REST endpoints."""


def test_create_approval_returns_201_for_existing_analysis_request(client):
    analysis_response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    })
    analysis_request_id = analysis_response.json()["id"]

    response = client.post("/approvals/", json={
        "analysis_request_id": analysis_request_id, "proposed_action": "publicar comentario en el PR"
    })

    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_create_approval_returns_404_when_analysis_request_does_not_exist(client):
    response = client.post("/approvals/", json={
        "analysis_request_id": 999, "proposed_action": "publicar comentario en el PR"
    })

    assert response.status_code == 404