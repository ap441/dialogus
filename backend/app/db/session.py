from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool, StaticPool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Configure connection pool based on database type
db_url = settings.database_url
is_sqlite = db_url.startswith("sqlite")
is_postgresql = "postgresql" in db_url

if is_sqlite:
    # SQLite: use StaticPool for in-process database
    connect_args = {"check_same_thread": False}
    pool_config = {"poolclass": StaticPool}
elif is_postgresql:
    # PostgreSQL: use connection pooling (default NullPool for serverless/managed)
    # For Supabase, NullPool avoids connection exhaustion
    connect_args = {}
    pool_config = {"poolclass": NullPool}
else:
    # Generic fallback
    connect_args = {}
    pool_config = {}

engine = create_engine(db_url, connect_args=connect_args, **pool_config)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
