/**
 * Execution Panel Component
 *
 * Live execution view showing workflow execution status, logs, and node states.
 */

import type { Edge, Node } from "@xyflow/react"
import { Clock, Pause, Play, RefreshCw, Square, X } from "lucide-react"
import { useCallback, useEffect, useRef, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { ExecutionTimeline } from "./ExecutionTimeline"

interface ExecutionLog {
  id: string
  node_id: string
  level: "info" | "error" | "debug" | "warning"
  message: string
  timestamp: string
}

interface ExecutionStatus {
  id: string
  execution_id: string
  workflow_id: string
  status: "running" | "completed" | "failed" | "paused" | "waiting_for_signal"
  started_at: string
  completed_at: string | null
  error_message: string | null
  current_node_id: string | null
  retry_count: number
  next_retry_at: string | null
  execution_state?: {
    completed_node_ids?: string[]
    node_results?: Record<string, any>
    [key: string]: any
  }
}

interface ExecutionPanelProps {
  workflowId: string | null
  executionId: string | null
  nodes: Node[]
  edges: Edge[]
  onExecutionStatusChange?: (status: ExecutionStatus) => void
  onNodeStatusChange?: (nodeId: string, status: string) => void
  onClose?: () => void
}

export function ExecutionPanel({
  executionId,
  nodes,
  onExecutionStatusChange,
  onNodeStatusChange,
  onClose,
}: ExecutionPanelProps) {
  const [executionStatus, setExecutionStatus] =
    useState<ExecutionStatus | null>(null)
  const [logs, setLogs] = useState<ExecutionLog[]>([])
  const [isPolling, setIsPolling] = useState(false)
  const [isReplaying, setIsReplaying] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Use refs to avoid dependency issues
  const nodesRef = useRef<Node[]>(nodes)
  const onNodeStatusChangeRef = useRef(onNodeStatusChange)
  const onExecutionStatusChangeRef = useRef(onExecutionStatusChange)

  // Keep refs in sync
  nodesRef.current = nodes
  onNodeStatusChangeRef.current = onNodeStatusChange
  onExecutionStatusChangeRef.current = onExecutionStatusChange

  const fetchExecutionStatus = useCallback(async () => {
    if (!executionId) return

    try {
      const status = await apiClient.request<ExecutionStatus>(
        `/api/v1/workflows/executions/${executionId}/status`,
      )
      setExecutionStatus(status)
      if (onExecutionStatusChangeRef.current) {
        onExecutionStatusChangeRef.current(status)
      }

      // Update node statuses based on execution state
      // Use refs to prevent infinite loops
      if (status.execution_state && onNodeStatusChangeRef.current) {
        const executionState = status.execution_state
        const statusUpdates: Record<string, string> = {}

        nodesRef.current.forEach((node) => {
          let nodeStatus = "idle"
          if (executionState.current_node_id === node.id) {
            nodeStatus = "running"
          } else if (executionState.completed_node_ids?.includes(node.id)) {
            const nodeResult = executionState.node_results?.[node.id]
            nodeStatus =
              nodeResult?.status === "failed" ? "failed" : "completed"
          }
          statusUpdates[node.id] = nodeStatus
        })

        // Batch status updates to prevent multiple re-renders
        Object.entries(statusUpdates).forEach(([nodeId, nodeStatus]) => {
          onNodeStatusChangeRef.current?.(nodeId, nodeStatus)
        })
      }
    } catch (error) {
      showErrorToast(
        error instanceof Error
          ? error.message
          : "Failed to fetch execution status",
      )
    }
  }, [executionId, showErrorToast])

  const fetchLogs = useCallback(async () => {
    if (!executionId) return

    try {
      const logsData = await apiClient.request<
        ExecutionLog[] | { logs: ExecutionLog[] }
      >(`/api/v1/workflows/executions/${executionId}/logs`)
      // Backend returns array directly, not wrapped in logs property
      setLogs(Array.isArray(logsData) ? logsData : logsData.logs || [])
    } catch (error) {
      console.error("Failed to fetch logs:", error)
    }
  }, [executionId])

  useEffect(() => {
    if (!executionId) {
      setExecutionStatus(null)
      setLogs([])
      setIsPolling(false)
      return
    }

    // Initial fetch
    fetchExecutionStatus()
    fetchLogs()

    // Poll for updates if execution is running
    if (isPolling) {
      const interval = setInterval(() => {
        fetchExecutionStatus()
        fetchLogs()
      }, 2000) // Poll every 2 seconds

      return () => clearInterval(interval)
    }
  }, [
    executionId,
    isPolling, // Initial fetch
    fetchExecutionStatus,
    fetchLogs,
  ]) // Remove fetchExecutionStatus and fetchLogs from deps to prevent loops

  // Auto-start polling if execution is running
  useEffect(() => {
    if (executionStatus?.status === "running") {
      setIsPolling(true)
    } else {
      setIsPolling(false)
    }
  }, [executionStatus?.status])

  const handlePause = useCallback(async () => {
    if (!executionId) return

    try {
      await apiClient.request(
        `/api/v1/workflows/executions/${executionId}/pause`,
        {
          method: "POST",
        },
      )
      showSuccessToast("Execution paused")
      fetchExecutionStatus()
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to pause execution",
      )
    }
  }, [executionId, fetchExecutionStatus, showErrorToast, showSuccessToast])

  const handleResume = useCallback(async () => {
    if (!executionId) return

    try {
      await apiClient.request(
        `/api/v1/workflows/executions/${executionId}/resume`,
        {
          method: "POST",
        },
      )
      showSuccessToast("Execution resumed")
      fetchExecutionStatus()
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to resume execution",
      )
    }
  }, [executionId, fetchExecutionStatus, showErrorToast, showSuccessToast])

  const handleTerminate = useCallback(async () => {
    if (!executionId) return

    try {
      await apiClient.request(
        `/api/v1/workflows/executions/${executionId}/terminate`,
        {
          method: "POST",
        },
      )
      showSuccessToast("Execution terminated")
      fetchExecutionStatus()
    } catch (error) {
      showErrorToast(
        error instanceof Error
          ? error.message
          : "Failed to terminate execution",
      )
    }
  }, [executionId, fetchExecutionStatus, showErrorToast, showSuccessToast])

  const handleReplay = useCallback(async () => {
    if (!executionId) return

    setIsReplaying(true)
    try {
      await apiClient.request(
        `/api/v1/workflows/executions/${executionId}/replay`,
        {
          method: "POST",
          body: JSON.stringify({}),
        },
      )
      showSuccessToast("Execution replay started")
      fetchExecutionStatus()
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to replay execution",
      )
    } finally {
      setIsReplaying(false)
    }
  }, [executionId, fetchExecutionStatus, showErrorToast, showSuccessToast])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "running":
        return "bg-blue-500"
      case "completed":
        return "bg-green-500"
      case "failed":
        return "bg-red-500"
      case "paused":
        return "bg-yellow-500"
      case "waiting_for_signal":
        return "bg-purple-500"
      default:
        return "bg-gray-500"
    }
  }

  const getLogLevelColor = (level: string) => {
    switch (level) {
      case "error":
        return "text-red-600"
      case "warning":
        return "text-yellow-600"
      case "debug":
        return "text-gray-600"
      default:
        return "text-gray-800"
    }
  }

  if (!executionId || !executionStatus) {
    return (
      <div className="h-full bg-background flex flex-col">
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="text-lg font-semibold">Execution</h2>
          {onClose && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        <div className="flex-1 flex items-center justify-center p-4">
          <p className="text-sm text-muted-foreground text-center">
            No execution selected
            <br />
            Run a workflow to see execution details
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-background flex flex-col">
      <div className="p-4 border-b space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Execution</h2>
          {onClose && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div
              className={`h-2 w-2 rounded-full ${getStatusColor(executionStatus.status)}`}
            />
            <Badge variant="outline">{executionStatus.status}</Badge>
            {executionStatus.retry_count > 0 && (
              <Badge variant="secondary">
                Retry {executionStatus.retry_count}
              </Badge>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            <div>
              Started:{" "}
              {new Date(executionStatus.started_at).toLocaleTimeString()}
            </div>
            {executionStatus.completed_at && (
              <div>
                Completed:{" "}
                {new Date(executionStatus.completed_at).toLocaleTimeString()}
              </div>
            )}
            {executionStatus.current_node_id && (
              <div>Current Node: {executionStatus.current_node_id}</div>
            )}
          </div>
        </div>

        <div className="flex gap-2 flex-wrap">
          {executionStatus.status === "running" && (
            <Button variant="outline" size="sm" onClick={handlePause}>
              <Pause className="h-3 w-3 mr-1" />
              Pause
            </Button>
          )}
          {executionStatus.status === "paused" && (
            <Button variant="outline" size="sm" onClick={handleResume}>
              <Play className="h-3 w-3 mr-1" />
              Resume
            </Button>
          )}
          {(executionStatus.status === "running" ||
            executionStatus.status === "paused") && (
            <Button variant="outline" size="sm" onClick={handleTerminate}>
              <Square className="h-3 w-3 mr-1" />
              Terminate
            </Button>
          )}
          {executionStatus.status === "failed" && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleReplay}
              disabled={isReplaying}
            >
              <RefreshCw
                className={`h-3 w-3 mr-1 ${isReplaying ? "animate-spin" : ""}`}
              />
              Replay
            </Button>
          )}
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Clock className="h-3 w-3 mr-1" />
                Timeline
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Execution Timeline</DialogTitle>
                <DialogDescription>
                  Complete timeline of execution events
                </DialogDescription>
              </DialogHeader>
              {executionId && <ExecutionTimeline executionId={executionId} />}
            </DialogContent>
          </Dialog>
        </div>

        {executionStatus.error_message && (
          <div className="p-2 bg-red-50 border border-red-200 rounded text-xs text-red-800">
            {executionStatus.error_message}
          </div>
        )}
      </div>

      <Tabs
        defaultValue="logs"
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="mx-4 mt-2">
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
        </TabsList>

        <TabsContent value="logs" className="flex-1 overflow-hidden m-0">
          <ScrollArea className="h-full p-4">
            <div className="space-y-1">
              {logs.length === 0 ? (
                <p className="text-sm text-muted-foreground">No logs yet</p>
              ) : (
                logs.map((log) => (
                  <div
                    key={log.id}
                    className="text-xs font-mono p-2 rounded bg-muted/50 border"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`font-semibold ${getLogLevelColor(log.level)}`}
                      >
                        {log.level.toUpperCase()}
                      </span>
                      <span className="text-muted-foreground">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="text-muted-foreground">
                        [{log.node_id}]
                      </span>
                    </div>
                    <div className="text-gray-800">{log.message}</div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="timeline" className="flex-1 overflow-hidden m-0">
          <ScrollArea className="h-full p-4">
            {executionId ? (
              <ExecutionTimeline executionId={executionId} />
            ) : (
              <p className="text-sm text-muted-foreground">
                No execution selected
              </p>
            )}
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
  )
}
