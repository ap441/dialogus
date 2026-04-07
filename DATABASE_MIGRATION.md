# Database Migration & Deployment Guide

## Architecture Overview

Your app now supports two database configurations:

### Local Development (SQLite)
- **File**: `dialogus.db` (in container volume)
- **Setup Time**: Instant
- **Best For**: Local development, testing
- **Limitation**: Single container must access database

### Production (Supabase PostgreSQL)
- **Host**: Managed PostgreSQL on Supabase servers
- **Access**: Network connection (HTTPS over port 5432)
- **Setup Time**: ~2 minutes (account creation + project setup)
- **Best For**: Production, multi-instance deployment, team collaboration
- **Included**: Automated backups, monitoring, 24/7 uptime

---

## Migration Steps

### Phase 1: Supabase Account Setup (5 minutes)

1. **Create Account**
   - Go to https://supabase.com
   - Click "Sign Up"
   - Use email or GitHub (GitHub recommended)
   - Verify email

2. **Create Project**
   - Dashboard → "New Project"
   - Project Name: `dialogus`
   - Database Password: **Create a STRONG password** (save to password manager!)
   - Region: Choose closest to your users
   - Click "Create New Project"
   - Wait for provisioning (shows green checkmark when ready)

3. **Get Connection String**
   - Left sidebar → Settings → Database → Connection pooling or direct
   - Connection type: "Connection string"
   - Copy the PostgreSQL URI:
     ```
     postgresql://postgres.XXXX:PASSWORD@db.XXXX.supabase.co:5432/postgres
     ```
   - Save this somewhere safe!

### Phase 2: Update Local Environment

1. **Stop current containers**
   ```bash
   docker compose down
   ```

2. **Create .env file** (in project root)
   ```bash
   # Copy from .env.example
   cp .env.example .env
   ```

3. **Edit .env** with your Supabase connection string
   ```bash
   # Edit with your editor or:
   nano .env
   ```
   
   Replace:
   ```
   DATABASE_URL=postgresql://postgres.XXXX:YOUR_PASSWORD@db.XXXX.supabase.co:5432/postgres
   ```

4. **Verify .env is in .gitignore** (never commit passwords!)
   ```bash
   grep ".env" .gitignore
   # Should see: .env (and .env.local, etc.)
   ```

### Phase 3: Deploy

1. **Rebuild containers with new database**
   ```bash
   docker compose up -d --build
   ```

2. **Watch backend initialize**
   ```bash
   docker compose logs -f backend
   ```
   
   Look for:
   - ✅ "Uvicorn running on http://0.0.0.0:8000"
   - ✅ No "connection refused" or "authentication failed" errors
   - ✅ Schema created (tables appear in Supabase dashboard)

3. **Verify connection** (in another terminal)
   ```bash
   curl http://localhost:8000/api/health
   # Should return: {"status":"ok"}
   ```

### Phase 4: Validation

1. **Check Supabase Dashboard**
   - Settings → Database → Tables
   - Should see: users, books, discussions, discussion_likes, discussion_posts
   - All should have data from seed

2. **Test Full Flow**
   ```bash
   # Open browser
   open http://localhost:3000
   
   # Try:
   # 1. Sign up with new user
   # 2. Create a discussion
   # 3. Add a reaction (like/dislike/recommend)
   # 4. Refresh page - data persists (from Supabase!)
   ```

3. **Verify Data in Supabase** (if curious)
   - Supabase Dashboard → SQL Editor
   - Run: `SELECT * FROM discussions;`
   - Should show your created content

---

## Troubleshooting

### Error: "authentication failed for user "postgres""
- ❌ **Cause**: Password in connection string is wrong
- ✅ **Fix**: Double-check password matches Step 1.2 (case-sensitive!)
- ✅ **Verify**: You can log into Supabase dashboard with same credentials

### Error: "Connection refused" or "Network unreachable"
- ❌ **Cause**: Connection string hostname is wrong, or Supabase project not running
- ✅ **Fix**: Make sure Supabase project shows green status
- ✅ **Check**: Are you behind a firewall? Test with: `ping db.XXXX.supabase.co`

### Error: "too many connections"
- ❌ **Cause**: Supabase free tier has 100 concurrent connection limit
- ✅ **Fix** (temporary): Restart backend: `docker compose restart backend`
- ✅ **Fix** (permanent): Upgrade Supabase tier, or implement connection pooling proxy

### Data not syncing / Tables empty after deployment
- ✅ **Check**: Backend logs for seed errors: `docker compose logs backend | grep -i seed`
- ✅ **Fix**: Manually seed via: `docker exec dialogus-backend-1 python -c "from app.seed import seed_data; from app.db.session import SessionLocal; db = SessionLocal(); seed_data(db)"`

### Frontend still showing old data
- ✅ **Clear browser cache**: Ctrl+Shift+Delete (Chrome) or Cmd+Shift+Delete (Mac)
- ✅ **Hard refresh**: Ctrl+F5 or Cmd+Shift+R
- ✅ **Check frontend logs**: `docker compose logs frontend`

---

## Rollback to SQLite (if needed)

If you want to go back to local SQLite for any reason:

```bash
docker compose down

# Edit .env
nano .env
# Change: DATABASE_URL=sqlite:///./dialogus.db

# Restart with local database
docker compose up -d --build
```

Your local `dialogus.db` file will be restored (if it still exists in the volume).

---

## Production Deployment Checklist

If deploying to production servers (AWS, Heroku, etc.):

- [ ] Create separate Supabase project for production (don't use dev project!)
- [ ] Update JWT_SECRET to random cryptographic value: `openssl rand -base64 32`
- [ ] Update CORS_ORIGINS to your actual frontend domain
- [ ] Use environment variables (never hardcode secrets)
- [ ] Enable SSL/TLS for all connections
- [ ] Test with real user load
- [ ] Set up automated backups (Supabase handles this)
- [ ] Monitor database metrics

---

## Supabase Free Tier Limits

| Resource | Limit |
|----------|-------|
| Database Size | 500 MB |
| Concurrent Connections | 100 |
| API Requests | Unlimited |
| Auth Users | Unlimited |
| Storage | 1 GB |
| Projects | 5 |

✅ Plenty for a growing application. Upgrade when you need more.

---

## Quick Reference

| Task | Command |
|------|---------|
| Start services | `docker compose up -d` |
| View backend logs | `docker compose logs -f backend` |
| View frontend logs | `docker compose logs -f frontend` |
| Stop all services | `docker compose down` |
| Reset database (caution!) | `docker volume rm dialogus_*` then `docker compose up -d` |
| Access Supabase | https://supabase.com/projects |
| Check database status | `curl http://localhost:8000/api/health` |

---

## What's Changed in Your Code

### Backend
- ✅ `app/db/session.py`: Now uses connection pooling for PostgreSQL
- ✅ `app/main.py`: Startup script detects both SQLite and PostgreSQL, backfills schemas
- ✅ `docker-compose.yml`: Reads DATABASE_URL from `.env` file
- ✅ No code changes needed to business logic - SQLAlchemy handles it!

### Frontend
- ✅ No changes - still connects to backend via Docker network

### Database
- Your data is now:
  - ✅ Centralized (accessible from anywhere with connection string)
  - ✅ Backed up automatically (Supabase feature)
  - ✅ Scalable (Supabase handles infrastructure)
  - ✅ Secure (SSL/TLS encrypted connections)

---

## Next Steps

1. Follow "Migration Steps" above to set up Supabase
2. Test the connection works
3. Verify all features still work (timeline, reactions, threads)
4. Show your friend/team the live app!

🎉 Your app now has a professional, scalable database!
