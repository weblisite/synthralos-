# How to Make a User an Admin - Quick Guide

## Important: Users Cannot Sign Up as Admins

**All users sign up as regular users** (`is_superuser = False`). There is no way to sign up directly as an admin because:
- Same authentication mechanism for everyone (Supabase Auth)
- Admin status is determined by the `is_superuser` field in the database
- This is a security best practice - admins must be explicitly promoted

---

## Method 1: Using the Promotion Script (Recommended for First Admin)

**Use this method to create your first admin user.**

### Step 1: Sign up as a regular user
1. Go to `/signup`
2. Create an account with your email and password
3. You'll be a regular user by default

### Step 2: Promote yourself to admin
```bash
cd backend
source .venv/bin/activate
python scripts/promote_user_to_admin.py <your-email>
```

**Example:**
```bash
python scripts/promote_user_to_admin.py myweblisite@gmail.com
```

**Output:**
```
✅ Successfully promoted user 'myweblisite@gmail.com' to superuser/admin
   User ID: 77cc3941-544c-4713-ab6a-477ec840cdbd
   Full Name: Antony Mungai
   Is Superuser: True
```

### Step 3: Log out and log back in
- The admin status is stored in the database
- You need to refresh your session to see the Admin link in the sidebar
- Log out and log back in to activate admin access

---

## Method 2: Using the Admin Panel (Requires Existing Admin)

**Only works if you already have an admin user.**

### Option A: Promote Existing User

1. **Login as admin**
   - Go to `/admin` → Users tab
   - You'll see all users in a table

2. **Find the user to promote**
   - Look for the user in the table
   - Click the actions menu (three dots) next to their name

3. **Click "Edit User"**
   - A dialog will open
   - Check the **"Is superuser?"** checkbox ✅
   - Optionally check **"Is active?"** if not already active
   - Click "Save"

4. **User is now admin**
   - They need to log out and log back in to see admin access

### Option B: Create New Admin User

1. **Login as admin**
   - Go to `/admin` → Users tab
   - Click **"Add User"** button

2. **Fill in the form**
   - Email: `newadmin@synthralos.ai`
   - Full Name: `New Admin`
   - Password: `securepassword123`
   - Confirm Password: `securepassword123`
   - **Check "Is superuser?"** ✅
   - **Check "Is active?"** ✅

3. **Click "Save"**
   - User is created as admin immediately
   - They can log in with the credentials you provided

---

## Method 3: Direct Database Update (Development Only)

**⚠️ Only use this in development/testing environments.**

```sql
-- Connect to your PostgreSQL database
-- Update the user's is_superuser field
UPDATE "user"
SET is_superuser = true
WHERE email = 'admin@synthralos.ai';
```

**Then:**
- User must log out and log back in
- Admin access will be available

---

## Quick Reference

### Check if User is Admin

**In Database:**
```sql
SELECT email, is_superuser FROM "user" WHERE email = 'user@synthralos.ai';
```

**In Frontend:**
```typescript
const { user } = useAuth()
if (user?.is_superuser) {
  // User is admin
}
```

**In Backend:**
```python
if current_user.is_superuser:
    # User is admin
```

### Admin Access Features

Once a user is admin, they can:
- ✅ Access `/admin` panel
- ✅ See "Admin" link in sidebar
- ✅ Manage users (create, edit, delete, promote)
- ✅ Manage connectors (register platform connectors, update status)
- ✅ View execution history
- ✅ Manage retries
- ✅ View cost analytics

---

## Troubleshooting

### "I promoted myself but don't see Admin link"

**Solution:**
1. Log out completely
2. Log back in
3. The Admin link should appear in the sidebar

### "I can't access /admin even though I'm admin"

**Solution:**
1. Check database: `SELECT is_superuser FROM "user" WHERE email = 'your@email.com';`
2. If `is_superuser = false`, promote again
3. Log out and log back in
4. Clear browser cache if needed

### "I don't have any admin users yet"

**Solution:**
- Use Method 1 (promotion script) to create your first admin
- This is the only way to bootstrap admin access

---

## Security Notes

1. **Never expose admin endpoints** without authentication
2. **Always verify `is_superuser`** on both frontend and backend
3. **Limit admin creation** - only promote trusted users
4. **Audit admin actions** - consider logging admin operations
5. **Use strong passwords** for admin accounts

---

## Summary

**To make someone an admin:**

1. **First admin:** Use promotion script
   ```bash
   python scripts/promote_user_to_admin.py <email>
   ```

2. **Subsequent admins:** Use admin panel
   - Login as admin → `/admin` → Users tab
   - Edit user → Check "Is superuser?" → Save

3. **Always:** User must log out and log back in to activate admin access

**Remember:** Users sign up as regular users. Admins are explicitly promoted, not created during signup.
