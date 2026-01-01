/**
 * System Alerts Component
 *
 * Displays system-level alerts like circuit breaker warnings, database errors, etc.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { AlertCircle, AlertTriangle, CheckCircle2, XCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface SystemAlert {
  id: string
  alert_type: string
  severity: "info" | "warning" | "error" | "critical"
  title: string
  message: string
  details?: Record<string, unknown>
  is_resolved: boolean
  resolved_at?: string
  resolved_by?: string
  created_at: string
  updated_at: string
}

interface SystemAlertsResponse {
  alerts: SystemAlert[]
  total: number
  unresolved_count: number
}

async function fetchSystemAlerts(): Promise<SystemAlertsResponse> {
  return apiClient.request<SystemAlertsResponse>("/api/v1/admin/system/alerts")
}

async function resolveAlert(alertId: string): Promise<unknown> {
  return apiClient.request(`/api/v1/admin/system/alerts/${alertId}/resolve`, {
    method: "POST",
  })
}

export function SystemAlerts() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const {
    data: alertsData,
    isLoading,
    error,
  } = useQuery<SystemAlertsResponse>({
    queryKey: ["systemAlerts"],
    queryFn: fetchSystemAlerts,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const resolveMutation = useMutation({
    mutationFn: resolveAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["systemAlerts"] })
      queryClient.invalidateQueries({ queryKey: ["systemHealth"] })
      showSuccessToast("Alert resolved successfully")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to resolve alert", error.message)
    },
  })

  if (error) {
    showErrorToast(
      "Failed to load system alerts",
      error instanceof Error ? error.message : "Unknown error",
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (error || !alertsData) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          Failed to load system alerts information.
        </AlertDescription>
      </Alert>
    )
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <XCircle className="h-5 w-5 text-red-500" />
      case "error":
        return <AlertCircle className="h-5 w-5 text-orange-500" />
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case "info":
        return <AlertCircle className="h-5 w-5 text-blue-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    const colors = {
      critical: "bg-red-500",
      error: "bg-orange-500",
      warning: "bg-yellow-500",
      info: "bg-blue-500",
    }
    return (
      <Badge
        className={colors[severity as keyof typeof colors] || "bg-gray-500"}
      >
        {severity.toUpperCase()}
      </Badge>
    )
  }

  const unresolvedAlerts = alertsData.alerts.filter((a) => !a.is_resolved)
  const resolvedAlerts = alertsData.alerts.filter((a) => a.is_resolved)

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>System Alerts</CardTitle>
              <CardDescription>
                Critical system issues and warnings requiring attention
              </CardDescription>
            </div>
            {alertsData.unresolved_count > 0 && (
              <Badge variant="destructive" className="text-lg px-3 py-1">
                {alertsData.unresolved_count} Unresolved
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg">
              <div className="text-2xl font-bold">{alertsData.total}</div>
              <div className="text-sm text-muted-foreground">Total Alerts</div>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="text-2xl font-bold text-red-500">
                {alertsData.unresolved_count}
              </div>
              <div className="text-sm text-muted-foreground">Unresolved</div>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="text-2xl font-bold text-green-500">
                {resolvedAlerts.length}
              </div>
              <div className="text-sm text-muted-foreground">Resolved</div>
            </div>
            <div className="p-4 border rounded-lg">
              <div className="text-2xl font-bold text-orange-500">
                {
                  unresolvedAlerts.filter((a) => a.severity === "critical")
                    .length
                }
              </div>
              <div className="text-sm text-muted-foreground">Critical</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Unresolved Alerts */}
      {unresolvedAlerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Active Alerts</CardTitle>
            <CardDescription>Unresolved system issues</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {unresolvedAlerts.map((alert) => (
                <Alert
                  key={alert.id}
                  variant={
                    alert.severity === "critical" ? "destructive" : "default"
                  }
                >
                  <div className="flex items-start gap-3">
                    {getSeverityIcon(alert.severity)}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <AlertTitle className="flex items-center gap-2">
                          {alert.title}
                          {getSeverityBadge(alert.severity)}
                        </AlertTitle>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => resolveMutation.mutate(alert.id)}
                          disabled={resolveMutation.isPending}
                        >
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                          Resolve
                        </Button>
                      </div>
                      <AlertDescription className="mt-2">
                        {alert.message}
                      </AlertDescription>
                      {alert.details &&
                        Object.keys(alert.details).length > 0 && (
                          <div className="mt-3 p-3 bg-muted rounded-md">
                            <div className="text-sm font-medium mb-2">
                              Details:
                            </div>
                            <pre className="text-xs overflow-auto">
                              {JSON.stringify(alert.details, null, 2)}
                            </pre>
                          </div>
                        )}
                      <div className="mt-2 text-xs text-muted-foreground">
                        Created: {new Date(alert.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </Alert>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resolved Alerts */}
      {resolvedAlerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Resolved Alerts</CardTitle>
            <CardDescription>Recently resolved issues</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {resolvedAlerts.slice(0, 10).map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <div>
                      <div className="font-medium">{alert.title}</div>
                      <div className="text-sm text-muted-foreground">
                        Resolved:{" "}
                        {alert.resolved_at
                          ? new Date(alert.resolved_at).toLocaleString()
                          : "Unknown"}
                      </div>
                    </div>
                  </div>
                  {getSeverityBadge(alert.severity)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {alertsData.alerts.length === 0 && (
        <Alert>
          <CheckCircle2 className="h-4 w-4" />
          <AlertTitle>All Clear</AlertTitle>
          <AlertDescription>
            No system alerts at this time. All systems are operating normally.
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}
