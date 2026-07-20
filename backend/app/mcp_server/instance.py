"""Creates the shared FastMCP server instance.

Kept in its own module (not inside server.py) to avoid a circular
import: tools.py needs to import `mcp` to register tools with
@mcp.tool, and server.py needs to import tools.py to trigger that
registration. A neutral third module breaks the cycle.
"""

from fastmcp import FastMCP

mcp = FastMCP("Nexus MCP Server")