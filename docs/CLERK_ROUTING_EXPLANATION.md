# Clerk Routing & Authentication Flow Explanation

## The Problem: 404 Error on `/login/factor-one`

### What Happened
When users logged in, Clerk tried to navigate to `/login/factor-one` for Multi-Factor Authentication (MFA), but TanStack Router didn't have a route handler for this path, resulting in a 404 error.

### Root Cause
Clerk was configured with `routing="path"` mode, which means Clerk controls URL paths during authentication flows:
- `/login` - Initial login page
- `/login/factor-one` - MFA verification step
- `/login/sso-callback` - SSO callback handling
- etc.

However, TanStack Router uses file-based routing and only had a route for `/login`, not for `/login/*` (catch-all sub-routes).

---

## The Solution: Virtual Routing

### What is "Virtual" Routing?
**Virtual routing** means Clerk handles authentication flows internally without changing the browser URL. All authentication steps (login, MFA, password reset, etc.) happen on the same URL (`/login`), but Clerk manages the UI state internally.

### Key Differences

| Routing Mode | URL Changes | Route Handling |
|--------------|-------------|----------------|
| **`path`** | Yes - Clerk changes URLs (`/login` → `/login/factor-one`) | Requires catch-all routes in your router |
| **`virtual`** | No - URL stays the same (`/login`) | No special routing needed |

---

## Authentication Flow After Fix

### Complete User Journey

1. **User visits protected page** (e.g., `/workflows`)
   - `_layout.tsx` checks authentication
   - If not authenticated, redirects to `/login?redirect=/workflows`

2. **User lands on `/login`**
   - Clerk's `<SignIn>` component renders
   - User enters credentials
   - If MFA is enabled, Clerk shows MFA step **on the same page** (virtual routing)
   - URL remains `/login` throughout the process

3. **After successful authentication**
   - Clerk reads `afterSignInUrl` prop (defaults to `/` or uses `redirect` query param)
   - Clerk redirects user to the target URL
   - User lands on dashboard (`/`) or their intended destination

4. **User is now authenticated**
   - `_layout.tsx` detects `isSignedIn === true`
   - Protected routes render normally
   - User can access all authenticated features

---

## Code Changes Made

### 1. `frontend/src/routes/login.tsx`

**Before:**
```tsx
<SignIn
  routing="path"           // ❌ Causes URL changes
  path="/login"
  afterSignInUrl="/"       // Hardcoded redirect
/>
```

**After:**
```tsx
// Added search param validation
export const Route = createFileRoute("/login")({
  component: LoginPage,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      redirect: (search.redirect as string) || undefined,
    }
  },
})

function LoginPage() {
  const { redirect } = Route.useSearch()
  const afterSignInUrl = redirect || "/"  // ✅ Uses redirect param or defaults to "/"

  return (
    <SignIn
      routing="virtual"     // ✅ No URL changes during auth flow
      afterSignInUrl={afterSignInUrl}  // ✅ Dynamic redirect
    />
  )
}
```

**Key Improvements:**
- ✅ Changed to `routing="virtual"` - no URL conflicts
- ✅ Reads `redirect` query parameter from URL
- ✅ Redirects to intended destination after login
- ✅ Falls back to `/` (dashboard) if no redirect param

### 2. `frontend/src/routes/signup.tsx`

**Changed:**
```tsx
<SignUp
  routing="virtual"  // ✅ Consistent with login
  afterSignUpUrl="/" // ✅ Redirects to dashboard after signup
/>
```

---

## Redirect Flow Examples

### Example 1: Direct Login
1. User visits `/login`
2. User logs in successfully
3. Redirected to `/` (dashboard) ✅

### Example 2: Protected Page Access
1. User visits `/workflows` (not authenticated)
2. `_layout.tsx` redirects to `/login?redirect=/workflows`
3. User logs in successfully
4. Redirected to `/workflows` ✅

### Example 3: Team Invitation
1. User clicks invitation link: `/teams/invitations/accept?token=abc123`
2. Not authenticated, redirected to `/login?redirect=/teams/invitations/accept?token=abc123`
3. User logs in successfully
4. Redirected back to invitation acceptance page ✅

---

## Why Users ARE Redirected to Dashboard

### The `afterSignInUrl` Prop
```tsx
afterSignInUrl={afterSignInUrl}  // "/" or the redirect param value
```

This prop tells Clerk: **"After successful authentication, redirect the user to this URL"**

### Default Behavior
- If no `redirect` query param: `afterSignInUrl = "/"` → **Dashboard**
- If `redirect` param exists: `afterSignInUrl = redirect` → **Intended destination**

### Verification
You can verify this works by:
1. Opening browser DevTools → Network tab
2. Logging in
3. Watching for a redirect to `/` (or your redirect URL)
4. The dashboard should load immediately

---

## Technical Details

### How Virtual Routing Works Internally

1. **Clerk manages UI state** - Shows/hides different components based on auth step
2. **No URL changes** - Browser URL stays at `/login`
3. **History API** - Clerk uses browser history internally for navigation
4. **After completion** - Clerk performs a full page redirect to `afterSignInUrl`

### Why This is Better

✅ **No routing conflicts** - Works with any router (TanStack, React Router, Next.js)
✅ **Simpler setup** - No need for catch-all routes
✅ **Better UX** - Smooth transitions without URL flickering
✅ **Easier debugging** - Single URL to monitor during auth flow

---

## Troubleshooting

### If users still see 404 errors:
1. Check that `routing="virtual"` is set (not `"path"`)
2. Verify `afterSignInUrl` is set correctly
3. Check browser console for Clerk errors
4. Ensure Clerk publishable key is configured

### If redirects don't work:
1. Check `redirect` query parameter is being read correctly
2. Verify `afterSignInUrl` prop is dynamic (not hardcoded)
3. Check browser network tab for redirect response
4. Verify `_layout.tsx` isn't blocking the redirect

---

## Summary

**The Fix:**
- Changed Clerk routing from `"path"` to `"virtual"`
- Added redirect parameter handling
- Users are redirected to dashboard (`/`) after login ✅

**The Flow:**
1. User logs in → Clerk handles auth internally (virtual routing)
2. After success → Clerk redirects to `afterSignInUrl` (`/` or redirect param)
3. User lands on dashboard → Protected routes render ✅

**Result:**
- ✅ No more 404 errors
- ✅ Users redirected to dashboard after login
- ✅ Supports redirect parameters for better UX
- ✅ Works seamlessly with TanStack Router
