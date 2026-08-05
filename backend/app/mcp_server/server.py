"""Entry point for running the Nexus MCP server.

Run with: python -m app.mcp_server.server
Listens over HTTP so it can be reached as a separate process from the
main FastAPI backend and, later, from the LangGraph client (Fase 2).
"""

from app.mcp_server import tools  # noqa: F401 — import triggers @mcp.tool registration
from app.mcp_server.instance import mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
