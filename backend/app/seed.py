import os

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User, Book, Discussion, DiscussionPost, Notification
from app.services.book_import import ingest_open_library_books


SEED_BOOKS = [
    {
        "title": "Shadow Slave",
        "author": "Guiltythree",
        "genre": "Fantasy",
        "description": "A dark fantasy progression story where survival, power, and sacrifice intertwine.",
        "cover_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600",
        "rating": 4.7,
        "publication_year": 2019,
        "language": "English",
        "pages": 920,
        "discussions": [
            {"title": "Question 1?", "excerpt": "What do you think of Sunny's decision in chapter 12?", "replies": 34},
            {"title": "Question 2?", "excerpt": "Is the dream realm metaphorical or literal in your interpretation?", "replies": 19},
            {"title": "Question 3?", "excerpt": "Favorite supporting character and why?", "replies": 8},
        ],
    },
    {
        "title": "The Novels Extra",
        "author": "Jee Gab Song",
        "genre": "Action",
        "description": "A meta-fictional action-fantasy where an author becomes a side character.",
        "cover_url": "https://images.unsplash.com/photo-1495640388908-05fa85288e61?w=600",
        "rating": 4.4,
        "publication_year": 2018,
        "language": "English",
        "pages": 680,
        "discussions": [
            {"title": "Character Arc", "excerpt": "Which arc had the best pacing and payoff?", "replies": 22},
        ],
    },
    {
        "title": "Supreme Magus",
        "author": "Legion20",
        "genre": "Fantasy",
        "description": "Reincarnation fantasy centered on growth, trauma, and magical systems.",
        "cover_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600",
        "rating": 4.3,
        "publication_year": 2019,
        "language": "English",
        "pages": 1100,
        "discussions": [
            {"title": "Magic Mechanics", "excerpt": "Which magic path seems strongest for late game?", "replies": 15},
        ],
    },
]


def seed_data(db: Session):
    demo_user = db.query(User).filter(User.email == "demo@dialogus.app").first()
    if db.query(User).count() == 0:
        demo_user = User(
            full_name="Demo Reader",
            email="demo@dialogus.app",
            hashed_password=hash_password("password123"),
        )
        db.add(demo_user)
        db.flush()

    if db.query(Book).count() == 0:
        for item in SEED_BOOKS:
            payload = dict(item)
            discussions = payload.pop("discussions")
            book = Book(**payload)
            db.add(book)
            db.flush()

            for disc in discussions:
                excerpt = disc["excerpt"]
                discussion = Discussion(
                    book_id=book.id,
                    author_id=demo_user.id if demo_user else None,
                    title=disc["title"],
                    excerpt=excerpt,
                    body=excerpt,
                    replies=disc["replies"],
                    likes_count=max(1, disc["replies"] // 3),
                )
                db.add(discussion)
                db.flush()

                db.add(
                    DiscussionPost(
                        discussion_id=discussion.id,
                        author_id=demo_user.id if demo_user else None,
                        parent_post_id=None,
                        content="Opening thought: I think this chapter signals a major shift in stakes.",
                    )
                )

    db.commit()

    if db.query(Notification).count() == 0 and demo_user:
        db.add(
            Notification(
                user_id=demo_user.id,
                actor_user_id=None,
                notification_type="system_welcome",
                title="Welcome to Dialogus",
                message="Your reading community is ready. Try replying to a discussion or reacting to a post.",
                link="/home",
                is_read=False,
            )
        )
        db.commit()

    # Optional enrichment from Open Library. Disabled by default in docker-compose to keep startup fast.
    if os.getenv("BOOK_IMPORT_ENABLED", "1").lower() not in {"0", "false", "no"}:
        ingest_open_library_books(db, per_subject=80)
