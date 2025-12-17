/**
 * Execution History Component
 *
 * Displays a table of workflow executions with filtering, sorting, and actions.
 */

import { type ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import { Play, RefreshCw } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DataTable } from "@/components/Common/DataTable"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

interface Execution {
  id: string
  execution_id: string
  workflow_id: string
  status: "running" | "completed" | "failed" | "paused" | "waiting_for_signal"
  started_at: string
  completed_at: string | null
  error_message: string | null
  retry_count: number
  duration_ms?: number
}

interface ExecutionHistoryProps {
  workflowId?: string
  limit?: number
}

export function ExecutionHistory({ workflowId, limit = 100 }: ExecutionHistoryProps) {
  const [executions, setExecutions] = useState<Execution[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { user, isAuthenticated, isLoading: isUserLoading } = useAuth()

  const fetchExecutions = useCallback(async () => {
    // Wait for authentication to be ready - check both session and user
    if (!isAuthenticated || isUserLoading) {
      setIsLoading(false)
      return
    }

    // Double-check that user exists before making API call
    if (!user) {
      console.warn("[ExecutionHistory] User not available, skipping fetch")
      setIsLoading(false)
      return
    }

    setIsLoading(true)
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session || !session.access_token) {
        console.warn("[ExecutionHistory] No session or access token available")
        setIsLoading(false)
        return
      }

      // Ensure limit is a valid integer and convert to number
      const validLimit = Math.max(1, Math.min(1000, Number(limit) || 100))
      
      // Build URL with proper query parameters
      const baseUrl = workflowId
        ? `/api/v1/workflows/by-workflow/${workflowId}/executions`
        : `/api/v1/workflows/executions`
      
      // Use URLSearchParams for proper encoding
      const params = new URLSearchParams({
        limit: String(validLimit),
        skip: '0'
      })
      
      const url = `${baseUrl}?${params.toString()}`
      
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
          "Content-Type": "application/json",
        },
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        // Handle backend validation errors (array format)
        let errorMessage = `Failed to fetch executions: ${response.status}`
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map((err: any) => 
            `${err.loc?.join('.') || 'field'}: ${err.msg || 'validation error'}`
          ).join(', ')
        } else if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail)
        }
        console.error("[ExecutionHistory] API error:", {
          status: response.status,
          statusText: response.statusText,
          error: errorData,
          errorMessage,
          fullError: JSON.stringify(errorData, null, 2),
        })
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setExecutions(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error("Failed to fetch executions:", error)
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch executions",
      )
      setExecutions([])
    } finally {
      setIsLoading(false)
    }
  }, [workflowId, limit, showErrorToast, isAuthenticated, isUserLoading, user])

  useEffect(() => {
    // Only fetch when authenticated and user data is loaded
    if (!isUserLoading && isAuthenticated) {
      fetchExecutions()
    } else if (!isUserLoading && !isAuthenticated) {
      setIsLoading(false)
    }
  }, [fetchExecutions, isAuthenticated, isUserLoading])

  const handleReplay = useCallback(
    async (execution: Execution) => {
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession()

        if (!session) {
          showErrorToast("You must be logged in to replay executions")
          return
        }

        const response = await fetch(
          `/api/v1/workflows/executions/${execution.id}/replay`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          },
        )

        if (!response.ok) {
          throw new Error("Failed to replay execution")
        }

        showSuccessToast("Execution replayed successfully")
        fetchExecutions()
      } catch (error) {
        showErrorToast(
          error instanceof Error ? error.message : "Failed to replay execution",
        )
      }
    },
    [showErrorToast, showSuccessToast, fetchExecutions],
  )

  const getStatusBadge = (status: Execution["status"]) => {
    const variants: Record<string, "default" | "destructive" | "secondary"> = {
      completed: "default",
      failed: "destructive",
      running: "secondary",
      paused: "secondary",
      waiting_for_signal: "secondary",
    }

    return (
      <Badge variant={variants[status] || "secondary"}>{status}</Badge>
    )
  }

  const formatDuration = (ms: number | undefined) => {
    if (!ms) return "N/A"
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
    return `${(ms / 60000).toFixed(1)}m`
  }

  const columns: ColumnDef<Execution>[] = [
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
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => getStatusBadge(row.original.status),
    },
    {
      accessorKey: "started_at",
      header: "Started",
      cell: ({ row }) => {
        const date = new Date(row.original.started_at)
        return <div>{format(date, "MMM d, yyyy HH:mm:ss")}</div>
      },
    },
    {
      accessorKey: "completed_at",
      header: "Completed",
      cell: ({ row }) => {
        const completed = row.original.completed_at
        if (!completed) return <div className="text-muted-foreground">-</div>
        const date = new Date(completed)
        return <div>{format(date, "MMM d, yyyy HH:mm:ss")}</div>
      },
    },
    {
      accessorKey: "duration",
      header: "Duration",
      cell: ({ row }) => {
        const execution = row.original
        if (execution.duration_ms) {
          return <div>{formatDuration(execution.duration_ms)}</div>
        }
        if (execution.completed_at && execution.started_at) {
          const duration =
            new Date(execution.completed_at).getTime() -
            new Date(execution.started_at).getTime()
          return <div>{formatDuration(duration)}</div>
        }
        return <div className="text-muted-foreground">-</div>
      },
    },
    {
      accessorKey: "retry_count",
      header: "Retries",
      cell: ({ row }) => {
        const count = row.original.retry_count
        return (
          <div className={count > 0 ? "text-orange-600" : ""}>{count}</div>
        )
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const execution = row.original
        return (
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleReplay(execution)}
              disabled={execution.status === "running"}
            >
              <Play className="h-4 w-4" />
            </Button>
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    // View execution details
                    console.log("View execution:", execution)
                  }}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Execution Details</DialogTitle>
                  <DialogDescription>
                    Execution ID: {execution.execution_id}
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <strong>Status:</strong> {getStatusBadge(execution.status)}
                  </div>
                  <div>
                    <strong>Started:</strong>{" "}
                    {format(new Date(execution.started_at), "PPpp")}
                  </div>
                  {execution.completed_at && (
                    <div>
                      <strong>Completed:</strong>{" "}
                      {format(new Date(execution.completed_at), "PPpp")}
                    </div>
                  )}
                  {execution.error_message && (
                    <div>
                      <strong>Error:</strong>{" "}
                      <div className="text-destructive">
                        {execution.error_message}
                      </div>
                    </div>
                  )}
                  <div>
                    <strong>Retry Count:</strong> {execution.retry_count}
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        )
      },
    },
  ]

  if (isLoading) {
    return <div>Loading executions...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Execution History</h2>
        <Button onClick={fetchExecutions} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>
      <DataTable columns={columns} data={executions} />
    </div>
  )
}

