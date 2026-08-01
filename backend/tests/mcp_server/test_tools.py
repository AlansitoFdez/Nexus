"""Tests for MCP tools, using FastMCP's in-memory client.

The server currently exposes zero tools — query_tickets_db was retired
along with the ticket domain; the real tools for this domain
(read_repository_files, get_pr_diff, post_pr_comment) land starting
Fase 3.1.
"""

import pytest
from fastmcp import Client

from app.mcp_server.instance import mcp


@pytest.mark.asyncio
async def test_server_exposes_no_tools_yet():
    async with Client(mcp) as client:
        tools_list = await client.list_tools()

    assert tools_list == []