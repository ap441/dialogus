from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, or_
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

router = APIRouter(tags=["discussions"])

REACTION_TYPES = {"like", "dislike", "recommend"}


def _reaction_counts(discussion: Discussion) -> ReactionCounts:
    counts = {"like": max(0, discussion.likes_count or 0), "dislike": 0, "recommend": 0}
    for reaction in discussion.likes:
        reaction_type = reaction.reaction_type or "like"
        if reaction_type in counts and reaction_type != "like":
            counts[reaction_type] += 1
    return ReactionCounts(**counts)


def _current_user_reaction(discussion: Discussion, current_user_id: int) -> str | None:
    for reaction in discussion.likes:
        if reaction.user_id == current_user_id:
            return reaction.reaction_type or "like"
    return None


def _discussion_payload(discussion: Discussion, current_user_id: int) -> DiscussionResponse:
    user_reaction = _current_user_reaction(discussion, current_user_id)
    reaction_counts = _reaction_counts(discussion)
    author_name = discussion.author.full_name if discussion.author else "Community"
    return DiscussionResponse(
        id=discussion.id,
        book_id=discussion.book_id,
        book_title=discussion.book.title if discussion.book else None,
        title=discussion.title,
        excerpt=discussion.excerpt,
        body=discussion.body,
        replies=discussion.replies,
        likes_count=reaction_counts.like,
        liked_by_me=user_reaction == "like",
        user_reaction=user_reaction,
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
    return [_discussion_payload(item, current_user.id) for item in discussions]


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

    return _discussion_payload(discussion, current_user.id)


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
        .filter(DiscussionLike.discussion_id == discussion_id, DiscussionLike.user_id == current_user.id)
        .first()
    )

    current_reaction = existing_reaction.reaction_type if existing_reaction else None
    if current_reaction not in REACTION_TYPES:
        current_reaction = "like" if existing_reaction else None

    if existing_reaction and current_reaction == reaction_type:
        if current_reaction == "like":
            discussion.likes_count = max(0, discussion.likes_count - 1)
        db.delete(existing_reaction)
        current_reaction = None
    elif existing_reaction:
        if current_reaction == "like":
            discussion.likes_count = max(0, discussion.likes_count - 1)
        if reaction_type == "like":
            discussion.likes_count += 1
        existing_reaction.reaction_type = reaction_type
        current_reaction = reaction_type
    else:
        db.add(
            DiscussionLike(
                discussion_id=discussion_id,
                user_id=current_user.id,
                reaction_type=reaction_type,
            )
        )
        if reaction_type == "like":
            discussion.likes_count += 1
        current_reaction = reaction_type

    db.commit()
    db.refresh(discussion)

    reaction_counts = _reaction_counts(discussion)
    return DiscussionReactionResponse(
        discussion_id=discussion.id,
        reaction_type=current_reaction,
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
    reaction_counts = _reaction_counts(discussion)
    user_reaction = _current_user_reaction(discussion, current_user.id)

    return DiscussionThreadResponse(
        id=discussion.id,
        book_id=discussion.book_id,
        book_title=discussion.book.title if discussion.book else "Unknown",
        title=discussion.title,
        excerpt=discussion.excerpt,
        body=discussion.body,
        replies=discussion.replies,
        likes_count=reaction_counts.like,
        liked_by_me=user_reaction == "like",
        user_reaction=user_reaction,
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
    discussion.replies += 1
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
