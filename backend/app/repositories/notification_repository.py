"""Repository for Notification database operations."""

from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    """Handles persistence for notifications sent to the support team."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, message: str, urgency: str, channel: str) -> Notification:
        notification = Notification(message=message, urgency=urgency, channel=channel)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification