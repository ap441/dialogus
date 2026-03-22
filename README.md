# Dialogus

Sprint 1 baseline for an intelligent book discovery and discussion platform.

## Implemented In This Iteration

- User authentication API (signup/login/me)
- Frontend auth pages (landing, login, signup)
- Book discovery API and home page (search, trending discussions, recommended books)
- Book detail API and page (book metadata + discussion list)
- Visual style aligned with provided Figma direction (dark atmospheric glassmorphism)

## Tech Stack

- Backend: FastAPI + SQLAlchemy + SQLite + JWT auth
- Frontend: Next.js (App Router) + TypeScript + CSS

## Run Backend

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

Backend default URL: `http://localhost:8000`

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:3000`

## Notes

- Seed data is created on backend startup into `backend/dialogus.db`.
- Demo user credentials:
  - Email: `demo@dialogus.app`
  - Password: `password123`
- Set `NEXT_PUBLIC_API_URL` if backend is not on `http://localhost:8000`.
- Backend database is configured by `DATABASE_URL`.
- Default is local SQLite for quick start. You can switch to Supabase Postgres without code changes.

## Supabase Database Setup

1. Create a Supabase project and open: Project Settings -> Database.
2. Copy the connection string and convert to SQLAlchemy format:
   - `postgresql+psycopg://postgres:<password>@<host>:5432/postgres`
3. Start backend with:

```bash
cd backend
DATABASE_URL='postgresql+psycopg://postgres:<password>@<host>:5432/postgres' .venv/bin/uvicorn app.main:app --reload
```

4. Optional CORS override:

```bash
CORS_ORIGINS='http://localhost:3000,http://127.0.0.1:3000'
```

## Python Compatibility

- FastAPI depends on pydantic-core, which currently does not provide stable support for Python 3.14 in this environment.
- Use Python 3.12 or 3.13 for local backend execution.

## Docker Run (Recommended On Python 3.14 Hosts)

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
