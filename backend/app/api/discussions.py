from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models import Book, Discussion, DiscussionLike, DiscussionPost, User
from app.schemas import (
    DiscussionCreateRequest,
    DiscussionLikeResponse,
    DiscussionResponse,
    DiscussionThreadResponse,
    ThreadPostCreateRequest,
    ThreadPostResponse,
)

router = APIRouter(tags=["discussions"])


def _discussion_payload(discussion: Discussion, current_user_id: int) -> DiscussionResponse:
    liked_by_me = any(like.user_id == current_user_id for like in discussion.likes)
    author_name = discussion.author.full_name if discussion.author else "Community"
    return DiscussionResponse(
        id=discussion.id,
        book_id=discussion.book_id,
        book_title=discussion.book.title if discussion.book else None,
        title=discussion.title,
        excerpt=discussion.excerpt,
        body=discussion.body,
        replies=discussion.replies,
        likes_count=discussion.likes_count,
        liked_by_me=liked_by_me,
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


@router.post("/api/discussions/{discussion_id}/like", response_model=DiscussionLikeResponse)
def toggle_discussion_like(
    discussion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
    if not discussion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discussion not found")

    existing_like = (
        db.query(DiscussionLike)
        .filter(DiscussionLike.discussion_id == discussion_id, DiscussionLike.user_id == current_user.id)
        .first()
    )

    liked = False
    if existing_like:
        db.delete(existing_like)
        discussion.likes_count = max(0, discussion.likes_count - 1)
    else:
        db.add(DiscussionLike(discussion_id=discussion_id, user_id=current_user.id))
        discussion.likes_count += 1
        liked = True

    db.commit()
    db.refresh(discussion)

    return DiscussionLikeResponse(discussion_id=discussion.id, likes_count=discussion.likes_count, liked=liked)


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

    liked_by_me = (
        db.query(DiscussionLike)
        .filter(DiscussionLike.discussion_id == discussion_id, DiscussionLike.user_id == current_user.id)
        .first()
        is not None
    )

    return DiscussionThreadResponse(
        id=discussion.id,
        book_id=discussion.book_id,
        book_title=discussion.book.title if discussion.book else "Unknown",
        title=discussion.title,
        excerpt=discussion.excerpt,
        body=discussion.body,
        replies=discussion.replies,
        likes_count=discussion.likes_count,
        liked_by_me=liked_by_me,
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
        parent_depth = 0
        current_parent_id = post.parent_post_id
        while current_parent_id is not None:
            parent_node = db.query(DiscussionPost).filter(DiscussionPost.id == current_parent_id).first()
            if not parent_node:
                break
            parent_depth += 1
            current_parent_id = parent_node.parent_post_id
        depth = parent_depth

    return ThreadPostResponse(
        id=post.id,
        discussion_id=post.discussion_id,
        parent_post_id=post.parent_post_id,
        author_name=current_user.full_name,
        content=post.content,
        created_at=post.created_at,
        depth=depth,
    )
