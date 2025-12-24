/**
 * Connector Statistics Component
 *
 * Displays connector statistics for admin users.
 */

import { useQuery } from "@tanstack/react-query"
import { Database, Package, Users } from "lucide-react"
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { apiClient } from "@/lib/apiClient"

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884d8",
  "#82ca9d",
  "#ffc658",
  "#ff7300",
]

interface ConnectorStats {
  total_connectors: number
  platform_connectors: number
  user_connectors: number
  by_status: Record<string, number>
  by_category: Record<string, number>
}

const fetchConnectorStats = async (): Promise<ConnectorStats> => {
  return apiClient.request<ConnectorStats>("/api/v1/admin/connectors/stats")
}

export function ConnectorStats() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["connectorStats"],
    queryFn: fetchConnectorStats,
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (!stats) {
    return null
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Connectors
            </CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_connectors}</div>
            <p className="text-xs text-muted-foreground">
              All connectors in the platform
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Platform Connectors
            </CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.platform_connectors}
            </div>
            <p className="text-xs text-muted-foreground">
              Available to all users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              User Connectors
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.user_connectors}</div>
            <p className="text-xs text-muted-foreground">Created by users</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>By Status</CardTitle>
            <CardDescription>Connector distribution by status</CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(stats.by_status).length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={Object.entries(stats.by_status).map(
                        ([name, value]) => ({
                          name: name.charAt(0).toUpperCase() + name.slice(1),
                          value,
                        }),
                      )}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name}: ${percent !== undefined ? (percent * 100).toFixed(0) : 0}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.entries(stats.by_status).map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {Object.entries(stats.by_status).map(([status, count]) => (
                    <div
                      key={status}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="capitalize">{status}</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-sm text-muted-foreground text-center py-8">
                No status data available
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>By Category</CardTitle>
            <CardDescription>
              Connector distribution by category
            </CardDescription>
          </CardHeader>
          <CardContent>
            {Object.keys(stats.by_category).length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={Object.entries(stats.by_category).map(
                        ([name, value]) => ({
                          name,
                          value,
                        }),
                      )}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name}: ${percent !== undefined ? (percent * 100).toFixed(0) : 0}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.entries(stats.by_category).map((_, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-2">
                  {Object.entries(stats.by_category).map(
                    ([category, count]) => (
                      <div
                        key={category}
                        className="flex items-center justify-between text-sm"
                      >
                        <span>{category}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ),
                  )}
                </div>
              </>
            ) : (
              <div className="text-sm text-muted-foreground text-center py-8">
                No category data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
