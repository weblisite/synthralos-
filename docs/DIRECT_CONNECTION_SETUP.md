# Direct Connection Setup (IPv4 Compatible)

**Date:** December 17, 2025
**Connection Type:** Direct Connection with IPv4 compatibility
**Status:** ✅ Ready for Render deployment

## Overview

With the dedicated IPv4 address enabled, we can now use the **Direct Connection** instead of the pooler connection. This is ideal for persistent connections and works reliably on Render.

## Connection String Format

**Direct Connection (IPv4 Compatible):**
```
postgresql://postgres:synthralos-@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

**Key Differences from Pooler:**
- Username: `postgres` (not `postgres.lorefpaifkembnzmlodm`)
- Host: `db.lorefpaifkembnzmlodm.supabase.co` (not `aws-1-us-west-1.pooler.supabase.com`)
- Port: `5432` (same)
- IPv4: ✅ Compatible (dedicated IPv4 address)

## Render Environment Variable

**Update `SUPABASE_DB_URL` in Render:**

1. Go to Render Dashboard → `synthralos-backend` → Environment
2. Find `SUPABASE_DB_URL`
3. Set it to:
   ```
   postgresql://postgres:synthralos-@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
   ```
4. Save Changes

## Password

**Password:** `synthralos-`

**Note:** The dash (`-`) doesn't require URL encoding, so the password can be used as-is in the connection string.

## Benefits of Direct Connection

✅ **Persistent Connections:** Ideal for long-lived connections
✅ **IPv4 Compatible:** Works reliably on Render
✅ **Lower Latency:** Direct connection without pooler overhead
✅ **Simpler:** Standard PostgreSQL connection format

## Verification

After updating the connection string in Render:

1. **Check Deployment Logs:**
   - Look for: `Database migrations completed successfully`
   - Look for: `Backend started successfully`
   - No `password authentication failed` errors

2. **Test Connection:**
   - Backend should connect successfully
   - Database migrations should run
   - API endpoints should respond

## Troubleshooting

### If connection still fails:

1. **Verify IPv4 Compatibility:**
   - Check Supabase Dashboard → Settings → Database
   - Ensure "IPv4 compatible" shows green checkmark
   - If not enabled, enable IPv4 add-on

2. **Verify Password:**
   - Ensure password is `synthralos-` in Supabase
   - Password doesn't need URL encoding (dash is safe)

3. **Check Connection String Format:**
   - Username should be `postgres` (not `postgres.lorefpaifkembnzmlodm`)
   - Host should be `db.lorefpaifkembnzmlodm.supabase.co`
   - Port should be `5432`
   - No extra spaces or quotes

## Comparison: Direct vs Pooler

| Feature | Direct Connection | Pooler Connection |
|---------|------------------|-------------------|
| Username | `postgres` | `postgres.lorefpaifkembnzmlodm` |
| Host | `db.lorefpaifkembnzmlodm.supabase.co` | `aws-1-us-west-1.pooler.supabase.com` |
| Port | `5432` | `5432` (Session) or `6543` (Transaction) |
| IPv4 | ✅ Required | ✅ Recommended |
| Use Case | Persistent connections | Serverless/short-lived |
| Render | ✅ Works with IPv4 | ✅ Works |

## Current Configuration

**Connection String:**
```
postgresql://postgres:synthralos-@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```

**Status:** ✅ Ready for Render deployment
**IPv4:** ✅ Enabled
**Type:** Direct Connection
