from app.db.session import engine
from app.db.base import Base
from app.models.book import Book

Base.metadata.create_all(bind=engine)
