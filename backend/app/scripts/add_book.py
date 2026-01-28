from app.db.session import SessionLocal
from app.models.book import Book

def add_book():
    db = SessionLocal()

    book = Book(
        isbn_13="9780140449136",
        title="Meditations",
        description="A series of personal writings by Marcus Aurelius on Stoic philosophy."
    )

    db.add(book)
    db.commit()
    db.refresh(book)
    db.close()

    print(f"Inserted book with id={book.id}")

if __name__ == "__main__":
    add_book()
