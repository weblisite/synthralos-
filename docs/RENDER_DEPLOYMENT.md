# Render Deployment Guide

This guide explains how to deploy SynthralOS to Render using the Blueprint configuration.

## Architecture Overview

**SynthralOS uses Supabase for all data services:**
- ✅ **Database:** Supabase PostgreSQL (external service, not managed by Render)
- ✅ **Authentication:** Supabase Auth (external service, not managed by Render)
- ✅ **Storage:** Supabase Storage (external service, not managed by Render)

**Render Services:**
- ✅ **Backend:** FastAPI service (deployed on Render)
- ✅ **Frontend:** React/Vite service (deployed on Render)

**Important:** This deployment does NOT use Render's database service. All database operations connect to Supabase PostgreSQL.

---

## Prerequisites

1. **Supabase Account**
   - Create a project at https://supabase.com
   - Get your project URL and API keys
   - Set up database connection string

2. **Render Account**
   - Sign up at https://render.com
   - Connect your GitHub repository

3. **GitHub Repository**
   - Push your code to GitHub
   - Ensure `render.yaml` is in the root directory

---

## Deployment Steps

### Step 1: Prepare Supabase

1. **Create Supabase Project**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Choose a name and database password
   - Select a region close to your users

2. **Get Supabase Credentials**
   - **Project URL:** Settings > API > Project URL
     - Format: `https://[PROJECT_REF].supabase.co`
   - **Anon Key:** Settings > API > Project API keys > `anon` `public` key
   - **Database Connection String:** Settings > Database > Connection string
     - Use "Connection pooling" option (port 6543) for serverless/Render
     - Format: `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`

3. **Run Database Migrations**
   - See `docs/SUPABASE_DATABASE_MIGRATION.md` for migration instructions
   - All tables should be created before deploying

4. **Create Storage Buckets** (Optional but Recommended)
   - Go to Storage in Supabase Dashboard
   - Create buckets:
     - `ocr-documents` (public or private)
     - `rag-files` (public or private)
     - `user-uploads` (private recommended)
     - `workflow-attachments` (private recommended)
     - `code-executions` (private recommended)

### Step 2: Deploy via Render Blueprint

1. **Create New Blueprint**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select the repository containing `render.yaml`
   - Render will automatically detect the Blueprint

2. **Review Blueprint Configuration**
   - Render will show the services defined in `render.yaml`
   - You should see:
     - `synthralos-backend` (Backend API Service)
     - `synthralos-frontend` (Frontend Web Service)
     - **No database service** (using Supabase instead)

3. **Set Environment Variables**

   **Backend Service (`synthralos-backend`):**
   
   Required:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_ANON_KEY` - Your Supabase anon key
   - `SUPABASE_DB_URL` - Your Supabase database connection string
   - `FRONTEND_HOST` - Will be set after frontend deploys
   - `BACKEND_CORS_ORIGINS` - Will be set after frontend deploys
   
   Optional:
   - `OPENAI_API_KEY` - For OpenAI integrations
   - `ANTHROPIC_API_KEY` - For Anthropic integrations
   - `NANGO_SECRET_KEY` - For OAuth integrations
   - `REDIS_URL` - For caching (if using Redis)
   
   **Frontend Service (`synthralos-frontend`):**
   
   Required:
   - `VITE_API_URL` - Backend URL (set after backend deploys)
   - `VITE_SUPABASE_URL` - Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY` - Your Supabase anon key

4. **Deploy Services**
   - Click "Apply" to deploy all services
   - Render will build and deploy both services
   - Backend will deploy first, then frontend

### Step 3: Update Environment Variables After Deployment

1. **Get Backend URL**
   - After backend deploys, copy the URL
   - Format: `https://synthralos-backend.onrender.com`

2. **Update Frontend Environment Variables**
   - Go to Frontend Service → Environment
   - Update `VITE_API_URL` to: `https://synthralos-backend.onrender.com/api/v1`

3. **Update Backend Environment Variables**
   - Go to Backend Service → Environment
   - Update `FRONTEND_HOST` to: `https://synthralos-frontend.onrender.com`
   - Update `BACKEND_CORS_ORIGINS` to: `https://synthralos-frontend.onrender.com`

4. **Redeploy Services**
   - Backend: Click "Manual Deploy" → "Deploy latest commit"
   - Frontend: Click "Manual Deploy" → "Deploy latest commit"

---

## Environment Variables Reference

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SUPABASE_URL` | ✅ Yes | Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_ANON_KEY` | ✅ Yes | Supabase anon key | `eyJhbGc...` |
| `SUPABASE_DB_URL` | ✅ Yes | Database connection string | `postgresql://postgres...` |
| `FRONTEND_HOST` | ✅ Yes | Frontend URL | `https://synthralos-frontend.onrender.com` |
| `BACKEND_CORS_ORIGINS` | ✅ Yes | CORS allowed origins | `https://synthralos-frontend.onrender.com` |
| `SECRET_KEY` | ✅ Yes | Auto-generated by Render | - |
| `ENVIRONMENT` | ✅ Yes | Set to `production` | `production` |
| `PROJECT_NAME` | ✅ Yes | Project name | `SynthralOS` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `https://synthralos-backend.onrender.com/api/v1` |
| `VITE_SUPABASE_URL` | ✅ Yes | Supabase project URL | `https://abc123.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | ✅ Yes | Supabase anon key | `eyJhbGc...` |

---

## Troubleshooting

### Backend Deployment Issues

**Issue:** Backend fails to start
- **Check:** Database connection string (`SUPABASE_DB_URL`)
- **Check:** Supabase credentials are correct
- **Check:** Database migrations have been run
- **Solution:** Verify Supabase connection string format and credentials

**Issue:** CORS errors
- **Check:** `BACKEND_CORS_ORIGINS` includes frontend URL
- **Check:** `FRONTEND_HOST` is set correctly
- **Solution:** Update CORS settings and redeploy

### Frontend Deployment Issues

**Issue:** Frontend can't connect to backend
- **Check:** `VITE_API_URL` is set correctly
- **Check:** Backend is deployed and accessible
- **Solution:** Verify backend URL and update `VITE_API_URL`

**Issue:** Authentication not working
- **Check:** `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are set
- **Check:** Supabase project is active
- **Solution:** Verify Supabase credentials

**Issue:** Build fails with "Missing Supabase environment variables"
- **Check:** `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are set in Render
- **Solution:** Add missing environment variables and redeploy

### Database Connection Issues

**Issue:** Database connection timeout
- **Check:** Using connection pooler (port 6543) not direct connection (port 5432)
- **Check:** Connection string format is correct
- **Solution:** Use Supabase connection pooler URL for serverless environments

**Issue:** Migration errors
- **Check:** All migrations have been run in Supabase
- **Check:** Database schema matches codebase models
- **Solution:** Run migrations via Supabase Dashboard or Alembic

---

## Post-Deployment Checklist

- [ ] Backend service is running and healthy
- [ ] Frontend service is running and accessible
- [ ] Backend health check endpoint responds: `/api/v1/utils/health-check`
- [ ] Frontend can authenticate users via Supabase
- [ ] Database operations work (create user, workflows, etc.)
- [ ] File uploads work (OCR, RAG, etc.)
- [ ] CORS is configured correctly
- [ ] Environment variables are set correctly
- [ ] Storage buckets are created in Supabase
- [ ] Database migrations are applied

---

## Updating Deployment

### Manual Updates

1. Push changes to GitHub
2. Go to Render Dashboard
3. Select the service to update
4. Click "Manual Deploy" → "Deploy latest commit"

### Automatic Updates

Render automatically deploys when you push to the connected branch (usually `main`).

---

## Cost Considerations

**Render Services:**
- Backend: Starter plan ($7/month) or higher
- Frontend: Starter plan ($7/month) or higher

**Supabase:**
- Free tier includes:
  - 500 MB database
  - 1 GB file storage
  - 50,000 monthly active users
- Upgrade as needed

**Total Estimated Cost:** ~$14/month (Render) + Supabase (free tier or paid)

---

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Database Migration Guide](docs/SUPABASE_DATABASE_MIGRATION.md)
- [Migration Status Report](docs/MIGRATION_STATUS_REPORT.md)
- [Supabase Verification Report](docs/SUPABASE_COMPREHENSIVE_VERIFICATION.md)

---

**Last Updated:** 2025-01-15  
**Status:** Production Ready

