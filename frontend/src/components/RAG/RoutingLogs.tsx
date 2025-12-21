/**
 * Routing Logs Component
 *
 * Displays routing decision logs for RAG queries.
 * Integrates unused endpoint:
 * - GET /api/v1/rag/switch/logs
 */

import { useQuery } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import { AlertCircle, Database, RefreshCw, Route } from "lucide-react"
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import { apiClient } from "@/lib/apiClient"

interface RoutingLog {
  id: string
  query_id: string
  query_text: string
  selected_index_id: string
  selected_index_name?: string
  routing_decision: string
  confidence_score?: number
  alternatives?: Array<{
    index_id: string
    index_name?: string
    score: number
  }>
  created_at: string
}

export function RoutingLogs() {
  const [limit, setLimit] = useState(50)

  const {
    data: logs,
    isLoading,
    error,
    refetch,
  } = useQuery<RoutingLog[]>({
    queryKey: ["ragRoutingLogs", limit],
    queryFn: async () => {
      return apiClient.request<RoutingLog[]>(
        `/api/v1/rag/switch/logs?limit=${limit}`,
      )
    },
  })

  const columns: ColumnDef<RoutingLog>[] = [
    {
      accessorKey: "query_text",
      header: "Query",
      cell: ({ row }) => (
        <div className="max-w-md truncate" title={row.original.query_text}>
          {row.original.query_text}
        </div>
      ),
    },
    {
      accessorKey: "selected_index_name",
      header: "Selected Index",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-muted-foreground" />
          <span>
            {row.original.selected_index_name || row.original.selected_index_id}
          </span>
        </div>
      ),
    },
    {
      accessorKey: "routing_decision",
      header: "Decision",
      cell: ({ row }) => (
        <Badge variant="outline">{row.original.routing_decision}</Badge>
      ),
    },
    {
      accessorKey: "confidence_score",
      header: "Confidence",
      cell: ({ row }) => {
        const score = row.original.confidence_score
        if (score === undefined || score === null)
          return <span className="text-muted-foreground">-</span>
        const percentage = (score * 100).toFixed(1)
        return (
          <div className="flex items-center gap-2">
            <div className="w-16 bg-muted rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full"
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="text-sm">{percentage}%</span>
          </div>
        )
      },
    },
    {
      accessorKey: "created_at",
      header: "Timestamp",
      cell: ({ row }) => (
        <div className="text-sm text-muted-foreground">
          {format(new Date(row.original.created_at), "MMM d, yyyy HH:mm:ss")}
        </div>
      ),
    },
    {
      id: "alternatives",
      header: "Alternatives",
      cell: ({ row }) => {
        const alternatives = row.original.alternatives
        if (!alternatives || alternatives.length === 0) {
          return <span className="text-muted-foreground text-sm">-</span>
        }
        return (
          <Badge variant="secondary" className="text-xs">
            {alternatives.length} other{alternatives.length !== 1 ? "s" : ""}
          </Badge>
        )
      },
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
            <p>Failed to load routing logs</p>
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
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Route className="h-5 w-5" />
              Routing Logs
            </CardTitle>
            <CardDescription>
              View routing decisions made for RAG queries
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select
              value={limit.toString()}
              onValueChange={(v) => setLimit(Number(v))}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="25">25 logs</SelectItem>
                <SelectItem value="50">50 logs</SelectItem>
                <SelectItem value="100">100 logs</SelectItem>
                <SelectItem value="200">200 logs</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {logs && logs.length > 0 ? (
          <DataTable columns={columns} data={logs} />
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Route className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No routing logs found</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
