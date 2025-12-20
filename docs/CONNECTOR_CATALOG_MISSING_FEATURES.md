# Missing Connector Catalog Functionalities

Based on the API endpoints available and the PRD requirements, here are the functionalities that should be added to the Connector Catalog but are currently missing:

## Currently Implemented ✅

1. **View Connectors** - List all connectors in a table
2. **Register New Connector** - Wizard to register new connectors
3. **View Connector Details** - Modal showing connector information
4. **OAuth Authorization** - Authorize connectors via OAuth flow
5. **Test Connector Actions/Triggers** - Test connector functionality

## Missing Functionalities ❌

### 1. **Category Filtering** 🔴 HIGH PRIORITY
**Status:** API supports it, UI missing
**API Endpoint:** `GET /api/v1/connectors/list?category=Communication%20%26%20Collaboration`
**What's Missing:**
- Category filter dropdown/buttons in the UI
- Visual category badges/chips
- Filter by multiple categories

**Expected UI:**
```
[All] [Communication & Collaboration] [CRM & Sales] [Project Management] ...
```

**Implementation:**
- Add category filter buttons above the table
- Update `fetchConnectors` to accept category parameter
- Show active category filter

---

### 2. **Status Filtering** 🟡 MEDIUM PRIORITY
**Status:** API supports it, UI missing
**API Endpoint:** `GET /api/v1/connectors/list?status_filter=beta`
**What's Missing:**
- Status filter dropdown (draft, beta, stable, deprecated)
- Visual status indicators in the table

**Expected UI:**
```
Status: [All] [Beta] [Stable] [Deprecated]
```

---

### 3. **Authorization Status Display** 🔴 HIGH PRIORITY
**Status:** Partially implemented
**What's Missing:**
- Show authorization status in the table (Authorized ✅ / Not Authorized ❌)
- Check if user has authorized the connector before showing "Authorize" button
- Display last authorized date
- Show token expiration status

**Expected UI:**
```
| Name | Status | Version | Auth Status | Actions |
|------|--------|---------|-------------|---------|
| Gmail| beta   | 1.0.0   | ✅ Authorized| View    |
| Slack| beta   | 1.0.0   | ❌ Not Auth  | View    |
```

**API Needed:**
- `GET /api/v1/connectors/{slug}/auth-status` - Check if connector is authorized for current user

---

### 4. **Rotate Credentials** 🟡 MEDIUM PRIORITY
**Status:** API exists, UI missing
**API Endpoint:** `POST /api/v1/connectors/{slug}/rotate`
**What's Missing:**
- "Rotate Credentials" button in connector details modal
- Confirmation dialog before rotation
- Success/error feedback

**Expected UI:**
In connector details modal:
```
[Authorize] [Rotate Credentials] [Refresh Tokens] [Test]
```

**Use Case:**
- User wants to rotate OAuth tokens for security
- User wants to rotate API keys

---

### 5. **Refresh Tokens** 🟡 MEDIUM PRIORITY
**Status:** API exists, UI missing
**API Endpoint:** `POST /api/v1/connectors/{slug}/refresh`
**What's Missing:**
- "Refresh Tokens" button in connector details modal
- Automatic token refresh status indicator
- Manual refresh option

**Expected UI:**
In connector details modal:
```
Token Status: ✅ Valid (expires in 2 hours)
[Refresh Tokens]
```

---

### 6. **Disconnect/Revoke Authorization** 🔴 HIGH PRIORITY
**Status:** API missing, UI missing
**What's Missing:**
- "Disconnect" or "Revoke Authorization" button
- Confirmation dialog
- API endpoint to revoke tokens

**Expected UI:**
In connector details modal:
```
Authorization Status: ✅ Authorized
[Disconnect] [Rotate Credentials]
```

**API Needed:**
- `DELETE /api/v1/connectors/{slug}/authorization` - Revoke OAuth tokens

**Use Case:**
- User wants to disconnect a connector
- User wants to revoke access for security reasons

---

### 7. **View Connector Usage** 🟢 LOW PRIORITY
**Status:** Not implemented
**What's Missing:**
- Show where connectors are used (workflows, agents)
- List of workflows using this connector
- Usage statistics (how many times used, last used date)

**Expected UI:**
In connector details modal:
```
Usage:
- Used in 5 workflows
- Used by 2 agents
- Last used: 2 days ago
[View Workflows] [View Agents]
```

**API Needed:**
- `GET /api/v1/connectors/{slug}/usage` - Get connector usage information

---

### 8. **Enable/Disable Connector** 🟡 MEDIUM PRIORITY
**Status:** API exists, UI missing
**API Endpoint:** `PATCH /api/v1/connectors/{slug}/status`
**What's Missing:**
- Toggle to enable/disable connector
- Visual indicator of enabled/disabled status
- Confirmation for disabling

**Expected UI:**
In connector details modal or table:
```
Status: [Enabled] [Disabled]
```

**Use Case:**
- Temporarily disable a connector
- Deprecate a connector

---

### 9. **View Connector Versions** 🟢 LOW PRIORITY
**Status:** API exists, UI missing
**API Endpoint:** `GET /api/v1/connectors/{slug}/versions`
**What's Missing:**
- Version history in connector details modal
- Ability to switch between versions
- Version comparison

**Expected UI:**
In connector details modal:
```
Versions:
- 1.0.0 (current) ✅
- 0.9.0
- 0.8.0
```

---

### 10. **Bulk Operations** 🟢 LOW PRIORITY
**Status:** Not implemented
**What's Missing:**
- Select multiple connectors
- Bulk authorize
- Bulk disable
- Bulk delete

**Expected UI:**
```
[Select All] [Bulk Authorize] [Bulk Disable]
```

---

### 11. **Search Enhancement** 🟡 MEDIUM PRIORITY
**Status:** Basic search exists
**What's Missing:**
- Search by category
- Search by status
- Search by authorization status
- Advanced search filters

**Expected UI:**
```
Search: [________________] [Category: All ▼] [Status: All ▼] [Auth: All ▼]
```

---

### 12. **Connector Statistics** 🟢 LOW PRIORITY
**Status:** Not implemented
**What's Missing:**
- Total connectors count
- Authorized connectors count
- Connectors by category count
- Most used connectors

**Expected UI:**
```
Statistics:
- Total: 99 connectors
- Authorized: 15 connectors
- By Category: Communication (15), CRM (10), ...
```

---

### 13. **Quick Actions Menu** 🟡 MEDIUM PRIORITY
**Status:** Not implemented
**What's Missing:**
- Dropdown menu with quick actions per connector
- Actions: View, Authorize, Test, Rotate, Disconnect, Disable

**Expected UI:**
```
[View ▼]
  ├─ View Details
  ├─ Authorize
  ├─ Test Connector
  ├─ Rotate Credentials
  ├─ Refresh Tokens
  ├─ Disconnect
  └─ Disable
```

---

### 14. **Connector Health Status** 🟢 LOW PRIORITY
**Status:** Not implemented
**What's Missing:**
- Health check for connectors
- API availability status
- Token validity check
- Last successful action timestamp

**Expected UI:**
```
Health Status: ✅ Healthy
Last Check: 5 minutes ago
Last Success: 2 hours ago
```

---

### 15. **Export/Import Connectors** 🟢 LOW PRIORITY
**Status:** Not implemented
**What's Missing:**
- Export connector configurations
- Import connector configurations
- Backup/restore functionality

---

## Priority Recommendations

### Phase 1 (Critical - Should be implemented first):
1. ✅ **Category Filtering** - Essential for navigating 99 connectors
2. ✅ **Authorization Status Display** - Users need to know which connectors are authorized
3. ✅ **Disconnect/Revoke Authorization** - Security requirement

### Phase 2 (Important - Next priority):
4. ✅ **Rotate Credentials** - Security feature
5. ✅ **Refresh Tokens** - Token management
6. ✅ **Status Filtering** - Better organization
7. ✅ **Enable/Disable Connector** - Connector management

### Phase 3 (Nice to have):
8. ✅ **Quick Actions Menu** - Better UX
9. ✅ **Search Enhancement** - Better discoverability
10. ✅ **View Connector Usage** - Usage insights
11. ✅ **Connector Statistics** - Dashboard insights

### Phase 4 (Future enhancements):
12. ✅ **View Connector Versions** - Version management
13. ✅ **Bulk Operations** - Efficiency
14. ✅ **Connector Health Status** - Monitoring
15. ✅ **Export/Import** - Backup/restore

---

## Implementation Notes

### API Endpoints That Need to Be Created:
1. `GET /api/v1/connectors/{slug}/auth-status` - Check authorization status
2. `DELETE /api/v1/connectors/{slug}/authorization` - Revoke authorization
3. `GET /api/v1/connectors/{slug}/usage` - Get usage information
4. `GET /api/v1/connectors/stats` - Get connector statistics

### Frontend Components That Need to Be Created/Enhanced:
1. `CategoryFilter.tsx` - Category filter component
2. `StatusFilter.tsx` - Status filter component
3. `AuthStatusBadge.tsx` - Authorization status badge
4. `ConnectorActionsMenu.tsx` - Quick actions dropdown menu
5. `ConnectorUsagePanel.tsx` - Usage information panel
6. `ConnectorStats.tsx` - Statistics component

### Database Queries Needed:
1. Check if user has authorized a connector (query OAuth tokens)
2. Get connector usage (query workflows, agents using connector)
3. Get connector statistics (aggregate queries)

---

## Summary

The Connector Catalog currently has **basic functionality** (view, register, authorize, test) but is missing **critical management features** like:

- **Filtering and organization** (category, status filters)
- **Authorization management** (status display, disconnect, rotate)
- **Usage insights** (where connectors are used)
- **Bulk operations** (efficient management)

The most critical missing features are:
1. **Category filtering** - Essential for navigating 99 connectors
2. **Authorization status** - Users need to see what's authorized
3. **Disconnect functionality** - Security requirement

These should be prioritized for implementation.
