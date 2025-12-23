/**
 * Webhook Manager Component
 *
 * Manages webhook subscriptions for workflows:
 * - List webhook subscriptions
 * - Create new webhook subscriptions
 * - Delete webhook subscriptions
 * - Test webhook endpoints
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Copy, ExternalLink, Plus, Trash2, Webhook } from "lucide-react"
import { useState } from "react"
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { apiRequest, getApiUrl } from "@/lib/api"

interface WebhookSubscription {
  id: string
  workflow_id: string
  webhook_path: string
  webhook_url: string
  method: string
  headers?: Record<string, string>
  is_active: boolean
  created_at: string
  last_triggered_at?: string
  trigger_count: number
}

interface WebhookManagerProps {
  workflowId: string | null
}

export function WebhookManager({ workflowId }: WebhookManagerProps) {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [webhookPath, setWebhookPath] = useState("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: subscriptions, isLoading } = useQuery<WebhookSubscription[]>({
    queryKey: ["webhookSubscriptions", workflowId],
    queryFn: async () => {
      if (!workflowId) return []
      const data = await apiRequest<{ subscriptions: WebhookSubscription[] }>(
        `/api/v1/workflows/${workflowId}/webhooks/subscriptions`,
      )
      return data.subscriptions || []
    },
    enabled: !!workflowId,
  })

  const createSubscription = useMutation({
    mutationFn: async (path: string) => {
      if (!workflowId) throw new Error("Workflow ID is required")
      return apiRequest<WebhookSubscription>(
        `/api/v1/workflows/${workflowId}/webhooks/subscriptions`,
        {
          method: "POST",
          body: JSON.stringify({
            webhook_path: path,
          }),
        },
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["webhookSubscriptions", workflowId],
      })
      setIsCreateDialogOpen(false)
      setWebhookPath("")
      showSuccessToast(
        "Your webhook is now active",
        "Webhook subscription created",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        error.message || "Failed to create webhook",
        "Failed to create webhook",
      )
    },
  })

  const deleteSubscription = useMutation({
    mutationFn: async (subscriptionId: string) => {
      if (!workflowId) throw new Error("Workflow ID is required")
      return apiRequest(
        `/api/v1/workflows/${workflowId}/webhooks/subscriptions/${subscriptionId}`,
        {
          method: "DELETE",
        },
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["webhookSubscriptions", workflowId],
      })
      showSuccessToast(
        "The webhook has been removed",
        "Webhook subscription deleted",
      )
    },
    onError: (error: any) => {
      showErrorToast(
        error.message || "Failed to delete webhook",
        "Failed to delete webhook",
      )
    },
  })

  const copyWebhookUrl = (url: string) => {
    navigator.clipboard.writeText(url)
    showSuccessToast("Webhook URL copied", "Copied to clipboard")
  }

  const getWebhookUrl = (subscription: WebhookSubscription) => {
    const apiUrl = getApiUrl()
    return `${apiUrl}/api/v1/workflows/webhooks/${subscription.webhook_path}`
  }

  if (!workflowId) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            Save your workflow to manage webhooks
          </p>
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
              <Webhook className="h-5 w-5" />
              Webhook Subscriptions
            </CardTitle>
            <CardDescription>
              Manage webhook endpoints that trigger this workflow
            </CardDescription>
          </div>
          <Dialog
            open={isCreateDialogOpen}
            onOpenChange={setIsCreateDialogOpen}
          >
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Webhook
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Webhook Subscription</DialogTitle>
                <DialogDescription>
                  Create a webhook endpoint that will trigger this workflow
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="webhook-path">Webhook Path</Label>
                  <Input
                    id="webhook-path"
                    value={webhookPath}
                    onChange={(e) => setWebhookPath(e.target.value)}
                    placeholder="my-webhook-endpoint"
                    pattern="[a-z0-9-_]+"
                  />
                  <p className="text-xs text-muted-foreground">
                    Use lowercase letters, numbers, hyphens, and underscores
                    only
                  </p>
                </div>
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setIsCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={() => {
                      if (webhookPath.trim()) {
                        createSubscription.mutate(webhookPath.trim())
                      }
                    }}
                    disabled={
                      !webhookPath.trim() || createSubscription.isPending
                    }
                  >
                    {createSubscription.isPending ? "Creating..." : "Create"}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : subscriptions && subscriptions.length > 0 ? (
          <ScrollArea className="h-[400px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Path</TableHead>
                  <TableHead>URL</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Triggers</TableHead>
                  <TableHead>Last Triggered</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {subscriptions.map((subscription) => {
                  const webhookUrl = getWebhookUrl(subscription)
                  return (
                    <TableRow key={subscription.id}>
                      <TableCell>
                        <code className="text-sm bg-muted px-2 py-1 rounded">
                          {subscription.webhook_path}
                        </code>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <code className="text-xs bg-muted px-2 py-1 rounded truncate max-w-[300px]">
                            {webhookUrl}
                          </code>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => copyWebhookUrl(webhookUrl)}
                            title="Copy URL"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={() => window.open(webhookUrl, "_blank")}
                            title="Open in new tab"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            subscription.is_active ? "default" : "secondary"
                          }
                        >
                          {subscription.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell>{subscription.trigger_count || 0}</TableCell>
                      <TableCell>
                        {subscription.last_triggered_at
                          ? new Date(
                              subscription.last_triggered_at,
                            ).toLocaleString()
                          : "Never"}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => {
                            if (
                              confirm(
                                "Are you sure you want to delete this webhook?",
                              )
                            ) {
                              deleteSubscription.mutate(subscription.id)
                            }
                          }}
                          disabled={deleteSubscription.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </ScrollArea>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Webhook className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No webhook subscriptions yet</p>
            <p className="text-sm mt-2">
              Create a webhook to trigger this workflow via HTTP POST requests
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
