/**
 * Query Details Component
 *
 * Displays detailed information about a RAG query.
 * Integrates unused endpoint:
 * - GET /api/v1/rag/query/{query_id}
 */

import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import {
  AlertCircle,
  Database,
  FileText,
  RefreshCw,
  Search,
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
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { apiClient } from "@/lib/apiClient"

interface RAGQueryDetails {
  id: string
  index_id: string
  index_name?: string
  query_text: string
  response_text?: string
  retrieved_documents?: Array<{
    document_id: string
    content: string
    score: number
    metadata?: Record<string, any>
  }>
  metadata?: Record<string, any>
  created_at: string
  completed_at?: string
  duration_ms?: number
}

interface QueryDetailsProps {
  queryId: string
  onClose?: () => void
}

export function QueryDetails({ queryId, onClose }: QueryDetailsProps) {
  const {
    data: query,
    isLoading,
    error,
    refetch,
  } = useQuery<RAGQueryDetails>({
    queryKey: ["ragQuery", queryId],
    queryFn: async () => {
      return apiClient.request<RAGQueryDetails>(`/api/v1/rag/query/${queryId}`)
    },
  })

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

  if (error || !query) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Failed to load query details</p>
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
                <Search className="h-5 w-5" />
                Query Details
              </CardTitle>
              <CardDescription>
                Query ID: <span className="font-mono text-xs">{query.id}</span>
              </CardDescription>
            </div>
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                Close
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Index
              </div>
              <div className="mt-1 flex items-center gap-2">
                <Database className="h-4 w-4 text-muted-foreground" />
                <span>{query.index_name || query.index_id}</span>
              </div>
            </div>
            {query.duration_ms && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Duration
                </div>
                <div className="mt-1">
                  {query.duration_ms < 1000
                    ? `${query.duration_ms}ms`
                    : `${(query.duration_ms / 1000).toFixed(2)}s`}
                </div>
              </div>
            )}
            <div>
              <div className="text-sm font-medium text-muted-foreground">
                Created
              </div>
              <div className="mt-1 text-sm">
                {format(new Date(query.created_at), "PPpp")}
              </div>
            </div>
            {query.completed_at && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">
                  Completed
                </div>
                <div className="mt-1 text-sm">
                  {format(new Date(query.completed_at), "PPpp")}
                </div>
              </div>
            )}
          </div>

          <div>
            <div className="text-sm font-medium text-muted-foreground mb-2">
              Query Text
            </div>
            <div className="p-3 bg-muted rounded-md">
              <p className="text-sm">{query.query_text}</p>
            </div>
          </div>

          {query.response_text && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Response
              </div>
              <ScrollArea className="h-48 rounded-md border p-4">
                <p className="text-sm whitespace-pre-wrap">
                  {query.response_text}
                </p>
              </ScrollArea>
            </div>
          )}

          {query.retrieved_documents &&
            query.retrieved_documents.length > 0 && (
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-2">
                  Retrieved Documents ({query.retrieved_documents.length})
                </div>
                <div className="space-y-2">
                  {query.retrieved_documents.map((doc, index) => (
                    <Card key={doc.document_id || index}>
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm font-medium">
                              Document {index + 1}
                            </span>
                          </div>
                          <Badge variant="outline">
                            Score: {(doc.score * 100).toFixed(1)}%
                          </Badge>
                        </div>
                        <ScrollArea className="h-24 rounded-md border p-2 mt-2">
                          <p className="text-xs">{doc.content}</p>
                        </ScrollArea>
                        {doc.metadata &&
                          Object.keys(doc.metadata).length > 0 && (
                            <div className="mt-2">
                              <details className="text-xs">
                                <summary className="cursor-pointer text-muted-foreground">
                                  Metadata
                                </summary>
                                <pre className="mt-2 p-2 bg-muted rounded">
                                  {JSON.stringify(doc.metadata, null, 2)}
                                </pre>
                              </details>
                            </div>
                          )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

          {query.metadata && Object.keys(query.metadata).length > 0 && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Query Metadata
              </div>
              <ScrollArea className="h-32 rounded-md border p-4">
                <pre className="text-xs">
                  {JSON.stringify(query.metadata, null, 2)}
                </pre>
              </ScrollArea>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
