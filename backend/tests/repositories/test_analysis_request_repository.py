"""Tests for AnalysisRequestRepository database operations."""

import pytest

from app.repositories.analysis_request_repository import AnalysisRequestRepository, AnalysisRequestNotFoundError
from app.schemas.analysis_request import AnalysisRequestCreate, AnalysisRequestUpdate


def test_create_persists_a_new_analysis_request(db_session):
    """create() should save a new analysis request with the given data."""
    repo = AnalysisRequestRepository(db_session)

    request = repo.create(AnalysisRequestCreate(
        source_type="github_repo",
        repo_url="https://github.com/alan/nexus",
        review_request="revisa seguridad",
    ))

    assert request.id is not None
    assert request.status == "pending"


def test_get_by_id_returns_none_when_request_does_not_exist(db_session):
    """get_by_id() should return None when no request matches the given ID."""
    repo = AnalysisRequestRepository(db_session)

    assert repo.get_by_id(999) is None


def test_get_all_returns_every_request(db_session):
    """get_all() should return all persisted analysis requests."""
    repo = AnalysisRequestRepository(db_session)
    repo.create(AnalysisRequestCreate(source_type="pasted_code", pasted_code="a", review_request="x"))
    repo.create(AnalysisRequestCreate(source_type="pasted_code", pasted_code="b", review_request="y"))

    assert len(repo.get_all()) == 2


def test_update_only_modifies_provided_fields(db_session):
    """update() should not overwrite fields that weren't included in the payload."""
    repo = AnalysisRequestRepository(db_session)
    request = repo.create(AnalysisRequestCreate(source_type="pasted_code", pasted_code="a", review_request="x"))

    updated = repo.update(request.id, AnalysisRequestUpdate(status="running"))

    assert updated.status == "running"
    assert updated.pasted_code == "a"


def test_update_raises_error_when_request_does_not_exist(db_session):
    """update() should raise AnalysisRequestNotFoundError, not return None, when the ID doesn't exist.

    Fixes the inconsistency flagged against TicketRepository.update():
    update() acts on a target, so a missing target is a domain error.
    """
    repo = AnalysisRequestRepository(db_session)

    with pytest.raises(AnalysisRequestNotFoundError):
        repo.update(999, AnalysisRequestUpdate(status="running"))
