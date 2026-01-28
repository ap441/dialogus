from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.book import Book
from sqlalchemy import text
from app.core.embeddings import embed_text

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/")
def list_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return [
        {
            "id": b.id,
            "isbn_13": b.isbn_13,
            "title": b.title,
            "description": b.description,
        }
        for b in books
    ]

@router.get("/search")
def semantic_search(q: str, db: Session = Depends(get_db), limit: int = 5):
    query_embedding = embed_text(q)

    sql = text("""
        SELECT id, isbn_13, title, description,
               embedding <=> (:query_embedding)::vector AS distance
        FROM books
        ORDER BY embedding <=> (:query_embedding)::vector
        LIMIT :limit
    """)

    results = db.execute(
        sql,
        {
            "query_embedding": query_embedding,
            "limit": limit,
        }
    ).mappings().all()

    return [
        {
            "id": r["id"],
            "isbn_13": r["isbn_13"],
            "title": r["title"],
            "description": r["description"],
            "distance": float(r["distance"]),
        }
        for r in results
    ]
    
@router.get("/{book_id}/similar")
def similar_books(
    book_id: int,
    db: Session = Depends(get_db),
    limit: int = 5,
):
    sql = text("""
        SELECT b2.id,
               b2.isbn_13,
               b2.title,
               b2.description,
               b2.embedding <=> b1.embedding AS distance
        FROM books b1
        JOIN books b2 ON b2.id != b1.id
        WHERE b1.id = :book_id
        ORDER BY b2.embedding <=> b1.embedding
        LIMIT :limit
    """)

    results = db.execute(
        sql,
        {
            "book_id": book_id,
            "limit": limit,
        }
    ).mappings().all()

    return [
        {
            "id": r["id"],
            "isbn_13": r["isbn_13"],
            "title": r["title"],
            "description": r["description"],
            "distance": float(r["distance"]),
        }
        for r in results
    ]
