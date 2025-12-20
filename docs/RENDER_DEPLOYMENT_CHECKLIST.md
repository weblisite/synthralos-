# Render Deployment Checklist

**Status:** ✅ Ready for Deployment
**Date:** 2025-01-15

---

## Pre-Deployment Verification

### ✅ Configuration Files

- [x] `render.yaml` exists and is properly formatted
- [x] No Render database service included (using Supabase)
- [x] Backend service configured with Supabase environment variables
- [x] Frontend service configured with Supabase environment variables
- [x] Frontend Dockerfile includes Supabase build args
- [x] Backend Dockerfile configured correctly

### ✅ Supabase Setup

- [x] Supabase project created
- [x] Database migrations applied (all 38 tables exist)
- [x] Storage buckets created (optional but recommended)
- [x] Supabase credentials obtained:
  - [x] Project URL (`SUPABASE_URL`)
  - [x] Anon Key (`SUPABASE_ANON_KEY`)
  - [x] Database Connection String (`SUPABASE_DB_URL`)

### ✅ Codebase Status

- [x] All database operations use Supabase PostgreSQL
- [x] All authentication uses Supabase Auth
- [x] All storage operations use Supabase Storage
- [x] No hardcoded database connections
- [x] Environment variables properly configured

---

## Deployment Steps

### Step 1: Create Render Blueprint

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Click "New +" → "Blueprint"

2. **Connect Repository**
   - Select your GitHub repository
   - Render will detect `render.yaml` automatically

3. **Review Services**
   - You should see:
     - ✅ `synthralos-backend` (Backend API Service)
     - ✅ `synthralos-frontend` (Frontend Web Service)
     - ❌ No database service (this is correct - using Supabase)

### Step 2: Set Environment Variables (Backend)

**Before deploying, set these in Render Dashboard:**

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Your Supabase anon key
- `SUPABASE_DB_URL` - Your Supabase database connection string (use pooler)

**Can be set after deployment:**
- `FRONTEND_HOST` - Set after frontend deploys
- `BACKEND_CORS_ORIGINS` - Set after frontend deploys

**Optional:**
- `FIRST_SUPERUSER` - Admin email (default: admin@synthralos.ai)
- `FIRST_SUPERUSER_PASSWORD` - Admin password (change in production!)
- `OPENAI_API_KEY` - For OpenAI integrations
- `ANTHROPIC_API_KEY` - For Anthropic integrations
- `NANGO_SECRET_KEY` - For OAuth integrations

### Step 3: Set Environment Variables (Frontend)

**Before deploying, set these in Render Dashboard:**

**Required:**
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Your Supabase anon key

**Can be set after backend deploys:**
- `VITE_API_URL` - Backend URL (set after backend deploys)

### Step 4: Deploy Services

1. **Deploy Backend First**
   - Click "Apply" or "Deploy" on backend service
   - Wait for deployment to complete
   - Copy the backend URL (e.g., `https://synthralos-backend.onrender.com`)

2. **Update Frontend Environment Variables**
   - Go to Frontend Service → Environment
   - Update `VITE_API_URL` to: `https://synthralos-backend.onrender.com/api/v1`
   - Redeploy frontend

3. **Update Backend Environment Variables**
   - Go to Backend Service → Environment
   - Update `FRONTEND_HOST` to: `https://synthralos-frontend.onrender.com`
   - Update `BACKEND_CORS_ORIGINS` to: `https://synthralos-frontend.onrender.com`
   - Redeploy backend

### Step 5: Verify Deployment

**Backend Health Check:**
- Visit: `https://synthralos-backend.onrender.com/api/v1/utils/health-check`
- Should return: `{"status": "healthy"}`

**Frontend:**
- Visit: `https://synthralos-frontend.onrender.com`
- Should load the application
- Try logging in with Supabase Auth

**Database Connection:**
- Backend logs should show successful database connection
- No connection errors in Render logs

---

## Post-Deployment Verification

### ✅ Backend Checks

- [ ] Health check endpoint responds
- [ ] Database connection successful (check logs)
- [ ] Supabase Auth working (test login endpoint)
- [ ] CORS configured correctly
- [ ] No environment variable errors

### ✅ Frontend Checks

- [ ] Application loads
- [ ] Can connect to backend API
- [ ] Supabase Auth working (can login/signup)
- [ ] No console errors
- [ ] Environment variables loaded correctly

### ✅ Integration Checks

- [ ] User can sign up via Supabase Auth
- [ ] User can log in via Supabase Auth
- [ ] Backend can verify Supabase JWT tokens
- [ ] Database operations work (create workflow, etc.)
- [ ] File uploads work (if storage buckets created)

---

## Troubleshooting

### Backend Won't Start

**Check:**
1. `SUPABASE_DB_URL` is set correctly
2. Connection string uses pooler (port 6543)
3. Database password is correct
4. Supabase project is active

**Solution:**
- Verify Supabase credentials
- Check Render logs for specific errors
- Ensure database migrations are applied

### Frontend Build Fails

**Check:**
1. `VITE_SUPABASE_URL` is set
2. `VITE_SUPABASE_ANON_KEY` is set
3. Build args are passed to Dockerfile

**Solution:**
- Verify environment variables in Render dashboard
- Check Dockerfile includes build args
- Review build logs for specific errors

### CORS Errors

**Check:**
1. `BACKEND_CORS_ORIGINS` includes frontend URL
2. `FRONTEND_HOST` is set correctly
3. URLs match exactly (including https://)

**Solution:**
- Update CORS settings
- Redeploy backend
- Clear browser cache

### Authentication Not Working

**Check:**
1. Supabase credentials are correct
2. Supabase project is active
3. Frontend can connect to Supabase

**Solution:**
- Verify Supabase credentials
- Check Supabase project status
- Review browser console for errors

---

## Environment Variables Reference

### Backend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon key | `eyJhbGc...` |
| `SUPABASE_DB_URL` | Database connection string | `postgresql://postgres...` |
| `PROJECT_NAME` | Project name | `SynthralOS` |
| `ENVIRONMENT` | Environment | `production` |
| `SECRET_KEY` | Auto-generated by Render | - |

### Frontend Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_SUPABASE_URL` | Supabase project URL | `https://abc123.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key | `eyJhbGc...` |
| `VITE_API_URL` | Backend API URL | `https://synthralos-backend.onrender.com/api/v1` |

---

## Deployment Status

**Current Status:** ✅ Ready for Deployment

**What's Ready:**
- ✅ Blueprint configuration (`render.yaml`)
- ✅ Backend Dockerfile
- ✅ Frontend Dockerfile
- ✅ Environment variables documented
- ✅ Supabase integration verified
- ✅ Database migrations applied

**What Needs to Be Done:**
1. Create Render Blueprint
2. Set environment variables
3. Deploy services
4. Update URLs after deployment
5. Verify everything works

---

## Next Steps

1. **Create Blueprint in Render**
   - Follow Step 1 above
   - Review services before deploying

2. **Set Environment Variables**
   - Set Supabase credentials first
   - Set other variables as needed

3. **Deploy Backend**
   - Deploy backend service first
   - Wait for successful deployment
   - Copy backend URL

4. **Deploy Frontend**
   - Set `VITE_API_URL` to backend URL
   - Deploy frontend service
   - Wait for successful deployment

5. **Update CORS**
   - Update backend CORS settings
   - Redeploy backend

6. **Test Everything**
   - Run through verification checklist
   - Test authentication
   - Test database operations

---

**Last Updated:** 2025-01-15
**Status:** Ready for Production Deployment
