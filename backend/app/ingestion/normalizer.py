def normalize_edition(edition: dict):
    isbn_13 = None
    isbn_10 = None

    for isbn in edition.get("isbn_13", []) or []:
        isbn_13 = isbn.replace("-", "")
        break

    for isbn in edition.get("isbn_10", []) or []:
        isbn_10 = isbn.replace("-", "")
        break

    isbn = isbn_13 or isbn_10
    if not isbn:
        return None

    return {
        "isbn_13": isbn,
        "title": edition.get("title"),
        "description": None,
    }
