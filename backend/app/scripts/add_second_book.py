from app.db.session import SessionLocal
from app.models.book import Book

def add_book():
    db = SessionLocal()

    book = Book(
        isbn_13="9780679720201",
        title="Letters from a Stoic",
        description="Letters by Seneca offering advice on Stoic philosophy and daily life."
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    db.close()

    print(f"Inserted book with id={book.id}")

if __name__ == "__main__":
    add_book()

