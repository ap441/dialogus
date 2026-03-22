from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Book
from app.schemas import BookCardResponse, BookDetailResponse
from app.services.semantic_search import rank_books_semantically

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookCardResponse])
def list_books(q: str | None = None, db: Session = Depends(get_db)):
    books = db.query(Book).all()
    ranked = rank_books_semantically(books, q or "")
    return ranked[:50]


@router.get("/{book_id}", response_model=BookDetailResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
