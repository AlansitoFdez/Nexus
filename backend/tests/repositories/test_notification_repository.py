"""Tests for NotificationRepository database operations."""

from app.repositories.notification_repository import NotificationRepository


def test_create_persists_a_new_notification(db_session):
    """create() should save a new notification with the given data."""
    repo = NotificationRepository(db_session)

    notification = repo.create(message="ticket urgente", urgency="high", channel="log")

    assert notification.id is not None
    assert notification.urgency == "high"
    assert notification.channel == "log"