/**
 * Tool Details Component
 *
 * Displays detailed information about a code tool.
 * Integrates unused endpoints:
 * - GET /api/v1/code/tools/{tool_id}
 * - GET /api/v1/code/tools/{tool_id}/versions
 * - POST /api/v1/code/tools/{tool_id}/deprecate
 */

import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import {
  AlertTriangle,
  Calendar,
  Code2,
  FileText,
  Loader2,
  Package,
  RefreshCw,
  Tag,
  Trash2,
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
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface ToolVersion {
  version: string
  created_at: string
  description?: string
}

interface CodeTool {
  id: string
  name: string
  description: string
  language: string
  version: string
  author?: string
  repository_url?: string
  documentation_url?: string
  is_deprecated: boolean
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}

interface ToolDetailsProps {
  toolId: string
  onClose?: () => void
}

export function ToolDetails({ toolId, onClose }: ToolDetailsProps) {
  const [isDeprecating, setIsDeprecating] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  // Fetch tool details
  const {
    data: tool,
    isLoading,
    error,
    refetch,
  } = useQuery<CodeTool>({
    queryKey: ["codeTool", toolId],
    queryFn: async () => {
      return apiClient.request<CodeTool>(`/api/v1/code/tools/${toolId}`)
    },
  })

  // Fetch tool versions
  const { data: versions, isLoading: isLoadingVersions } = useQuery<
    ToolVersion[]
  >({
    queryKey: ["codeToolVersions", toolId],
    queryFn: async () => {
      return apiClient.request<ToolVersion[]>(
        `/api/v1/code/tools/${toolId}/versions`,
      )
    },
    enabled: !!toolId,
  })

  const handleDeprecate = async () => {
    if (
      !confirm(
        `Are you sure you want to deprecate "${tool?.name}"? This will mark it as deprecated but won't delete it.`,
      )
    ) {
      return
    }

    setIsDeprecating(true)
    try {
      await apiClient.request(`/api/v1/code/tools/${toolId}/deprecate`, {
        method: "POST",
      })
      showSuccessToast("Tool deprecated successfully")
      refetch()
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to deprecate tool",
      )
    } finally {
      setIsDeprecating(false)
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !tool) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8 text-muted-foreground">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Failed to load tool details</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => refetch()}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Code2 className="h-5 w-5" />
                {tool.name}
                {tool.is_deprecated && (
                  <Badge variant="destructive">Deprecated</Badge>
                )}
              </CardTitle>
              <CardDescription>{tool.description}</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {!tool.is_deprecated && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeprecate}
                  disabled={isDeprecating}
                >
                  {isDeprecating ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Trash2 className="h-4 w-4 mr-2" />
                  )}
                  Deprecate
                </Button>
              )}
              {onClose && (
                <Button variant="ghost" size="sm" onClick={onClose}>
                  Close
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Language
              </div>
              <div className="mt-1">
                <Badge variant="secondary">{tool.language}</Badge>
              </div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Version
              </div>
              <div className="mt-1">
                <Badge variant="outline">{tool.version}</Badge>
              </div>
            </div>
            {tool.author && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Author
                </div>
                <div className="mt-1">{tool.author}</div>
              </div>
            )}
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Created
              </div>
              <div className="mt-1 text-sm">
                {format(new Date(tool.created_at), "MMM d, yyyy")}
              </div>
            </div>
          </div>

          {tool.repository_url && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Repository
              </div>
              <Button variant="outline" size="sm" asChild>
                <a
                  href={tool.repository_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Package className="h-4 w-4 mr-2" />
                  View Repository
                </a>
              </Button>
            </div>
          )}

          {tool.documentation_url && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Documentation
              </div>
              <Button variant="outline" size="sm" asChild>
                <a
                  href={tool.documentation_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  View Documentation
                </a>
              </Button>
            </div>
          )}

          {tool.metadata && Object.keys(tool.metadata).length > 0 && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Metadata
              </div>
              <ScrollArea className="h-32 rounded-md border p-4">
                <pre className="text-xs">
                  {JSON.stringify(tool.metadata, null, 2)}
                </pre>
              </ScrollArea>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Versions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Tag className="h-5 w-5" />
            Versions
          </CardTitle>
          <CardDescription>Version history for this tool</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingVersions ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : versions && versions.length > 0 ? (
            <div className="space-y-2">
              {versions.map((version, index) => (
                <div
                  key={version.version}
                  className="flex items-center justify-between p-3 border rounded-md"
                >
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{version.version}</Badge>
                    {index === 0 && <Badge variant="default">Latest</Badge>}
                    {version.description && (
                      <span className="text-sm text-muted-foreground">
                        {version.description}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    {format(new Date(version.created_at), "MMM d, yyyy")}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Tag className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No version history available</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
