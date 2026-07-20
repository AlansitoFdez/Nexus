"""WebSocket endpoint for real-time ticket status updates.

For now this only accepts connections and sends a test message per
ticket subscription (Fase 1.5). Real events (node transitions,
approval requests) will be emitted from graph nodes starting in
Fase 2.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket connections grouped by ticket_id.

    Needed because multiple dashboard clients may be watching the same
    or different tickets simultaneously; this lets us send an event
    only to the connections actually interested in a given ticket.
    """

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, ticket_id: int, websocket: WebSocket):
        """Accepts a new connection and registers it under its ticket_id."""
        await websocket.accept()
        self.active_connections.setdefault(ticket_id, []).append(websocket)

    def disconnect(self, ticket_id: int, websocket: WebSocket):
        """Removes a closed connection from its ticket_id's list.

        Cleans up the ticket_id entry entirely once its list is empty,
        so the dict doesn't grow forever with stale, empty lists.
        """
        connections = self.active_connections.get(ticket_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(ticket_id, None)

    async def send_to_ticket(self, ticket_id: int, message: str):
        """Sends a text message to every connection watching this ticket."""
        for connection in self.active_connections.get(ticket_id, []):
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/tickets/{ticket_id}")
async def ticket_websocket(websocket: WebSocket, ticket_id: int):
    """Subscribes a client to real-time updates for a specific ticket."""
    await manager.connect(ticket_id, websocket)
    await websocket.send_text(f"Conectado al ticket {ticket_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ticket_id, websocket)