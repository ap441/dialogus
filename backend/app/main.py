from dotenv import load_dotenv

load_dotenv(".env.local")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.discovery import router as discovery_router
from app.api.books import router as books_router
from app.api.discussions import router as discussions_router
from app.core.config import settings
from app.db.session import Base, engine, SessionLocal
from app.models import User, Book, Discussion  # noqa: F401 - imported for table creation
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
    db_url = str(engine.url)
    is_sqlite = db_url.startswith("sqlite")
    is_postgresql = "postgresql" in db_url
    
    with engine.begin() as conn:
        # Create all tables first (idempotent)
        Base.metadata.create_all(bind=engine)
        
        # Backfill missing columns for discussions table
        if is_sqlite:
            columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(discussions)").fetchall()}
        else:  # PostgreSQL
            result = conn.exec_driver_sql(
                "SELECT column_name FROM information_schema.columns WHERE table_name='discussions'"
            )
            columns = {row[0] for row in result}
        
        if "author_id" not in columns:
            try:
                conn.exec_driver_sql("ALTER TABLE discussions ADD COLUMN author_id INTEGER")
            except Exception:
                pass  # Column may already exist
        
        if "body" not in columns:
            try:
                conn.exec_driver_sql("ALTER TABLE discussions ADD COLUMN body TEXT DEFAULT ''")
            except Exception:
                pass
        
        if "likes_count" not in columns:
            try:
                conn.exec_driver_sql("ALTER TABLE discussions ADD COLUMN likes_count INTEGER DEFAULT 0")
            except Exception:
                pass
        
        # Backfill missing columns for discussion_likes table
        if is_sqlite:
            like_columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(discussion_likes)").fetchall()}
        else:  # PostgreSQL
            result = conn.exec_driver_sql(
                "SELECT column_name FROM information_schema.columns WHERE table_name='discussion_likes'"
            )
            like_columns = {row[0] for row in result}
        
        if "reaction_type" not in like_columns:
            try:
                conn.exec_driver_sql("ALTER TABLE discussion_likes ADD COLUMN reaction_type TEXT DEFAULT 'like'")
                conn.exec_driver_sql("UPDATE discussion_likes SET reaction_type = COALESCE(reaction_type, 'like')")
            except Exception:
                pass
    
    # Seed demo data
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(discovery_router)
app.include_router(books_router)
app.include_router(discussions_router)
