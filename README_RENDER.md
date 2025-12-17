# Quick Start: Deploy SynthralOS on Render

This is a quick reference guide. For detailed instructions, see [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md).

## Prerequisites

- GitHub repository with your code
- Render account (free tier available)
- Supabase account (for authentication)

## One-Click Deploy (Blueprint)

1. **Push your code to GitHub**
2. **Go to Render Dashboard** → New → Blueprint
3. **Connect your repository**
4. **Select `render.yaml`** from the root directory
5. **Review configuration** and click "Apply"
6. **Set environment variables** in the Render dashboard:
   - `SUPABASE_URL` and `SUPABASE_ANON_KEY` (required)
   - `SECRET_KEY` (generate with: `openssl rand -hex 32`)
   - `FRONTEND_HOST` and `BACKEND_CORS_ORIGINS` (set after frontend deploys)
7. **Wait for deployment** (5-10 minutes)

## Manual Deploy (Step by Step)

### 1. Create PostgreSQL Database

- Name: `synthralos-db`
- Plan: Starter
- Save connection details

### 2. Create Backend Service

- **Source**: Connect GitHub repo
- **Environment**: Docker
- **Dockerfile**: `./backend/Dockerfile`
- **Docker Context**: `./backend`
- **Start Command**: `/app/render-start.sh`
- **Health Check**: `/api/v1/utils/health-check`

**Environment Variables**:
```bash
ENVIRONMENT=production
PROJECT_NAME=SynthralOS
POSTGRES_SERVER=<from database>
POSTGRES_PORT=<from database>
POSTGRES_USER=<from database>
POSTGRES_PASSWORD=<from database>
POSTGRES_DB=<from database>
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-key>
SECRET_KEY=<generate-random-string>
```

### 3. Create Frontend Service

- **Source**: Connect GitHub repo
- **Environment**: Docker
- **Dockerfile**: `./frontend/Dockerfile`
- **Docker Context**: `./frontend`
- **Start Command**: `nginx -g 'daemon off;'`

**Environment Variables**:
```bash
VITE_API_URL=https://synthralos-backend.onrender.com/api/v1
```

### 4. Update Backend CORS

After frontend deploys, update backend:
- `FRONTEND_HOST`: `https://synthralos-frontend.onrender.com`
- `BACKEND_CORS_ORIGINS`: `https://synthralos-frontend.onrender.com`

## Post-Deployment

1. **Create admin user**:
   ```bash
   # In Render backend shell
   python backend/scripts/promote_user_to_admin.py
   ```

2. **Test the application**:
   - Visit frontend URL
   - Sign up/login
   - Verify API endpoints work

## Troubleshooting

- **Backend won't start**: Check logs, verify database credentials
- **Frontend shows errors**: Verify `VITE_API_URL` is correct
- **Database errors**: Check PostgreSQL service is running

## Support

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for detailed documentation.

