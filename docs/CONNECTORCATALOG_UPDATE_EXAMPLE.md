# ConnectorCatalog Update Example

This document shows how to update `ConnectorCatalog.tsx` to use the new Nango connection components.

## Changes Needed

### 1. Import New Components

```typescript
import { ConnectButton } from '@/components/Connectors/ConnectButton';
import { ConnectionStatus } from '@/components/Connectors/ConnectionStatus';
import { useConnections } from '@/hooks/useConnections';
```

### 2. Add Connections Hook

```typescript
export function ConnectorCatalog() {
  // ... existing state ...
  
  // Add connections hook
  const { connections, isConnected, connect, disconnect, getConnectionStatus } = useConnections();
  
  // ... rest of component
}
```

### 3. Update Columns to Show Connection Status

In the `columns` definition, add a connection status column:

```typescript
const columns: ColumnDef<Connector>[] = [
  // ... existing columns ...
  {
    id: "connection_status",
    header: "Status",
    cell: ({ row }) => {
      const connector = row.original;
      const connection = getConnectionStatus(connector.id);
      return <ConnectionStatus status={connection?.status || 'disconnected'} />;
    },
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const connector = row.original;
      const connection = getConnectionStatus(connector.id);
      const isConn = isConnected(connector.id);
      
      return (
        <div className="flex items-center gap-2">
          {isConn ? (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  // Show connection details or reconnect
                }}
              >
                Manage
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  if (connection) {
                    disconnect({ 
                      connectorId: connector.id, 
                      connectionId: connection.id 
                    });
                  }
                }}
              >
                Disconnect
              </Button>
            </>
          ) : (
            <ConnectButton
              connectorId={connector.id}
              connectorName={connector.name}
              onConnected={() => {
                // Refresh connections
                refetchConnections();
              }}
            />
          )}
        </div>
      );
    },
  },
];
```

### 4. Update Connector Details Dialog

In the connector details dialog, replace OAuth buttons with:

```typescript
{connectorDetails?.manifest?.nango?.enabled && (
  <div className="space-y-2">
    {isConnected(selectedConnector.id) ? (
      <div className="space-y-2">
        <ConnectionStatus status="connected" />
        <div className="flex gap-2">
          <ConnectButton
            connectorId={selectedConnector.id}
            connectorName={selectedConnector.name}
            onConnected={() => {
              fetchConnectorDetails(selectedConnector.slug);
            }}
          />
          <Button
            variant="destructive"
            onClick={() => {
              const connection = getConnectionStatus(selectedConnector.id);
              if (connection) {
                disconnect({ 
                  connectorId: selectedConnector.id, 
                  connectionId: connection.id 
                });
              }
            }}
          >
            Disconnect
          </Button>
        </div>
      </div>
    ) : (
      <ConnectButton
        connectorId={selectedConnector.id}
        connectorName={selectedConnector.name}
        onConnected={() => {
          fetchConnectorDetails(selectedConnector.slug);
        }}
      />
    )}
  </div>
)}
```

### 5. Remove Old OAuth Code

Remove or update:
- `OAuthModal` usage (if not needed)
- `handleDisconnect` function (use hook instead)
- `fetchAuthStatuses` function (use hook instead)

## Complete Example Integration

See the updated `ConnectorCatalog.tsx` for full implementation. The key changes are:

1. Use `useConnections()` hook instead of manual API calls
2. Replace OAuth buttons with `ConnectButton` component
3. Show connection status with `ConnectionStatus` component
4. Use hook's `disconnect` function instead of custom handler


