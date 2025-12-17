/**
 * Cost Analytics Component
 *
 * Displays cost analytics dashboard with charts and metrics.
 */

import { useCallback, useEffect, useState } from "react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

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

  const fetchCostMetrics = useCallback(async () => {
    setIsLoading(true)
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        showErrorToast("You must be logged in to view cost analytics")
        return
      }

      // Fetch cost analytics from backend
      const response = await fetch(`/api/v1/admin/analytics/costs`, {
        headers: {
          Authorization: `Bearer ${session.access_token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch cost analytics")
      }

      const data = await response.json()
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

  if (isLoading) {
    return <div>Loading cost analytics...</div>
  }

  if (!metrics) {
    return <div>No cost data available</div>
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Cost Analytics</h2>
      
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
        <Card>
          <CardHeader>
            <CardTitle>Cost by Service</CardTitle>
            <CardDescription>Breakdown by service type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {metrics.cost_by_service.map((service) => (
                <div
                  key={service.service}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{service.service}</Badge>
                    <span className="text-sm text-muted-foreground">
                      {service.executions} executions
                    </span>
                  </div>
                  <div className="font-semibold">${service.cost.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
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
                  formatter={(value: number | undefined) => value !== undefined ? `$${value.toFixed(2)}` : "$0.00"}
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

