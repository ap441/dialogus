from sentence_transformers import SentenceTransformer
from app.db.session import SessionLocal
from app.models.book import Book

model = SentenceTransformer("all-MiniLM-L6-v2")

def generate():
    db = SessionLocal()
    books = db.query(Book).filter(Book.embedding == None).all()

    for book in books:
        text = f"{book.title}. {book.description or ''}"
        book.embedding = model.encode(text).tolist()

    db.commit()
    db.close()
    print("Embeddings generated")

if __name__ == "__main__":
    generate()
