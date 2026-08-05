"""Creates the shared FastMCP server instance, protected by an API key.

Kept in its own module (not inside server.py) to avoid a circular
import — same reasoning documented aquí desde la Fase 1.4.
"""

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from app.config import settings

auth = StaticTokenVerifier(
    tokens={settings.MCP_API_KEY: {"client_id": "nexus-backend"}},
)

mcp = FastMCP("Nexus MCP Server", auth=auth)
