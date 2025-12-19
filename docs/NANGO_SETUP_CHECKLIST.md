# Nango OAuth Setup Checklist

## ✅ Implementation Complete

### Backend
- [x] Created `UserConnectorConnection` SQLModel
- [x] Created Nango service wrapper (`backend/app/services/nango_service.py`)
- [x] Added Nango environment variables to config
- [x] Added Nango SDK to `pyproject.toml`
- [x] Created API endpoints:
  - [x] `POST /api/v1/connectors/{id}/connect` - Initiate OAuth
  - [x] `GET /api/v1/connectors/callback` - Handle OAuth callback
  - [x] `GET /api/v1/connectors/connections` - List connections
  - [x] `DELETE /api/v1/connectors/{id}/disconnect` - Disconnect
- [x] Created database migration file

### Frontend
- [x] Created `ConnectButton` component
- [x] Created `ConnectionStatus` component
- [x] Created `useConnections` hook

### Documentation
- [x] Created implementation guide
- [x] Created setup checklist

## ⏳ Next Steps

### 1. Install Dependencies
```bash
cd backend
pip install nango
# Or if using uv:
uv pip install nango
```

### 2. Run Database Migration
```bash
cd backend
alembic upgrade head
```

Or apply via Supabase MCP:
```python
# Read migration file and apply
mcp_supabase_apply_migration(
    name="add_user_connector_connection",
    query=<migration_sql>
)
```

### 3. Add Environment Variables to Render
Add these to your Render backend service:
- `NANGO_SECRET_KEY` - Your Nango secret key from dashboard
- `NANGO_BASE_URL` - Optional, defaults to `https://api.nango.dev`
- `NANGO_ENABLED=true`

### 4. Update ConnectorCatalog Component
Update `frontend/src/components/Connectors/ConnectorCatalog.tsx` to:
- Import `ConnectButton` and `ConnectionStatus`
- Use `useConnections` hook to fetch connection status
- Show connection status for each connector
- Replace existing OAuth buttons with `ConnectButton`

### 5. Test OAuth Flow
1. Deploy backend with new endpoints
2. Test connecting a connector (e.g., Gmail)
3. Verify popup opens and OAuth completes
4. Check connection appears in `/api/v1/connectors/connections`
5. Test disconnect functionality

### 6. Update Workflow Builder
When users add connector nodes to workflows:
- Show dropdown of user's connected accounts for that connector
- Store `connection_id` in node config
- Use connection when executing workflow

## Files Created/Modified

### New Files
- `backend/app/models/user_connector_connection.py`
- `backend/app/services/nango_service.py`
- `backend/app/alembic/versions/XXXX_add_user_connector_connection.py`
- `frontend/src/components/Connectors/ConnectButton.tsx`
- `frontend/src/components/Connectors/ConnectionStatus.tsx`
- `frontend/src/hooks/useConnections.ts`
- `docs/NANGO_OAUTH_IMPLEMENTATION.md`
- `docs/NANGO_SETUP_CHECKLIST.md`

### Modified Files
- `backend/app/core/config.py` - Added Nango config
- `backend/app/api/routes/connectors.py` - Added Nango endpoints
- `backend/pyproject.toml` - Added nango dependency

## Testing Checklist

- [ ] Install Nango SDK
- [ ] Run database migration
- [ ] Add environment variables
- [ ] Test connect endpoint
- [ ] Test OAuth popup flow
- [ ] Test callback endpoint
- [ ] Test list connections
- [ ] Test disconnect
- [ ] Test error handling
- [ ] Test multiple connections per connector
- [ ] Test workflow execution with connections

## Notes

- All 99 connectors already have Nango configuration in their manifests
- Provider keys should match connector slugs or be configured in manifest `nango.provider_key`
- Nango handles token refresh automatically
- Connections are isolated per user
- Multiple connections per connector supported via `instance_id`


