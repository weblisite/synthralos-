/**
 * Cost Analytics Component
 *
 * Displays cost analytics dashboard with charts and metrics.
 */

import { Wifi, WifiOff } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Alert, AlertDescription } from "@/components/ui/alert"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { useDashboardWebSocket } from "@/hooks/useDashboardWebSocket"
import { apiClient } from "@/lib/apiClient"

interface CostMetrics {
  total_cost: number
  total_executions: number
  avg_cost_per_execution: number
  cost_by_service: {
    service: string
    cost: number
    executions: number
    models?: {
      [model: string]: {
        cost: number
        tokens_input: number
        tokens_output: number
      }
    }
  }[]
  cost_trend: {
    date: string
    cost: number
    executions: number
  }[]
  date_from?: string
  date_to?: string
}

export function CostAnalytics() {
  const [metrics, setMetrics] = useState<CostMetrics | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { showErrorToast } = useCustomToast()
  const { isConnected, usePollingFallback } = useDashboardWebSocket()

  const fetchCostMetrics = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await apiClient.request<CostMetrics>(
        "/api/v1/admin/analytics/costs",
      )
      setMetrics({
        total_cost: data.total_cost || 0,
        total_executions: data.total_executions || 0,
        avg_cost_per_execution: data.avg_cost_per_execution || 0,
        cost_by_service: data.cost_by_service || [],
        cost_trend: data.cost_trend || [],
      })
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to fetch cost metrics",
      )
    } finally {
      setIsLoading(false)
    }
  }, [showErrorToast])

  useEffect(() => {
    fetchCostMetrics()
  }, [fetchCostMetrics])

  // Refetch when WebSocket triggers update
  useEffect(() => {
    if (isConnected && !usePollingFallback) {
      // WebSocket will trigger React Query invalidation, which will refetch
      // This effect is just for initial load
    }
  }, [isConnected, usePollingFallback])

  if (isLoading) {
    return <div>Loading cost analytics...</div>
  }

  if (!metrics) {
    return <div>No cost data available</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Cost Analytics</h2>
        {usePollingFallback && (
          <Alert className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950 max-w-md">
            <WifiOff className="h-4 w-4 text-yellow-600" />
            <AlertDescription className="text-yellow-800 dark:text-yellow-200 text-sm">
              Using polling fallback
            </AlertDescription>
          </Alert>
        )}
        {isConnected && !usePollingFallback && (
          <Alert className="border-green-500 bg-green-50 dark:bg-green-950 max-w-md">
            <Wifi className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800 dark:text-green-200 text-sm">
              Real-time updates active
            </AlertDescription>
          </Alert>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total Cost</CardTitle>
            <CardDescription>All time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${metrics.total_cost.toFixed(2)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Executions</CardTitle>
            <CardDescription>All time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {metrics.total_executions.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Avg Cost/Execution</CardTitle>
            <CardDescription>Per execution</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${metrics.avg_cost_per_execution.toFixed(4)}
            </div>
          </CardContent>
        </Card>
      </div>

      {metrics.cost_by_service.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Cost by Service</CardTitle>
              <CardDescription>Breakdown by service type</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={metrics.cost_by_service}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="service"
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    formatter={(value: number) => `$${value.toFixed(2)}`}
                    labelStyle={{ color: "#000" }}
                    contentStyle={{ backgroundColor: "#fff" }}
                  />
                  <Legend />
                  <Bar dataKey="cost" fill="#8884d8" name="Cost ($)" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cost Distribution</CardTitle>
              <CardDescription>Percentage breakdown by service</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={metrics.cost_by_service.map((service) => ({
                      name: service.service,
                      value: service.cost,
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {metrics.cost_by_service.map((_, index) => {
                      const colors = [
                        "#0088FE",
                        "#00C49F",
                        "#FFBB28",
                        "#FF8042",
                        "#8884d8",
                        "#82ca9d",
                      ]
                      return (
                        <Cell
                          key={`cell-${index}`}
                          fill={colors[index % colors.length]}
                        />
                      )
                    })}
                  </Pie>
                  <Tooltip
                    formatter={(value: number) => `$${value.toFixed(2)}`}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Cost by Model (if available) */}
          {metrics.cost_by_service.some(
            (service) =>
              service.models && Object.keys(service.models).length > 0,
          ) && (
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Cost by Model</CardTitle>
                <CardDescription>Breakdown by AI model</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {metrics.cost_by_service
                    .filter(
                      (service) =>
                        service.models &&
                        Object.keys(service.models).length > 0,
                    )
                    .map((service) => {
                      const modelData = Object.entries(
                        service.models || {},
                      ).map(([model, data]) => ({
                        model,
                        cost: data.cost,
                        tokens_input: data.tokens_input,
                        tokens_output: data.tokens_output,
                      }))
                      return (
                        <div key={service.service} className="space-y-2">
                          <h4 className="font-semibold">{service.service}</h4>
                          <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={modelData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis
                                dataKey="model"
                                tick={{ fontSize: 10 }}
                                angle={-45}
                                textAnchor="end"
                                height={80}
                              />
                              <YAxis tick={{ fontSize: 10 }} />
                              <Tooltip
                                formatter={(value: number) =>
                                  `$${value.toFixed(4)}`
                                }
                                labelStyle={{ color: "#000" }}
                                contentStyle={{ backgroundColor: "#fff" }}
                              />
                              <Legend />
                              <Bar
                                dataKey="cost"
                                fill="#82ca9d"
                                name="Cost ($)"
                              />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      )
                    })}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Cost Trend</CardTitle>
          <CardDescription>Cost over time</CardDescription>
        </CardHeader>
        <CardContent>
          {metrics.cost_trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={metrics.cost_trend}>
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
                  formatter={(value: number | undefined) =>
                    value !== undefined ? `$${value.toFixed(2)}` : "$0.00"
                  }
                  labelStyle={{ color: "#000" }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="cost"
                  stroke="#8884d8"
                  strokeWidth={2}
                  name="Cost ($)"
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="executions"
                  stroke="#82ca9d"
                  strokeWidth={2}
                  name="Executions"
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-sm text-muted-foreground text-center py-8">
              No cost trend data available
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
