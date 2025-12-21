/**
 * Connector Details Component
 *
 * Displays detailed information about a connector including actions, triggers, and versions.
 * Integrates unused endpoints:
 * - GET /api/v1/connectors/{slug}/actions
 * - GET /api/v1/connectors/{slug}/triggers
 * - GET /api/v1/connectors/{slug}/versions
 * - POST /api/v1/connectors/{slug}/rotate
 */

import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import {
  AlertCircle,
  Code2,
  Loader2,
  Plug,
  RotateCcw,
  Tag,
  Zap,
} from "lucide-react"
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
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface ConnectorAction {
  name: string
  description?: string
  parameters?: Record<string, any>
  returns?: Record<string, any>
}

interface ConnectorTrigger {
  name: string
  description?: string
  parameters?: Record<string, any>
  event_types?: string[]
}

interface ConnectorVersion {
  id: string
  version: string
  created_at: string
  is_active: boolean
  manifest?: Record<string, any>
}

interface ConnectorDetailsProps {
  connectorSlug: string
  connectorName?: string
  onClose?: () => void
}

export function ConnectorDetails({
  connectorSlug,
  connectorName,
  onClose,
}: ConnectorDetailsProps) {
  const [isRotating, setIsRotating] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Fetch connector actions
  const {
    data: actions,
    isLoading: isLoadingActions,
    error: actionsError,
  } = useQuery<{ actions: ConnectorAction[] }>({
    queryKey: ["connectorActions", connectorSlug],
    queryFn: async () => {
      return apiClient.request<{ actions: ConnectorAction[] }>(
        `/api/v1/connectors/${connectorSlug}/actions`,
      )
    },
  })

  // Fetch connector triggers
  const {
    data: triggers,
    isLoading: isLoadingTriggers,
    error: triggersError,
  } = useQuery<{ triggers: ConnectorTrigger[] }>({
    queryKey: ["connectorTriggers", connectorSlug],
    queryFn: async () => {
      return apiClient.request<{ triggers: ConnectorTrigger[] }>(
        `/api/v1/connectors/${connectorSlug}/triggers`,
      )
    },
  })

  // Fetch connector versions
  const {
    data: versions,
    isLoading: isLoadingVersions,
    error: versionsError,
  } = useQuery<{ versions: ConnectorVersion[] }>({
    queryKey: ["connectorVersions", connectorSlug],
    queryFn: async () => {
      return apiClient.request<{ versions: ConnectorVersion[] }>(
        `/api/v1/connectors/${connectorSlug}/versions`,
      )
    },
  })

  const handleRotateCredentials = async () => {
    if (
      !confirm(
        "Are you sure you want to rotate credentials? This will refresh OAuth tokens or rotate API keys.",
      )
    ) {
      return
    }

    setIsRotating(true)
    try {
      await apiClient.request(`/api/v1/connectors/${connectorSlug}/rotate`, {
        method: "POST",
      })
      showSuccessToast("Credentials rotated successfully")
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to rotate credentials",
      )
    } finally {
      setIsRotating(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Plug className="h-5 w-5" />
                {connectorName || connectorSlug}
              </CardTitle>
              <CardDescription>
                Connector Slug:{" "}
                <span className="font-mono text-xs">{connectorSlug}</span>
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRotateCredentials}
                disabled={isRotating}
              >
                {isRotating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Rotating...
                  </>
                ) : (
                  <>
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Rotate Credentials
                  </>
                )}
              </Button>
              {onClose && (
                <Button variant="ghost" size="sm" onClick={onClose}>
                  Close
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      <Tabs defaultValue="actions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="actions">
            Actions
            {actions?.actions && (
              <Badge variant="secondary" className="ml-2">
                {actions.actions.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="triggers">
            Triggers
            {triggers?.triggers && (
              <Badge variant="secondary" className="ml-2">
                {triggers.triggers.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="versions">
            Versions
            {versions?.versions && (
              <Badge variant="secondary" className="ml-2">
                {versions.versions.length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        {/* Actions Tab */}
        <TabsContent value="actions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Actions
              </CardTitle>
              <CardDescription>
                Available actions for this connector
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingActions ? (
                <div className="space-y-2">
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-20 w-full" />
                </div>
              ) : actionsError ? (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Failed to load actions</p>
                </div>
              ) : actions?.actions && actions.actions.length > 0 ? (
                <div className="space-y-4">
                  {actions.actions.map((action, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="text-lg">{action.name}</CardTitle>
                        {action.description && (
                          <CardDescription>
                            {action.description}
                          </CardDescription>
                        )}
                      </CardHeader>
                      {action.parameters &&
                        Object.keys(action.parameters).length > 0 && (
                          <CardContent>
                            <div className="space-y-2">
                              <div className="text-sm font-medium">
                                Parameters
                              </div>
                              <ScrollArea className="h-32 rounded-md border p-4">
                                <pre className="text-xs">
                                  {JSON.stringify(action.parameters, null, 2)}
                                </pre>
                              </ScrollArea>
                            </div>
                          </CardContent>
                        )}
                      {action.returns &&
                        Object.keys(action.returns).length > 0 && (
                          <CardContent>
                            <div className="space-y-2">
                              <div className="text-sm font-medium">Returns</div>
                              <ScrollArea className="h-32 rounded-md border p-4">
                                <pre className="text-xs">
                                  {JSON.stringify(action.returns, null, 2)}
                                </pre>
                              </ScrollArea>
                            </div>
                          </CardContent>
                        )}
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Zap className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No actions available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Triggers Tab */}
        <TabsContent value="triggers">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code2 className="h-5 w-5" />
                Triggers
              </CardTitle>
              <CardDescription>
                Available triggers for this connector
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingTriggers ? (
                <div className="space-y-2">
                  <Skeleton className="h-20 w-full" />
                  <Skeleton className="h-20 w-full" />
                </div>
              ) : triggersError ? (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Failed to load triggers</p>
                </div>
              ) : triggers?.triggers && triggers.triggers.length > 0 ? (
                <div className="space-y-4">
                  {triggers.triggers.map((trigger, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="text-lg">
                          {trigger.name}
                        </CardTitle>
                        {trigger.description && (
                          <CardDescription>
                            {trigger.description}
                          </CardDescription>
                        )}
                      </CardHeader>
                      {trigger.event_types &&
                        trigger.event_types.length > 0 && (
                          <CardContent>
                            <div className="space-y-2">
                              <div className="text-sm font-medium">
                                Event Types
                              </div>
                              <div className="flex flex-wrap gap-2">
                                {trigger.event_types.map((eventType) => (
                                  <Badge key={eventType} variant="outline">
                                    {eventType}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          </CardContent>
                        )}
                      {trigger.parameters &&
                        Object.keys(trigger.parameters).length > 0 && (
                          <CardContent>
                            <div className="space-y-2">
                              <div className="text-sm font-medium">
                                Parameters
                              </div>
                              <ScrollArea className="h-32 rounded-md border p-4">
                                <pre className="text-xs">
                                  {JSON.stringify(trigger.parameters, null, 2)}
                                </pre>
                              </ScrollArea>
                            </div>
                          </CardContent>
                        )}
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Code2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No triggers available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Versions Tab */}
        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Tag className="h-5 w-5" />
                Versions
              </CardTitle>
              <CardDescription>
                Version history for this connector
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingVersions ? (
                <div className="space-y-2">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              ) : versionsError ? (
                <div className="text-center py-8 text-muted-foreground">
                  <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>Failed to load versions</p>
                </div>
              ) : versions?.versions && versions.versions.length > 0 ? (
                <div className="space-y-2">
                  {versions.versions.map((version) => (
                    <div
                      key={version.id}
                      className="flex items-center justify-between p-3 border rounded-md"
                    >
                      <div className="flex items-center gap-3">
                        <Badge
                          variant={version.is_active ? "default" : "outline"}
                        >
                          {version.version}
                        </Badge>
                        {version.is_active && (
                          <Badge variant="secondary">Active</Badge>
                        )}
                        <span className="text-sm text-muted-foreground">
                          {format(new Date(version.created_at), "MMM d, yyyy")}
                        </span>
                      </div>
                      {version.manifest && (
                        <details className="text-xs">
                          <summary className="cursor-pointer text-muted-foreground">
                            View Manifest
                          </summary>
                          <ScrollArea className="h-32 rounded-md border p-2 mt-2">
                            <pre className="text-xs">
                              {JSON.stringify(version.manifest, null, 2)}
                            </pre>
                          </ScrollArea>
                        </details>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Tag className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No versions found</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
