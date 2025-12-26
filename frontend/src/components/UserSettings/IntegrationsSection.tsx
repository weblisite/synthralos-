import { useQuery } from "@tanstack/react-query"
import { formatDistanceToNow } from "date-fns"
import {
  CheckCircle2,
  Database,
  RefreshCw,
  Trash2,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { apiClient } from "@/lib/apiClient"

export function IntegrationsSection() {
  const { data, isLoading } = useQuery({
    queryKey: ["user-connections"],
    queryFn: () => apiClient.connectors.listConnections(),
  })

  const connections = data?.connections || []

  if (isLoading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Integrations</h2>
        <p className="text-muted-foreground">
          Manage your connected accounts and integrations
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Connected Accounts
          </CardTitle>
          <CardDescription>
            OAuth connections to external services via connectors
          </CardDescription>
        </CardHeader>
        <CardContent>
          {connections.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No connected accounts</p>
              <p className="text-sm mt-2">
                Visit{" "}
                <a href="/connectors" className="text-primary underline">
                  Connectors
                </a>{" "}
                to connect your accounts
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Service</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Connected</TableHead>
                  <TableHead>Last Synced</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {connections.map((connection: any) => (
                  <TableRow key={connection.id}>
                    <TableCell className="font-medium">
                      {connection.connector_name ||
                        connection.connector_slug ||
                        "Unknown"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          connection.status === "connected"
                            ? "default"
                            : connection.status === "error"
                              ? "destructive"
                              : "secondary"
                        }
                      >
                        {connection.status === "connected" && (
                          <CheckCircle2 className="mr-1 h-3 w-3" />
                        )}
                        {connection.status === "error" && (
                          <XCircle className="mr-1 h-3 w-3" />
                        )}
                        {connection.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {connection.connected_at
                        ? formatDistanceToNow(
                            new Date(connection.connected_at),
                            {
                              addSuffix: true,
                            },
                          )
                        : "Never"}
                    </TableCell>
                    <TableCell>
                      {connection.last_synced_at
                        ? formatDistanceToNow(
                            new Date(connection.last_synced_at),
                            {
                              addSuffix: true,
                            },
                          )
                        : "Never"}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm">
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
