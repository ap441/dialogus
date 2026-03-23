import math
import re
from collections import Counter

from app.models import Book


TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}

SYNONYMS = {
    "ai": {"artificial", "intelligence", "machine", "learning"},
    "fantasy": {"magic", "sword", "epic", "myth"},
    "romance": {"love", "relationship", "heart"},
    "scifi": {"science", "fiction", "space", "future"},
    "science": {"physics", "biology", "chemistry", "technology"},
    "thriller": {"mystery", "crime", "suspense"},
    "history": {"historical", "war", "civilization"},
}


def _tokenize(text: str) -> list[str]:
    tokens = TOKEN_RE.findall((text or "").lower())
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def _expand_query(tokens: list[str]) -> list[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded.update(SYNONYMS.get(token, set()))
    return list(expanded)


def _book_text(book: Book) -> str:
    return " ".join(
        [
            book.title or "",
            book.author or "",
            book.genre or "",
            book.description or "",
        ]
    )


def _cosine_similarity(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0

    dot = sum(a[token] * b[token] for token in a.keys() & b.keys())
    mag_a = math.sqrt(sum(value * value for value in a.values()))
    mag_b = math.sqrt(sum(value * value for value in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _score_book(book: Book, query_terms: list[str]) -> float:
    book_tokens = _tokenize(_book_text(book))
    query_counter = Counter(query_terms)
    book_counter = Counter(book_tokens)

    cosine = _cosine_similarity(query_counter, book_counter)
    overlap = len(set(query_terms) & set(book_tokens)) / max(len(set(query_terms)), 1)
    rating_bonus = (book.rating or 0.0) / 10.0

    # Keep weights simple and stable for small datasets.
    return cosine * 0.65 + overlap * 0.3 + rating_bonus * 0.05


def rank_books_semantically(books: list[Book], query: str) -> list[Book]:
    if not query or not query.strip():
        return sorted(books, key=lambda book: ((book.rating or 0.0), (book.title or "").lower()), reverse=True)

    query_tokens = _tokenize(query)
    query_terms = _expand_query(query_tokens)
    if not query_terms:
        return sorted(books, key=lambda book: ((book.rating or 0.0), (book.title or "").lower()), reverse=True)

    scored = [(book, _score_book(book, query_terms)) for book in books]
    scored.sort(key=lambda item: item[1], reverse=True)
    positive = [book for book, score in scored if score > 0]
    if positive:
        return positive
    return [book for book, _ in scored]
