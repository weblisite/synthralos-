/**
 * Analytics Panel Component
 *
 * Displays workflow execution analytics:
 * - Execution statistics
 * - Performance metrics
 * - Usage trends
 * - Cost estimates
 */

import { useQuery } from "@tanstack/react-query"
import { BarChart3, DollarSign } from "lucide-react"
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiRequest } from "@/lib/api"

interface AnalyticsPanelProps {
  workflowId?: string
  days?: number
}

interface ExecutionStats {
  total_executions: number
  completed: number
  failed: number
  running: number
  success_rate: number
  failure_rate: number
  avg_duration_seconds: number
}

interface PerformanceMetrics extends ExecutionStats {
  throughput_per_hour: number
  period_days: number
}

interface UsageTrend {
  date: string
  total_executions: number
  completed: number
  failed: number
  success_rate: number
}

interface CostEstimate {
  total_executions: number
  avg_duration_seconds: number
  estimated_cost_usd: number
  period_days: number
}

export function AnalyticsPanel({ workflowId, days = 30 }: AnalyticsPanelProps) {
  const { data: stats, isLoading: statsLoading } = useQuery<ExecutionStats>({
    queryKey: ["workflowStats", workflowId, days],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (workflowId) params.append("workflow_id", workflowId)
      if (days) params.append("days", days.toString())
      return apiRequest<ExecutionStats>(
        `/api/v1/workflows/analytics/stats?${params}`,
      )
    },
  })

  const { data: performance, isLoading: perfLoading } =
    useQuery<PerformanceMetrics>({
      queryKey: ["workflowPerformance", workflowId, days],
      queryFn: async () => {
        const params = new URLSearchParams()
        if (workflowId) params.append("workflow_id", workflowId)
        params.append("days", days.toString())
        return apiRequest<PerformanceMetrics>(
          `/api/v1/workflows/analytics/performance?${params}`,
        )
      },
    })

  const { data: trends, isLoading: trendsLoading } = useQuery<{
    trends: UsageTrend[]
  }>({
    queryKey: ["workflowTrends", workflowId, days],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (workflowId) params.append("workflow_id", workflowId)
      params.append("days", days.toString())
      return apiRequest<{ trends: UsageTrend[] }>(
        `/api/v1/workflows/analytics/trends?${params}`,
      )
    },
  })

  const { data: cost, isLoading: costLoading } = useQuery<CostEstimate>({
    queryKey: ["workflowCost", workflowId, days],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (workflowId) params.append("workflow_id", workflowId)
      params.append("days", days.toString())
      return apiRequest<CostEstimate>(
        `/api/v1/workflows/analytics/cost?${params}`,
      )
    },
  })

  if (statsLoading || perfLoading || trendsLoading || costLoading) {
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Workflow Analytics
        </CardTitle>
        <CardDescription>
          {workflowId ? `Analytics for workflow` : "Overall analytics"} ({days}{" "}
          days)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="stats">
          <TabsList>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="cost">Cost</TabsTrigger>
          </TabsList>

          <TabsContent value="stats" className="space-y-4">
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Total Executions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {stats.total_executions}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Success Rate</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {(stats.success_rate * 100).toFixed(1)}%
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Failed</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-destructive">
                      {stats.failed}
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-2">
                    <CardDescription>Avg Duration</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {stats.avg_duration_seconds.toFixed(1)}s
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="performance" className="space-y-4">
            {performance && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">Throughput</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {performance.throughput_per_hour.toFixed(2)}
                      </div>
                      <p className="text-xs text-muted-foreground">
                        executions/hour
                      </p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm">
                        Average Duration
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold">
                        {performance.avg_duration_seconds.toFixed(1)}s
                      </div>
                    </CardContent>
                  </Card>
                </div>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">
                      Performance Metrics
                    </CardTitle>
                    <CardDescription>
                      Visual breakdown of execution performance
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart
                        data={[
                          {
                            name: "Completed",
                            value: performance.completed,
                            fill: "#82ca9d",
                          },
                          {
                            name: "Failed",
                            value: performance.failed,
                            fill: "#ff7300",
                          },
                          {
                            name: "Running",
                            value: performance.running,
                            fill: "#8884d8",
                          },
                        ]}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Area
                          type="monotone"
                          dataKey="value"
                          stroke="#8884d8"
                          fill="#8884d8"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          <TabsContent value="trends" className="space-y-4">
            {trends && trends.trends.length > 0 && (
              <div className="space-y-4">
                <div className="text-sm text-muted-foreground">
                  Usage trends over {days} days
                </div>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Execution Trends</CardTitle>
                    <CardDescription>
                      Total, completed, and failed executions over time
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={trends.trends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="date"
                          tick={{ fontSize: 12 }}
                          angle={-45}
                          textAnchor="end"
                          height={80}
                        />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip
                          labelStyle={{ color: "#000" }}
                          contentStyle={{ backgroundColor: "#fff" }}
                        />
                        <Legend />
                        <Area
                          type="monotone"
                          dataKey="total_executions"
                          stackId="1"
                          stroke="#8884d8"
                          fill="#8884d8"
                          name="Total Executions"
                        />
                        <Area
                          type="monotone"
                          dataKey="completed"
                          stackId="1"
                          stroke="#82ca9d"
                          fill="#82ca9d"
                          name="Completed"
                        />
                        <Area
                          type="monotone"
                          dataKey="failed"
                          stackId="1"
                          stroke="#ff7300"
                          fill="#ff7300"
                          name="Failed"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">
                      Success Rate Trend
                    </CardTitle>
                    <CardDescription>
                      Success rate percentage over time
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <LineChart data={trends.trends}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="date"
                          tick={{ fontSize: 12 }}
                          angle={-45}
                          textAnchor="end"
                          height={80}
                        />
                        <YAxis
                          tick={{ fontSize: 12 }}
                          domain={[0, 100]}
                          label={{
                            value: "Success Rate (%)",
                            angle: -90,
                            position: "insideLeft",
                          }}
                        />
                        <Tooltip
                          formatter={(value: number) => `${value.toFixed(1)}%`}
                          labelStyle={{ color: "#000" }}
                          contentStyle={{ backgroundColor: "#fff" }}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="success_rate"
                          stroke="#8884d8"
                          strokeWidth={2}
                          dot={{ r: 4 }}
                          name="Success Rate (%)"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            )}
            {trends && trends.trends.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No trend data available for the selected period
              </div>
            )}
          </TabsContent>

          <TabsContent value="cost" className="space-y-4">
            {cost && (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="h-5 w-5" />
                      Cost Estimate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">
                      ${cost.estimated_cost_usd.toFixed(4)}
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">
                      Based on {cost.total_executions} executions over{" "}
                      {cost.period_days} days
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Average duration: {cost.avg_duration_seconds.toFixed(1)}s
                      per execution
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
