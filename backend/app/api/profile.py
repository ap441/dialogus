from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models import Discussion, DiscussionLike, DiscussionPost, Notification, User
from app.schemas import ProfileResponse, ProfileUpdateRequest, UserResponse

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _profile_payload(db: Session, user: User) -> ProfileResponse:
    discussion_count = db.query(func.count(Discussion.id)).filter(Discussion.author_id == user.id).scalar() or 0
    reply_count = db.query(func.count(DiscussionPost.id)).filter(DiscussionPost.author_id == user.id).scalar() or 0
    reaction_count = db.query(func.count(DiscussionLike.id)).filter(DiscussionLike.user_id == user.id).scalar() or 0
    notification_count = db.query(func.count(Notification.id)).filter(Notification.user_id == user.id).scalar() or 0
    unread_notification_count = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == user.id, Notification.is_read.is_(False))
        .scalar()
        or 0
    )

    return ProfileResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role or "member",
        bio=user.bio or "",
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        discussion_count=discussion_count,
        reply_count=reply_count,
        reaction_count=reaction_count,
        notification_count=notification_count,
        unread_notification_count=unread_notification_count,
    )


@router.get("/me", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _profile_payload(db, current_user)


@router.put("/me", response_model=ProfileResponse)
def update_profile(
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.full_name = payload.full_name.strip() or current_user.full_name
    current_user.bio = payload.bio.strip() if payload.bio else ""
    current_user.avatar_url = payload.avatar_url.strip() if payload.avatar_url else None
    db.commit()
    db.refresh(current_user)
    return _profile_payload(db, current_user)


@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = db.query(User).filter(User.full_name.ilike(f"%{q}%")).limit(10).all()
    return users


@router.get("/{user_id}", response_model=ProfileResponse)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _profile_payload(db, user)
