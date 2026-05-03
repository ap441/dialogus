from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models import Book, Discussion, DiscussionLike, DiscussionPost, User
from app.schemas import (
    DiscussionCreateRequest,
    DiscussionReactionRequest,
    DiscussionReactionResponse,
    DiscussionResponse,
    DiscussionThreadResponse,
    ReactionCounts,
    ThreadPostCreateRequest,
    ThreadPostResponse,
)
from app.services.notifications import create_notification

router = APIRouter(tags=["discussions"])

REACTION_TYPES = {"like", "dislike", "recommend"}


def _reaction_counts(db: Session, discussion_id: int) -> ReactionCounts:
    counts = {"like": 0, "dislike": 0, "recommend": 0}
    reactions = (
        db.query(DiscussionLike.reaction_type)
        .filter(DiscussionLike.discussion_id == discussion_id)
        .all()
    )
    for reaction in reactions:
        reaction_type = (reaction.reaction_type or "like").lower()
        if reaction_type in counts:
            counts[reaction_type] += 1
    return ReactionCounts(**counts)


def _discussion_reply_count(db: Session, discussion_id: int) -> int:
    return (
        db.query(func.count(DiscussionPost.id))
        .filter(DiscussionPost.discussion_id == discussion_id)
        .scalar()
        or 0
    )


def _current_user_reaction(db: Session, discussion_id: int, current_user_id: int) -> str | None:
    reactions = (
        db.query(DiscussionLike.reaction_type)
        .filter(DiscussionLike.discussion_id == discussion_id, DiscussionLike.user_id == current_user_id)
        .all()
    )
    reaction_set = {(reaction.reaction_type or "like").lower() for reaction in reactions}
    for reaction_type in ("like", "dislike", "recommend"):
        if reaction_type in reaction_set:
            return reaction_type
    return None


def _current_user_reactions(db: Session, discussion_id: int, current_user_id: int) -> list[str]:
    reaction = (
        db.query(DiscussionLike.reaction_type)
        .filter(DiscussionLike.discussion_id == discussion_id, DiscussionLike.user_id == current_user_id)
        .all()
    )
    active = sorted(
        {(item.reaction_type or "like").lower() for item in reaction if (item.reaction_type or "like").lower() in REACTION_TYPES}
    )
    return active


def _discussion_payload(db: Session, discussion: Discussion, current_user_id: int) -> DiscussionResponse:
    user_reactions = _current_user_reactions(db, discussion.id, current_user_id)
    user_reaction = user_reactions[0] if user_reactions else None
    reaction_counts = _reaction_counts(db, discussion.id)
    author_name = discussion.author.full_name if discussion.author else "Community"
    return DiscussionResponse(
        id=discussion.id,
        book_id=discussion.book_id,
        book_title=discussion.book.title if discussion.book else None,
        title=discussion.title,
        excerpt=discussion.excerpt,
        body=discussion.body,
        replies=_discussion_reply_count(db, discussion.id),
        likes_count=reaction_counts.like,
        liked_by_me="like" in user_reactions,
        user_reaction=user_reaction,
        user_reactions=user_reactions,
        reaction_counts=reaction_counts,
        author_name=author_name,
        created_at=discussion.created_at,
    )


def _flatten_posts(posts: list[DiscussionPost]) -> list[ThreadPostResponse]:
    children_by_parent: dict[int | None, list[DiscussionPost]] = defaultdict(list)
    for post in posts:
        children_by_parent[post.parent_post_id].append(post)

    for siblings in children_by_parent.values():
        siblings.sort(key=lambda item: item.created_at)

    flattened: list[ThreadPostResponse] = []

    def walk(parent_id: int | None, depth: int):
        for post in children_by_parent.get(parent_id, []):
            author_name = post.author.full_name if post.author else "Community"
            flattened.append(
                ThreadPostResponse(
                    id=post.id,
                    discussion_id=post.discussion_id,
                    parent_post_id=post.parent_post_id,
                    author_name=author_name,
                    content=post.content,
                    created_at=post.created_at,
                    depth=depth,
                )
            )
            walk(post.id, depth + 1)

    walk(None, 0)
    return flattened


@router.get("/api/discussions/timeline", response_model=list[DiscussionResponse])
def get_timeline(
    q: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    timeline_query = db.query(Discussion).order_by(desc(Discussion.created_at))

    if q:
        like_filter = f"%{q}%"
        timeline_query = timeline_query.join(Book).filter(
            or_(
                Discussion.title.ilike(like_filter),
                Discussion.excerpt.ilike(like_filter),
                Book.title.ilike(like_filter),
            )
        )

    discussions = timeline_query.limit(max(1, min(limit, 100))).all()
    return [_discussion_payload(db, item, current_user.id) for item in discussions]


@router.post("/api/books/{book_id}/discussions", response_model=DiscussionResponse)
def create_discussion(
    book_id: int,
    payload: DiscussionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    discussion = Discussion(
        book_id=book.id,
        author_id=current_user.id,
        title=payload.title.strip(),
        excerpt=payload.excerpt.strip(),
        body=payload.body.strip(),
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)

    return _discussion_payload(db, discussion, current_user.id)


@router.post("/api/discussions/{discussion_id}/reaction", response_model=DiscussionReactionResponse)
def set_discussion_reaction(
    discussion_id: int,
    payload: DiscussionReactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")

    reaction_type = payload.reaction_type.strip().lower()
    if reaction_type not in REACTION_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reaction type")

    existing_reaction = (
        db.query(DiscussionLike)
        .filter(
            DiscussionLike.discussion_id == discussion_id,
            DiscussionLike.user_id == current_user.id,
            DiscussionLike.reaction_type == reaction_type,
        )
        .first()
    )

    if existing_reaction:
        db.delete(existing_reaction)
        toggled_reaction: str | None = None
    else:
        db.add(
            DiscussionLike(
                discussion_id=discussion_id,
                user_id=current_user.id,
                reaction_type=reaction_type,
            )
        )
        toggled_reaction = reaction_type

        if discussion.author_id and discussion.author_id != current_user.id and reaction_type in {"like", "recommend"}:
            verb = "liked" if reaction_type == "like" else "recommended"
            create_notification(
                db,
                recipient_id=discussion.author_id,
                actor_user=current_user,
                notification_type=f"reaction_{reaction_type}",
                title="New appreciation on your discussion",
                message=f"{current_user.full_name} {verb} your discussion '{discussion.title}'.",
                link=f"/discussions/{discussion.id}",
            )

    db.commit()
    db.refresh(discussion)

    reaction_counts = _reaction_counts(db, discussion.id)
    discussion.likes_count = reaction_counts.like
    user_reactions = _current_user_reactions(db, discussion.id, current_user.id)
    db.commit()
    return DiscussionReactionResponse(
        discussion_id=discussion.id,
        reaction_type=toggled_reaction,
        user_reactions=user_reactions,
        likes_count=reaction_counts.like,
        reaction_counts=reaction_counts,
    )


@router.post("/api/discussions/{discussion_id}/like", response_model=DiscussionReactionResponse)
def toggle_discussion_like(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return set_discussion_reaction(
        discussion_id,
        DiscussionReactionRequest(reaction_type="like"),
        db=db,
        current_user=current_user,
    )


@router.get("/api/discussions/{discussion_id}/thread", response_model=DiscussionThreadResponse)
def get_discussion_thread(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")

    posts = (
        db.query(DiscussionPost)
        .filter(DiscussionPost.discussion_id == discussion_id)
        .order_by(DiscussionPost.created_at.asc())
        .all()
    )
    flattened_posts = _flatten_posts(posts)
    reaction_counts = _reaction_counts(db, discussion.id)
    user_reactions = _current_user_reactions(db, discussion.id, current_user.id)
    user_reaction = user_reactions[0] if user_reactions else None

    return DiscussionThreadResponse(
        id=discussion.id,
        book_id=discussion.book_id,
        book_title=discussion.book.title if discussion.book else "Unknown",
        title=discussion.title,
        excerpt=discussion.excerpt,
        body=discussion.body,
        replies=_discussion_reply_count(db, discussion.id),
        likes_count=reaction_counts.like,
        liked_by_me="like" in user_reactions,
        user_reaction=user_reaction,
        user_reactions=user_reactions,
        reaction_counts=reaction_counts,
        author_name=discussion.author.full_name if discussion.author else "Community",
        created_at=discussion.created_at,
        posts=flattened_posts,
    )


@router.post("/api/discussions/{discussion_id}/posts", response_model=ThreadPostResponse)
def create_thread_post(
    discussion_id: int,
    payload: ThreadPostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")

    if payload.parent_post_id is not None:
        parent = (
            db.query(DiscussionPost)
            .filter(DiscussionPost.id == payload.parent_post_id, DiscussionPost.discussion_id == discussion_id)
            .first()
        )
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parent post")

    post = DiscussionPost(
        discussion_id=discussion_id,
        author_id=current_user.id,
        parent_post_id=payload.parent_post_id,
        content=payload.content.strip(),
    )
    db.add(post)
    db.flush()

    recipients: set[int] = set()
    if discussion.author_id and discussion.author_id != current_user.id:
        recipients.add(discussion.author_id)
    if payload.parent_post_id is not None:
        parent = (
            db.query(DiscussionPost)
            .filter(DiscussionPost.id == payload.parent_post_id, DiscussionPost.discussion_id == discussion_id)
            .first()
        )
        if parent and parent.author_id and parent.author_id != current_user.id:
            recipients.add(parent.author_id)

    for recipient_id in recipients:
        notification_type = "reply_to_discussion" if recipient_id == discussion.author_id else "reply_to_reply"
        recipient_label = "your discussion" if recipient_id == discussion.author_id else "your reply"
        create_notification(
            db,
            recipient_id=recipient_id,
            actor_user=current_user,
            notification_type=notification_type,
            title="New reply",
            message=f"{current_user.full_name} replied to {recipient_label} in '{discussion.title}'.",
            link=f"/discussions/{discussion.id}",
        )

    discussion.replies = _discussion_reply_count(db, discussion_id)
    db.commit()
    db.refresh(post)

    depth = 0
    if post.parent_post_id is not None:
        current_parent_id = post.parent_post_id
        while current_parent_id is not None:
            parent_node = db.query(DiscussionPost).filter(DiscussionPost.id == current_parent_id).first()
            if not parent_node:
                break
            depth += 1
            current_parent_id = parent_node.parent_post_id

    return ThreadPostResponse(
        id=post.id,
        discussion_id=post.discussion_id,
        parent_post_id=post.parent_post_id,
        author_name=current_user.full_name,
        content=post.content,
        created_at=post.created_at,
        depth=depth,
    )
