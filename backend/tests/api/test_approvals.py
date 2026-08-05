"""Tests for approval REST endpoints."""

from app.main import app


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


def test_list_approvals_filters_by_analysis_request_id(client):
    request_one = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    }).json()
    request_two = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def bar(): pass", "review_request": "revisa rendimiento"
    }).json()
    client.post("/approvals/", json={
        "analysis_request_id": request_one["id"], "proposed_action": "publicar en el PR 1"
    })
    client.post("/approvals/", json={
        "analysis_request_id": request_two["id"], "proposed_action": "publicar en el PR 2"
    })

    response = client.get(f"/approvals/?analysis_request_id={request_one['id']}")

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["analysis_request_id"] == request_one["id"]


def test_list_approvals_returns_empty_list_when_analysis_request_has_none(client):
    request = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    }).json()

    response = client.get(f"/approvals/?analysis_request_id={request['id']}")

    assert response.status_code == 200
    assert response.json() == []


def test_decide_approval_returns_404_when_not_found(client):
    response = client.post("/approvals/999/decision", json={"decision": "approved"})
    assert response.status_code == 404


def test_decide_approval_returns_422_for_invalid_decision_value(client):
    analysis_response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    })
    approval_response = client.post("/approvals/", json={
        "analysis_request_id": analysis_response.json()["id"], "proposed_action": "publicar comentario en el PR"
    })

    response = client.post(f"/approvals/{approval_response.json()['id']}/decision", json={"decision": "maybe"})

    assert response.status_code == 422


def test_decide_approval_returns_200_and_schedules_graph_resume(client):
    """The Approval row's status is still "pending" in the response —
    human_approval_node is what flips it to approved/rejected once the
    graph actually wakes up (Fase 2.10) — but the resume itself should
    have been scheduled and run against the mocked graph from the
    client fixture (BackgroundTasks run synchronously under TestClient).
    """
    analysis_response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    })
    analysis_request_id = analysis_response.json()["id"]
    approval_response = client.post("/approvals/", json={
        "analysis_request_id": analysis_request_id, "proposed_action": "publicar comentario en el PR"
    })
    approval_id = approval_response.json()["id"]

    response = client.post(f"/approvals/{approval_id}/decision", json={"decision": "approved"})

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    app.state.graph.astream.assert_called()


def test_decide_approval_returns_409_on_second_call_before_any_status_change(client):
    """Regression test for the actual race in 2.4: the mocked graph's
    astream() never really touches this Approval's status (that's
    human_approval_node's job on a real resume) — so under the old
    status-only guard, both decisions here would have read "pending"
    and both would have gotten a 200. claim_pending()'s atomic UPDATE is
    what makes the second one fail, without needing status to have
    changed at all."""
    analysis_response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    })
    approval_response = client.post("/approvals/", json={
        "analysis_request_id": analysis_response.json()["id"], "proposed_action": "publicar comentario en el PR"
    })
    approval_id = approval_response.json()["id"]

    first = client.post(f"/approvals/{approval_id}/decision", json={"decision": "approved"})
    second = client.post(f"/approvals/{approval_id}/decision", json={"decision": "approved"})

    assert first.status_code == 200
    assert second.status_code == 409


def test_decide_approval_returns_409_when_already_decided(client):
    analysis_response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    })
    approval_response = client.post("/approvals/", json={
        "analysis_request_id": analysis_response.json()["id"], "proposed_action": "publicar comentario en el PR"
    })
    approval_id = approval_response.json()["id"]

    first = client.post(f"/approvals/{approval_id}/decision", json={"decision": "approved"})
    assert first.status_code == 200

    # decide_approval doesn't flip the Approval's own status (human_approval_node
    # does, on resume) — simulate that here to exercise the 409 guard directly,
    # since the mocked graph's ainvoke() is a no-op that never actually resumes it.
    # Uses TestSessionLocal (bound to nexus_test), not app.database.SessionLocal
    # (the real dev DB) — same "patch where it's used, not where it's defined"
    # principle documented in the methodology addendum, applied here by simply
    # building the session against the test engine directly.
    from app.repositories.analysis_request_repository import AnalysisRequestRepository
    from app.repositories.approval_repository import ApprovalRepository
    from app.schemas.approval import ApprovalUpdate
    from tests.api.conftest import TestSessionLocal

    db = TestSessionLocal()
    try:
        repo = ApprovalRepository(db, AnalysisRequestRepository(db))
        repo.update(approval_id, ApprovalUpdate(status="approved"))
    finally:
        db.close()

    second = client.post(f"/approvals/{approval_id}/decision", json={"decision": "approved"})
    assert second.status_code == 409
