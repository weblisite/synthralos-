/**
 * Dashboard Statistics Component
 *
 * Displays comprehensive platform statistics and metrics.
 */

import { useQuery } from "@tanstack/react-query"
import {
  Activity,
  Bot,
  Code,
  Database,
  FileText,
  Globe,
  Plug,
  Workflow,
  Zap,
} from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { supabase } from "@/lib/supabase"

interface DashboardStats {
  workflows: {
    total: number
    active: number
    inactive: number
  }
  executions: {
    total_30d: number
    completed_30d: number
    failed_30d: number
    running: number
    success_rate: number
  }
  agents: {
    total_30d: number
    completed_30d: number
    failed_30d: number
    running: number
    success_rate: number
  }
  connectors: {
    total: number
    active: number
  }
  rag: {
    indexes: number
    queries_30d: number
  }
  ocr: {
    total_30d: number
    completed_30d: number
    failed_30d: number
    success_rate: number
  }
  scraping: {
    total_30d: number
    completed_30d: number
    failed_30d: number
    success_rate: number
  }
  browser: {
    sessions_30d: number
  }
  osint: {
    streams: number
  }
  code: {
    total_30d: number
    completed_30d: number
    failed_30d: number
    success_rate: number
  }
  recent_activity: Array<{
    type: string
    id: string
    title: string
    status: string
    timestamp: string
  }>
}

const fetchDashboardStats = async (): Promise<DashboardStats> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view dashboard stats")
  }

  const response = await fetch("/api/v1/stats/dashboard", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch dashboard stats")
  }

  return response.json()
}

const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
}: {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ComponentType<{ className?: string }>
  trend?: "up" | "down" | "neutral"
}) => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  )
}

const ActivityItem = ({
  activity,
}: {
  activity: DashboardStats["recent_activity"][0]
}) => {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case "workflow_execution":
        return <Workflow className="h-4 w-4" />
      case "agent_task":
        return <Bot className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500"
      case "failed":
        return "bg-red-500"
      case "running":
        return "bg-blue-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="flex items-center gap-3 py-2 border-b last:border-0">
      <div className="flex-shrink-0">{getActivityIcon(activity.type)}</div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{activity.title}</p>
        <p className="text-xs text-muted-foreground">
          {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
        </p>
      </div>
      <Badge className={getStatusColor(activity.status)}>{activity.status}</Badge>
    </div>
  )
}

export function DashboardStats() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ["dashboardStats"],
    queryFn: fetchDashboardStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error || !stats) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            Failed to load dashboard statistics. Please try again later.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Statistics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Workflows"
          value={stats.workflows.total}
          subtitle={`${stats.workflows.active} active`}
          icon={Workflow}
        />
        <StatCard
          title="Executions (30d)"
          value={stats.executions.total_30d}
          subtitle={`${stats.executions.success_rate.toFixed(1)}% success rate`}
          icon={Zap}
        />
        <StatCard
          title="Agent Tasks (30d)"
          value={stats.agents.total_30d}
          subtitle={`${stats.agents.success_rate.toFixed(1)}% success rate`}
          icon={Bot}
        />
        <StatCard
          title="Connectors"
          value={stats.connectors.total}
          subtitle={`${stats.connectors.active} active`}
          icon={Plug}
        />
        <StatCard
          title="RAG Indexes"
          value={stats.rag.indexes}
          subtitle={`${stats.rag.queries_30d} queries (30d)`}
          icon={Database}
        />
        <StatCard
          title="OCR Jobs (30d)"
          value={stats.ocr.total_30d}
          subtitle={`${stats.ocr.success_rate.toFixed(1)}% success rate`}
          icon={FileText}
        />
        <StatCard
          title="Scraping Jobs (30d)"
          value={stats.scraping.total_30d}
          subtitle={`${stats.scraping.success_rate.toFixed(1)}% success rate`}
          icon={Globe}
        />
        <StatCard
          title="Code Executions (30d)"
          value={stats.code.total_30d}
          subtitle={`${stats.code.success_rate.toFixed(1)}% success rate`}
          icon={Code}
        />
      </div>

      {/* Detailed Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Workflow Executions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Workflow Executions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Completed</span>
              <span className="font-semibold">{stats.executions.completed_30d}</span>
            </div>
            <Progress value={stats.executions.success_rate} className="h-2" />
            <div className="flex justify-between text-sm">
              <span>Failed</span>
              <span className="font-semibold text-red-500">
                {stats.executions.failed_30d}
              </span>
            </div>
            {stats.executions.running > 0 && (
              <div className="flex justify-between text-sm">
                <span>Running</span>
                <Badge variant="secondary">{stats.executions.running}</Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Agent Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="h-5 w-5" />
              Agent Tasks
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Completed</span>
              <span className="font-semibold">{stats.agents.completed_30d}</span>
            </div>
            <Progress value={stats.agents.success_rate} className="h-2" />
            <div className="flex justify-between text-sm">
              <span>Failed</span>
              <span className="font-semibold text-red-500">
                {stats.agents.failed_30d}
              </span>
            </div>
            {stats.agents.running > 0 && (
              <div className="flex justify-between text-sm">
                <span>Running</span>
                <Badge variant="secondary">{stats.agents.running}</Badge>
              </div>
            )}
          </CardContent>
        </Card>

        {/* System Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Activity className="h-5 w-5" />
              System Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Browser Sessions (30d)</span>
              <span className="font-semibold">{stats.browser.sessions_30d}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>OSINT Streams</span>
              <span className="font-semibold">{stats.osint.streams}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>RAG Queries (30d)</span>
              <span className="font-semibold">{stats.rag.queries_30d}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[300px]">
            {stats.recent_activity.length > 0 ? (
              <div className="space-y-1">
                {stats.recent_activity.map((activity) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-8">
                No recent activity
              </p>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}

