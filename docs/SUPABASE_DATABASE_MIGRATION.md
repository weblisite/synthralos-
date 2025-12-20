# Migrating to Supabase Database

This guide explains how to migrate from Render PostgreSQL database to Supabase for all database operations.

## Overview

SynthralOS now uses **Supabase for everything**:
- ✅ **Authentication** - Supabase Auth
- ✅ **Database** - Supabase PostgreSQL
- ✅ **Storage** - Supabase Storage (can be added later)

## Why Supabase?

- **Unified Platform**: One service for auth, database, and storage
- **Free Tier**: Generous free tier for development
- **PostgreSQL**: Full PostgreSQL database with extensions
- **Real-time**: Built-in real-time subscriptions
- **Row Level Security**: Database-level security policies
- **No Separate Database**: No need for Render database

## Migration Steps

### 1. Get Supabase Database Connection String

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to **Settings** → **Database**
4. Scroll down to **Connection string**
5. Choose **Connection pooling** (recommended for serverless/Render)
6. Copy the connection string

**Format:**
```
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Or get individual values:**
- **Host**: `db.[PROJECT_REF].supabase.co` (direct) or `aws-0-[REGION].pooler.supabase.com` (pooler)
- **Port**: `5432` (direct) or `6543` (pooler - recommended)
- **Database**: `postgres`
- **User**: `postgres.[PROJECT_REF]` (pooler) or `postgres` (direct)
- **Password**: Your database password (found in Settings > Database)

### 2. Update Environment Variables

#### For Local Development (.env file)

```bash
# Supabase Auth
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key

# Supabase Database - Option 1: Full connection string (recommended)
SUPABASE_DB_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Supabase Database - Option 2: Password only (alternative)
# SUPABASE_DB_PASSWORD=your-database-password
```

#### For Render Deployment

1. Go to Render Dashboard → Your Backend Service → Environment
2. Add/Update these variables:
   - `SUPABASE_URL` = Your Supabase project URL
   - `SUPABASE_ANON_KEY` = Your Supabase anon key
   - `SUPABASE_DB_URL` = Your Supabase database connection string (pooler)

3. **Remove** these variables (no longer needed):
   - `POSTGRES_SERVER`
   - `POSTGRES_PORT`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`

### 3. Run Database Migrations

Your existing Alembic migrations will work with Supabase PostgreSQL:

```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Run migrations
alembic upgrade head
```

### 4. Verify Connection

Check that your application connects to Supabase:

```bash
# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Check logs for successful database connection
```

## Configuration Priority

The backend uses this priority order for database connection:

1. **`SUPABASE_DB_URL`** (full connection string) - **Recommended**
2. **`SUPABASE_URL` + `SUPABASE_DB_PASSWORD`** (auto-build connection)
3. **Legacy `POSTGRES_*` variables** (for backward compatibility)

## Connection Pooling

**Important**: Use Supabase's connection pooler (port 6543) for:
- ✅ Serverless environments (Render, Vercel, etc.)
- ✅ High concurrency applications
- ✅ Better connection management

**Direct connection** (port 5432) is for:
- Local development
- Long-lived connections
- When you need specific PostgreSQL features

## Render Deployment Changes

### Before (with Render database):
```yaml
databases:
  - name: synthralos-db
    plan: free
```

### After (Supabase only):
```yaml
# No database needed - using Supabase
```

The `render.yaml` file has been updated to remove the database dependency.

## Troubleshooting

### Connection Issues

**Error**: "Connection refused" or "Timeout"
- **Solution**: Make sure you're using the **pooler connection** (port 6543) for Render
- **Check**: Verify your `SUPABASE_DB_URL` includes `pooler.supabase.com:6543`

**Error**: "IPv6 not supported"
- **Solution**: Use the connection pooler URL which supports IPv4
- **Format**: `postgresql://postgres.[REF]:[PASS]@aws-0-[REGION].pooler.supabase.com:6543/postgres`

### Migration Issues

**Error**: "Table already exists"
- **Solution**: Your tables might already exist. Check Supabase dashboard → Table Editor
- **Action**: Drop existing tables or use `alembic upgrade head --sql` to preview changes

**Error**: "Permission denied"
- **Solution**: Make sure you're using the correct database password
- **Check**: Supabase Dashboard → Settings → Database → Database password

## Benefits of Supabase Database

1. **Unified Platform**: Auth + Database + Storage in one place
2. **Real-time**: Built-in real-time subscriptions
3. **Row Level Security**: Database-level security policies
4. **Extensions**: Access to PostgreSQL extensions
5. **Backups**: Automatic backups (on paid plans)
6. **Monitoring**: Built-in database monitoring
7. **No Separate Service**: One less service to manage

## Next Steps

- ✅ Database migration complete
- 🔄 Consider adding Supabase Storage for file uploads
- 🔄 Consider enabling Row Level Security (RLS) policies
- 🔄 Consider using Supabase real-time subscriptions

## Support

If you encounter issues:
1. Check Supabase Dashboard → Database → Connection pooling
2. Verify environment variables are set correctly
3. Check backend logs for connection errors
4. Ensure migrations have run successfully
