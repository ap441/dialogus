import json
from typing import Any
from urllib.parse import quote
from urllib.request import urlopen

from sqlalchemy.orm import Session

from app.models import Book


OPEN_LIBRARY_SUBJECTS = [
    "fantasy",
    "science_fiction",
    "history",
    "psychology",
    "business",
    "mystery",
]


def _genre_from_subject(subject: str) -> str:
    return subject.replace("_", " ").title()


def _fetch_subject_works(subject: str, limit: int = 20) -> list[dict[str, Any]]:
    safe_subject = quote(subject)
    url = f"https://openlibrary.org/subjects/{safe_subject}.json?limit={limit}"
    with urlopen(url, timeout=8) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("works", [])


def _build_cover_url(cover_id: int | None) -> str:
    if not cover_id:
        return "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600"
    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"


def _work_to_book_payload(work: dict[str, Any], genre: str) -> dict[str, Any]:
    title = (work.get("title") or "Untitled").strip()
    authors = work.get("authors") or []
    author_name = "Unknown"
    if authors and isinstance(authors[0], dict):
        author_name = (authors[0].get("name") or "Unknown").strip()

    first_publish_year = work.get("first_publish_year") or 0
    cover_id = work.get("cover_id")

    return {
        "title": title,
        "author": author_name,
        "genre": genre,
        "description": f"Popular {genre.lower()} title discovered from Open Library.",
        "cover_url": _build_cover_url(cover_id),
        "rating": 3.8,
        "publication_year": first_publish_year,
        "language": "English",
        "pages": 0,
    }


def ingest_open_library_books(db: Session, per_subject: int = 20):
    existing_pairs = {
        (book.title.lower().strip(), book.author.lower().strip())
        for book in db.query(Book.title, Book.author).all()
        if book.title and book.author
    }

    items_to_add: list[Book] = []

    for subject in OPEN_LIBRARY_SUBJECTS:
        try:
            works = _fetch_subject_works(subject, limit=per_subject)
        except Exception:
            continue

        genre = _genre_from_subject(subject)
        for work in works:
            payload = _work_to_book_payload(work, genre)
            key = (payload["title"].lower(), payload["author"].lower())
            if key in existing_pairs:
                continue

            items_to_add.append(Book(**payload))
            existing_pairs.add(key)

    if items_to_add:
        db.add_all(items_to_add)
        db.commit()
