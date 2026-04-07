# Supabase Database Setup - Quick Start

## ✅ Changes Made to Your App

Your codebase is now configured for centralized PostgreSQL database via Supabase:

### Files Updated:
1. **`docker-compose.yml`** - Now reads `DATABASE_URL` from `.env` file
2. **`app/db/session.py`** - Added PostgreSQL connection pooling support
3. **`app/main.py`** - Enhanced startup to handle both SQLite and PostgreSQL schema backfill
4. **`.gitignore`** - Added `.env` files (never commit passwords!)

### Files Created:
1. **`.env.example`** - Template for environment variables
2. **`DATABASE_MIGRATION.md`** - Complete migration guide
3. **`SUPABASE_SETUP.md`** - Supabase-specific setup instructions
4. **`test_db_connection.py`** - Connection test utility

---

## 🚀 Next Steps (3 Steps, ~10 minutes)

### Step 1: Create Supabase Project (5 minutes)

```bash
# 1. Go to https://supabase.com
# 2. Sign up (use GitHub for faster setup)
# 3. Create new project named "dialogus"
# 4. Create a STRONG database password (save it!)
# 5. Wait for green status ✓
# 6. Go to Settings → Database → Connection Pooling
# 7. Copy the PostgreSQL URI
```

Save the connection string that looks like:
```
postgresql://postgres.XXXX:PASSWORD@db.XXXX.supabase.co:5432/postgres
```

### Step 2: Create .env File (2 minutes)

```bash
cd /home/scarlet/Documents/Projects/dialogus

# Create .env file
cp .env.example .env

# Edit .env and paste your connection string:
# DATABASE_URL=postgresql://postgres.XXXX:PASSWORD@db.XXXX.supabase.co:5432/postgres

# On Mac/Linux, you can use nano:
nano .env
```

**Important:** Never commit this file! It contains your database password.

### Step 3: Deploy (3 minutes)

```bash
# Stop current containers (optional, but clean)
docker compose down

# Start with new database
docker compose up -d --build

# Watch backend initialize
docker compose logs -f backend
```

**Look for:**
- ✅ `Uvicorn running on http://0.0.0.0:8000`
- ✅ No connection errors

**Press Ctrl+C** when you see it's running.

---

## 🧪 Verify It Works

### Via Terminal

```bash
# Test database connection
python test_db_connection.py

# Test API
curl http://localhost:8000/api/health
# Should return: {"status":"ok"}
```

### Via Browser

```bash
# Open in browser
open http://localhost:3000

# Try:
# 1. Sign up with an email
# 2. Create a discussion
# 3. Add a reaction
# 4. REFRESH the page - data persists! (It's now in Supabase!)
```

### Verify in Supabase Dashboard

```
1. Go to https://supabase.com/projects
2. Click your "dialogus" project
3. Left sidebar → SQL Editor
4. Run: SELECT * FROM discussions;
5. You should see your demo data + anything you created!
```

---

## 📊 What's Different?

| Aspect | Before (SQLite) | After (Supabase) |
|--------|-----------------|-----------------|
| Database Access | Local file only | Network accessible |
| Data Persistence | Container volume | Cloud servers |
| Backups | Manual | Automatic |
| Scalability | Single container | Multi-instance ready |
| Team Access | Requires SSH | Direct via connection string |
| Cost | Free | Free (with limits) |

---

## ⚡ Troubleshooting

### "Connection refused"
```bash
# Make sure backend service is running
docker compose ps

# Check backend logs for errors
docker compose logs backend | tail -50
```

### "Authentication failed"
```bash
# Verify password is correct (case-sensitive!)
# Re-copy connection string from Supabase dashboard
# Check for typos in .env file
nano .env
```

### "Too many connections"
```bash
# Restart backend (clears stale connections)
docker compose restart backend

# Check Supabase dashboard for connection count
```

### Data not showing in Supabase dashboard
```bash
# Wait 10 seconds for backend to finish seeding
# Check backend logs
docker compose logs backend | grep seed

# Manually trigger seed if needed
docker exec dialogus-backend-1 python -c \
  "from app.seed import seed_data; from app.db.session import SessionLocal; \
   db = SessionLocal(); seed_data(db); print('✅ Seed complete')"
```

---

## 📚 Reference Docs

- [Supabase PostgreSQL Docs](https://supabase.com/docs/guides/database)
- [SQLAlchemy PostgreSQL](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html)
- [Fast API with Databases](https://fastapi.tiangolo.com/advanced/sql-databases/)

---

## 🔒 Security Checklist

- [ ] `.env` file created (not in git)
- [ ] `.env` added to `.gitignore` (verified)
- [ ] Database password is STRONG (8+ chars, mixed case, numbers, symbols)
- [ ] You've saved password in secure password manager
- [ ] Connection string only shared with trusted team members
- [ ] HTTPS/TLS used for all connections (Supabase default)

---

## 💾 Keeping Your SQLite Database (Optional)

If you want to keep local SQLite for offline development:

```bash
# Stop containers
docker compose down

# The dialogus.db file is preserved in Docker volume
# To use it again, just remove your .env and restart:
rm .env
docker compose up -d --build

# It will use the default SQLite database again
```

Or keep both environments:

```bash
# .env For production (Supabase)
# .env.local for local testing (SQLite)

# Backend auto-loads from: .env, then .env.local
# So add to .env.local: DATABASE_URL=sqlite:///./dialogus.db
```

---

## 🎯 You're All Set!

Your app now has a **production-ready, centralized database** that:

✅ Tracks all user registrations globally  
✅ Persists authentication tokens securely  
✅ Stores all discussions with full threading  
✅ Records every reaction/appreciation  
✅ Automatically backs up your data  
✅ Scales as your user base grows  

**Next:** Share the app with users! Everyone connects to the same Supabase database.

---

## Questions?

Check these files for more details:
- [DATABASE_MIGRATION.md](DATABASE_MIGRATION.md) - Detailed migration guide
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Supabase-specific instructions
- [.env.example](.env.example) - Environment variable reference
