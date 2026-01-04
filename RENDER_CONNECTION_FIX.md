# Fix Render Database Connection Issue

## Problem

The deployment is failing with:
```
psycopg.OperationalError: connection failed: connection to server at "54.241.103.102", port 5432 failed: server closed the connection unexpectedly
```

**Root Cause:** The `SUPABASE_DB_URL` environment variable in Render is set to use an IP address instead of a hostname. Supabase blocks IP-based connections from Render.

## Solution: Update SUPABASE_DB_URL in Render

### Step 1: Get the Correct Connection String

Based on your Supabase project (`lorefpaifkembnzmlodm`), use one of these:

#### Option A: Session Pooler (RECOMMENDED - Best for Render)
```
postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-1-us-west-1.pooler.supabase.com:5432/postgres
```

**Why this works:**
- Uses Supabase's pooler infrastructure (bypasses IP restrictions)
- Designed for cloud deployments like Render
- Handles IPv4 proxying automatically
- Better connection management

#### Option B: Direct Connection (Hostname)
```
postgresql://postgres:synthralosautomation@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

**Note:** This may still fail if Supabase has IP restrictions enabled.

### Step 2: Update Render Environment Variable

1. Go to **Render Dashboard** → Your Backend Service → **Environment**
2. Find the `SUPABASE_DB_URL` variable
3. **Replace** the current value (which contains IP `54.241.103.102`) with:

**For Session Pooler (Recommended):**
```
postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-1-us-west-1.pooler.supabase.com:5432/postgres
```

**For Direct Connection:**
```
postgresql://postgres:synthralosautomation@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

4. Click **Save Changes**
5. Render will automatically redeploy

### Step 3: Verify Connection String Format

The connection string should:
- ✅ Use hostname (not IP address)
- ✅ Include username, password, host, port, and database
- ✅ Use `postgresql://` protocol
- ✅ Have password URL-encoded if it contains special characters

**Current (WRONG - Contains IP):**
```
postgresql://postgres:synthralosautomation@54.241.103.102:5432/postgres
```

**Correct (Session Pooler):**
```
postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-1-us-west-1.pooler.supabase.com:5432/postgres
```

**Correct (Direct - Hostname):**
```
postgresql://postgres:synthralosautomation@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

## How to Get Your Exact Connection String from Supabase

1. Go to **Supabase Dashboard** → Your Project → **Settings** → **Database**
2. Scroll to **"Connection string"** section
3. Select **"Connection pooling"** tab
4. Choose **"Session"** mode
5. Copy the connection string (it will look like the Session Pooler format above)
6. Replace `[YOUR-PASSWORD]` with your actual password: `synthralosautomation`

## Why This Happens

1. **DNS Resolution**: Sometimes hostnames resolve to IPs, and the connection string gets set with the IP
2. **IP Restrictions**: Supabase may block connections from Render's IP ranges
3. **Connection Limits**: Too many connection attempts from the same IP can trigger blocks

## Why Session Pooler Works

- ✅ Routes through Supabase's infrastructure (not Render's IP)
- ✅ Automatically handles IPv4 proxying
- ✅ Designed for cloud deployments
- ✅ Better connection pooling and management
- ✅ Works from any IP address

## After Updating

1. Render will automatically redeploy
2. The migration should succeed
3. The application should start normally

## If It Still Fails

1. **Check Supabase Dashboard** → **Settings** → **Database** → **IPv4 settings**
   - Ensure IPv4 add-on is enabled
   - Check for IP restrictions

2. **Check Supabase Logs** → **Postgres Logs**
   - Look for connection attempts
   - Check for error messages

3. **Try Transaction Pooler** (port 6543):
   ```
   postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-0-us-west-1.pooler.supabase.com:6543/postgres
   ```

4. **Contact Supabase Support** if issues persist

## Quick Fix Command

If you have Render CLI access, you can update it directly:

```bash
render env:set SUPABASE_DB_URL "postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-1-us-west-1.pooler.supabase.com:5432/postgres"
```

---

**IMPORTANT:** Make sure to use the Session Pooler connection string format shown above. This is the recommended solution for Render deployments.
