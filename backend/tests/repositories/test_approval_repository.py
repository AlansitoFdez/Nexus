"""Tests for ApprovalRepository database operations."""

import pytest

from app.repositories.analysis_request_repository import AnalysisRequestRepository, AnalysisRequestNotFoundError
from app.repositories.approval_repository import ApprovalRepository
from app.schemas.analysis_request import AnalysisRequestCreate
from app.schemas.approval import ApprovalCreate


class FakeAnalysisRequestRepositoryReturningNone:
    """A fake AnalysisRequestRepository whose get_by_id always returns None."""

    def get_by_id(self, analysis_request_id: int) -> None:
        return None


def test_create_persists_a_new_approval_for_an_existing_analysis_request(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    approval_repo = ApprovalRepository(db_session, analysis_repo)
    approval = approval_repo.create(ApprovalCreate(analysis_request_id=request.id, proposed_action="publicar en el PR"))

    assert approval.id is not None
    assert approval.status == "pending"


def test_create_raises_error_when_analysis_request_does_not_exist(db_session):
    fake_repo = FakeAnalysisRequestRepositoryReturningNone()
    approval_repo = ApprovalRepository(db_session, fake_repo)

    with pytest.raises(AnalysisRequestNotFoundError):
        approval_repo.create(ApprovalCreate(analysis_request_id=999, proposed_action="publicar en el PR"))


def test_get_by_id_returns_none_when_approval_does_not_exist(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    approval_repo = ApprovalRepository(db_session, analysis_repo)

    result = approval_repo.get_by_id(999)

    assert result is None


def test_get_by_analysis_request_id_returns_only_matching_approvals(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    approval_repo = ApprovalRepository(db_session, analysis_repo)

    request_one = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))
    request_two = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def bar(): pass", review_request="revisa rendimiento"
    ))
    approval_repo.create(ApprovalCreate(analysis_request_id=request_one.id, proposed_action="publicar en el PR 1"))
    approval_repo.create(ApprovalCreate(analysis_request_id=request_two.id, proposed_action="publicar en el PR 2"))

    result = approval_repo.get_by_analysis_request_id(request_one.id)

    assert len(result) == 1
    assert result[0].analysis_request_id == request_one.id
    assert result[0].proposed_action == "publicar en el PR 1"


def test_get_by_analysis_request_id_returns_empty_list_when_none_exist(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    approval_repo = ApprovalRepository(db_session, analysis_repo)

    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))

    result = approval_repo.get_by_analysis_request_id(request.id)

    assert result == []


def test_claim_pending_succeeds_for_a_pending_unclaimed_approval(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    approval_repo = ApprovalRepository(db_session, analysis_repo)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))
    approval = approval_repo.create(ApprovalCreate(analysis_request_id=request.id, proposed_action="publicar en el PR"))

    assert approval_repo.claim_pending(approval.id) is True

    db_session.expire_all()
    claimed = approval_repo.get_by_id(approval.id)
    assert claimed.claimed_at is not None
    # status stays untouched — writing the actual decision is still
    # exclusively human_approval_node's job, not this call's.
    assert claimed.status == "pending"


def test_claim_pending_fails_on_second_call_for_the_same_approval(db_session):
    """The exact race 2.4 closes: two callers racing to claim the same
    still-pending approval — only the first one wins."""
    analysis_repo = AnalysisRequestRepository(db_session)
    approval_repo = ApprovalRepository(db_session, analysis_repo)
    request = analysis_repo.create(AnalysisRequestCreate(
        source_type="pasted_code", pasted_code="def foo(): pass", review_request="revisa seguridad"
    ))
    approval = approval_repo.create(ApprovalCreate(analysis_request_id=request.id, proposed_action="publicar en el PR"))

    assert approval_repo.claim_pending(approval.id) is True
    assert approval_repo.claim_pending(approval.id) is False


def test_claim_pending_fails_for_a_nonexistent_approval(db_session):
    analysis_repo = AnalysisRequestRepository(db_session)
    approval_repo = ApprovalRepository(db_session, analysis_repo)

    assert approval_repo.claim_pending(999) is False