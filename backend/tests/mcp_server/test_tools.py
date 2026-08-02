"""Tests for MCP tools, using FastMCP's in-memory client.

query_tickets_db was retired along with the ticket domain. The server
now exposes the full code review domain tool set:
read_repository_files (Fase 3.1), get_pr_diff (Fase 3.2), and
post_pr_comment (Fase 3.3). All underlying github_client functions are
mocked here — their own logic (URL parsing, zip filtering/diff
fetching, GitHub error translation) is covered in
test_github_client.py; this file only checks that each tool is
registered and correctly wired, including translating GitHubAPIError
into a client-visible ToolError.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from app.mcp_server import tools  # noqa: F401 — import triggers @mcp.tool registration
from app.mcp_server.github_client import GitHubAPIError
from app.mcp_server.instance import mcp


@pytest.mark.asyncio
async def test_server_exposes_both_tools():
    async with Client(mcp) as client:
        tools_list = await client.list_tools()

    assert {tool.name for tool in tools_list} == {
        "read_repository_files", "get_pr_diff", "post_pr_comment",
    }


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


@pytest.mark.asyncio
async def test_get_pr_diff_returns_fetched_diff():
    with patch(
        "app.mcp_server.tools._get_pr_diff",
        AsyncMock(return_value="diff --git a/src/main.py b/src/main.py\n+print('nuevo')\n"),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "get_pr_diff", {"repo_url": "https://github.com/alan/nexus", "pr_number": 42}
            )

    assert result.data == "diff --git a/src/main.py b/src/main.py\n+print('nuevo')\n"


@pytest.mark.asyncio
async def test_get_pr_diff_translates_github_error_to_tool_error():
    with patch(
        "app.mcp_server.tools._get_pr_diff",
        AsyncMock(side_effect=GitHubAPIError("PR not found")),
    ):
        async with Client(mcp) as client:
            with pytest.raises(ToolError, match="PR not found"):
                await client.call_tool(
                    "get_pr_diff", {"repo_url": "https://github.com/alan/nexus", "pr_number": 999}
                )


@pytest.mark.asyncio
async def test_get_pr_diff_rejects_non_positive_pr_number():
    async with Client(mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "get_pr_diff", {"repo_url": "https://github.com/alan/nexus", "pr_number": 0}
            )


@pytest.mark.asyncio
async def test_post_pr_comment_returns_comment_url():
    with patch(
        "app.mcp_server.tools._post_pr_comment",
        AsyncMock(return_value="https://github.com/alan/nexus/pull/42#issuecomment-1"),
    ):
        async with Client(mcp) as client:
            result = await client.call_tool(
                "post_pr_comment",
                {
                    "repo_url": "https://github.com/alan/nexus",
                    "pr_number": 42,
                    "comment_body": "## Hallazgos\nNinguno.",
                },
            )

    assert result.data == "https://github.com/alan/nexus/pull/42#issuecomment-1"


@pytest.mark.asyncio
async def test_post_pr_comment_translates_github_error_to_tool_error():
    with patch(
        "app.mcp_server.tools._post_pr_comment",
        AsyncMock(side_effect=GitHubAPIError("authentication failed")),
    ):
        async with Client(mcp) as client:
            with pytest.raises(ToolError, match="authentication failed"):
                await client.call_tool(
                    "post_pr_comment",
                    {
                        "repo_url": "https://github.com/alan/nexus",
                        "pr_number": 42,
                        "comment_body": "## Hallazgos\nNinguno.",
                    },
                )


@pytest.mark.asyncio
async def test_post_pr_comment_rejects_empty_comment_body():
    async with Client(mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "post_pr_comment",
                {"repo_url": "https://github.com/alan/nexus", "pr_number": 42, "comment_body": ""},
            )
