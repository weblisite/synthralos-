# Worker Environment Variables Setup

## Problem

The worker service is failing with:
```
ValueError: Database configuration required. Set either SUPABASE_DB_URL, or SUPABASE_URL + SUPABASE_DB_PASSWORD, or legacy POSTGRES_* variables.
```

## Solution

The worker service needs the same environment variables as the backend service. You need to manually set them in the Render dashboard.

## Required Environment Variables

Go to **Render Dashboard** → **synthralos-workflow-worker** → **Environment** tab and add:

### Database Configuration (REQUIRED)

1. **`SUPABASE_DB_URL`** (Required)
   - Get from: Supabase Dashboard → Settings → Database → Connection string
   - Use "Connection pooling" option (port 6543)
   - Format: `postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`

   OR (Alternative):

2. **`SUPABASE_URL`** + **`SUPABASE_DB_PASSWORD`**
   - `SUPABASE_URL`: `https://[PROJECT_REF].supabase.co`
   - `SUPABASE_DB_PASSWORD`: Database password from Supabase Dashboard

### Authentication (REQUIRED)

3. **`SUPABASE_ANON_KEY`** (Required)
   - Get from: Supabase Dashboard → Settings → API → Project API keys → anon/public key

4. **`SECRET_KEY`** (Required)
   - Generate a secure random string (same as backend)
   - Or copy from backend service environment variables

### Application Configuration

5. **`ENVIRONMENT`** = `production` (Already set in blueprint)

6. **`PROJECT_NAME`** = `SynthralOS` (Already set in blueprint)

### Optional Worker-Specific Settings

7. **`WORKFLOW_WORKER_CONCURRENCY`** = `10` (Optional, defaults to 10)
   - Number of concurrent workflow executions the worker can handle

8. **`WORKFLOW_NODE_TIMEOUT_SECONDS`** = `300` (Optional, defaults to 300)
   - Default timeout for individual nodes (5 minutes)

### Other Backend Environment Variables (Copy from Backend Service)

Copy these from your **backend service** environment variables:

- `NANGO_SECRET_KEY` (if using connectors)
- `NANGO_BASE_URL` (if using connectors)
- `CHROMA_SERVER_HOST` (if using RAG)
- `CHROMA_SERVER_HTTP_PORT` (if using RAG)
- `CHROMA_SERVER_AUTH_TOKEN` (if using ChromaDB Cloud)
- `TWITTER_BEARER_TOKEN` (if using Social Monitoring)
- `LANGFUSE_KEY` (if using Langfuse)
- `POSTHOG_KEY` (if using PostHog)
- Any other environment variables your backend uses

## Quick Setup Steps

1. **Open Render Dashboard**: https://dashboard.render.com
2. **Navigate to**: Your Blueprint → `synthralos-workflow-worker` service
3. **Go to**: Environment tab
4. **Add Required Variables**:
   - Click "Add Environment Variable"
   - Add each variable listed above
   - Use the same values as your backend service
5. **Save**: Click "Save Changes"
6. **Restart**: The service will automatically restart

## Copying from Backend Service

**Easiest way**: Copy all environment variables from your backend service:

1. Go to **backend service** → **Environment** tab
2. Note down all environment variables (especially database ones)
3. Go to **worker service** → **Environment** tab
4. Add the same variables

## Verification

After setting environment variables, check the logs:

1. Go to **worker service** → **Logs** tab
2. Look for: `🚀 Workflow worker started (poll_interval=1.0s)`
3. If you see errors, check that all required variables are set correctly

## Common Issues

### Issue: Still getting database error
**Solution**: Make sure `SUPABASE_DB_URL` is set correctly. It should be the full connection string including password.

### Issue: Worker starts but doesn't process workflows
**Solution**: Check that `SUPABASE_DB_URL` uses the **pooler** port (6543), not the direct port (5432).

### Issue: Connection timeout
**Solution**: Ensure you're using the Supabase connection pooler URL (port 6543), not the direct connection.

## Environment Variable Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SUPABASE_DB_URL` | ✅ Yes | Full database connection string | `postgresql://postgres.xxx:password@aws-0-us-east-1.pooler.supabase.com:6543/postgres` |
| `SUPABASE_URL` | ✅ Yes* | Supabase project URL | `https://xxx.supabase.co` |
| `SUPABASE_ANON_KEY` | ✅ Yes | Supabase anonymous key | `eyJhbGc...` |
| `SECRET_KEY` | ✅ Yes | Application secret key | `your-secret-key` |
| `ENVIRONMENT` | ✅ Yes | Environment name | `production` |
| `WORKFLOW_WORKER_CONCURRENCY` | ❌ No | Concurrent executions | `10` |
| `WORKFLOW_NODE_TIMEOUT_SECONDS` | ❌ No | Node timeout | `300` |

*Required if not using `SUPABASE_DB_URL`

## Need Help?

If you're still having issues:
1. Check Render logs for specific error messages
2. Verify environment variables are set (no typos)
3. Ensure database connection string is correct
4. Make sure worker service has access to the same database as backend
