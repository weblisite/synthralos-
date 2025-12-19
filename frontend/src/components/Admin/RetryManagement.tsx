/**
 * Retry Management Component
 *
 * Displays failed executions and allows manual retry management.
 */

import { useCallback, useEffect, useState } from "react"
import { Play, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { DataTable } from "@/components/Common/DataTable"
import { type ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface FailedExecution {
  id: string
  execution_id: string
  workflow_id: string
  status: "failed"
  started_at: string
  completed_at: string | null
  error_message: string | null
  retry_count: number
  next_retry_at: string | null
}

export function RetryManagement() {
  const [failedExecutions, setFailedExecutions] = useState<FailedExecution[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const fetchFailedExecutions = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await apiClient.request<FailedExecution[]>(
        `/api/v1/workflows/executions/failed?limit=1000`
      )
      setFailedExecutions(Array.isArray(data) ? data : [])
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch failed executions",
      )
    } finally {
      setIsLoading(false)
    }
  }, [showErrorToast])

  useEffect(() => {
    fetchFailedExecutions()
  }, [fetchFailedExecutions])

  const handleRetry = useCallback(
    async (execution: FailedExecution) => {
      try {
        await apiClient.request(`/api/v1/workflows/executions/${execution.id}/replay`, {
          method: "POST",
        })
        showSuccessToast("Execution retried successfully")
        fetchFailedExecutions()
      } catch (error) {
        showErrorToast(
          error instanceof Error ? error.message : "Failed to retry execution",
        )
      }
    },
    [showErrorToast, showSuccessToast, fetchFailedExecutions],
  )

  const columns: ColumnDef<FailedExecution>[] = [
    {
      accessorKey: "execution_id",
      header: "Execution ID",
      cell: ({ row }) => {
        const execution = row.original
        return (
          <div className="font-mono text-xs">
            {execution.execution_id.slice(0, 12)}...
          </div>
        )
      },
    },
    {
      accessorKey: "error_message",
      header: "Error",
      cell: ({ row }) => {
        const error = row.original.error_message
        return (
          <div className="max-w-md truncate text-sm text-destructive">
            {error || "Unknown error"}
          </div>
        )
      },
    },
    {
      accessorKey: "retry_count",
      header: "Retries",
      cell: ({ row }) => {
        const count = row.original.retry_count
        return (
          <Badge variant={count > 0 ? "destructive" : "secondary"}>
            {count}
          </Badge>
        )
      },
    },
    {
      accessorKey: "started_at",
      header: "Failed At",
      cell: ({ row }) => {
        const date = new Date(row.original.completed_at || row.original.started_at)
        return <div>{format(date, "MMM d, yyyy HH:mm:ss")}</div>
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const execution = row.original
        return (
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleRetry(execution)}
          >
            <Play className="h-4 w-4 mr-2" />
            Retry
          </Button>
        )
      },
    },
  ]

  if (isLoading) {
    return <div>Loading retry management...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Retry Management</h2>
        <Button onClick={fetchFailedExecutions} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Failed Executions</CardTitle>
          <CardDescription>
            {failedExecutions.length} failed execution(s) requiring attention
          </CardDescription>
        </CardHeader>
        <CardContent>
          {failedExecutions.length > 0 ? (
            <DataTable columns={columns} data={failedExecutions} />
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No failed executions found
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

