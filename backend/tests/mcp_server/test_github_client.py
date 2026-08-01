"""Tests for github_client — the real GitHub API integration (Fase 3.1).

All network calls are mocked; nothing here talks to the actual GitHub
API. That's the difference between this and an end-to-end check: it
verifies the parsing/filtering/error-translation logic Nexus owns, not
whether GitHub's API is up.
"""

import io
import zipfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.mcp_server.github_client import (
    GitHubAPIError,
    fetch_repository_files,
    parse_repo_url,
)


def _make_zip(files: dict[str, bytes]) -> bytes:
    """Builds an in-memory zip mimicking GitHub's zipball shape: every
    entry prefixed with a top-level {owner}-{repo}-{sha}/ directory.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for path, content in files.items():
            archive.writestr(f"alan-nexus-abc123/{path}", content)
    return buffer.getvalue()


def _mock_response(status_code: int = 200, json_data=None, content: bytes = b"", headers=None):
    response = MagicMock()
    response.status_code = status_code
    response.is_error = status_code >= 400
    response.headers = headers or {}
    response.json.return_value = json_data or {}
    response.content = content
    return response


def _mock_client(responses: list):
    """Returns a MagicMock standing in for httpx.AsyncClient's async
    context manager, whose .get() yields the given responses in order.
    """
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.get = AsyncMock(side_effect=responses)
    return client


class TestParseRepoUrl:
    def test_plain_https_url(self):
        assert parse_repo_url("https://github.com/alan/nexus") == ("alan", "nexus")

    def test_trailing_slash(self):
        assert parse_repo_url("https://github.com/alan/nexus/") == ("alan", "nexus")

    def test_trailing_dot_git(self):
        assert parse_repo_url("https://github.com/alan/nexus.git") == ("alan", "nexus")

    def test_invalid_url_raises(self):
        with pytest.raises(GitHubAPIError):
            parse_repo_url("not-a-github-url")


class TestFetchRepositoryFiles:
    @pytest.mark.asyncio
    async def test_success_concatenates_included_files_with_headers(self):
        archive = _make_zip({
            "src/main.py": b"print('hola')",
            "README.md": b"# excluded, not a source extension",
            "node_modules/lib.js": b"excluded, noise directory",
        })
        responses = [
            _mock_response(200, json_data={"default_branch": "main"}),
            _mock_response(200, content=archive),
        ]

        with patch("app.mcp_server.github_client.httpx.AsyncClient", return_value=_mock_client(responses)):
            result = await fetch_repository_files("https://github.com/alan/nexus")

        assert "=== src/main.py ===\nprint('hola')" in result
        assert "README.md" not in result
        assert "node_modules" not in result

    @pytest.mark.asyncio
    async def test_repo_not_found_raises_clean_error(self):
        responses = [_mock_response(404)]

        with patch("app.mcp_server.github_client.httpx.AsyncClient", return_value=_mock_client(responses)):
            with pytest.raises(GitHubAPIError, match="not found"):
                await fetch_repository_files("https://github.com/alan/missing")

    @pytest.mark.asyncio
    async def test_rate_limit_raises_clean_error(self):
        responses = [_mock_response(403, headers={"X-RateLimit-Remaining": "0"})]

        with patch("app.mcp_server.github_client.httpx.AsyncClient", return_value=_mock_client(responses)):
            with pytest.raises(GitHubAPIError, match="rate limit"):
                await fetch_repository_files("https://github.com/alan/nexus")

    @pytest.mark.asyncio
    async def test_auth_failure_raises_clean_error(self):
        responses = [_mock_response(401)]

        with patch("app.mcp_server.github_client.httpx.AsyncClient", return_value=_mock_client(responses)):
            with pytest.raises(GitHubAPIError, match="authentication failed"):
                await fetch_repository_files("https://github.com/alan/nexus")

    @pytest.mark.asyncio
    async def test_no_readable_source_files_raises(self):
        archive = _make_zip({"README.md": b"only docs here"})
        responses = [
            _mock_response(200, json_data={"default_branch": "main"}),
            _mock_response(200, content=archive),
        ]

        with patch("app.mcp_server.github_client.httpx.AsyncClient", return_value=_mock_client(responses)):
            with pytest.raises(GitHubAPIError, match="No readable source files"):
                await fetch_repository_files("https://github.com/alan/docs-only")

    @pytest.mark.asyncio
    async def test_oversized_file_is_skipped(self):
        from app.mcp_server import github_client as gc

        archive = _make_zip({
            "src/huge.py": b"x" * (gc.MAX_FILE_SIZE_BYTES + 1),
            "src/small.py": b"print('ok')",
        })
        responses = [
            _mock_response(200, json_data={"default_branch": "main"}),
            _mock_response(200, content=archive),
        ]

        with patch("app.mcp_server.github_client.httpx.AsyncClient", return_value=_mock_client(responses)):
            result = await fetch_repository_files("https://github.com/alan/nexus")

        assert "huge.py" not in result
        assert "small.py" in result
