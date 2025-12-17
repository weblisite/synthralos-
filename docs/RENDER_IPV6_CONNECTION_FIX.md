# Fixing IPv6 Connection Issues on Render

## Problem

When deploying to Render, you may encounter this error:

```
sqlalchemy.exc.OperationalError: (psycopg.OperationalError) connection is bad: 
connection to server at "2600:1f1c:f9:4d08:5ce0:1deb:c0df:c81c", port 5432 failed: 
Network is unreachable
```

This happens because:
- Supabase direct connections (port 5432) may resolve to IPv6 addresses
- Render's network cannot reach IPv6 addresses
- The connection pooler (port 6543) avoids this issue

## Solution: Use Connection Pooler

**You MUST use the Supabase connection pooler (port 6543) for Render deployments.**

### Step 1: Get Pooler Connection String

1. Go to your Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Navigate to **Settings** → **Database**
4. Scroll down to **Connection string**
5. **Select "Connection pooling"** (NOT "Direct connection")
6. Copy the connection string

**Pooler Format:**
```
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Direct Format (DO NOT USE ON RENDER):**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
```

### Step 2: Update Render Environment Variable

1. Go to Render Dashboard → Your Backend Service → Environment
2. Find `SUPABASE_DB_URL`
3. Replace it with the **pooler connection string** (port 6543)
4. Save and redeploy

### Step 3: Verify

After redeploying, check the logs. You should see:
- ✅ Successful database connection
- ✅ Migrations running successfully
- ✅ No IPv6 addresses in connection attempts

## Why Pooler?

- ✅ **IPv4 only** - Avoids IPv6 resolution issues
- ✅ **Optimized for serverless** - Better connection handling
- ✅ **More reliable** - Designed for serverless environments like Render
- ✅ **Same performance** - No noticeable difference for most use cases

## Alternative: Force IPv4 (Not Recommended)

If you must use direct connection, you can try adding `?options=-c%20ipv4_only=1` to the connection string, but the pooler is strongly recommended.

## Still Having Issues?

1. **Verify connection string format**: Must use `postgresql://postgres.[PROJECT_REF]:...` format for pooler
2. **Check Supabase region**: Ensure your Supabase project is in a supported region
3. **Check Render region**: Ensure Render service is in a compatible region
4. **Verify password**: Ensure database password is correct (no special characters need URL encoding)

## Quick Checklist

- [ ] Using connection pooler string (port 6543)
- [ ] Connection string format: `postgresql://postgres.[PROJECT_REF]:...`
- [ ] Hostname contains `pooler.supabase.com`
- [ ] Port is `6543` (not `5432`)
- [ ] Password is correctly URL-encoded if it contains special characters

