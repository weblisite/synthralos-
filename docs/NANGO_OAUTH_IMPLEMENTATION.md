# Nango OAuth Implementation Guide

## Overview

This document describes the Nango OAuth integration for SynthralOS connectors. Nango is used as a unified OAuth proxy that handles OAuth flows for all 99+ connectors, managing token storage, refresh, and security.

## Architecture

### Flow Diagram

```
User → Frontend (Connect Button) 
    → Backend (/api/v1/connectors/{id}/connect)
    → Nango Service (create_connection)
    → Nango API (OAuth URL)
    → Popup Window (User authorizes)
    → Nango Callback
    → Backend (/api/v1/connectors/callback)
    → Database (Update connection status)
    → Frontend (Show success)
```

## Database Schema

### `user_connector_connection` Table

Stores user's OAuth connections to connectors:

```sql
CREATE TABLE user_connector_connection (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES user(id) ON DELETE CASCADE,
    connector_id UUID REFERENCES connector(id) ON DELETE CASCADE,
    nango_connection_id VARCHAR UNIQUE NOT NULL,
    status VARCHAR DEFAULT 'pending',  -- pending, connected, disconnected, error
    connected_at TIMESTAMP WITH TIME ZONE,
    disconnected_at TIMESTAMP WITH TIME ZONE,
    last_synced_at TIMESTAMP WITH TIME ZONE,
    config JSONB,  -- Connector-specific config (e.g., account name, workspace)
    last_error VARCHAR,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Indexes:**
- `user_id` - For querying user's connections
- `connector_id` - For querying connections by connector
- `nango_connection_id` - For OAuth callback lookup
- `status` - For filtering by connection status
- Composite: `(user_id, connector_id)` - For common queries

## Backend Implementation

### 1. Nango Service (`backend/app/services/nango_service.py`)

Wrapper around Nango SDK:

```python
from app.services.nango_service import get_nango_service

nango_service = get_nango_service()

# Create OAuth connection
oauth_data = await nango_service.create_connection(
    user_id=str(user.id),
    connector_slug="gmail",
    connection_id="user_123_gmail_work",
    return_url="https://yourapp.com/callback",
    provider_key="gmail"  # Optional, defaults to connector_slug
)

# Get access token
access_token = await nango_service.get_access_token(
    connection_id="user_123_gmail_work",
    provider_key="gmail"
)

# Delete connection
await nango_service.delete_connection(
    connection_id="user_123_gmail_work",
    provider_key="gmail"
)
```

### 2. API Endpoints

#### POST `/api/v1/connectors/{connector_id}/connect`

Initiate OAuth connection.

**Query Parameters:**
- `instance_id` (optional): For multiple accounts (e.g., "work@gmail.com")

**Response:**
```json
{
  "oauth_url": "https://api.nango.dev/oauth/gmail?connection_id=...",
  "connection_id": "uuid-of-connection",
  "nango_connection_id": "user_123_gmail_work",
  "popup": true,
  "already_connected": false
}
```

#### GET `/api/v1/connectors/callback`

Handle OAuth callback from Nango.

**Query Parameters:**
- `connection_id`: Nango connection identifier
- `provider_config_key`: Nango provider key (optional)

**Response:**
```json
{
  "success": true,
  "connection_id": "uuid",
  "connector_slug": "gmail",
  "status": "connected"
}
```

#### GET `/api/v1/connectors/connections`

List user's connections.

**Query Parameters:**
- `connector_id` (optional): Filter by connector

**Response:**
```json
{
  "connections": [
    {
      "id": "uuid",
      "connector_id": "uuid",
      "connector_slug": "gmail",
      "connector_name": "Gmail",
      "status": "connected",
      "connected_at": "2025-01-19T10:00:00Z",
      "last_synced_at": "2025-01-19T10:00:00Z"
    }
  ],
  "total_count": 1
}
```

#### DELETE `/api/v1/connectors/{connector_id}/disconnect`

Disconnect a connection.

**Query Parameters:**
- `connection_id`: Connection UUID to disconnect

**Response:**
```json
{
  "success": true,
  "message": "Disconnected successfully"
}
```

## Frontend Implementation

### 1. ConnectButton Component

```tsx
import { ConnectButton } from '@/components/Connectors/ConnectButton';

<ConnectButton
  connectorId="gmail-uuid"
  connectorName="Gmail"
  instanceId="work@gmail.com"  // Optional
  onConnected={() => {
    // Refresh connections list
    refetchConnections();
  }}
/>
```

### 2. ConnectionStatus Component

```tsx
import { ConnectionStatus } from '@/components/Connectors/ConnectionStatus';

<ConnectionStatus status="connected" />
```

### 3. useConnections Hook

```tsx
import { useConnections } from '@/hooks/useConnections';

const { 
  connections, 
  isConnected, 
  connect, 
  disconnect 
} = useConnections('gmail-uuid');

// Check if connected
if (isConnected('gmail-uuid')) {
  // Show connected UI
}

// Connect
connect({ connectorId: 'gmail-uuid', instanceId: 'work@gmail.com' });

// Disconnect
disconnect({ connectorId: 'gmail-uuid', connectionId: 'connection-uuid' });
```

## Environment Variables

Add to Render environment variables:

```bash
NANGO_BASE_URL=https://api.nango.dev  # Or your self-hosted URL
NANGO_SECRET_KEY=your_nango_secret_key  # From Nango dashboard
NANGO_PUBLIC_KEY=your_nango_public_key  # Optional, for frontend
NANGO_ENABLED=true
```

## Workflow Execution Integration

When executing workflows that use connectors:

```python
# backend/app/services/workflow_executor.py

async def execute_connector_action(
    workflow_execution_id: str,
    node_id: str,
    action: str,
    user_id: UUID,
    session: SessionDep
):
    # Get workflow node config
    node = get_workflow_node(node_id)
    connector_id = node.connector_id
    connection_id = node.connection_id  # User selects which connection
    
    # Get user's connection
    connection = session.query(UserConnectorConnection).filter(
        UserConnectorConnection.id == connection_id,
        UserConnectorConnection.user_id == user_id,
        UserConnectorConnection.status == "connected"
    ).first()
    
    # Get connector and provider key
    connector = await get_connector_by_id(connector_id, session)
    connector_version = session.get(ConnectorVersion, connector.latest_version_id)
    manifest = connector_version.manifest
    nango_config = manifest.get("nango", {})
    provider_key = nango_config.get("provider_key", connector.slug)
    
    # Get access token from Nango
    nango_service = get_nango_service()
    access_token = await nango_service.get_access_token(
        connection_id=connection.nango_connection_id,
        provider_key=provider_key
    )
    
    # Execute the action using the connector's API
    result = await execute_connector_api_call(
        connector=connector,
        action=action,
        access_token=access_token,
        params=node.config
    )
    
    # Update last synced time
    connection.last_synced_at = datetime.utcnow()
    session.commit()
    
    return result
```

## Migration Steps

1. **Install Nango SDK:**
   ```bash
   pip install nango
   ```

2. **Run Database Migration:**
   ```bash
   alembic upgrade head
   ```

3. **Add Environment Variables to Render:**
   - `NANGO_SECRET_KEY`
   - `NANGO_BASE_URL` (optional, defaults to https://api.nango.dev)
   - `NANGO_ENABLED=true`

4. **Configure Nango Dashboard:**
   - Ensure all 99 connectors have OAuth apps configured
   - Provider keys match connector slugs or are configured in manifests

5. **Test Connection Flow:**
   - Click "Connect" on a connector
   - Complete OAuth flow
   - Verify connection appears in `/api/v1/connectors/connections`
   - Test disconnect

## Connector-Specific Configuration

Store connector-specific config in `connection.config` JSONB field:

```json
{
  "gmail_account": "work@gmail.com",
  "slack_workspace": "acme-corp",
  "github_repo": "my-project",
  "custom_setting": "value"
}
```

## Multiple Connections Per Connector

Users can have multiple connections to the same connector (e.g., multiple Gmail accounts):

- Use `instance_id` parameter when connecting
- Connection ID format: `{user_id}_{connector_id}_{instance_id}`
- Store instance identifier in `connection.config.instance_id`

## Error Handling

- Connection errors stored in `last_error` field
- `error_count` tracks retry attempts
- Status set to "error" on failure
- Users can retry connection from UI

## Security Considerations

1. **Token Storage:** Nango handles token storage securely (encrypted)
2. **Token Refresh:** Nango automatically refreshes expired tokens
3. **Connection Isolation:** Each user's connections are isolated by `user_id`
4. **Authorization:** Users can only access their own connections
5. **Popup Security:** OAuth popup validates origin before accepting messages

## Testing

1. **Unit Tests:** Test Nango service wrapper
2. **Integration Tests:** Test OAuth flow end-to-end
3. **E2E Tests:** Test popup window flow in browser
4. **Error Scenarios:** Test connection failures, token expiration, etc.

## Troubleshooting

### Connection Fails to Create
- Check Nango API key is correct
- Verify connector has Nango enabled in manifest
- Check provider key matches Nango configuration

### Popup Doesn't Open
- Check browser popup blocker settings
- Verify `oauth_url` is returned from backend
- Check browser console for errors

### Callback Not Received
- Verify `return_url` is correct
- Check Nango webhook configuration
- Verify connection_id matches

### Token Retrieval Fails
- Check connection status is "connected"
- Verify provider key is correct
- Check Nango connection exists in Nango dashboard

## Next Steps

1. ✅ Database migration created
2. ✅ Nango service implemented
3. ✅ API endpoints implemented
4. ✅ Frontend components created
5. ⏳ Update ConnectorCatalog to use new components
6. ⏳ Add connection selection in workflow builder
7. ⏳ Implement workflow execution with connections
8. ⏳ Add connection management UI
9. ⏳ Test with all 99 connectors


