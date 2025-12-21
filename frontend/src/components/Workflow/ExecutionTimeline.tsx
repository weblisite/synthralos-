/**
 * Execution Timeline Component
 *
 * Displays a visual timeline of workflow execution events.
 * Integrates unused endpoint:
 * - GET /api/v1/workflows/executions/{execution_id}/timeline
 */

import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Loader2,
  RefreshCw,
  XCircle,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface TimelineEvent {
  timestamp: string
  event_type: string
  node_id?: string
  node_name?: string
  status?: string
  message?: string
  duration_ms?: number
  metadata?: Record<string, any>
}

interface ExecutionTimeline {
  execution_id: string
  workflow_id: string
  workflow_name?: string
  status: string
  started_at: string
  completed_at?: string
  total_duration_ms?: number
  events: TimelineEvent[]
}

interface ExecutionTimelineProps {
  executionId: string
  onClose?: () => void
}

const getEventIcon = (_eventType: string, status?: string) => {
  if (status === "completed" || status === "success") {
    return <CheckCircle2 className="h-4 w-4 text-green-500" />
  }
  if (status === "failed" || status === "error") {
    return <XCircle className="h-4 w-4 text-red-500" />
  }
  if (status === "running" || status === "in_progress") {
    return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
  }
  return <Clock className="h-4 w-4 text-muted-foreground" />
}

const getEventBadge = (eventType: string) => {
  const badgeVariants: Record<
    string,
    "default" | "secondary" | "destructive" | "outline"
  > = {
    workflow_started: "default",
    workflow_completed: "default",
    workflow_failed: "destructive",
    node_started: "secondary",
    node_completed: "default",
    node_failed: "destructive",
    node_skipped: "outline",
  }
  return badgeVariants[eventType] || "outline"
}

export function ExecutionTimeline({
  executionId,
  onClose,
}: ExecutionTimelineProps) {
  const { showErrorToast } = useCustomToast()

  const {
    data: timeline,
    isLoading,
    error,
    refetch,
  } = useQuery<ExecutionTimeline>({
    queryKey: ["workflowExecutionTimeline", executionId],
    queryFn: async () => {
      return apiClient.request<ExecutionTimeline>(
        `/api/v1/workflows/executions/${executionId}/timeline`,
      )
    },
    refetchInterval: (data) => {
      // Poll if execution is still running
      if (data?.status === "running" || data?.status === "pending") {
        return 2000 // Poll every 2 seconds
      }
      return false
    },
  })

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !timeline) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Failed to load execution timeline</p>
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
                <Clock className="h-5 w-5" />
                Execution Timeline
              </CardTitle>
              <CardDescription>
                {timeline.workflow_name && (
                  <>Workflow: {timeline.workflow_name} | </>
                )}
                Execution ID:{" "}
                <span className="font-mono text-xs">
                  {executionId.slice(0, 8)}...
                </span>
              </CardDescription>
            </div>
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                Close
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-muted rounded-md">
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Status
              </div>
              <div className="mt-1">
                <Badge
                  variant={
                    timeline.status === "completed"
                      ? "default"
                      : timeline.status === "failed"
                        ? "destructive"
                        : "secondary"
                  }
                >
                  {timeline.status}
                </Badge>
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Started
              </div>
              <div className="mt-1 text-sm">
                {format(new Date(timeline.started_at), "PPpp")}
              </div>
            </div>
            {timeline.completed_at && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Duration
                </div>
                <div className="mt-1 text-sm">
                  {timeline.total_duration_ms
                    ? timeline.total_duration_ms < 1000
                      ? `${timeline.total_duration_ms}ms`
                      : `${(timeline.total_duration_ms / 1000).toFixed(2)}s`
                    : "-"}
                </div>
              </div>
            )}
          </div>

          {/* Timeline Events */}
          <div>
            <div className="text-sm font-medium text-muted-foreground mb-4">
              Events ({timeline.events?.length || 0})
            </div>
            {timeline.events && timeline.events.length > 0 ? (
              <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

                <div className="space-y-4">
                  {timeline.events.map((event, index) => (
                    <div
                      key={index}
                      className="relative flex items-start gap-4"
                    >
                      {/* Icon */}
                      <div className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-background border-2 border-border">
                        {getEventIcon(event.event_type, event.status)}
                      </div>

                      {/* Content */}
                      <div className="flex-1 space-y-1 pb-4">
                        <div className="flex items-center gap-2">
                          <Badge variant={getEventBadge(event.event_type)}>
                            {event.event_type.replace(/_/g, " ")}
                          </Badge>
                          {event.node_name && (
                            <span className="text-sm font-medium">
                              {event.node_name}
                            </span>
                          )}
                          {event.duration_ms && (
                            <span className="text-xs text-muted-foreground">
                              ({event.duration_ms}ms)
                            </span>
                          )}
                        </div>
                        {event.message && (
                          <p className="text-sm text-muted-foreground">
                            {event.message}
                          </p>
                        )}
                        <div className="text-xs text-muted-foreground">
                          {format(new Date(event.timestamp), "PPpp")}
                        </div>
                        {event.metadata &&
                          Object.keys(event.metadata).length > 0 && (
                            <details className="mt-2">
                              <summary className="cursor-pointer text-xs text-muted-foreground">
                                Metadata
                              </summary>
                              <ScrollArea className="h-24 rounded-md border p-2 mt-2">
                                <pre className="text-xs">
                                  {JSON.stringify(event.metadata, null, 2)}
                                </pre>
                              </ScrollArea>
                            </details>
                          )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No timeline events found</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
