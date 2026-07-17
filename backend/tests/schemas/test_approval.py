"""Tests for Approval Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.approval import ApprovalCreate


def test_approval_create_accepts_valid_data():
    """ApprovalCreate should build successfully with valid data."""
    approval = ApprovalCreate(ticket_id=1, proposed_action="reiniciar el servicio")

    assert approval.ticket_id == 1
    assert approval.proposed_action == "reiniciar el servicio"


def test_approval_create_fails_without_ticket_id():
    """ticket_id is required and creation should fail without it."""
    with pytest.raises(ValidationError):
        ApprovalCreate(proposed_action="reiniciar el servicio")


def test_approval_create_fails_without_proposed_action():
    """proposed_action is required and creation should fail without it."""
    with pytest.raises(ValidationError):
        ApprovalCreate(ticket_id=1)