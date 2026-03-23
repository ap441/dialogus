from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.discovery import router as discovery_router
from app.api.books import router as books_router
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
    Base.metadata.create_all(bind=engine)
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
