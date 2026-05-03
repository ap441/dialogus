import json
import os
import time
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
    "romance",
    "thriller",
    "horror",
    "biography",
    "self_help",
    "philosophy",
    "poetry",
    "young_adult",
    "adventure",
    "classics",
    "crime",
    "dystopia",
    "historical_fiction",
    "literary_fiction",
    "mythology",
    "politics",
    "economics",
    "programming",
    "computer_science",
    "mathematics",
    "art",
    "music",
    "travel",
    "health",
    "education",
]


def _genre_from_subject(subject: str) -> str:
    return subject.replace("_", " ").title()


def _clip(text: str, max_len: int) -> str:
    text = (text or "").strip()
    return text[:max_len]


def _fetch_subject_works(subject: str, limit: int = 20) -> list[dict[str, Any]]:
    safe_subject = quote(subject)
    url = f"https://openlibrary.org/subjects/{safe_subject}.json?limit={limit}"
    with urlopen(url, timeout=4) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("works", [])


def _fetch_work_details(work_key: str) -> dict[str, Any]:
    # Example work key: /works/OL82563W
    safe_key = quote(work_key.strip())
    url = f"https://openlibrary.org{safe_key}.json"
    with urlopen(url, timeout=4) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_description(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        text = value.get("value")
        if isinstance(text, str):
            return text.strip()
    return ""


def _build_cover_url(cover_id: int | None) -> str:
    if not cover_id:
        return "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600"
    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"


def _work_to_book_payload(work: dict[str, Any], genre: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    title = _clip(str(work.get("title") or "Untitled"), 200)
    authors = work.get("authors") or []
    author_name = "Unknown"
    if authors and isinstance(authors[0], dict):
        author_name = _clip(str(authors[0].get("name") or "Unknown"), 120)

    first_publish_year = work.get("first_publish_year") or 0
    cover_id = work.get("cover_id")
    work_description = _extract_description(work.get("description"))
    details_description = _extract_description((details or {}).get("description"))
    description = work_description or details_description

    if not description:
        subject_list = work.get("subject") or (details or {}).get("subjects") or []
        subject_hint = ""
        if isinstance(subject_list, list) and subject_list:
            subject_hint = ", ".join(str(item) for item in subject_list[:3])
        year_hint = f" First published in {first_publish_year}." if first_publish_year else ""
        tail = f" Themes include {subject_hint}." if subject_hint else ""
        description = f"{title} by {author_name} is a {genre.lower()} title discovered from Open Library.{year_hint}{tail}".strip()

    return {
        "title": title,
        "author": author_name,
        "genre": _clip(genre, 80),
        "description": description,
        "cover_url": _clip(_build_cover_url(cover_id), 255),
        "rating": 3.8,
        "publication_year": first_publish_year,
        "language": "English",
        "pages": 0,
    }


def ingest_open_library_books(db: Session, per_subject: int = 80):
    per_subject = int(os.getenv("BOOK_IMPORT_PER_SUBJECT", str(per_subject)))
    max_subjects = int(os.getenv("BOOK_IMPORT_MAX_SUBJECTS", "18"))
    max_description_lookups = int(os.getenv("BOOK_IMPORT_MAX_DESCRIPTION_LOOKUPS", "0"))
    max_runtime_seconds = int(os.getenv("BOOK_IMPORT_MAX_RUNTIME_SECONDS", "20"))
    started = time.monotonic()

    existing_rows = db.query(Book).all()
    existing_by_pair: dict[tuple[str, str], Book] = {}
    for row in existing_rows:
        if row.title and row.author:
            existing_by_pair[(row.title.lower().strip(), row.author.lower().strip())] = row

    items_to_add: list[Book] = []
    descriptions_updated = 0
    description_lookups = 0

    for subject in OPEN_LIBRARY_SUBJECTS[:max_subjects]:
        if time.monotonic() - started > max_runtime_seconds:
            break
        try:
            works = _fetch_subject_works(subject, limit=per_subject)
        except Exception:
            continue

        genre = _genre_from_subject(subject)
        for work in works:
            if time.monotonic() - started > max_runtime_seconds:
                break
            authors = work.get("authors") or []
            author_name = "Unknown"
            if authors and isinstance(authors[0], dict):
                author_name = _clip(str(authors[0].get("name") or "Unknown"), 120)
            title = _clip(str(work.get("title") or "Untitled"), 200)
            key = (title.lower(), author_name.lower())

            existing = existing_by_pair.get(key)
            needs_description_refresh = bool(
                existing
                and existing.description
                and existing.description.startswith("Popular ")
                and "discovered from Open Library" in existing.description
            )

            details: dict[str, Any] | None = None
            work_key = work.get("key")
            should_lookup_details = bool(work_key) and description_lookups < max_description_lookups and (
                not _extract_description(work.get("description")) or needs_description_refresh
            )

            if should_lookup_details:
                try:
                    details = _fetch_work_details(str(work_key))
                    description_lookups += 1
                except Exception:
                    details = None

            payload = _work_to_book_payload(work, genre, details=details)
            key = (payload["title"].lower(), payload["author"].lower())

            if key in existing_by_pair:
                existing_book = existing_by_pair[key]
                if needs_description_refresh and payload["description"] and payload["description"] != existing_book.description:
                    existing_book.description = payload["description"]
                    descriptions_updated += 1
                if existing_book.cover_url.endswith("photo-1512820790803-83ca734da794?w=600") and payload["cover_url"]:
                    existing_book.cover_url = payload["cover_url"]
                continue

            items_to_add.append(Book(**payload))
            existing_by_pair[key] = items_to_add[-1]

    if items_to_add or descriptions_updated:
        db.add_all(items_to_add)
        db.commit()
