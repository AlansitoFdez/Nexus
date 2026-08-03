"""WebSocket endpoint for real-time analysis request status updates.

Accepts connections and relays events (node transitions, approval
requests) emitted from graph nodes as the code-review pipeline runs.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Tracks active WebSocket connections grouped by analysis_request_id.

    Needed because multiple dashboard clients may be watching the same
    or different analysis requests simultaneously; this lets us send an
    event only to the connections actually interested in a given request.
    """

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, analysis_request_id: int, websocket: WebSocket):
        """Accepts a new connection and registers it under its analysis_request_id."""
        await websocket.accept()
        self.active_connections.setdefault(analysis_request_id, []).append(websocket)

    def disconnect(self, analysis_request_id: int, websocket: WebSocket):
        """Removes a closed connection from its analysis_request_id's list.

        Cleans up the analysis_request_id entry entirely once its list is
        empty, so the dict doesn't grow forever with stale, empty lists.
        """
        connections = self.active_connections.get(analysis_request_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(analysis_request_id, None)

    async def send_to_analysis_request(self, analysis_request_id: int, message: str):
        """Sends a text message to every connection watching this request.

        Iterates a snapshot of the connection list, not the live one:
        disconnect() can run concurrently — triggered by a *different*
        socket's own receive_text() raising WebSocketDisconnect while
        this loop is suspended on an await — and mutating the same list
        object mid-iteration raises RuntimeError.

        Each send is also isolated in its own try/except: a client that
        already closed its tab, but whose WebSocketDisconnect the server
        hasn't processed yet, would otherwise raise here and propagate
        all the way up into whichever graph node awaited this call
        (entry_node, post_comment_node) — killing that node, and the
        whole analysis run, over a dead connection that has nothing to
        do with the analysis itself.
        """
        connections = list(self.active_connections.get(analysis_request_id, []))
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(analysis_request_id, connection)


manager = ConnectionManager()


@router.websocket("/ws/analysis-requests/{analysis_request_id}")
async def analysis_request_websocket(websocket: WebSocket, analysis_request_id: int):
    """Subscribes a client to real-time updates for a specific analysis request."""
    await manager.connect(analysis_request_id, websocket)
    await websocket.send_text(f"Conectado al análisis {analysis_request_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(analysis_request_id, websocket)