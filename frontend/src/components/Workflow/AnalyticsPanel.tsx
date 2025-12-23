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
import { Badge } from "@/components/ui/badge"
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
              </div>
            )}
          </TabsContent>

          <TabsContent value="trends" className="space-y-4">
            {trends && trends.trends.length > 0 && (
              <div className="space-y-4">
                <div className="text-sm text-muted-foreground">
                  Usage trends over {days} days
                </div>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2">
                    {trends.trends.map((trend, idx) => (
                      <Card key={idx}>
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium">{trend.date}</div>
                              <div className="text-sm text-muted-foreground">
                                {trend.total_executions} executions
                              </div>
                            </div>
                            <div className="text-right">
                              <Badge variant="default">
                                {trend.completed} completed
                              </Badge>
                              {trend.failed > 0 && (
                                <Badge variant="destructive" className="ml-2">
                                  {trend.failed} failed
                                </Badge>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </ScrollArea>
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
