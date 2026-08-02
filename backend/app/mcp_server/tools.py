"""MCP tools for Nexus.

query_tickets_db was retired along with the rest of the ticket domain
— it depended on TicketRepository, which no longer exists. This
module now exposes the full set planned for the code review domain:
read_repository_files and get_pr_diff (Fase 3.1/3.2, read-only), and
post_pr_comment (Fase 3.3, below) — the first genuinely write action
against the GitHub API. post_pr_comment is called by post_comment_node
after human_approval_node, only when post_to_pr is still True.
"""

from typing import Annotated

from fastmcp.exceptions import ToolError
from pydantic import Field

from app.mcp_server.github_client import (
    GitHubAPIError,
    fetch_repository_files,
    get_pr_diff as _get_pr_diff,
    post_pr_comment as _post_pr_comment,
)
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


@mcp.tool
async def post_pr_comment(
    repo_url: Annotated[
        str,
        Field(description="Full GitHub repository URL, e.g. https://github.com/owner/repo"),
    ],
    pr_number: Annotated[
        int,
        Field(ge=1, description="The pull request number to comment on."),
    ],
    comment_body: Annotated[
        str,
        Field(min_length=1, description="The comment text to post, typically the analysis's final_report."),
    ],
) -> str:
    """Posts a comment on a pull request.

    Only ever called after a human has approved the action via
    human_approval_node — this tool itself has no awareness of
    approval state, it just executes the write once asked to.

    Args:
        repo_url: Full GitHub repository URL.
        pr_number: The pull request number to comment on.
        comment_body: The comment text to post.

    Returns:
        The URL of the created comment.
    """
    try:
        return await _post_pr_comment(repo_url, pr_number, comment_body)
    except GitHubAPIError as exc:
        raise ToolError(str(exc)) from exc
