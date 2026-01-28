import requests

BASE_URL = "https://openlibrary.org/search.json"

def fetch_books(query: str, page: int = 1, limit: int = 100):
    params = {
        "q": query,
        "page": page,
        "limit": limit,
        "language": "eng",
    }

    res = requests.get(BASE_URL, params=params, timeout=10)
    res.raise_for_status()
    return res.json().get("docs", [])
