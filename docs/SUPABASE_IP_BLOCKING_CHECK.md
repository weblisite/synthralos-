# Checking if Supabase is Blocking Render IP Addresses

## Problem

If you're seeing connection errors like:
```
connection to server at "54.241.103.102", port 5432 failed: server closed the connection unexpectedly
```

This could indicate that Supabase is blocking connections from Render's IP addresses.

## How to Check

### Step 1: Check Supabase Dashboard Settings

1. Go to **Supabase Dashboard** → Your Project → **Settings** → **Database**
2. Look for these sections:

#### A. IPv4 Settings
- Click **"IPv4 settings"** button
- Verify IPv4 add-on is enabled
- Check if there are any IP restrictions listed

#### B. Connection Pooling
- Scroll to **"Connection Pooling"** section
- Check if there are any IP allowlists or restrictions
- Look for "Allowed IPs" or "IP Restrictions" settings

#### C. Network Access
- Look for **"Network Access"** or **"Firewall"** section
- Check if there's an IP allowlist enabled
- If enabled, Render's IP addresses need to be added

### Step 2: Check Connection Logs

1. Go to **Supabase Dashboard** → **Logs** → **Postgres Logs**
2. Look for connection attempts from Render
3. Check for error messages like:
   - "Connection refused"
   - "IP not allowed"
   - "Too many connections from IP"

### Step 3: Test Connection from Different IP

Try connecting from your local machine with the same connection string:
- If it works locally but not from Render → IP blocking is likely
- If it fails both places → Different issue (credentials, network, etc.)

## Solutions

### Solution 1: Use Session Pooler (Recommended)

The Session Pooler handles IP restrictions automatically:

1. In Supabase Dashboard → **Settings** → **Database** → **Connection string**
2. Change **Method** from "Direct connection" to **"Connection pooling"**
3. Select **"Session"** mode (port 5432, IPv4 proxied)
4. Copy the connection string:
   ```
   postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-1-us-west-1.pooler.supabase.com:5432/postgres
   ```
5. Update `SUPABASE_DB_URL` in Render with this connection string

**Why this works:**
- Pooler uses Supabase's infrastructure IPs (not Render's)
- Automatically handles IPv4 proxying
- Designed to work from any IP address
- Better connection management

### Solution 2: Disable IP Restrictions (If Available)

1. Go to **Settings** → **Database** → **Network Access**
2. If there's an IP allowlist, either:
   - Disable it temporarily to test
   - Add Render's IP ranges (if you can find them)

**Note:** Render's IP ranges change frequently, so this is not a reliable long-term solution.

### Solution 3: Contact Supabase Support

If you can't find IP restriction settings:
1. Contact Supabase support
2. Ask them to check if your project has IP restrictions enabled
3. Request that Render's IP ranges be whitelisted (if possible)

## Why Direct Connections Fail from Render

Even with IPv4 proxying enabled, direct connections can fail because:

1. **DNS Resolution**: Hostname resolves to IP `54.241.103.102`
2. **Network Routing**: Render's network may route through blocked IP ranges
3. **Connection Limits**: Too many connection attempts trigger blocks
4. **Firewall Rules**: Supabase may have firewall rules blocking certain IP ranges

## Recommended Solution

**Use the Session Pooler** - It's specifically designed to solve these issues:

- ✅ Works from any IP address
- ✅ Handles IPv4 proxying automatically
- ✅ Better connection management
- ✅ Designed for cloud deployments like Render
- ✅ Still uses port 5432 (same as direct connection)

## Connection String Comparison

**Direct Connection (Current - Failing):**
```
postgresql://postgres:synthralosautomation@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
```
- Username: `postgres`
- Host: `db.lorefpaifkembnzmlodm.supabase.co`
- Port: `5432`
- ❌ May be blocked by IP restrictions

**Session Pooler (Recommended - Should Work):**
```
postgresql://postgres.lorefpaifkembnzmlodm:synthralosautomation@aws-1-us-west-1.pooler.supabase.com:5432/postgres
```
- Username: `postgres.lorefpaifkembnzmlodm` (includes project ref)
- Host: `aws-1-us-west-1.pooler.supabase.com` (pooler endpoint)
- Port: `5432` (same port)
- ✅ Handles IP restrictions automatically

## Next Steps

1. **Try Session Pooler first** (easiest solution)
2. If that doesn't work, check Supabase Dashboard for IP restrictions
3. Contact Supabase support if needed

The Session Pooler is the recommended approach for Render deployments and should resolve the IP blocking issue.
