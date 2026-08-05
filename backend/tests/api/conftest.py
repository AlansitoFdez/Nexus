"""Shared fixtures for API endpoint tests, using an isolated test database."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from tests.db import engine, TestSessionLocal


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


async def _empty_astream(*args, **kwargs):
    """Stands in for the real graph's astream(): an async generator that
    finishes immediately without yielding any chunks. The `return`
    before the unreachable `yield` is what makes this an async generator
    function at all — needed since runner.py does `async for chunk in
    graph.astream(...)`, which requires something async-iterable, not
    just an awaitable.
    """
    return
    yield


@pytest.fixture
def client():
    """Provides a TestClient bound to the FastAPI app.

    Stands in a mocked compiled graph on app.state.graph instead of
    letting the real lifespan build one against a real Redis
    checkpointer. Without this, TestClient's BackgroundTasks run
    synchronously as part of the request, so every endpoint test that
    merely creates an AnalysisRequest (most of them, as setup for
    something else entirely) would trigger a real graph run — real
    ChatGroq calls, real GitHub reads — which breaks the project's own
    rule that no test talks to the real network. Graph-execution
    behavior itself is test_graph.py's job, with its own explicitly
    mocked LLM/MCP clients.

    astream is wrapped in a MagicMock with side_effect (not assigned
    directly) so tests can still assert it was called, the same way
    they'd assert on any other mock.
    """
    fake_graph = MagicMock()
    fake_graph.astream = MagicMock(side_effect=_empty_astream)
    app.state.graph = fake_graph
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_websocket_manager():
    from app.api.websocket import manager
    manager.active_connections.clear()
    yield
    manager.active_connections.clear()
