"""MCP tools for Nexus.

query_tickets_db was retired along with the rest of the ticket domain
— it depended on TicketRepository, which no longer exists. This
module is being rebuilt from Fase 3.1 onward with the new domain's
tools: read_repository_files, get_pr_diff (both below), and
post_pr_comment (3.3, pending).

get_pr_diff isn't called by any graph node yet — unlike
read_repository_files, which entry_node was already designed against
in Fase 2.2. AnalysisRequest has no pr_number field yet either. Both
are deliberately deferred to Fase 3.3, to be resolved once
post_pr_comment's real contract is known (it will need to identify a
PR too, and possibly more — see the doc for the reasoning).
"""

from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field

from app.mcp_server.github_client import GitHubAPIError, fetch_repository_files, get_pr_diff as _get_pr_diff
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


@mcp.tool
async def get_pr_diff(
    repo_url: Annotated[
        str,
        Field(description="Full GitHub repository URL, e.g. https://github.com/owner/repo"),
    ],
    pr_number: Annotated[
        int,
        Field(ge=1, description="The pull request number within the repository."),
    ],
) -> str:
    """Fetches the unified diff of a specific pull request.

    Args:
        repo_url: Full GitHub repository URL.
        pr_number: The pull request number.

    Returns:
        The raw unified diff as a string. An empty string means the
        PR has no changes, not that the request failed.
    """
    try:
        return await _get_pr_diff(repo_url, pr_number)
    except GitHubAPIError as exc:
        raise ToolError(str(exc)) from exc
