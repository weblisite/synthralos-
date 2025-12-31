# Clerk ↔ Supabase Database Sync Architecture

## Overview

This document explains how Clerk (authentication provider) communicates with and syncs user data to your Supabase PostgreSQL database and storage.

## Architecture Flow

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Clerk     │────────▶│   Backend    │────────▶│  Supabase   │
│  (Auth)     │ Webhook │  (FastAPI)   │   SQL   │  Database   │
└─────────────┘         └──────────────┘         └─────────────┘
     │                        │                         │
     │                        │                         │
     │                        ▼                         │
     │                  ┌──────────────┐                │
     │                  │   Supabase   │                │
     │                  │   Storage    │                │
     │                  │  (Avatars)   │                │
     │                  └──────────────┘                │
     │                                                   │
     └───────────────────────────────────────────────────┘
              User authenticates → Token → Backend
```

## How It Works

### 1. **User Authentication Flow**

When a user signs up or logs in via Clerk:

1. **Clerk handles authentication** (email/password, social logins, MFA, etc.)
2. **Clerk issues JWT token** to the frontend
3. **Frontend sends token** to backend API in `Authorization: Bearer <token>` header
4. **Backend verifies token** using Clerk's JWKS endpoint
5. **Backend checks database** for user by email
6. **If user doesn't exist**, backend creates user record in Supabase database (lazy creation)
7. **If user exists**, backend returns user data from database

**Code Location**: `backend/app/api/deps.py` → `get_current_user()`

### 2. **Webhook-Based Sync (Primary Method)**

Clerk sends webhook events to your backend when user data changes:

#### Webhook Endpoint
- **URL**: `https://your-backend.com/api/v1/webhooks/clerk`
- **Method**: POST
- **Authentication**: Svix signature verification

#### Events Handled

**`user.created`**
- Triggered when a new user signs up in Clerk
- Backend creates corresponding user record in Supabase database
- Sets: `email`, `full_name`, `is_active=True`
- Password field is empty (Clerk handles auth)

**`user.updated`**
- Triggered when user updates profile in Clerk
- Backend updates user record in database
- Syncs: `full_name`, `avatar_url` (from Clerk's image_url)
- Updates `UserPreferences.avatar_url` if changed

**`user.deleted`**
- Triggered when user deletes account in Clerk
- Backend sets `is_active=False` in database (soft delete)
- Preserves user data for audit purposes

**Code Location**: `backend/app/api/routes/clerk_webhooks.py`

### 3. **Lazy User Creation (Fallback)**

If webhook fails or user authenticates before webhook arrives:

- When `get_current_user()` is called and user doesn't exist in database
- Backend automatically creates user record using Clerk token data
- This ensures users can access the app even if webhook delivery is delayed

**Code Location**: `backend/app/api/deps.py` → lines 88-114

### 4. **Avatar/Image Storage**

**Current Implementation:**
- Clerk stores user avatars in Clerk's CDN
- Avatar URL is synced to `UserPreferences.avatar_url` in database
- Frontend displays avatar from Clerk's CDN URL

**Future Enhancement (Optional):**
- Download avatar from Clerk and upload to Supabase Storage
- Store in Supabase Storage bucket: `avatars`
- Update `UserPreferences.avatar_url` to point to Supabase Storage URL

## Database Schema

### User Table (Supabase PostgreSQL)
```sql
CREATE TABLE "user" (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) DEFAULT '',  -- Empty for Clerk users
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### UserPreferences Table
```sql
CREATE TABLE "user_preferences" (
    id UUID PRIMARY KEY,
    user_id UUID UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,
    avatar_url VARCHAR(500),  -- Clerk CDN URL or Supabase Storage URL
    theme VARCHAR(50),
    timezone VARCHAR(100),
    language VARCHAR(10),
    -- ... other preferences
);
```

## Configuration

### Environment Variables

**Backend** (`backend/.env`):
```bash
# Clerk Configuration
CLERK_SECRET_KEY=sk_test_...
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_WEBHOOK_SECRET=ep_...  # For webhook signature verification
CLERK_JWKS_URL=https://your-clerk-instance.clerk.accounts.dev/.well-known/jwks.json

# Supabase Database (PostgreSQL)
SUPABASE_DB_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Supabase Storage (if using for avatars)
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=eyJ...
```

**Frontend** (`frontend/.env`):
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

### Clerk Dashboard Setup

1. **Create Webhook Endpoint**:
   - Go to Clerk Dashboard → Webhooks
   - Add endpoint: `https://your-backend.com/api/v1/webhooks/clerk`
   - Select events: `user.created`, `user.updated`, `user.deleted`
   - Copy webhook secret to `CLERK_WEBHOOK_SECRET`

2. **Configure Allowed Origins**:
   - Add your frontend URL to Clerk's allowed origins
   - Example: `https://app.synthralos.ai`

## Data Flow Examples

### Example 1: New User Signup

1. User signs up via Clerk UI (`/signup`)
2. Clerk creates user account
3. Clerk sends `user.created` webhook to backend
4. Backend webhook handler:
   ```python
   - Extracts email, first_name, last_name from webhook payload
   - Creates User record in Supabase database
   - Sets is_active=True, hashed_password=""
   ```
5. User logs in → Clerk issues token
6. Frontend sends token to backend API
7. Backend verifies token, finds user in database, returns user data

### Example 2: User Updates Profile Picture

1. User uploads avatar in Clerk UserProfile component
2. Clerk stores image in Clerk CDN
3. Clerk sends `user.updated` webhook with `image_url`
4. Backend webhook handler:
   ```python
   - Finds user by email
   - Updates UserPreferences.avatar_url = image_url
   - Commits to database
   ```
5. Frontend displays new avatar from Clerk CDN URL

### Example 3: User Deletes Account

1. User deletes account in Clerk UserProfile component
2. Clerk sends `user.deleted` webhook
3. Backend webhook handler:
   ```python
   - Finds user by email
   - Sets is_active=False (soft delete)
   - Preserves user data for audit
   ```

## Error Handling

### Webhook Failures
- If webhook delivery fails, user creation falls back to lazy creation on first API call
- Webhook retries are handled by Clerk/Svix
- Backend logs all webhook events for debugging

### Database Connection Issues
- If Supabase database is unavailable, webhook handler logs error and returns 500
- Clerk will retry webhook delivery
- User can still authenticate (lazy creation will retry on next API call)

### Token Verification Failures
- Invalid tokens return 403 Forbidden
- Expired tokens return 403 with "Token expired" message
- JWKS endpoint failures are logged and cached

## Monitoring

### Logs to Monitor

1. **Webhook Events**:
   ```python
   logger.info(f"Received Clerk webhook event: {event_type}")
   logger.info(f"Created user from Clerk webhook: {email}")
   ```

2. **User Creation**:
   ```python
   logger.info(f"Created new user in database: {email}")
   logger.warning(f"Error creating user, retrying: {error}")
   ```

3. **Token Verification**:
   ```python
   logger.info(f"Verified Clerk token for user: {email}")
   logger.error(f"Error verifying Clerk token: {error}")
   ```

## Troubleshooting

### Users Not Appearing in Database

1. **Check webhook configuration**:
   - Verify webhook URL is correct in Clerk Dashboard
   - Check webhook secret matches `CLERK_WEBHOOK_SECRET`
   - Verify webhook events are enabled

2. **Check webhook logs**:
   - Look for webhook events in backend logs
   - Check for signature verification errors

3. **Check lazy creation**:
   - User should be created on first API call if webhook failed
   - Check `get_current_user()` logs

### Avatar Not Syncing

1. **Check webhook payload**:
   - Verify `image_url` is present in `user.updated` event
   - Check `UserPreferences` table for `avatar_url` value

2. **Check frontend**:
   - Verify Clerk UserProfile component is saving avatar
   - Check browser console for errors

### Database Connection Issues

1. **Check Supabase connection**:
   - Verify `SUPABASE_DB_URL` is correct
   - Test database connectivity
   - Check for circuit breaker errors

2. **Check connection pool**:
   - Monitor connection pool usage
   - Check for connection timeout errors

## Future Enhancements

1. **Avatar Migration to Supabase Storage**:
   - Download avatar from Clerk CDN
   - Upload to Supabase Storage bucket
   - Update `avatar_url` to Supabase Storage URL

2. **Bi-directional Sync**:
   - Sync custom fields from database to Clerk metadata
   - Update Clerk user metadata when preferences change

3. **Real-time Sync**:
   - Use Supabase Realtime to notify frontend of user updates
   - Update UI immediately when webhook processes

4. **User Migration Tool**:
   - Script to migrate existing Supabase Auth users to Clerk
   - Preserve user data and relationships
