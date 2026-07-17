"""Tests for Ticket Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.ticket import TicketCreate


def test_ticket_create_accepts_valid_original_text():
    """TicketCreate should build successfully with a valid original_text."""
    ticket = TicketCreate(original_text="la app se cierra sola")

    assert ticket.original_text == "la app se cierra sola"


def test_ticket_create_fails_without_original_text():
    """TicketCreate should reject creation when original_text is missing."""
    with pytest.raises(ValidationError):
        TicketCreate()