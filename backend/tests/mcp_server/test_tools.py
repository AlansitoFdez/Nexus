"""Tests for MCP tools, using FastMCP's in-memory client.

query_tickets_db was retired along with the ticket domain. As of Fase
3.1, the server exposes its first real tool for the code review
domain: read_repository_files. fetch_repository_files itself is
mocked here — its own logic (URL parsing, zip filtering, GitHub error
translation) is covered in test_github_client.py; this file only
checks that the tool is registered and correctly wired to it,
including translating GitHubAPIError into a client-visible ToolError.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from app.mcp_server import tools  # noqa: F401 — import triggers @mcp.tool registration
from app.mcp_server.github_client import GitHubAPIError
from app.mcp_server.instance import mcp


@pytest.mark.asyncio
async def test_server_exposes_read_repository_files():
    async with Client(mcp) as client:
        tools_list = await client.list_tools()

    assert [tool.name for tool in tools_list] == ["read_repository_files"]


@pytest.mark.asyncio
async def test_read_repository_files_returns_fetched_content():
    with patch(
        "app.mcp_server.tools.fetch_repository_files",
        AsyncMock(return_value="=== src/main.py ===\nprint('hola')"),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "read_repository_files", {"repo_url": "https://github.com/alan/nexus"}
            )

    assert result.data == "=== src/main.py ===\nprint('hola')"


@pytest.mark.asyncio
async def test_read_repository_files_translates_github_error_to_tool_error():
    with patch(
        "app.mcp_server.tools.fetch_repository_files",
        AsyncMock(side_effect=GitHubAPIError("repo not found")),
    ):
        async with Client(mcp) as client:
            with pytest.raises(ToolError, match="repo not found"):
                await client.call_tool(
                    "read_repository_files", {"repo_url": "https://github.com/alan/missing"}
                )
