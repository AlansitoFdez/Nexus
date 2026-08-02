"""Tests for the GET /metrics/ endpoint."""


def test_get_metrics_on_empty_database_returns_zeroes(client):
    response = client.get("/metrics/")

    assert response.status_code == 200
    body = response.json()
    assert body["total_analysis_requests"] == 0
    assert body["by_status"] == {}
    assert body["findings_by_specialist"] == {}
    assert body["findings_by_severity"] == {}
    assert body["pr_comments_posted"] == 0
    assert body["average_analysis_seconds"] is None


def test_get_metrics_reflects_created_analysis_requests(client):
    client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def foo(): pass", "review_request": "revisa seguridad"
    })
    client.post("/analysis-requests/", json={
        "source_type": "pasted_code", "pasted_code": "def bar(): pass", "review_request": "revisa rendimiento"
    })

    response = client.get("/metrics/")

    assert response.status_code == 200
    body = response.json()
    assert body["total_analysis_requests"] == 2
    assert body["by_status"] == {"pending": 2}
