"""Client for the real GitHub REST API: reading repository contents,
pull request diffs, and posting PR comments.

First genuinely external integration in Nexus (Fase 3.1) — unlike
create_external_ticket in the retired ticket domain, which simulated an
external system against Nexus's own table, this talks to a live
GitHub API: real auth, real rate limits, real network failures. Kept
in its own module, separate from tools.py, so the MCP tool boundary
(read_repository_files in tools.py) stays a thin wrapper — the same
separation already used between repositories and API endpoints
elsewhere in the project.

Design choice: fetch the whole repo as a zipball (`GET
/repos/{owner}/{repo}/zipball/{ref}`) instead of walking the git tree
and requesting each file's content individually via the contents API.
The per-file approach is simpler to write but costs one GitHub API
request per file — for a repo with a few hundred files that burns
through the (already limited, even with a token) rate limit in a
single analysis. The zipball approach costs exactly 2 requests
(repo info, then the archive) no matter how many files the repo has,
which is the difference between this being usable on a real repo and
not.
"""

import io
import re
import zipfile
from typing import Final

import httpx

from app.config import settings

GITHUB_API_BASE: Final = "https://api.github.com"

# code_content is never persisted (see entry_node) — it only lives in
# graph state for one run — but it does get passed whole into the
# router/specialist LLM prompts down the line. An uncapped repo would
# blow past context limits and cost silently, so both caps below are
# deliberately conservative starting points, not tuned against a real
# model yet.
MAX_FILE_SIZE_BYTES: Final = 100_000  # skip any single file larger than this
MAX_TOTAL_SIZE_BYTES: Final = 500_000  # stop collecting once this much content is gathered

# Extensions worth sending to a code review LLM. Lockfiles, configs,
# and binaries add token cost without review value in this domain.
INCLUDED_EXTENSIONS: Final = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rb", ".php",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".rs", ".sql",
}

EXCLUDED_DIR_PARTS: Final = {
    "node_modules", ".git", "venv", ".venv", "dist", "build",
    "__pycache__", ".next", "vendor",
}


class GitHubAPIError(Exception):
    """Raised for any failure talking to the GitHub API — repo not
    found or inaccessible, auth failure, rate limit exceeded, or no
    readable source files in the archive. Caught at the MCP tool
    boundary (tools.py) and translated into a ToolError with a clean
    message for the client — same principle as domain exceptions
    translated to HTTP codes at the REST endpoint layer.
    """


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    """Extracts (owner, repo) from a GitHub URL.

    Accepts the common shapes: with or without a trailing slash, with
    or without a trailing .git, with or without the https:// scheme.
    """
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$", repo_url.strip())
    if not match:
        raise GitHubAPIError(f"'{repo_url}' doesn't look like a valid GitHub repository URL")
    return match.group(1), match.group(2)


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _raise_for_github_status(response: httpx.Response, context: str) -> None:
    if response.status_code == 404:
        raise GitHubAPIError(f"{context}: not found or inaccessible (missing, private, or doesn't exist)")
    if response.status_code in (401, 403):
        if response.headers.get("X-RateLimit-Remaining") == "0":
            raise GitHubAPIError(f"{context}: GitHub API rate limit exceeded, try again later")
        raise GitHubAPIError(f"{context}: authentication failed, check GITHUB_TOKEN")
    if response.is_error:
        raise GitHubAPIError(f"{context}: GitHub API returned {response.status_code}")


def _is_included(path: str) -> bool:
    parts = path.split("/")
    if any(part in EXCLUDED_DIR_PARTS for part in parts):
        return False
    return any(path.endswith(ext) for ext in INCLUDED_EXTENSIONS)


def _extract_source_files(archive_bytes: bytes) -> str:
    """Walks the zipball in memory and concatenates included source
    files, each preceded by a header naming its path (with the
    zipball's own {owner}-{repo}-{sha}/ prefix stripped) so the LLM
    can attribute findings to the right file.
    """
    chunks: list[str] = []
    total_size = 0

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for info in archive.infolist():
            if info.is_dir() or info.file_size > MAX_FILE_SIZE_BYTES:
                continue

            # Strip the top-level {owner}-{repo}-{sha}/ directory GitHub
            # wraps every zipball in.
            path = info.filename.split("/", 1)[-1]
            if not path or not _is_included(path):
                continue

            if total_size >= MAX_TOTAL_SIZE_BYTES:
                break

            try:
                file_content = archive.read(info).decode("utf-8")
            except UnicodeDecodeError:
                continue  # binary file that slipped past the extension filter

            chunks.append(f"=== {path} ===\n{file_content}")
            total_size += len(file_content)

    if not chunks:
        raise GitHubAPIError("No readable source files found in the repository archive")

    return "\n\n".join(chunks)


async def fetch_repository_files(repo_url: str) -> str:
    """Fetches and concatenates the contents of a GitHub repo's source
    files, for the code review graph to hand to the LLM specialists.

    Returns a single string with each included file's content preceded
    by a header naming its path.
    """
    owner, repo = parse_repo_url(repo_url)

    async with httpx.AsyncClient(headers=_headers(), timeout=30.0, follow_redirects=True) as client:
        repo_response = await client.get(f"{GITHUB_API_BASE}/repos/{owner}/{repo}")
        _raise_for_github_status(repo_response, f"Fetching repo {owner}/{repo}")
        default_branch = repo_response.json()["default_branch"]

        zip_response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/zipball/{default_branch}"
        )
        _raise_for_github_status(zip_response, f"Downloading archive for {owner}/{repo}")

    return _extract_source_files(zip_response.content)


async def get_pr_diff(repo_url: str, pr_number: int) -> str:
    """Fetches the unified diff of a specific pull request.

    Uses GitHub's content negotiation on the pulls endpoint (Accept:
    application/vnd.github.v3.diff) to get the diff text directly in
    one request, instead of fetching PR metadata (base/head SHAs) and
    computing the diff ourselves against the compare API.

    Returns the raw unified diff as a string — an empty string is a
    legitimate result for a PR with no changes, not an error.
    """
    owner, repo = parse_repo_url(repo_url)

    headers = _headers() | {"Accept": "application/vnd.github.v3.diff"}
    async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
        )
        _raise_for_github_status(response, f"Fetching diff for {owner}/{repo}#{pr_number}")

    return response.text


async def post_pr_comment(repo_url: str, pr_number: int, comment_body: str) -> str:
    """Posts a comment on a pull request.

    GitHub treats every PR as an issue under the hood for general
    (non-inline) comments, so this hits the issues comments endpoint
    rather than a PR-specific one — that's not a Nexus simplification,
    it's how the GitHub API itself is shaped.

    This is the first genuinely write action Nexus's GitHub
    integration performs — everything in Fase 3.1/3.2 only read.
    GITHUB_TOKEN needs write access to pull requests for this to
    succeed (see the token scope note when GITHUB_TOKEN was added).

    Returns:
        The html_url of the created comment, so the caller can surface
        a direct link back to what was just posted.
    """
    owner, repo = parse_repo_url(repo_url)

    async with httpx.AsyncClient(headers=_headers(), timeout=30.0, follow_redirects=True) as client:
        response = await client.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": comment_body},
        )
        _raise_for_github_status(response, f"Posting comment on {owner}/{repo}#{pr_number}")

    return response.json()["html_url"]
