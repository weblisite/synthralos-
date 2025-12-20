/**
 * Admin Dashboard Component
 *
 * Main admin dashboard with execution history, retry management, and cost analytics.
 */

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ActivityLogs } from "./ActivityLogs"
import { CostAnalytics } from "./CostAnalytics"
import { ExecutionHistory } from "./ExecutionHistory"
import { RetryManagement } from "./RetryManagement"
import { SystemHealth } from "./SystemHealth"
import { SystemMetrics } from "./SystemMetrics"

export function AdminDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-muted-foreground">
          Manage executions, retries, monitor costs, and configure platform
          settings
        </p>
      </div>

      <Tabs defaultValue="executions" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="executions">Executions</TabsTrigger>
          <TabsTrigger value="retries">Retries</TabsTrigger>
          <TabsTrigger value="costs">Costs</TabsTrigger>
          <TabsTrigger value="health">Health</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="executions" className="space-y-4">
          <ExecutionHistory />
        </TabsContent>

        <TabsContent value="retries" className="space-y-4">
          <RetryManagement />
        </TabsContent>

        <TabsContent value="costs" className="space-y-4">
          <CostAnalytics />
        </TabsContent>

        <TabsContent value="health" className="space-y-4">
          <SystemHealth />
        </TabsContent>

        <TabsContent value="metrics" className="space-y-4">
          <SystemMetrics />
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <ActivityLogs />
        </TabsContent>
      </Tabs>
    </div>
  )
}
