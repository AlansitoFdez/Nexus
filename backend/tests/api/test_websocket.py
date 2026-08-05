"""Tests for the analysis request WebSocket endpoint."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.websocket import ConnectionManager

client = TestClient(app)


def test_client_receives_connection_confirmation():
    """A client connecting to an analysis request's WebSocket should get a confirmation message."""
    with client.websocket_connect("/ws/analysis-requests/1") as websocket:
        data = websocket.receive_text()

    assert data == "Conectado al análisis 1"


def test_two_clients_on_different_analysis_requests_dont_interfere():
    """A message sent to request 1 should not reach a client watching request 2."""
    with client.websocket_connect("/ws/analysis-requests/1") as ws_request_1:
        with client.websocket_connect("/ws/analysis-requests/2") as ws_request_2:
            msg_1 = ws_request_1.receive_text()
            msg_2 = ws_request_2.receive_text()

    assert msg_1 == "Conectado al análisis 1"
    assert msg_2 == "Conectado al análisis 2"


def test_connecting_second_client_does_not_leak_into_first_client():
    """Regression test: connecting a second client to the same request
    should not resend the connection confirmation to the first one."""
    from app.api.websocket import manager
    import asyncio

    with client.websocket_connect("/ws/analysis-requests/5") as ws_a:
        assert ws_a.receive_text() == "Conectado al análisis 5"

        with client.websocket_connect("/ws/analysis-requests/5") as ws_b:
            assert ws_b.receive_text() == "Conectado al análisis 5"

            asyncio.run(manager.send_to_analysis_request(5, "evento de prueba"))
            assert ws_a.receive_text() == "evento de prueba"


@pytest.mark.asyncio
async def test_send_to_analysis_request_disconnects_dead_sockets_without_raising():
    """A socket that already closed its tab, but whose WebSocketDisconnect
    the server hasn't processed yet, raises on send_text() — this must
    not propagate. entry_node/post_comment_node await this call with no
    try/except of their own, so an unhandled exception here would kill
    the whole graph run over a connection that has nothing to do with
    the analysis being processed."""
    manager = ConnectionManager()
    healthy = AsyncMock()
    dead = AsyncMock()
    dead.send_text = AsyncMock(side_effect=RuntimeError("connection closed"))
    manager.active_connections[1] = [healthy, dead]

    await manager.send_to_analysis_request(1, "hola")

    healthy.send_text.assert_awaited_once_with("hola")
    assert manager.active_connections[1] == [healthy]
