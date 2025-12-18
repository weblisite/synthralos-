# Render Environment Variable Setup - Step by Step

**Issue:** Database connection failing on Render  
**Solution:** Update `SUPABASE_DB_URL` with URL-encoded password

## Step-by-Step Instructions

### Step 1: Get the Correct Connection String

**Copy this EXACT string** (password is already URL-encoded):

```
postgresql://postgres.lorefpaifkembnzmlodm:%5Bsynthralos-%5D@aws-1-us-west-1.pooler.supabase.com:5432/postgres
```

**Key points:**
- Password `[synthralos-]` is encoded as `%5Bsynthralos-%5D`
- Host: `aws-1-us-west-1.pooler.supabase.com`
- Port: `5432` (Session pooler)

### Step 2: Update Render Environment Variable

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Sign in to your account

2. **Select Your Backend Service**
   - Click on `synthralos-backend` service

3. **Open Environment Tab**
   - Click on **Environment** in the left sidebar
   - Or scroll down to the **Environment Variables** section

4. **Find SUPABASE_DB_URL**
   - Look for the `SUPABASE_DB_URL` variable
   - Click **Edit** or the pencil icon next to it

5. **Paste the Connection String**
   - **Delete** the old value completely
   - **Paste** this exact string:
     ```
     postgresql://postgres.lorefpaifkembnzmlodm:%5Bsynthralos-%5D@aws-1-us-west-1.pooler.supabase.com:5432/postgres
     ```
   - **Important:** 
     - Do NOT add quotes around it
     - Do NOT add spaces before or after
     - Copy the ENTIRE string including `postgresql://` at the start

6. **Save Changes**
   - Click **Save Changes** button
   - Render will automatically redeploy your service

### Step 3: Verify Deployment

1. **Check Deployment Logs**
   - Go to **Logs** tab in Render
   - Wait for the deployment to complete
   - Look for these success messages:
     - ✅ `Database migrations completed successfully`
     - ✅ `Backend started successfully`
     - ✅ No `password authentication failed` errors

2. **If Still Failing**

   **Check 1: Verify Password**
   - Go to Supabase Dashboard → Settings → Database
   - Check if the database password is actually `[synthralos-]`
   - If different, update the connection string with the correct password (URL-encoded)

   **Check 2: Verify Connection String Format**
   - Ensure no extra characters or spaces
   - Ensure password is URL-encoded (`%5B` and `%5D` for brackets)
   - Ensure hostname is correct (`aws-1-us-west-1.pooler.supabase.com`)

   **Check 3: Try Alternative Port**
   - If port 5432 doesn't work, try port 6543 (Transaction pooler):
     ```
     postgresql://postgres.lorefpaifkembnzmlodm:%5Bsynthralos-%5D@aws-1-us-west-1.pooler.supabase.com:6543/postgres
     ```

## Alternative: Copy from Supabase Dashboard

If you prefer to copy directly from Supabase:

1. **Go to Supabase Dashboard**
   - Navigate to your project
   - Go to **Settings** → **Database**

2. **Get Connection String**
   - Scroll to **Connection string** section
   - Select **Session pooler** (port 5432) or **Transaction pooler** (port 6543)
   - Click **Copy** button

3. **Verify Password Encoding**
   - The copied string should have URL-encoded password
   - If it shows `[synthralos-]` (with brackets), you need to manually encode it:
     - Replace `[` with `%5B`
     - Replace `]` with `%5D`

4. **Paste into Render**
   - Follow Step 2 above to update the environment variable

## Troubleshooting

### Error: "password authentication failed"

**Possible causes:**
1. Password not URL-encoded
2. Wrong password
3. Connection string format incorrect

**Solution:**
- Double-check the password is `[synthralos-]` in Supabase
- Ensure it's URL-encoded as `%5Bsynthralos-%5D` in the connection string
- Verify no extra spaces or characters

### Error: "connection to server failed"

**Possible causes:**
1. Wrong hostname
2. Wrong port
3. Network/firewall issue

**Solution:**
- Verify hostname: `aws-1-us-west-1.pooler.supabase.com`
- Try both ports: `5432` (Session) and `6543` (Transaction)
- Check Supabase dashboard for correct connection string

### Connection String Not Updating

**Solution:**
- Make sure you clicked **Save Changes** after editing
- Wait for automatic redeployment to complete
- Check if there are multiple `SUPABASE_DB_URL` variables (delete duplicates)
- Verify you're editing the correct service (`synthralos-backend`)

## Quick Reference

**Correct Connection String:**
```
postgresql://postgres.lorefpaifkembnzmlodm:%5Bsynthralos-%5D@aws-1-us-west-1.pooler.supabase.com:5432/postgres
```

**Password Encoding:**
- Original: `[synthralos-]`
- Encoded: `%5Bsynthralos-%5D`

**Where to Update:**
- Render Dashboard → `synthralos-backend` → Environment → `SUPABASE_DB_URL`

