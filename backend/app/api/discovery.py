from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models import Discussion, Book, User
from app.api.discussions import _discussion_payload
from app.schemas import HomeResponse
from app.services.semantic_search import rank_books_semantically

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


@router.get("/home", response_model=HomeResponse)
def get_home_data(
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    discussions_query = db.query(Discussion).order_by(desc(Discussion.replies), desc(Discussion.created_at))
    books = db.query(Book).all()

    if q:
        like_filter = f"%{q}%"
        discussions_query = discussions_query.filter(Discussion.title.ilike(like_filter))
    ranked_books = rank_books_semantically(books, q or "")

    trending_discussions = discussions_query.limit(5).all()
    return HomeResponse(
        welcome_name=current_user.full_name,
        trending_discussions=[_discussion_payload(db, item, current_user.id) for item in trending_discussions],
        recommended_books=ranked_books[:8],
    )
