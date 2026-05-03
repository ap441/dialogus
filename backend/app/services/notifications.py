from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Notification, User


def create_notification(
    db: Session,
    *,
    recipient_id: int,
    actor_user: User | None,
    notification_type: str,
    title: str,
    message: str,
    link: str | None = None,
) -> Notification | None:
    if actor_user and recipient_id == actor_user.id:
        return None

    notification = Notification(
        user_id=recipient_id,
        actor_user_id=actor_user.id if actor_user else None,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )
    db.add(notification)
    return notification
