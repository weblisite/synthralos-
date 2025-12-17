# Fixing Database Authentication Error on Render

## Error

```
sqlalchemy.exc.OperationalError: (psycopg.OperationalError) connection failed: 
connection to server at "3.101.5.153", port 5432 failed: 
FATAL: password authentication failed for user "postgres"
```

## Root Cause

The `SUPABASE_DB_URL` environment variable in Render is either:
1. **Not set** - Missing environment variable
2. **Wrong format** - Using incorrect connection string format
3. **Wrong password** - Database password is incorrect
4. **Using direct connection** - Port 5432 instead of pooler (port 6543)

## Solution: Fix SUPABASE_DB_URL in Render

### Step 1: Get Correct Connection String from Supabase

1. Go to **Supabase Dashboard**: https://supabase.com/dashboard
2. Select your project
3. Navigate to **Settings** → **Database**
4. Scroll to **Connection string** section
5. **Select "Connection pooling"** (NOT "Direct connection")
6. Copy the connection string

**Correct Format (Pooler - Recommended for Render):**
```
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Example:**
```
postgresql://postgres.eflnoopwsvrysthajkke:your-password-here@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### Step 2: Update Render Environment Variable

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Select your **Backend Service** (`synthralos-backend`)
3. Click on **Environment** tab
4. Find `SUPABASE_DB_URL` variable
5. **Replace** the value with the pooler connection string from Step 1
6. **Important**: 
   - Ensure the password is correctly URL-encoded if it contains special characters
   - Ensure port is `6543` (pooler), not `5432` (direct)
   - Ensure hostname contains `pooler.supabase.com`
7. Click **Save Changes**

### Step 3: Verify Connection String Format

Your `SUPABASE_DB_URL` should look like this:

```
postgresql://postgres.eflnoopwsvrysthajkke:your-password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**Key Points:**
- ✅ Starts with `postgresql://`
- ✅ Username format: `postgres.[PROJECT_REF]` (with project reference)
- ✅ Hostname: `aws-0-[REGION].pooler.supabase.com` (contains "pooler")
- ✅ Port: `6543` (pooler port)
- ✅ Database: `postgres`

### Step 4: Redeploy

1. After saving the environment variable, Render will automatically redeploy
2. Or manually trigger: **Manual Deploy** → **Deploy latest commit**
3. Check the logs to verify successful connection

### Step 5: Verify Success

After redeploy, check logs. You should see:
- ✅ `Running database migrations...`
- ✅ `Database migrations completed successfully`
- ✅ No authentication errors
- ✅ Backend service starts successfully

## Common Issues

### Issue 1: Password Contains Special Characters

If your database password contains special characters (`@`, `#`, `%`, etc.), you need to URL-encode them:

- `@` → `%40`
- `#` → `%23`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`
- `?` → `%3F`

**Example:**
If password is `my@pass#123`, use `my%40pass%23123` in the connection string.

### Issue 2: Using Direct Connection Instead of Pooler

**Wrong (Direct - Port 5432):**
```
postgresql://postgres:password@db.eflnoopwsvrysthajkke.supabase.co:5432/postgres
```

**Correct (Pooler - Port 6543):**
```
postgresql://postgres.eflnoopwsvrysthajkke:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### Issue 3: Missing Project Reference in Username

**Wrong:**
```
postgresql://postgres:password@...
```

**Correct:**
```
postgresql://postgres.[PROJECT_REF]:password@...
```

### Issue 4: Wrong Hostname

**Wrong (Direct connection hostname):**
```
db.[PROJECT_REF].supabase.co
```

**Correct (Pooler hostname):**
```
aws-0-[REGION].pooler.supabase.com
```

## Quick Checklist

- [ ] Using connection pooler string (port 6543)
- [ ] Connection string format: `postgresql://postgres.[PROJECT_REF]:...`
- [ ] Hostname contains `pooler.supabase.com`
- [ ] Port is `6543` (not `5432`)
- [ ] Password is correctly URL-encoded if it contains special characters
- [ ] Project reference is correct in username
- [ ] Region matches your Supabase project region

## Still Having Issues?

1. **Double-check password**: Go to Supabase Dashboard → Settings → Database → Reset database password if needed
2. **Verify project reference**: Check your Supabase project URL - the project ref is the subdomain
3. **Check region**: Ensure the region in the connection string matches your Supabase project region
4. **Test connection locally**: Try the connection string locally first to verify it works
5. **Check Render logs**: Look for more detailed error messages in Render deployment logs

