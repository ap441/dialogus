from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.books import router as books_router

app = FastAPI(title="Dialogus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Dialogus backend running"}

app.include_router(books_router)
