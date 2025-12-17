/**
 * Activity Logs Component
 *
 * Displays recent platform activity and events.
 */

import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import { Activity, Clock } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"

interface ActivityItem {
  type: string
  id: string
  execution_id?: string
  workflow_id?: string
  status?: string
  timestamp: string
  description: string
}

interface ActivityData {
  activity: ActivityItem[]
  total: number
  timestamp: string
}

async function fetchActivityLogs(): Promise<ActivityData> {
  const { supabase } = await import("@/lib/supabase")
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session?.access_token) {
    throw new Error("No authentication token")
  }

  const response = await fetch("/api/v1/admin/system/activity?limit=50", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch activity logs: ${response.status}`)
  }

  return response.json()
}

export function ActivityLogs() {
  const { showErrorToast } = useCustomToast()

  const { data: activityData, isLoading, error } = useQuery<ActivityData>({
    queryKey: ["activityLogs"],
    queryFn: fetchActivityLogs,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (error) {
    showErrorToast("Failed to load activity logs", error instanceof Error ? error.message : "Unknown error")
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-64 w-full" />
      </div>
    )
  }

  if (error || !activityData) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Failed to load activity logs</p>
      </div>
    )
  }

  const getStatusBadge = (status?: string) => {
    if (!status) return null

    const statusColors: Record<string, string> = {
      completed: "bg-green-500",
      failed: "bg-red-500",
      running: "bg-blue-500",
      paused: "bg-yellow-500",
    }

    return (
      <Badge className={statusColors[status] || "bg-gray-500"}>
        {status}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Recent Activity</h2>
        <p className="text-muted-foreground">
          Platform events and workflow executions
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Activity Log
              </CardTitle>
              <CardDescription>
                {activityData?.total ?? 0} recent events
              </CardDescription>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Clock className="h-4 w-4" />
              Last 24 hours
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {!activityData?.activity || activityData.activity.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No recent activity
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Time</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>ID</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {activityData.activity.map((item: ActivityItem, index: number) => (
                  <TableRow key={index}>
                    <TableCell className="font-mono text-xs">
                      {format(new Date(item.timestamp), "HH:mm:ss")}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {item.type}
                      </Badge>
                    </TableCell>
                    <TableCell>{item.description}</TableCell>
                    <TableCell>{getStatusBadge(item.status)}</TableCell>
                    <TableCell className="font-mono text-xs">
                      {item.execution_id
                        ? item.execution_id.substring(0, 8) + "..."
                        : item.id.substring(0, 8) + "..."}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <div className="text-xs text-muted-foreground text-center">
        Last updated: {activityData?.timestamp ? new Date(activityData.timestamp).toLocaleString() : "Never"}
      </div>
    </div>
  )
}

