from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models import Book
from app.schemas import BookCardResponse, BookDetailResponse
from app.models import User
from app.api.discussions import _discussion_payload
from app.services.semantic_search import rank_books_semantically

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookCardResponse])
def list_books(q: str | None = None, limit: int = 1000, db: Session = Depends(get_db)):
    books = db.query(Book).all()
    ranked = rank_books_semantically(books, q or "")
    safe_limit = max(1, min(limit, 1000))
    return ranked[:safe_limit]


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookDetailResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        genre=book.genre,
        cover_url=book.cover_url,
        rating=book.rating,
        description=book.description,
        publication_year=book.publication_year,
        language=book.language,
        pages=book.pages,
        discussions=[_discussion_payload(discussion, current_user.id) for discussion in book.discussions],
    )
