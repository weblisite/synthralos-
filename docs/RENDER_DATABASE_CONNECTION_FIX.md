# Render Database Connection Fix

**Issue:** Password authentication failed on Render deployment  
**Error:** `FATAL: password authentication failed for user "postgres"`  
**Date:** December 17, 2025  
**Update:** Now using Direct Connection with IPv4 compatibility

## Problem

The `SUPABASE_DB_URL` environment variable in Render contains a password with special characters (`[` and `]`) that need to be URL-encoded.

## Connection Type

**Direct Connection (IPv4 Compatible):**
- ✅ Uses dedicated IPv4 address
- ✅ Ideal for persistent connections
- ✅ Works reliably on Render with IPv4 add-on
- ✅ Format: `postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres`

## Solution

### Step 1: Password

The password is `synthralos-` (no brackets).

**Note:** The dash (`-`) doesn't require URL encoding, so the password can be used as-is in the connection string.

### Step 2: Update Render Environment Variable

1. Go to your Render Dashboard
2. Navigate to your `synthralos-backend` service
3. Go to **Environment** tab
4. Find the `SUPABASE_DB_URL` environment variable
5. Update it with the Direct Connection string:

```
postgresql://postgres:synthralos-@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

**Note:** This uses Direct Connection with IPv4 compatibility enabled.

### Step 3: Verify Connection String Format

**Correct Format (Direct Connection - IPv4 Compatible):**
```
postgresql://postgres:synthralos-@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

**Components:**
- **Username:** `postgres`
- **Password:** `synthralos-` (no brackets, no encoding needed)
- **Host:** `db.lorefpaifkembnzmlodm.supabase.co`
- **Port:** `5432` (Direct connection)
- **Database:** `postgres`
- **IPv4:** ✅ Compatible (dedicated IPv4 address)

### Step 4: Redeploy

After updating the environment variable:
1. Click **Save Changes**
2. Render will automatically redeploy the service
3. Check the logs to verify the database connection succeeds

## Alternative: Use Supabase Dashboard Connection String

You can copy directly from Supabase Dashboard:

1. Go to Supabase Dashboard → Settings → Database
2. Click **Connection string** → **Direct connection**
3. Ensure **IPv4 compatible** is enabled (green checkmark)
4. Copy the connection string
5. **Important:** Replace `[YOUR-PASSWORD]` with your actual password: `synthralos-`
6. Paste it into Render's `SUPABASE_DB_URL` environment variable

## Verification

After updating, check the Render logs. You should see:
- ✅ `Database migrations completed successfully`
- ✅ `Backend started successfully`
- ❌ No more `password authentication failed` errors

## Troubleshooting

### If connection still fails:

1. **Verify password is correct:**
   - Check Supabase Dashboard → Settings → Database → Database password
   - Ensure the password matches `[synthralos-]`

2. **Check connection string format:**
   - Ensure no extra spaces or quotes
   - Ensure password is URL-encoded
   - Ensure hostname is correct (`aws-1-us-west-1.pooler.supabase.com`)

3. **Try Transaction Pooler (port 6543):**
   ```
   postgresql://postgres.lorefpaifkembnzmlodm:%5Bsynthralos-%5D@aws-1-us-west-1.pooler.supabase.com:6543/postgres
   ```

4. **Check Render environment variable:**
   - Ensure `SUPABASE_DB_URL` is set (not empty)
   - Ensure it's not being overridden by another variable
   - Check for typos in the variable name

## Related Documentation

- `docs/RENDER_DEPLOYMENT.md` - Full deployment guide
- `docs/CONNECTION_STRING_UPDATE.md` - Connection string details
- `docs/RENDER_DATABASE_AUTH_FIX.md` - Previous authentication fixes

