# Render Deployment Guide for SynthralOS

This guide will help you deploy SynthralOS on Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. GitHub repository with your code pushed
3. Environment variables ready (see Environment Variables section)

## Deployment Options

### Option 1: Using Render Blueprint (Recommended)

1. **Connect your GitHub repository** to Render
2. **Create a new Blueprint** from your repository
3. **Select the `render.yaml` file** in the root directory
4. **Review and deploy** - Render will create all services automatically

### Option 2: Manual Service Creation

#### 1. Create PostgreSQL Database

1. Go to Render Dashboard → New → PostgreSQL
2. Name: `synthralos-db`
3. Plan: Starter (or higher for production)
4. Database: `synthralos`
5. User: `synthralos_user`
6. Click "Create Database"
7. **Save the connection details** - you'll need them for the backend

#### 2. Create Backend Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `synthralos-backend`
   - **Environment**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Build Command**: (leave empty, Docker handles it)
   - **Start Command**: `fastapi run --host 0.0.0.0 --port $PORT app/main.py`
   - **Health Check Path**: `/api/v1/health`

4. **Environment Variables**:
   ```bash
   ENVIRONMENT=production
   PROJECT_NAME=SynthralOS
   API_V1_STR=/api/v1
   SECRET_KEY=<generate a secure random string>
   ACCESS_TOKEN_EXPIRE_MINUTES=11520

   # Database (from PostgreSQL service)
   POSTGRES_SERVER=<from database service>
   POSTGRES_PORT=<from database service>
   POSTGRES_USER=<from database service>
   POSTGRES_PASSWORD=<from database service>
   POSTGRES_DB=<from database service>

   # Supabase (required)
   SUPABASE_URL=<your-supabase-url>
   SUPABASE_ANON_KEY=<your-supabase-anon-key>

   # Frontend URL (set after frontend is deployed)
   FRONTEND_HOST=https://synthralos-frontend.onrender.com
   BACKEND_CORS_ORIGINS=https://synthralos-frontend.onrender.com

   # Optional: Add other services as needed
   # REDIS_URL=<redis-url>
   # OPENAI_API_KEY=<your-key>
   # ANTHROPIC_API_KEY=<your-key>
   # etc.
   ```

5. Click "Create Web Service"

#### 3. Create Frontend Service

1. Go to Render Dashboard → New → Web Service
2. Connect your GitHub repository
3. Configure:
   - **Name**: `synthralos-frontend`
   - **Environment**: Docker
   - **Dockerfile Path**: `./frontend/Dockerfile`
   - **Docker Context**: `./frontend`
   - **Build Command**: (leave empty)
   - **Start Command**: `nginx -g 'daemon off;'`

4. **Environment Variables**:
   ```bash
   VITE_API_URL=https://synthralos-backend.onrender.com/api/v1
   ```

5. Click "Create Web Service"

#### 4. Update Backend CORS Settings

After the frontend is deployed, update the backend environment variables:
- `FRONTEND_HOST`: Set to your frontend URL
- `BACKEND_CORS_ORIGINS`: Set to your frontend URL

## Environment Variables Reference

### Required Variables

#### Backend
- `ENVIRONMENT`: `production`
- `PROJECT_NAME`: `SynthralOS`
- `POSTGRES_SERVER`: Database host (from Render PostgreSQL service)
- `POSTGRES_PORT`: Database port (from Render PostgreSQL service)
- `POSTGRES_USER`: Database user (from Render PostgreSQL service)
- `POSTGRES_PASSWORD`: Database password (from Render PostgreSQL service)
- `POSTGRES_DB`: Database name (from Render PostgreSQL service)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `SECRET_KEY`: Generate a secure random string (use `openssl rand -hex 32`)

#### Frontend
- `VITE_API_URL`: Backend API URL (e.g., `https://synthralos-backend.onrender.com/api/v1`)

### Optional Variables

#### Backend (add as needed)
- `REDIS_URL`: Redis connection string (if using Redis)
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `GOOGLE_API_KEY`: Google API key
- `COHERE_API_KEY`: Cohere API key
- `NANGO_SECRET_KEY`: Nango secret key
- `NANGO_PUBLIC_KEY`: Nango public key
- `CHROMA_SERVER_HOST`: ChromaDB host
- `CHROMA_SERVER_HTTP_PORT`: ChromaDB port
- `SENTRY_DSN`: Sentry DSN for error tracking
- `SIGNOZ_ENDPOINT`: Signoz endpoint for observability
- `POSTHOG_KEY`: PostHog key for analytics
- `LANGFUSE_KEY`: Langfuse key for LLM observability
- `WAZUH_URL`: Wazuh endpoint for security monitoring

## Database Migrations

The backend will automatically run migrations on startup using the `backend/render-start.sh` script. This script:
1. Runs Alembic migrations (`alembic upgrade head`)
2. Starts the backend server

If you need to run migrations manually:

1. Go to your backend service in Render
2. Open the Shell/Console
3. Run: `python -m alembic upgrade head`

## Health Checks

- **Backend**: `/api/v1/utils/health-check` (already implemented)
- **Frontend**: Root path `/`

## Custom Domain Setup

1. Go to your service settings
2. Click "Add Custom Domain"
3. Enter your domain name
4. Follow DNS configuration instructions
5. Update `FRONTEND_HOST` and `BACKEND_CORS_ORIGINS` accordingly

## Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify all required environment variables are set
- Ensure database is accessible
- Check that migrations completed successfully

### Frontend shows API errors
- Verify `VITE_API_URL` is set correctly
- Check backend CORS settings
- Ensure backend is running and accessible

### Database connection errors
- Verify database credentials in environment variables
- Check that database service is running
- Ensure network connectivity between services

## Post-Deployment Steps

1. **Run database migrations** (if not automatic)
2. **Create admin user** (use the script: `python backend/scripts/promote_user_to_admin.py`)
3. **Register connectors** (if needed: `python backend/scripts/register_connectors.py`)
4. **Test the application**:
   - Frontend loads correctly
   - User can sign up/login
   - API endpoints respond
   - Database operations work

## Scaling

- **Backend**: Upgrade plan or add more instances
- **Database**: Upgrade PostgreSQL plan for more storage/performance
- **Frontend**: Usually doesn't need scaling (static files)

## Monitoring

- Use Render's built-in logs and metrics
- Set up external monitoring (Sentry, PostHog, etc.) using environment variables
- Monitor database performance in Render dashboard

## Security Notes

- Never commit `.env` files or secrets
- Use Render's environment variable encryption
- Regularly rotate `SECRET_KEY` and API keys
- Enable HTTPS (automatic on Render)
- Review CORS settings regularly
