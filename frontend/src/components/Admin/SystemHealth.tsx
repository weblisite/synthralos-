/**
 * System Health Component
 *
 * Displays system health status, service availability, and database connectivity.
 */

import { useQuery } from "@tanstack/react-query"
import { AlertCircle, CheckCircle2, Database, Server, XCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"

interface ServiceStatus {
  name: string
  status: "available" | "unavailable"
  message: string
}

interface HealthData {
  status: "healthy" | "degraded" | "unhealthy"
  timestamp: string
  services: Record<string, boolean>
  database: {
    status: string
    user_count?: number
    error?: string
  }
  checks: ServiceStatus[]
}

async function fetchSystemHealth(): Promise<HealthData> {
  const { supabase } = await import("@/lib/supabase")
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session?.access_token) {
    throw new Error("No authentication token")
  }

  const response = await fetch("/api/v1/admin/system/health", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch system health: ${response.status}`)
  }

  return response.json()
}

export function SystemHealth() {
  const { showErrorToast } = useCustomToast()

  const { data: health, isLoading, error } = useQuery<HealthData>({
    queryKey: ["systemHealth"],
    queryFn: fetchSystemHealth,
    refetchInterval: 30000, // Refresh every 30 seconds
    onError: (error: Error) => {
      showErrorToast("Failed to load system health", error.message)
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (error || !health) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load system health information.
        </AlertDescription>
      </Alert>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-500"
      case "degraded":
        return "bg-yellow-500"
      case "unhealthy":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "healthy":
        return <Badge className="bg-green-500">Healthy</Badge>
      case "degraded":
        return <Badge className="bg-yellow-500">Degraded</Badge>
      case "unhealthy":
        return <Badge className="bg-red-500">Unhealthy</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Status</CardTitle>
              <CardDescription>
                Overall platform health and availability
              </CardDescription>
            </div>
            {getStatusBadge(health.status)}
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <div
              className={`h-3 w-3 rounded-full ${getStatusColor(health.status)}`}
            />
            <span className="text-sm text-muted-foreground">
              Last checked: {new Date(health.timestamp).toLocaleString()}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Database Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            <CardTitle>Database</CardTitle>
          </div>
          <CardDescription>PostgreSQL database connectivity</CardDescription>
        </CardHeader>
        <CardContent>
          {health.database.status === "connected" ? (
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <div>
                <p className="font-medium">Connected</p>
                {health.database.user_count !== undefined && (
                  <p className="text-sm text-muted-foreground">
                    {health.database.user_count} users registered
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <div>
                <p className="font-medium text-red-500">Connection Error</p>
                {health.database.error && (
                  <p className="text-sm text-muted-foreground">
                    {health.database.error}
                  </p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Service Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            <CardTitle>Services</CardTitle>
          </div>
          <CardDescription>External service availability</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(health.services).map(([service, available]) => (
              <div
                key={service}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-2">
                  {available ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-gray-400" />
                  )}
                  <span className="font-medium capitalize">{service}</span>
                </div>
                <Badge variant={available ? "default" : "secondary"}>
                  {available ? "Configured" : "Not Configured"}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Health Checks */}
      {health.checks.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Health Checks</CardTitle>
            <CardDescription>Detailed service checks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {health.checks.map((check, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 border rounded"
                >
                  <div className="flex items-center gap-2">
                    {check.status === "available" ||
                    check.status === "connected" ? (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm font-medium">{check.name}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {check.message}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

