from app.ingestion.openlibrary import fetch_books
import json

docs = fetch_books("stoic philosophy", limit=5)

print(f"Fetched {len(docs)} docs\n")

for i, doc in enumerate(docs, start=1):
    print(f"--- DOC {i} ---")
    print("keys:", doc.keys())
    print("title:", doc.get("title"))
    print("isbn:", doc.get("isbn"))
    print("edition_key:", doc.get("edition_key"))
    print()
