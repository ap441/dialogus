from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.discussions import _discussion_payload
from app.db.session import get_db
from app.deps import get_current_admin_user
from app.models import Book, Discussion, DiscussionPost, Notification, User
from app.schemas import (
    AdminDashboardResponse,
    AdminStatsResponse,
    AdminUserResponse,
    AdminUserRoleUpdateRequest,
    DiscussionResponse,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _admin_user_payload(db: Session, user: User) -> AdminUserResponse:
    discussion_count = db.query(func.count(Discussion.id)).filter(Discussion.author_id == user.id).scalar() or 0
    reply_count = db.query(func.count(DiscussionPost.id)).filter(DiscussionPost.author_id == user.id).scalar() or 0
    notification_count = db.query(func.count(Notification.id)).filter(Notification.user_id == user.id).scalar() or 0
    unread_notification_count = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user.id, Notification.is_read.is_(False))
        .scalar()
        or 0
    )

    return AdminUserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role or "member",
        bio=user.bio or "",
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        discussion_count=discussion_count,
        reply_count=reply_count,
        notification_count=notification_count,
        unread_notification_count=unread_notification_count,
    )


@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    all_users = db.query(User).order_by(desc(User.created_at)).limit(50).all()
    recent_discussions = (
        db.query(Discussion)
        .order_by(desc(Discussion.created_at))
        .limit(12)
        .all()
    )
    recent_notifications = (
        db.query(Notification)
        .order_by(desc(Notification.created_at))
        .limit(12)
        .all()
    )

    stats = AdminStatsResponse(
        total_users=db.query(func.count(User.id)).scalar() or 0,
        total_admins=db.query(func.count(User.id)).filter(func.lower(User.role) == "admin").scalar() or 0,
        total_books=db.query(func.count(Book.id)).scalar() or 0,
        total_discussions=db.query(func.count(Discussion.id)).scalar() or 0,
        total_replies=db.query(func.count(DiscussionPost.id)).scalar() or 0,
        total_notifications=db.query(func.count(Notification.id)).scalar() or 0,
        unread_notifications=db.query(func.count(Notification.id)).filter(Notification.is_read.is_(False)).scalar() or 0,
    )

    return AdminDashboardResponse(
        stats=stats,
        users=[_admin_user_payload(db, user) for user in all_users],
        recent_discussions=[_discussion_payload(db, discussion, current_user.id) for discussion in recent_discussions],
        recent_notifications=[
            # reuse the notification response shape from the dedicated router by serializing through the ORM fields
            {
                "id": notification.id,
                "notification_type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "link": notification.link,
                "is_read": notification.is_read,
                "actor_name": notification.actor.full_name if notification.actor else None,
                "created_at": notification.created_at,
                "read_at": notification.read_at,
            }
            for notification in recent_notifications
        ],
    )


@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
def update_user_role(
    user_id: int,
    payload: AdminUserRoleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    normalized_role = payload.role.strip().lower()
    if normalized_role not in {"member", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

    if user.id == current_user.id and normalized_role != "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove your own admin role")

    user.role = normalized_role
    db.commit()
    db.refresh(user)
    return _admin_user_payload(db, user)
