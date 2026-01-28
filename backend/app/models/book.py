from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.db.base import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    isbn_13 = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)

    embedding = Column(Vector(384))
