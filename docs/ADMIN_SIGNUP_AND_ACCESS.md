# Admin Signup and Dashboard Access - Complete Guide

## How Users Sign Up

### Regular User Signup

**Users CANNOT sign up as admins directly.** All users sign up as regular users:

1. **Signup Process:**
   - Navigate to `/signup`
   - Fill in email, password, and full name
   - Submit form
   - User is created in Supabase Auth
   - User is created in local database with `is_superuser = False` (default)

2. **Signup Flow:**
   ```
   User → Supabase Signup → User Created → Database Sync → Regular User (is_superuser = False)
   ```

3. **Code:**
   ```typescript
   // frontend/src/routes/signup.tsx
   const { error } = await supabase.auth.signUp({
     email,
     password,
     options: {
       data: {
         full_name: fullName,
       },
     },
   })
   ```

   ```python
   # backend/app/api/deps.py - Auto-creates user in database
   if not user:
       new_user = User(
           email=user_email,
           hashed_password="",
           full_name=full_name,
           is_active=True,
           is_superuser=False,  # Default: NOT admin
       )
   ```

---

## How Admins Are Created/Promoted

### Method 1: Promote Existing User (Recommended)

**Using the promotion script:**

```bash
cd backend
source .venv/bin/activate
python scripts/promote_user_to_admin.py <email>
```

**Example:**
```bash
python scripts/promote_user_to_admin.py myweblisite@gmail.com
```

**What it does:**
- Finds user in database by email
- Sets `is_superuser = True`
- User can now access admin panel

**Output:**
```
✅ Successfully promoted user 'myweblisite@gmail.com' to superuser/admin
   User ID: 77cc3941-544c-4713-ab6a-477ec840cdbd
   Full Name: Antony Mungai
   Is Superuser: True
```

### Method 2: Create Admin User via Admin Panel

**Only existing admins can create new admin users:**

1. Login as admin
2. Navigate to `/admin` → Users tab
3. Click "Add User" button
4. Fill in form:
   - Email
   - Full Name
   - Password
   - **Check "Is superuser?" checkbox** ✅
   - Check "Is active?" checkbox ✅
5. Submit form

**Code:**
```typescript
// frontend/src/components/Admin/AddUser.tsx
const formSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
  is_superuser: z.boolean(),  // Admin checkbox
  is_active: z.boolean(),
})

// When submitted, creates user with is_superuser = true
```

**API Endpoint:**
```http
POST /api/v1/users/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "admin@synthralos.ai",
  "password": "securepassword",
  "full_name": "Admin User",
  "is_superuser": true,
  "is_active": true
}
```

### Method 3: Edit Existing User (Promote to Admin)

**Only existing admins can promote users:**

1. Login as admin
2. Navigate to `/admin` → Users tab
3. Find user in table
4. Click actions menu → "Edit"
5. Check "Is superuser?" checkbox
6. Save

**Code:**
```typescript
// frontend/src/components/Admin/EditUser.tsx
<FormField
  name="is_superuser"
  render={({ field }) => (
    <Checkbox
      checked={field.value}
      onCheckedChange={field.onChange}
    />
  )}
/>
```

**API Endpoint:**
```http
PATCH /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_superuser": true
}
```

### Method 4: Direct Database Update (Not Recommended)

**Only for development/testing:**

```sql
UPDATE "user"
SET is_superuser = true
WHERE email = 'admin@synthralos.ai';
```

---

## Admin Dashboard Access

### ✅ Admins Can Access BOTH Dashboards

**Admins have access to:**
1. ✅ **Regular User Dashboard** (`/`) - Same as regular users
2. ✅ **Admin Panel** (`/admin`) - Admin-only features

### How It Works

**Sidebar Navigation (`frontend/src/components/Sidebar/AppSidebar.tsx`):**

```typescript
const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Plug, title: "Connectors", path: "/connectors" },
  { icon: Bot, title: "Agents", path: "/agents" },
  // ... all regular user features
]

// Admins get ALL regular items PLUS Admin link
const items = currentUser?.is_superuser
  ? [...baseItems, { icon: Users, title: "Admin", path: "/admin" }]
  : baseItems
```

**Result:**
- **Regular Users:** See Dashboard, Connectors, Agents, RAG, OCR, etc. (no Admin link)
- **Admins:** See Dashboard, Connectors, Agents, RAG, OCR, etc. **PLUS** Admin link

### Admin Access Breakdown

| Feature | Regular User | Admin |
|---------|-------------|-------|
| **User Dashboard** (`/`) | ✅ Yes | ✅ Yes |
| **Connectors** (`/connectors`) | ✅ Yes | ✅ Yes |
| **Workflows** (`/workflows`) | ✅ Yes | ✅ Yes |
| **Agents** (`/agents`) | ✅ Yes | ✅ Yes |
| **RAG** (`/rag`) | ✅ Yes | ✅ Yes |
| **OCR** (`/ocr`) | ✅ Yes | ✅ Yes |
| **Scraping** (`/scraping`) | ✅ Yes | ✅ Yes |
| **Browser** (`/browser`) | ✅ Yes | ✅ Yes |
| **OSINT** (`/osint`) | ✅ Yes | ✅ Yes |
| **Code** (`/code`) | ✅ Yes | ✅ Yes |
| **Chat** (`/chat`) | ✅ Yes | ✅ Yes |
| **Admin Panel** (`/admin`) | ❌ No | ✅ Yes |

---

## Admin Panel Features

**Admins can access:**

1. **Admin Dashboard** (`/admin` → Dashboard tab)
   - Execution History
   - Retry Management
   - Cost Analytics

2. **User Management** (`/admin` → Users tab)
   - View all users
   - Create new users (with admin option)
   - Edit users (promote to admin)
   - Delete users
   - Activate/deactivate users

3. **Connector Management** (`/admin` → Connectors tab)
   - View all connectors (platform + custom)
   - Register platform connectors
   - Update connector status
   - Delete connectors
   - View connector statistics

---

## Security: Admin Panel Protection

**Admin panel is protected at multiple levels:**

### 1. Frontend Protection (`frontend/src/routes/_layout/admin.tsx`)

```typescript
function Admin() {
  const { user: currentUser } = useAuth()

  // Check if user is admin
  if (!currentUser?.is_superuser) {
    return (
      <div>
        <h2>Access Denied</h2>
        <p>You must be an admin to access this page.</p>
      </div>
    )
  }

  // Admin panel content
}
```

### 2. Backend Protection (`backend/app/api/routes/admin_connectors.py`)

```python
@router.post("/admin/connectors/register")
def register_platform_connector(
    current_user: User = Depends(get_current_active_superuser),  # Admin check
):
    # Only admins can reach here
```

### 3. Route Protection (`frontend/src/routes/_layout/admin.tsx`)

```typescript
export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  beforeLoad: async ({ context }) => {
    // Could add additional checks here
  },
})
```

---

## Summary

### How Users Sign Up
- ✅ **Regular users:** Sign up via `/signup` (no admin option)
- ❌ **Cannot sign up as admin directly**
- ✅ **All users start as regular users** (`is_superuser = False`)

### How Admins Are Created
1. ✅ **Promote existing user** (script: `promote_user_to_admin.py`)
2. ✅ **Create via admin panel** (existing admin creates new admin)
3. ✅ **Edit existing user** (existing admin promotes user)
4. ⚠️ **Direct database update** (development only)

### Admin Dashboard Access
- ✅ **Admins can access BOTH dashboards:**
  - Regular user dashboard (`/`) - All features
  - Admin panel (`/admin`) - Admin-only features
- ✅ **Regular users can ONLY access:**
  - Regular user dashboard (`/`) - All features
  - ❌ Admin panel is blocked

### Security
- ✅ Frontend checks `is_superuser` before showing admin panel
- ✅ Backend checks `is_superuser` for all admin endpoints
- ✅ Regular users see "Access Denied" if they try to access `/admin`

---

## Quick Reference

### Promote User to Admin
```bash
cd backend && source .venv/bin/activate
python scripts/promote_user_to_admin.py <email>
```

### Create Admin via Admin Panel
1. Login as admin
2. `/admin` → Users tab
3. Click "Add User"
4. Check "Is superuser?" ✅
5. Submit

### Check if User is Admin
```typescript
const { user } = useAuth()
if (user?.is_superuser) {
  // User is admin
}
```

### Admin Navigation
- **Regular Users:** Dashboard, Connectors, Agents, RAG, OCR, Scraping, Browser, OSINT, Code, Chat
- **Admins:** All of the above **PLUS** Admin link

---

**Key Point:** Admins are **superusers** - they have access to everything regular users have, **plus** admin-only features. They don't lose access to regular features when they become admins.
