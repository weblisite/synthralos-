/**
 * Agent Task History Component
 *
 * Displays a list of all agent tasks with status tracking.
 * Integrates unused endpoints:
 * - GET /api/v1/agents/tasks
 * - GET /api/v1/agents/status/{task_id}
 */

import { useQuery } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import {
  AlertCircle,
  Bot,
  CheckCircle2,
  Clock,
  Loader2,
  RefreshCw,
  XCircle,
} from "lucide-react"
import { useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { apiClient } from "@/lib/apiClient"

interface AgentTask {
  id: string
  agent_id: string
  agent_name?: string
  task_type: string
  status: "pending" | "running" | "completed" | "failed" | "cancelled"
  input_data?: Record<string, any>
  output_data?: Record<string, any>
  error_message?: string
  started_at: string
  completed_at?: string
  duration_ms?: number
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case "completed":
      return (
        <Badge variant="default" className="bg-green-500">
          <CheckCircle2 className="h-3 w-3 mr-1" />
          Completed
        </Badge>
      )
    case "running":
      return (
        <Badge variant="default" className="bg-blue-500">
          <Loader2 className="h-3 w-3 mr-1 animate-spin" />
          Running
        </Badge>
      )
    case "failed":
      return (
        <Badge variant="destructive">
          <XCircle className="h-3 w-3 mr-1" />
          Failed
        </Badge>
      )
    case "cancelled":
      return (
        <Badge variant="secondary">
          <XCircle className="h-3 w-3 mr-1" />
          Cancelled
        </Badge>
      )
    default:
      return (
        <Badge variant="outline">
          <Clock className="h-3 w-3 mr-1" />
          Pending
        </Badge>
      )
  }
}

export function AgentTaskHistory() {
  const [selectedTask, setSelectedTask] = useState<AgentTask | null>(null)
  const [isDetailsOpen, setIsDetailsOpen] = useState(false)

  // Fetch all agent tasks
  const {
    data: tasks,
    isLoading,
    error,
    refetch,
  } = useQuery<AgentTask[]>({
    queryKey: ["agentTasks"],
    queryFn: async () => {
      return apiClient.request<AgentTask[]>("/api/v1/agents/tasks")
    },
    refetchInterval: 5000, // Poll every 5 seconds for running tasks
  })

  // Poll task status if a running task is selected
  const { data: taskStatus } = useQuery({
    queryKey: ["agentTaskStatus", selectedTask?.id],
    queryFn: async () => {
      if (!selectedTask) return null
      return apiClient.request<AgentTask>(
        `/api/v1/agents/status/${selectedTask.id}`,
      )
    },
    enabled: !!selectedTask && selectedTask.status === "running",
    refetchInterval: 2000, // Poll every 2 seconds for running tasks
  })

  const handleViewDetails = (task: AgentTask) => {
    setSelectedTask(task)
    setIsDetailsOpen(true)
  }

  const columns: ColumnDef<AgentTask>[] = [
    {
      accessorKey: "id",
      header: "Task ID",
      cell: ({ row }) => (
        <div className="font-mono text-xs">
          {row.original.id.slice(0, 8)}...
        </div>
      ),
    },
    {
      accessorKey: "agent_name",
      header: "Agent",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-muted-foreground" />
          <span>{row.original.agent_name || row.original.agent_id}</span>
        </div>
      ),
    },
    {
      accessorKey: "task_type",
      header: "Type",
      cell: ({ row }) => (
        <Badge variant="outline">{row.original.task_type}</Badge>
      ),
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const task = row.original
        // Use polled status if available and task is running
        const displayStatus =
          task.id === selectedTask?.id && taskStatus
            ? taskStatus.status
            : task.status
        return getStatusBadge(displayStatus)
      },
    },
    {
      accessorKey: "started_at",
      header: "Started",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">
          {format(new Date(row.original.started_at), "MMM d, yyyy HH:mm")}
        </div>
      ),
    },
    {
      accessorKey: "duration_ms",
      header: "Duration",
      cell: ({ row }) => {
        const duration = row.original.duration_ms
        if (!duration)
          return <span className="text-sm text-muted-foreground">-</span>
        if (duration < 1000) return `${duration}ms`
        return `${(duration / 1000).toFixed(2)}s`
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleViewDetails(row.original)}
        >
          View Details
        </Button>
      ),
    },
  ]

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Failed to load agent tasks</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => refetch()}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Agent Task History
              </CardTitle>
              <CardDescription>
                View and monitor all agent task executions
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {tasks && tasks.length > 0 ? (
            <DataTable columns={columns} data={tasks} />
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No agent tasks found</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Task Details Dialog */}
      <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Task Details</DialogTitle>
            <DialogDescription>
              {selectedTask?.id && (
                <span className="font-mono text-xs">{selectedTask.id}</span>
              )}
            </DialogDescription>
          </DialogHeader>
          {selectedTask && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Status
                  </div>
                  <div className="mt-1">
                    {getStatusBadge(taskStatus?.status || selectedTask.status)}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Agent
                  </div>
                  <div className="mt-1">
                    {selectedTask.agent_name || selectedTask.agent_id}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Task Type
                  </div>
                  <div className="mt-1">{selectedTask.task_type}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Duration
                  </div>
                  <div className="mt-1">
                    {selectedTask.duration_ms
                      ? `${(selectedTask.duration_ms / 1000).toFixed(2)}s`
                      : "-"}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">
                    Started
                  </div>
                  <div className="mt-1 text-sm">
                    {format(new Date(selectedTask.started_at), "PPpp")}
                  </div>
                </div>
                {selectedTask.completed_at && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">
                      Completed
                    </div>
                    <div className="mt-1 text-sm">
                      {format(new Date(selectedTask.completed_at), "PPpp")}
                    </div>
                  </div>
                )}
              </div>

              {selectedTask.error_message && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground mb-2">
                    Error Message
                  </div>
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md text-sm">
                    {selectedTask.error_message}
                  </div>
                </div>
              )}

              {selectedTask.input_data && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground mb-2">
                    Input Data
                  </div>
                  <ScrollArea className="h-32 rounded-md border p-4">
                    <pre className="text-xs">
                      {JSON.stringify(selectedTask.input_data, null, 2)}
                    </pre>
                  </ScrollArea>
                </div>
              )}

              {selectedTask.output_data && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground mb-2">
                    Output Data
                  </div>
                  <ScrollArea className="h-48 rounded-md border p-4">
                    <pre className="text-xs">
                      {JSON.stringify(selectedTask.output_data, null, 2)}
                    </pre>
                  </ScrollArea>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
