"""Tests for AnalysisRequest Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.analysis_request import AnalysisRequestCreate


def test_create_accepts_valid_github_repo_source():
    """A github_repo request with only repo_url set should validate."""
    request = AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad y rendimiento",
    )

    assert request.repo_url == "https://github.com/alan/nexus"
    assert request.pasted_code is None


def test_create_accepts_valid_pasted_code_source():
    """A pasted_code request with only pasted_code set should validate."""
    request = AnalysisRequestCreate(
        source_type="pasted_code",
        pasted_code="def foo(): pass",
        review_request="revisa buenas prácticas",
    )

    assert request.pasted_code == "def foo(): pass"
    assert request.repo_url is None


def test_create_fails_when_github_repo_missing_repo_url():
    """source_type='github_repo' without repo_url should fail validation."""
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(source_type="github_repo", review_request="revisa seguridad")


def test_create_fails_when_both_sources_are_set():
    """Providing both repo_url and pasted_code should fail validation, regardless of source_type."""
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(
            source_type="github_repo",
            repo_url="https://github.com/alan/nexus",
            pasted_code="def foo(): pass",
            review_request="revisa seguridad",
        )


def test_create_fails_when_pasted_code_source_missing_pasted_code():
    """source_type='pasted_code' without pasted_code should fail validation."""
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(source_type="pasted_code", review_request="revisa seguridad")