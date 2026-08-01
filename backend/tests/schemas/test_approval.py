"""Tests for Approval Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.approval import ApprovalCreate


def test_approval_create_accepts_valid_data():
    approval = ApprovalCreate(analysis_request_id=1, proposed_action="publicar comentario en el PR")

    assert approval.analysis_request_id == 1
    assert approval.proposed_action == "publicar comentario en el PR"


def test_approval_create_fails_without_analysis_request_id():
    with pytest.raises(ValidationError):
        ApprovalCreate(proposed_action="publicar comentario en el PR")


def test_approval_create_fails_without_proposed_action():
    with pytest.raises(ValidationError):
        ApprovalCreate(analysis_request_id=1)