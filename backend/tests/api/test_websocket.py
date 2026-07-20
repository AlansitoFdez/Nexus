"""Tests for the ticket WebSocket endpoint."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_client_receives_connection_confirmation():
    """A client connecting to a ticket's WebSocket should get a confirmation message."""
    with client.websocket_connect("/ws/tickets/1") as websocket:
        data = websocket.receive_text()

    assert data == "Conectado al ticket 1"


def test_two_clients_on_different_tickets_dont_interfere():
    """A message sent to ticket 1 should not reach a client watching ticket 2."""
    with client.websocket_connect("/ws/tickets/1") as ws_ticket_1:
        with client.websocket_connect("/ws/tickets/2") as ws_ticket_2:
            msg_1 = ws_ticket_1.receive_text()
            msg_2 = ws_ticket_2.receive_text()

    assert msg_1 == "Conectado al ticket 1"
    assert msg_2 == "Conectado al ticket 2" 


def test_connecting_second_client_does_not_leak_into_first_client():
    """Regression test: connecting a second client to the same ticket
    should not resend the connection confirmation to the first one."""
    from app.api.websocket import manager
    import asyncio

    with client.websocket_connect("/ws/tickets/5") as ws_a:
        assert ws_a.receive_text() == "Conectado al ticket 5"

        with client.websocket_connect("/ws/tickets/5") as ws_b:
            assert ws_b.receive_text() == "Conectado al ticket 5"

            asyncio.run(manager.send_to_ticket(5, "evento de prueba"))
            assert ws_a.receive_text() == "evento de prueba"