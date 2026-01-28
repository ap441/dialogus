from app.ingestion.openlibrary import fetch_books
from app.ingestion.editions import fetch_editions
from app.ingestion.normalizer import normalize_edition
from app.db.session import SessionLocal
from app.models.book import Book
from app.core.embeddings import embed_text
import time

def ingest(query: str, pages: int = 5):
    db = SessionLocal()
    inserted = 0

    for page in range(1, pages + 1):
        works = fetch_books(query, page=page, limit=100)
        print(f"Page {page}: fetched {len(works)} works")

        for work in works:
            work_key = work.get("key")
            if not work_key:
                continue

            editions = fetch_editions(work_key, limit=3)

            for edition in editions:
                data = normalize_edition(edition)
                if not data:
                    continue

                exists = (
                    db.query(Book)
                    .filter(Book.isbn_13 == data["isbn_13"])
                    .first()
                )
                if exists:
                    continue

                book = Book(
                    isbn_13=data["isbn_13"],
                    title=data["title"],
                    description=data["description"],
                )

                book.embedding = embed_text(
                    f"{book.title}. {book.description or ''}"
                )

                db.add(book)
                inserted += 1
                break

        db.commit()
        time.sleep(1)  # be polite to Open Library

    db.close()
    print(f"Inserted {inserted} books total")


if __name__ == "__main__":
    ingest("philosophy", pages=10)
