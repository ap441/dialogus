# Supabase Database Setup Guide

## Step 1: Create a Supabase Project

1. Go to https://supabase.com and sign up (or log in)
2. Click "New Project"
3. Fill in:
   - **Project Name**: `dialogus` (or your choice)
   - **Database Password**: Create a secure password (save this!)
   - **Region**: Choose closest to your users (e.g., `us-east-1`, `eu-west-1`)
4. Click "Create New Project" and wait ~2 minutes for provisioning

## Step 2: Get Your Connection String

1. In Supabase dashboard, go to **Settings** → **Database**
2. Under "Connection string", select **URI**
3. Copy the connection string that looks like:
   ```
   postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
   ```
4. Replace `[YOUR_PASSWORD]` with your database password from Step 1

## Step 3: Set Environment Variable

Choose one approach:

### Option A: Update docker-compose.yml (Recommended for local dev)
Not recommended to commit passwords to git. Use `.env` file instead.

### Option B: Use .env File (Best Practice)
1. Create a `.env` file in the workspace root:
   ```bash
   cd /home/scarlet/Documents/Projects/dialogus
   touch .env
   ```

2. Add your connection string:
   ```
   DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_ID].supabase.co:5432/postgres
   ```

3. Update `docker-compose.yml` to load this file (see updated file)

## Step 4: Deploy

```bash
docker compose down
docker compose up -d --build
```

The backend will:
- Detect the remote PostgreSQL database
- Automatically create all tables on startup
- Backfill schema (add missing columns like `reaction_type`)
- Seed demo data

## Step 5: Verify Connection

```bash
docker compose logs -f backend
```

Look for:
- `✓ Database connected` (or similar success message)
- `Uvicorn running on http://0.0.0.0:8000`

If you see any "connection refused" errors, verify:
- Supabase project is active and running
- Connection string is correct
- Firewall allows outbound HTTPS (port 5432)

## Troubleshooting

### "Too many connections" error
- Supabase free tier limits concurrent connections. Restart containers if stuck connections exist.
- Solution: Upgrade to paid tier for higher limits, or implement connection pooling.

### "Password authentication failed"
- Double-check the password in your connection string matches Step 1
- Verify the connection string format

### Database appears empty
- First startup may take 30 seconds for schema creation and seeding
- Check backend logs: `docker compose logs backend`

## Next Steps

1. Test the API: http://localhost:3000
2. Verify authentication and data persistence
3. Your data is now backed by a cloud database!

---

**Supabase Free Tier Includes:**
- PostgreSQL database (up to 500 MB)
- Up to 100 concurrent connections (enough for development)
- Real-time capabilities (bonus feature)
- Supports up to 5 projects
