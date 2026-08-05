"""Tests for AnalysisRequest Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.analysis_request import (
    MAX_PASTED_CODE_LENGTH,
    MAX_REVIEW_REQUEST_LENGTH,
    AnalysisRequestCreate,
)


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


def test_analysis_request_create_defaults_post_to_pr_to_false():
    request = AnalysisRequestCreate(source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa x")
    assert request.post_to_pr is False


def test_analysis_request_create_accepts_explicit_post_to_pr_true():
    """post_to_pr=True is only valid alongside github_repo + pr_number
    — see check_post_to_pr_requires_github_repo_and_pr_number."""
    request = AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa x",
        post_to_pr=True,
        pr_number=42,
    )
    assert request.post_to_pr is True
    assert request.pr_number == 42


def test_create_fails_when_post_to_pr_true_with_pasted_code():
    """post_to_pr=True has no PR to target when the source is pasted
    code — there's no repo to associate the comment with."""
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(
            source_type="pasted_code",
            pasted_code="def foo(): pass",
            review_request="revisa x",
            post_to_pr=True,
        )


def test_create_fails_when_post_to_pr_true_without_pr_number():
    """post_to_pr=True with a github_repo source but no pr_number still
    doesn't say which PR to comment on."""
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(
            source_type="github_repo",
            repo_url="https://github.com/alan/nexus",
            review_request="revisa x",
            post_to_pr=True,
        )


def test_create_fails_when_review_request_exceeds_max_length():
    """Without this, an unbounded review_request would ride along
    unchanged into every specialist's prompt (Fase 3 review, 3.3)."""
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(
            source_type="pasted_code",
            pasted_code="def foo(): pass",
            review_request="x" * (MAX_REVIEW_REQUEST_LENGTH + 1),
        )


def test_create_fails_when_pasted_code_exceeds_max_length():
    with pytest.raises(ValidationError):
        AnalysisRequestCreate(
            source_type="pasted_code",
            pasted_code="x" * (MAX_PASTED_CODE_LENGTH + 1),
            review_request="revisa x",
        )
