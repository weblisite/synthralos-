# Admin Authentication with Supabase Auth - Explained

## Current Implementation

### How It Works Now

**Both admin and regular users use the same Supabase Auth mechanism:**

1. **Authentication Flow:**
   ```
   User → Supabase Auth → JWT Token → Backend Verification → Database Lookup → Role Check
   ```

2. **Process:**
   - User authenticates via Supabase Auth (same for admin and regular users)
   - Supabase returns a JWT access token
   - Backend verifies token using Supabase client
   - Backend extracts email from token
   - Backend looks up user in local PostgreSQL database by email
   - Backend checks `is_superuser` field in database
   - Admin endpoints use `get_current_active_superuser()` which checks `is_superuser`

3. **Key Points:**
   - ✅ Same authentication mechanism for all users
   - ✅ Admin status stored in local database (`is_superuser` field)
   - ✅ Role check happens after token verification
   - ⚠️ Requires database lookup for every request

### Current Code Flow

**Backend (`backend/app/api/deps.py`):**
```python
def get_current_user(session: SessionDep, credentials: TokenDep) -> User:
    # 1. Verify Supabase token
    supabase = get_supabase_client()
    user_response = supabase.auth.get_user(token)
    
    # 2. Extract email from token
    user_email = user_response.user.email
    
    # 3. Look up user in database
    user = session.exec(select(User).where(User.email == user_email)).first()
    
    # 4. Return user (includes is_superuser field)
    return user

def get_current_active_superuser(current_user: CurrentUser) -> User:
    # 5. Check is_superuser field from database
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough privileges")
    return current_user
```

**Frontend (`frontend/src/hooks/useAuth.ts`):**
```typescript
// All users authenticate the same way
const { data } = await supabase.auth.signInWithPassword({
  email,
  password,
})

// User data fetched from backend API (includes is_superuser)
const { data: user } = useQuery({
  queryFn: async () => await UsersService.readUserMe()
})
```

---

## Is This Correct?

**Yes, this approach works, but it's not the Supabase-recommended best practice.**

### ✅ What's Good:
- Same auth mechanism for all users (simpler)
- Role-based access control (RBAC) implemented
- Secure (admin check happens server-side)
- Works correctly

### ⚠️ What Could Be Better:
- Requires database lookup for every request
- Admin status not in Supabase (not synced with Supabase Auth)
- Can't use Supabase RLS policies based on roles
- Two sources of truth (Supabase Auth + local database)

---

## Supabase Best Practice: Using `app_metadata`

### Recommended Approach

**Store admin roles in Supabase's `app_metadata` instead of (or in addition to) local database:**

1. **Benefits:**
   - ✅ Role included in JWT token (no database lookup needed)
   - ✅ Single source of truth (Supabase Auth)
   - ✅ Can use Supabase RLS policies
   - ✅ More efficient (check token directly)
   - ✅ Works with Supabase Admin API

2. **How It Works:**
   ```
   User → Supabase Auth → JWT Token (with app_metadata.role) → Backend Verification → Role Check from Token
   ```

3. **Implementation:**

**Setting Admin Role in Supabase:**
```javascript
// Using Supabase Admin API (server-side only)
const { data, error } = await supabase.auth.admin.updateUserById(
  userId,
  {
    app_metadata: {
      role: 'admin'  // or 'superuser', 'user', etc.
    }
  }
)
```

**Reading Role from Token:**
```python
# In backend/app/api/deps.py
def get_current_user(session: SessionDep, credentials: TokenDep) -> User:
    token = credentials.credentials
    
    # Decode JWT to get app_metadata
    payload = jwt.decode(token, options={"verify_signature": False})
    app_metadata = payload.get("app_metadata", {})
    user_role = app_metadata.get("role", "user")
    
    # Check if admin directly from token
    is_admin = user_role in ["admin", "superuser"]
    
    # Still sync with database for other user data
    user = session.exec(select(User).where(User.email == user_email)).first()
    
    # Update database if role changed
    if user and user.is_superuser != is_admin:
        user.is_superuser = is_admin
        session.add(user)
        session.commit()
    
    return user
```

---

## Hybrid Approach (Recommended)

**Best of both worlds - use Supabase `app_metadata` as source of truth, sync with database:**

### Architecture:
```
Supabase Auth (app_metadata.role) → JWT Token → Backend → Sync with Database → Use Database for RBAC
```

### Benefits:
- ✅ Single source of truth (Supabase `app_metadata`)
- ✅ Role in JWT token (efficient)
- ✅ Database sync for complex queries
- ✅ Can use Supabase RLS policies
- ✅ Backward compatible with existing code

### Implementation:

**1. Update user role in Supabase:**
```python
# backend/scripts/promote_user_to_admin.py (updated)
from supabase import create_client

def promote_user_to_admin_supabase(email: str) -> None:
    """Promote user to admin in Supabase app_metadata."""
    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY  # Admin key
    )
    
    # Get user by email
    users = supabase.auth.admin.list_users()
    user = next((u for u in users if u.email == email), None)
    
    if not user:
        print(f"User {email} not found in Supabase")
        return
    
    # Update app_metadata
    supabase.auth.admin.update_user_by_id(
        user.id,
        {
            "app_metadata": {
                "role": "admin",
                "is_superuser": True
            }
        }
    )
    
    # Also update local database
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.email == email)).first()
        if db_user:
            db_user.is_superuser = True
            session.add(db_user)
            session.commit()
```

**2. Check role from token:**
```python
# backend/app/api/deps.py (updated)
def get_current_user(session: SessionDep, credentials: TokenDep) -> User:
    token = credentials.credentials
    
    # Verify token with Supabase
    supabase = get_supabase_client()
    user_response = supabase.auth.get_user(token)
    
    # Extract role from app_metadata (in token)
    app_metadata = user_response.user.app_metadata or {}
    user_role = app_metadata.get("role", "user")
    is_superuser = app_metadata.get("is_superuser", False) or user_role in ["admin", "superuser"]
    
    # Get or create user in database
    user_email = user_response.user.email
    user = session.exec(select(User).where(User.email == user_email)).first()
    
    if not user:
        # Create user
        user = User(
            email=user_email,
            hashed_password="",
            full_name=user_response.user.user_metadata.get("full_name"),
            is_active=True,
            is_superuser=is_superuser,  # Sync from Supabase
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        # Sync is_superuser from Supabase
        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            session.add(user)
            session.commit()
            session.refresh(user)
    
    return user
```

---

## Comparison: Current vs. Best Practice

| Aspect | Current (Database) | Best Practice (app_metadata) |
|--------|-------------------|----------------------------|
| **Auth Mechanism** | Same for all users ✅ | Same for all users ✅ |
| **Role Storage** | Local database | Supabase `app_metadata` |
| **Role in Token** | ❌ No | ✅ Yes |
| **Database Lookup** | Required every request | Optional (for sync) |
| **Performance** | Slower (DB query) | Faster (token check) |
| **Supabase RLS** | ❌ Can't use | ✅ Can use |
| **Single Source** | ❌ Two sources | ✅ One source |
| **Complexity** | Simple | More complex |

---

## Recommendation

### Option 1: Keep Current Implementation (Simpler)
**If you're happy with current performance:**
- ✅ Works correctly
- ✅ Simple to maintain
- ✅ No changes needed
- ⚠️ Requires database lookup per request

### Option 2: Migrate to Supabase `app_metadata` (Better)
**If you want Supabase best practices:**
- ✅ More efficient (role in token)
- ✅ Can use Supabase RLS
- ✅ Single source of truth
- ⚠️ Requires migration
- ⚠️ More complex setup

### Option 3: Hybrid Approach (Recommended)
**Best of both worlds:**
- ✅ Use `app_metadata` as source of truth
- ✅ Sync with database for complex queries
- ✅ Backward compatible
- ✅ Can gradually migrate

---

## Answer to Your Question

**Q: What sort of auth is the admin using so as to differentiate the user auth and the admin auth as it needs to be different?**

**A: Currently, admin and regular users use the same Supabase Auth mechanism. The differentiation happens via the `is_superuser` field in your local database, not in the authentication itself.**

**This is actually correct!** In Supabase Auth (and most modern auth systems), you don't use different authentication mechanisms for admins vs. users. Instead:

1. **Same Authentication:** All users authenticate the same way (Supabase Auth)
2. **Role-Based Access:** Admin status is determined by roles/permissions (stored in database or `app_metadata`)
3. **Authorization Check:** Backend checks role after authentication

**The current implementation is correct, but could be improved by:**
- Using Supabase's `app_metadata` to store roles in the JWT token
- Reducing database lookups by checking role from token
- Enabling Supabase RLS policies for database-level security

---

## Next Steps (Optional)

If you want to improve the implementation:

1. **Add `app_metadata` support:**
   - Update `promote_user_to_admin.py` to set Supabase `app_metadata`
   - Update `get_current_user()` to read role from token
   - Sync with database for backward compatibility

2. **Use Supabase Admin API:**
   - Requires `SUPABASE_SERVICE_ROLE_KEY` (server-side only)
   - Can manage users and roles directly in Supabase

3. **Enable Supabase RLS:**
   - Create RLS policies based on `app_metadata.role`
   - Database-level security for sensitive data

Would you like me to implement the improved version using Supabase `app_metadata`?

