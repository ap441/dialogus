from datetime import datetime

from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    discussions: Mapped[list["Discussion"]] = relationship(back_populates="author")
    discussion_posts: Mapped[list["DiscussionPost"]] = relationship(back_populates="author")
    discussion_likes: Mapped[list["DiscussionLike"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    author: Mapped[str] = mapped_column(String(120))
    genre: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    cover_url: Mapped[str] = mapped_column(String(255))
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    publication_year: Mapped[int] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(40), default="English")
    pages: Mapped[int] = mapped_column(Integer, default=0)

    discussions: Mapped[list["Discussion"]] = relationship(back_populates="book", cascade="all, delete-orphan")


class Discussion(Base):
    __tablename__ = "discussions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    excerpt: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, default="")
    replies: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    book: Mapped[Book] = relationship(back_populates="discussions")
    author: Mapped[User | None] = relationship(back_populates="discussions")
    posts: Mapped[list["DiscussionPost"]] = relationship(back_populates="discussion", cascade="all, delete-orphan")
    likes: Mapped[list["DiscussionLike"]] = relationship(back_populates="discussion", cascade="all, delete-orphan")


class DiscussionPost(Base):
    __tablename__ = "discussion_posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    discussion_id: Mapped[int] = mapped_column(ForeignKey("discussions.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_post_id: Mapped[int | None] = mapped_column(ForeignKey("discussion_posts.id", ondelete="CASCADE"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    discussion: Mapped[Discussion] = relationship(back_populates="posts")
    author: Mapped[User | None] = relationship(back_populates="discussion_posts")
    parent: Mapped["DiscussionPost | None"] = relationship(remote_side="DiscussionPost.id", back_populates="children")
    children: Mapped[list["DiscussionPost"]] = relationship(back_populates="parent", cascade="all, delete-orphan")


class DiscussionLike(Base):
    __tablename__ = "discussion_likes"
    __table_args__ = (UniqueConstraint("discussion_id", "user_id", name="uq_discussion_like"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    discussion_id: Mapped[int] = mapped_column(ForeignKey("discussions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    discussion: Mapped[Discussion] = relationship(back_populates="likes")
    user: Mapped[User] = relationship(back_populates="discussion_likes")
