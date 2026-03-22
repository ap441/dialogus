from fastapi import APIRouter, Depends
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Discussion, Book
from app.schemas import HomeResponse

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


@router.get("/home", response_model=HomeResponse)
def get_home_data(q: str | None = None, db: Session = Depends(get_db)):
    discussions_query = db.query(Discussion).order_by(desc(Discussion.replies), desc(Discussion.created_at))
    books_query = db.query(Book).order_by(desc(Book.rating), Book.title)

    if q:
        like_filter = f"%{q}%"
        discussions_query = discussions_query.filter(Discussion.title.ilike(like_filter))
        books_query = books_query.filter(Book.title.ilike(like_filter))

    return HomeResponse(
        welcome_name="[Username]",
        trending_discussions=discussions_query.limit(5).all(),
        recommended_books=books_query.limit(8).all(),
    )
