/**
 * System Metrics Component
 *
 * Displays platform-wide statistics and metrics.
 */

import { useQuery } from "@tanstack/react-query"
import {
  Activity,
  Database,
  Globe,
  Monitor,
  Search,
  Server,
  Users,
  Workflow,
} from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
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

interface SystemMetrics {
  users: {
    total: number
    active: number
    admins: number
    regular: number
  }
  workflows: {
    total: number
    active: number
    inactive: number
  }
  executions: {
    total: number
    last_24h: number
    completed: number
    failed: number
    running: number
    success_rate: number
  }
  resources: {
    rag_indexes: number
    connectors: number
    ocr_jobs: number
    scrape_jobs: number
    browser_sessions: number
    osint_streams: number
    code_tools: number
  }
  timestamp: string
}

async function fetchSystemMetrics(): Promise<SystemMetrics> {
  return apiClient.request<SystemMetrics>("/api/v1/admin/system/metrics")
}

export function SystemMetrics() {
  const { showErrorToast } = useCustomToast()

  const {
    data: metrics,
    isLoading,
    error,
  } = useQuery<SystemMetrics>({
    queryKey: ["systemMetrics"],
    queryFn: fetchSystemMetrics,
    refetchInterval: 60000, // Refresh every minute
  })

  if (error) {
    showErrorToast(
      "Failed to load system metrics",
      error instanceof Error ? error.message : "Unknown error",
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    )
  }

  if (error || !metrics) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Failed to load system metrics</p>
      </div>
    )
  }

  const statCards = [
    {
      title: "Total Users",
      value: metrics.users.total,
      description: `${metrics.users.active} active, ${metrics.users.admins} admins`,
      icon: Users,
      color: "text-blue-500",
    },
    {
      title: "Workflows",
      value: metrics.workflows.total,
      description: `${metrics.workflows.active} active`,
      icon: Workflow,
      color: "text-purple-500",
    },
    {
      title: "Total Executions",
      value: metrics.executions.total,
      description: `${metrics.executions.last_24h} in last 24h`,
      icon: Activity,
      color: "text-green-500",
    },
    {
      title: "Success Rate",
      value: `${metrics.executions.success_rate}%`,
      description: `${metrics.executions.completed} completed, ${metrics.executions.failed} failed`,
      icon: Server,
      color: "text-orange-500",
    },
    {
      title: "Connectors",
      value: metrics.resources.connectors,
      description: "Available integrations",
      icon: Globe,
      color: "text-indigo-500",
    },
    {
      title: "RAG Indexes",
      value: metrics.resources.rag_indexes,
      description: "Knowledge bases",
      icon: Database,
      color: "text-cyan-500",
    },
    {
      title: "Browser Sessions",
      value: metrics.resources.browser_sessions,
      description: "Active sessions",
      icon: Monitor,
      color: "text-pink-500",
    },
    {
      title: "OSINT Streams",
      value: metrics.resources.osint_streams,
      description: "Active streams",
      icon: Search,
      color: "text-red-500",
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Platform Metrics</h2>
        <p className="text-muted-foreground">
          Real-time statistics and usage metrics
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Execution Statistics</CardTitle>
            <CardDescription>Workflow execution breakdown</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Total</span>
              <span className="font-medium">{metrics.executions.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Completed</span>
              <span className="font-medium text-green-600">
                {metrics.executions.completed}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Failed</span>
              <span className="font-medium text-red-600">
                {metrics.executions.failed}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Running</span>
              <span className="font-medium text-blue-600">
                {metrics.executions.running}
              </span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span className="text-sm font-medium">Success Rate</span>
              <span className="font-bold">
                {metrics.executions.success_rate}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resource Usage</CardTitle>
            <CardDescription>Platform resource statistics</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={[
                  {
                    name: "RAG Indexes",
                    value: metrics.resources.rag_indexes,
                  },
                  {
                    name: "Connectors",
                    value: metrics.resources.connectors,
                  },
                  {
                    name: "OCR Jobs",
                    value: metrics.resources.ocr_jobs,
                  },
                  {
                    name: "Scrape Jobs",
                    value: metrics.resources.scrape_jobs,
                  },
                  {
                    name: "Browser Sessions",
                    value: metrics.resources.browser_sessions,
                  },
                  {
                    name: "OSINT Streams",
                    value: metrics.resources.osint_streams,
                  },
                  {
                    name: "Code Tools",
                    value: metrics.resources.code_tools,
                  },
                ]}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#8884d8" name="Count" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">OCR Jobs</span>
                <span className="font-medium">
                  {metrics?.resources?.ocr_jobs ?? 0}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Scrape Jobs</span>
                <span className="font-medium">
                  {metrics?.resources?.scrape_jobs ?? 0}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Code Tools</span>
                <span className="font-medium">
                  {metrics?.resources?.code_tools ?? 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="text-xs text-muted-foreground text-center">
        Last updated:{" "}
        {metrics?.timestamp
          ? new Date(metrics.timestamp).toLocaleString()
          : "Never"}
      </div>
    </div>
  )
}
