from dotenv import load_dotenv

load_dotenv(".env.local")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.discovery import router as discovery_router
from app.api.books import router as books_router
from app.api.discussions import router as discussions_router
from app.api.profile import router as profile_router
from app.api.admin import router as admin_router
from app.api.notifications import router as notifications_router
from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.models import User, Book, Discussion, DiscussionPost, DiscussionLike, Notification  # noqa: F401 - imported for table creation
from app.seed import seed_data

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Initialize database schema and seed data on startup."""
    # Step 1: Create or update all tables based on models
    Base.metadata.create_all(bind=engine)
    
    # Step 2: Run migrations to add missing columns
    db = SessionLocal()
    try:
        from sqlalchemy import text
        
        # Try to add columns
        alter_statements = [
            "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'member'",
            "ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''",
            "ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255)",
            "ALTER TABLE discussions ADD COLUMN author_id INTEGER REFERENCES users(id)",
            "ALTER TABLE discussions ADD COLUMN body TEXT DEFAULT ''",
            "ALTER TABLE discussions ADD COLUMN likes_count INTEGER DEFAULT 0",
            "ALTER TABLE discussion_likes ADD COLUMN reaction_type VARCHAR(16) DEFAULT 'like'"
        ]
        
        migration_success = True
        for stmt in alter_statements:
            try:
                db.execute(text(stmt))
                db.commit()
            except Exception as e:
                db.rollback()
                # Check if this is a "column already exists" error
                if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                    print(f"⚠ Migration warning: {str(e)[:100]}")
                    migration_success = False
        
        # Set defaults for existing data
        try:
            db.execute(text("UPDATE users SET role = COALESCE(role, 'member') WHERE role IS NULL OR role = ''"))
            db.commit()
        except:
            db.rollback()
        
        # Step 3: Seed demo data only if migrations succeeded
        if migration_success:
            seed_data(db)
        else:
            print("⚠ Skipping seed_data due to migration issues. Schema may be out of sync.")
    except Exception as e:
        print(f"⚠ Startup error: {str(e)[:200]}")
        db.rollback()
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(discovery_router)
app.include_router(books_router)
app.include_router(discussions_router)
app.include_router(profile_router)
app.include_router(admin_router)
app.include_router(notifications_router)
