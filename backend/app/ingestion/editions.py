import requests

BASE_URL = "https://openlibrary.org"

def fetch_editions(work_key: str, limit: int = 5):
    url = f"{BASE_URL}{work_key}/editions.json"
    params = {"limit": limit}

    res = requests.get(url, params=params, timeout=10)
    res.raise_for_status()
    return res.json().get("entries", [])
