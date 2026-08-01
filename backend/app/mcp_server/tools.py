"""MCP tools for Nexus.

query_tickets_db was retired along with the rest of the ticket domain
— it depended on TicketRepository, which no longer exists. This
module is being rebuilt from Fase 3.1 onward with the new domain's
tools: read_repository_files (below), get_pr_diff (3.2), and
post_pr_comment (3.3).
"""

from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field

from app.mcp_server.github_client import GitHubAPIError, fetch_repository_files
from app.mcp_server.instance import mcp


@mcp.tool
async def read_repository_files(
    repo_url: Annotated[
        str,
        Field(description="Full GitHub repository URL, e.g. https://github.com/owner/repo"),
    ],
) -> str:
    """Reads and concatenates the source files of a GitHub repository.

    Downloads the repository's default branch as an archive and
    returns the content of its source files — filtered by extension,
    with noise directories like node_modules/venv excluded, and each
    file preceded by a header naming its path. Used by entry_node to
    resolve code_content for analysis requests with
    source_type="github_repo".

    Args:
        repo_url: Full GitHub repository URL.

    Returns:
        The concatenated content of the repository's source files.
    """
    try:
        return await fetch_repository_files(repo_url)
    except GitHubAPIError as exc:
        raise ToolError(str(exc)) from exc
