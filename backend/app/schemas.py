from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ReactionCounts(BaseModel):
    like: int = 0
    dislike: int = 0
    recommend: int = 0


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
    role: str = "member"
    bio: str | None = ""
    avatar_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdateRequest(BaseModel):
    full_name: str
    bio: str | None = ""
    avatar_url: str | None = None


class ProfileResponse(UserResponse):
    discussion_count: int = 0
    reply_count: int = 0
    reaction_count: int = 0
    notification_count: int = 0
    unread_notification_count: int = 0


class AdminUserResponse(UserResponse):
    discussion_count: int = 0
    reply_count: int = 0
    notification_count: int = 0
    unread_notification_count: int = 0


class AdminUserRoleUpdateRequest(BaseModel):
    role: str


class AdminStatsResponse(BaseModel):
    total_users: int = 0
    total_admins: int = 0
    total_books: int = 0
    total_discussions: int = 0
    total_replies: int = 0
    total_notifications: int = 0
    unread_notifications: int = 0


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    link: str | None = None
    is_read: bool
    actor_name: str | None = None
    created_at: datetime
    read_at: datetime | None = None


class NotificationListResponse(BaseModel):
    unread_count: int
    notifications: list[NotificationResponse]


class AdminDashboardResponse(BaseModel):
    stats: AdminStatsResponse
    users: list[AdminUserResponse]
    recent_discussions: list["DiscussionResponse"]
    recent_notifications: list[NotificationResponse]


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
    user_reaction: str | None = None
    user_reactions: list[str] = Field(default_factory=list)
    reaction_counts: ReactionCounts = Field(default_factory=ReactionCounts)
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


class DiscussionReactionRequest(BaseModel):
    reaction_type: str


class DiscussionReactionResponse(BaseModel):
    discussion_id: int
    reaction_type: str | None
    user_reactions: list[str] = Field(default_factory=list)
    likes_count: int
    reaction_counts: ReactionCounts


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
    user_reaction: str | None = None
    user_reactions: list[str] = Field(default_factory=list)
    reaction_counts: ReactionCounts = Field(default_factory=ReactionCounts)
    author_name: str
    created_at: datetime
    posts: list[ThreadPostResponse]
