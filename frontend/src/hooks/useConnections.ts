import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { apiClient } from "@/lib/apiClient"

interface Connection {
  id: string
  connector_id: string
  connector_slug: string | null
  connector_name: string | null
  nango_connection_id: string
  status: "connected" | "disconnected" | "pending" | "error"
  connected_at: string | null
  disconnected_at: string | null
  last_synced_at: string | null
  config: Record<string, any> | null
  error_count: number
  last_error: string | null
}

interface ConnectionsResponse {
  connections: Connection[]
  total_count: number
}

export function useConnections(connectorId?: string) {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery<ConnectionsResponse>({
    queryKey: ["connections", connectorId],
    queryFn: async () => {
      const url = connectorId
        ? `/api/v1/connectors/connections?connector_id=${connectorId}`
        : "/api/v1/connectors/connections"
      return apiClient.request<ConnectionsResponse>(url)
    },
  })

  const connectMutation = useMutation({
    mutationFn: async ({
      connectorId,
      instanceId,
    }: {
      connectorId: string
      instanceId?: string
    }) => {
      const url = new URL(
        `/api/v1/connectors/${connectorId}/connect`,
        window.location.origin,
      )
      if (instanceId) {
        url.searchParams.set("instance_id", instanceId)
      }
      return apiClient.request<{
        oauth_url: string | null
        connection_id: string
        nango_connection_id: string
        popup: boolean
        already_connected?: boolean
        message?: string
      }>(url.pathname + url.search, {
        method: "POST",
      })
    },
    onSuccess: (data) => {
      if (data.already_connected) {
        toast.success(data.message || "Already connected")
      }
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to initiate connection")
    },
  })

  const disconnectMutation = useMutation({
    mutationFn: async ({
      connectorId,
      connectionId,
    }: {
      connectorId: string
      connectionId: string
    }) => {
      return apiClient.request<{ success: boolean; message: string }>(
        `/api/v1/connectors/${connectorId}/disconnect?connection_id=${connectionId}`,
        {
          method: "DELETE",
        },
      )
    },
    onSuccess: (data) => {
      toast.success(data.message || "Disconnected successfully")
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to disconnect")
    },
  })

  const getConnectionStatus = (connectorId: string): Connection | undefined => {
    if (!data?.connections) return undefined
    return data.connections.find(
      (conn) =>
        conn.connector_id === connectorId && conn.status === "connected",
    )
  }

  const isConnected = (connectorId: string): boolean => {
    return !!getConnectionStatus(connectorId)
  }

  return {
    connections: data?.connections || [],
    totalCount: data?.total_count || 0,
    isLoading,
    error,
    connect: connectMutation.mutate,
    disconnect: disconnectMutation.mutate,
    isConnecting: connectMutation.isPending,
    isDisconnecting: disconnectMutation.isPending,
    getConnectionStatus,
    isConnected,
  }
}
