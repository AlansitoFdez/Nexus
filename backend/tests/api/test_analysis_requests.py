"""Tests for analysis request REST endpoints using a real, isolated test database."""


def test_create_analysis_request_returns_201_with_created_request(client):
    response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code",
        "pasted_code": "def foo(): pass",
        "review_request": "revisa buenas prácticas",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["findings"] == []


def test_create_analysis_request_returns_422_when_both_sources_set(client):
    response = client.post("/analysis-requests/", json={
        "source_type": "github_repo",
        "repo_url": "https://github.com/alan/nexus",
        "pasted_code": "def foo(): pass",
        "review_request": "revisa seguridad",
    })

    assert response.status_code == 422


def test_get_analysis_request_returns_404_when_not_found(client):
    response = client.get("/analysis-requests/999")
    assert response.status_code == 404


def test_no_public_patch_endpoint_for_analysis_requests(client):
    """AnalysisRequestUpdate is for graph nodes to use internally — no
    client-facing PATCH is exposed for it (removed in the 2.5 review:
    nothing in the frontend ever called it, and it let any client
    overwrite status/final_report/pr_comment_url mid-run)."""
    create_response = client.post("/analysis-requests/", json={
        "source_type": "pasted_code",
        "pasted_code": "def foo(): pass",
        "review_request": "revisa rendimiento",
    })
    request_id = create_response.json()["id"]

    response = client.patch(f"/analysis-requests/{request_id}", json={"status": "running"})

    assert response.status_code == 405