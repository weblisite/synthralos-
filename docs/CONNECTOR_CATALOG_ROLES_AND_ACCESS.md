# Connector Catalog: Roles, Access, and Functionality

## Current State Analysis

### ✅ What's Currently Implemented
- Connector catalog is accessible to **all authenticated users** at `/connectors`
- Users can view connectors, register new connectors, authorize connectors, and test connectors
- No role-based access control (RBAC) is implemented yet
- API has TODO comment: "only superusers or connector developers can register" but currently allows all users

### ❌ What's Missing
- Role-based access control (User vs Admin)
- Separate admin interface for connector management
- User-specific connector authorization status
- Custom connector registration (user-created connectors)

---

## Access Model: Users vs Admins

### **Regular Users** (SaaS Platform Users)

**What They Should See:**
- ✅ **Connector Catalog** - Browse available platform connectors
- ✅ **Connector Details** - View connector information, actions, triggers
- ✅ **OAuth Authorization** - Authorize connectors to connect their accounts
- ✅ **Test Connectors** - Test connector actions before using in workflows
- ✅ **Custom Connector Registration** - Register their own custom connectors (SaaS feature)

**What They Should NOT See:**
- ❌ Platform connector registration (admin-only)
- ❌ Connector version management (admin-only)
- ❌ Enable/disable platform connectors (admin-only)
- ❌ View connector usage across all users (admin-only)

**User-Specific Features:**
- **My Authorizations** - View which connectors they've authorized
- **My Custom Connectors** - View connectors they've created
- **Authorization Status** - See which connectors are authorized for their account
- **Disconnect** - Revoke their own authorizations

---

### **Platform Admins** (SynthralOS Team)

**What They Should See:**
- ✅ **Admin Connector Management Panel** - Separate admin interface
- ✅ **Platform Connector Registration** - Register connectors available to all users
- ✅ **Connector Version Management** - Manage connector versions
- ✅ **Enable/Disable Connectors** - Control which connectors are available
- ✅ **Connector Usage Analytics** - See how connectors are used across all users
- ✅ **Connector Health Monitoring** - Monitor connector health and API status
- ✅ **Bulk Operations** - Bulk enable/disable/update connectors

**Admin-Only Features:**
- **Platform Connector Registry** - Manage the 99+ platform connectors
- **Connector Approval** - Approve user-submitted custom connectors (if applicable)
- **Connector Deprecation** - Deprecate old connector versions
- **System-Wide Statistics** - Analytics across all users

---

## Connector Registration: Two Types

### 1. **Platform Connector Registration** (Admin-Only)

**Who:** Platform admins (SynthralOS team)  
**Purpose:** Register connectors that become available to ALL users  
**Location:** Admin Panel (`/admin/connectors`)

**Process:**
1. Admin navigates to Admin Panel → Connector Management
2. Admin clicks "Register Platform Connector"
3. Admin provides:
   - Connector manifest (JSON)
   - Wheel file URL (optional)
   - Category assignment
   - Status (draft → beta → stable)
4. Connector becomes available to all users
5. Users can then authorize and use it

**API Endpoint:**
```python
POST /api/v1/admin/connectors/register
# Requires: is_superuser = True
```

**UI Location:**
- Admin Panel: `/admin/connectors`
- Separate from user connector catalog

---

### 2. **Custom Connector Registration** (User Feature)

**Who:** Regular users (SaaS platform users)  
**Purpose:** Users create their own custom connectors for private use  
**Location:** User Connector Catalog (`/connectors`)

**Process:**
1. User navigates to Connector Catalog (`/connectors`)
2. User clicks "Register Custom Connector"
3. User provides:
   - Connector manifest (JSON)
   - Wheel file URL (optional)
   - Connector name, slug, description
4. Connector is created as **user-owned**
5. Only the user who created it can see and use it
6. Optionally: User can submit for platform approval (future feature)

**API Endpoint:**
```python
POST /api/v1/connectors/register
# Requires: authenticated user
# Creates: user-scoped connector
```

**UI Location:**
- User Connector Catalog: `/connectors`
- "Register Custom Connector" button (already exists)

**Database Model:**
```python
class Connector:
    id: UUID
    slug: str
    name: str
    status: str
    owner_id: UUID | None  # NULL = platform connector, UUID = user-owned
    is_platform: bool  # True = available to all, False = user-specific
    created_by: UUID  # User who created it
```

---

## Revised Feature List by Role

### **User Connector Catalog** (`/connectors`)

#### Phase 1: Core User Features (Current + Missing)

1. ✅ **View Platform Connectors** - Browse 99+ platform connectors
2. ✅ **Category Filtering** - Filter by category (Communication, CRM, etc.)
3. ✅ **Search Connectors** - Search by name, description
4. ✅ **View Connector Details** - See actions, triggers, documentation
5. ✅ **Authorization Status** - See which connectors are authorized
6. ✅ **OAuth Authorization** - Authorize connectors (connect accounts)
7. ✅ **Disconnect/Revoke** - Revoke their own authorizations
8. ✅ **Test Connector Actions** - Test before using in workflows
9. ✅ **Register Custom Connector** - Create user-owned connectors
10. ✅ **View My Custom Connectors** - See connectors they created
11. ✅ **Refresh Tokens** - Manually refresh OAuth tokens
12. ✅ **Rotate Credentials** - Rotate their own credentials

#### Phase 2: Enhanced User Features

13. **My Authorizations Tab** - View all authorized connectors
14. **Authorization History** - See when connectors were authorized
15. **Token Expiration Warnings** - Alerts for expiring tokens
16. **Connector Usage** - See where they're using connectors (their workflows)
17. **Quick Actions** - Quick authorize/test/disconnect from table

---

### **Admin Connector Management Panel** (`/admin/connectors`)

#### Phase 1: Core Admin Features

1. ✅ **Platform Connector Registry** - Manage platform connectors
2. ✅ **Register Platform Connector** - Add connectors for all users
3. ✅ **Connector Version Management** - Manage versions, deprecate old ones
4. ✅ **Enable/Disable Connectors** - Control availability
5. ✅ **Connector Status Management** - Set status (draft → beta → stable → deprecated)
6. ✅ **Bulk Operations** - Bulk enable/disable/update
7. ✅ **Connector Usage Analytics** - See usage across all users
8. ✅ **Connector Health Monitoring** - Monitor API status, errors
9. ✅ **User-Submitted Connectors** - Review and approve user connectors (future)

#### Phase 2: Advanced Admin Features

10. **Connector Approval Workflow** - Approve/reject user submissions
11. **Connector Deprecation** - Deprecate connectors with migration path
12. **System-Wide Statistics** - Analytics dashboard
13. **Connector Logs** - View connector execution logs
14. **Rate Limiting Management** - Configure rate limits per connector
15. **Webhook Management** - Manage webhook subscriptions

---

## Implementation Plan

### Step 1: Add Role-Based Access Control

**Backend Changes:**
```python
# backend/app/api/routes/connectors.py

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_connector(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    manifest: dict[str, Any],
    wheel_url: str | None = None,
    is_platform: bool = False,  # New parameter
) -> Any:
    """
    Register a connector.
    
    - If is_platform=True: Requires superuser (platform connector)
    - If is_platform=False: Creates user-owned connector
    """
    if is_platform and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can register platform connectors")
    
    # Register connector with owner_id
    connector = registry.register_connector(
        session=session,
        manifest=manifest,
        wheel_url=wheel_url,
        owner_id=None if is_platform else current_user.id,
        is_platform=is_platform,
    )
    return connector

@router.get("/list")
def list_connectors(
    session: SessionDep,
    current_user: CurrentUser,
    include_custom: bool = True,  # Include user's custom connectors
) -> Any:
    """
    List connectors available to user.
    
    Returns:
    - All platform connectors (is_platform=True)
    - User's custom connectors (if include_custom=True)
    """
    # Get platform connectors
    platform_connectors = registry.list_connectors(
        session=session,
        is_platform=True,
    )
    
    # Get user's custom connectors
    custom_connectors = []
    if include_custom:
        custom_connectors = registry.list_connectors(
            session=session,
            owner_id=current_user.id,
        )
    
    return {
        "platform": platform_connectors,
        "custom": custom_connectors,
    }
```

**Frontend Changes:**
```typescript
// frontend/src/components/Connectors/ConnectorCatalog.tsx

// Add tabs for Platform vs Custom connectors
<Tabs>
  <TabsList>
    <TabsTrigger value="platform">Platform Connectors</TabsTrigger>
    <TabsTrigger value="custom">My Custom Connectors</TabsTrigger>
  </TabsList>
  
  <TabsContent value="platform">
    {/* Show platform connectors */}
  </TabsContent>
  
  <TabsContent value="custom">
    {/* Show user's custom connectors */}
    <Button onClick={() => setShowWizard(true)}>
      Register Custom Connector
    </Button>
  </TabsContent>
</Tabs>
```

---

### Step 2: Create Admin Connector Management Panel

**New Route:**
```typescript
// frontend/src/routes/_layout/admin/connectors.tsx
export const Route = createFileRoute("/_layout/admin/connectors")({
  component: AdminConnectorManagement,
  beforeLoad: ({ context }) => {
    // Check if user is admin
    if (!context.user?.is_superuser) {
      throw redirect({ to: "/" })
    }
  },
})
```

**Admin Components:**
- `AdminConnectorRegistry.tsx` - Platform connector management
- `PlatformConnectorWizard.tsx` - Register platform connectors
- `ConnectorVersionManager.tsx` - Version management
- `ConnectorAnalytics.tsx` - Usage analytics

---

### Step 3: Add Authorization Status Check

**Backend API:**
```python
@router.get("/{slug}/auth-status")
def get_connector_auth_status(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Check if connector is authorized for current user.
    """
    oauth_service = default_oauth_service
    tokens = oauth_service.get_tokens(
        session=session,
        connector_slug=slug,
        user_id=current_user.id,
    )
    
    return {
        "authorized": tokens is not None,
        "expires_at": tokens.get("expires_at") if tokens else None,
        "token_type": tokens.get("token_type") if tokens else None,
    }
```

**Frontend:**
```typescript
// Show authorization status badge in table
{connector.auth_status === "authorized" && (
  <Badge variant="success">✅ Authorized</Badge>
)}
{connector.auth_status === "not_authorized" && (
  <Badge variant="secondary">❌ Not Authorized</Badge>
)}
```

---

## Summary: What Users Should See

### ✅ **User Connector Catalog** (`/connectors`)

**Primary Purpose:** Browse, authorize, and use connectors

**Features:**
1. **Browse Platform Connectors** - View 99+ available connectors
2. **Filter & Search** - Find connectors by category, name
3. **Authorization Management** - Authorize/disconnect connectors
4. **Test Connectors** - Test actions before using
5. **Custom Connectors** - Register and manage their own connectors
6. **Usage Tracking** - See where they're using connectors

**User Flow:**
```
1. User opens Connector Catalog
2. Browses platform connectors
3. Clicks "Authorize" on Gmail connector
4. Completes OAuth flow
5. Connector shows "✅ Authorized"
6. User can now use Gmail in workflows/agents
7. User can register custom connector if needed
```

---

### ✅ **Admin Connector Management** (`/admin/connectors`)

**Primary Purpose:** Manage platform connectors for all users

**Features:**
1. **Platform Registry** - Manage 99+ platform connectors
2. **Register Platform Connectors** - Add new connectors for all users
3. **Version Management** - Manage versions, deprecate old ones
4. **Enable/Disable** - Control connector availability
5. **Analytics** - See usage across all users
6. **Health Monitoring** - Monitor connector health

**Admin Flow:**
```
1. Admin opens Admin Panel → Connectors
2. Clicks "Register Platform Connector"
3. Provides manifest and wheel URL
4. Sets status to "beta"
5. Connector becomes available to all users
6. Users can now authorize and use it
```

---

## Answers to Your Questions

### 1. **Should users see the connector catalog?**

**YES** ✅ - Users MUST see the connector catalog because:
- They need to browse available connectors
- They need to authorize connectors (connect their accounts)
- They need to test connectors before using
- They may want to register custom connectors

**Current Implementation:** ✅ Correct - Catalog is accessible to users

---

### 2. **Are my suggested fixes optimized for users?**

**PARTIALLY** ⚠️ - Some features are user-focused, some are admin-only:

**User-Optimized Features:**
- ✅ Category filtering - Users need this
- ✅ Authorization status - Users need this
- ✅ Disconnect - Users need this
- ✅ Refresh tokens - Users need this
- ✅ Rotate credentials - Users need this

**Admin-Only Features:**
- ❌ Enable/disable connectors - Admin only
- ❌ Version management - Admin only
- ❌ System-wide analytics - Admin only

**Revised Recommendation:**
- **User Catalog:** Focus on browsing, authorizing, testing, custom connectors
- **Admin Panel:** Focus on platform connector management, analytics, versioning

---

### 3. **How do admins register platform connectors?**

**Current State:** ❌ No admin interface exists

**Solution:**
1. Create Admin Panel at `/admin/connectors`
2. Add "Register Platform Connector" button (admin-only)
3. Use same wizard but with `is_platform=True` flag
4. Connector becomes available to all users

**Implementation:**
- New route: `/admin/connectors`
- New component: `AdminConnectorManagement.tsx`
- Requires `is_superuser` check
- Separate from user catalog

---

### 4. **Should users register connectors?**

**YES** ✅ - As a SaaS platform feature:

**Two Types:**
1. **Platform Connectors** - Admin registers, available to all users
2. **Custom Connectors** - Users register, private to them

**User Custom Connector Registration:**
- Users can create their own connectors
- Connectors are user-scoped (only visible to creator)
- Useful for private integrations
- Can be submitted for platform approval (future feature)

**Current Implementation:** ✅ Already supports this (but needs RBAC)

---

## Next Steps

1. **Add RBAC** - Separate user vs admin access
2. **Create Admin Panel** - `/admin/connectors` for platform management
3. **Update User Catalog** - Focus on user features (authorize, test, custom)
4. **Add Authorization Status** - Show which connectors are authorized
5. **Add Database Fields** - `owner_id`, `is_platform` to Connector model

This will create a proper SaaS platform where:
- **Users** can browse, authorize, and use connectors
- **Admins** can manage platform connectors for all users
- **Both** can register connectors (platform vs custom)

