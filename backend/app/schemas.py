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
    title: str
    excerpt: str
    replies: int
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
