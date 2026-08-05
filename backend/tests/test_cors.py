"""Tests for CORS configuration."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_allows_requests_from_frontend_origin():
    """The API should allow requests from the configured frontend origin."""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_blocks_requests_from_untrusted_origin():
    """The API should not authorize an origin that isn't explicitly allowed."""
    response = client.get("/health", headers={"Origin": "http://evil-site.com"})

    assert "access-control-allow-origin" not in response.headers
