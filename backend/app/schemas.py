from datetime import datetime

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleTokenRequest(BaseModel):
    token: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True


class DiscussionResponse(BaseModel):
    id: int
    book_id: int | None = None
    book_title: str | None = None
    title: str
    excerpt: str
    body: str = ""
    replies: int
    likes_count: int = 0
    liked_by_me: bool = False
    author_name: str = "Community"
    created_at: datetime

    class Config:
        from_attributes = True


class BookCardResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    cover_url: str
    rating: float

    class Config:
        from_attributes = True


class BookDetailResponse(BookCardResponse):
    description: str
    publication_year: int
    language: str
    pages: int
    discussions: list[DiscussionResponse]


class HomeResponse(BaseModel):
    welcome_name: str
    trending_discussions: list[DiscussionResponse]
    recommended_books: list[BookCardResponse]


class DiscussionCreateRequest(BaseModel):
    title: str
    excerpt: str
    body: str = ""


class DiscussionLikeResponse(BaseModel):
    discussion_id: int
    likes_count: int
    liked: bool


class ThreadPostCreateRequest(BaseModel):
    content: str
    parent_post_id: int | None = None


class ThreadPostResponse(BaseModel):
    id: int
    discussion_id: int
    parent_post_id: int | None
    author_name: str
    content: str
    created_at: datetime
    depth: int


class DiscussionThreadResponse(BaseModel):
    id: int
    book_id: int
    book_title: str
    title: str
    excerpt: str
    body: str
    replies: int
    likes_count: int
    liked_by_me: bool
    author_name: str
    created_at: datetime
    posts: list[ThreadPostResponse]
