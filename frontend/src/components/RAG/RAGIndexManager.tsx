/**
 * RAG Index Manager Component
 *
 * Manages RAG indexes, documents, and queries.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Database, FileText, Plus, Search, Trash2 } from "lucide-react"
import { useState } from "react"
import { format } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { DataTable } from "@/components/Common/DataTable"
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
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"
import type { ColumnDef } from "@tanstack/react-table"

interface RAGIndex {
  id: string
  name: string
  vector_db_type: string
  created_at: string
}

interface RAGQuery {
  id: string
  index_id: string
  query_text: string
  results: Record<string, any>
  latency_ms: number
  created_at: string
}

const fetchRAGIndexes = async (): Promise<RAGIndex[]> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view RAG indexes")
  }

  const response = await fetch("/api/v1/rag/indexes", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch RAG indexes")
  }

  return response.json()
}

const createRAGIndex = async (name: string, vectorDbType: string): Promise<RAGIndex> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to create RAG indexes")
  }

  const response = await fetch("/api/v1/rag/index", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name,
      vector_db_type: vectorDbType,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to create RAG index")
  }

  return response.json()
}

const queryRAGIndex = async (
  indexId: string,
  queryText: string,
): Promise<RAGQuery> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to query RAG indexes")
  }

  const response = await fetch("/api/v1/rag/query", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      index_id: indexId,
      query_text: queryText,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to query RAG index")
  }

  return response.json()
}

const addDocumentToIndex = async (
  indexId: string,
  content: string,
  metadata: Record<string, any>,
): Promise<void> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to add documents")
  }

  const response = await fetch("/api/v1/rag/document", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      index_id: indexId,
      content,
      document_metadata: metadata,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to add document")
  }
}

const indexColumns: ColumnDef<RAGIndex>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <div className="font-semibold">{row.original.name}</div>
    ),
  },
  {
    accessorKey: "vector_db_type",
    header: "Vector DB",
    cell: ({ row }) => (
      <Badge variant="outline">{row.original.vector_db_type}</Badge>
    ),
  },
  {
    accessorKey: "created_at",
    header: "Created",
    cell: ({ row }) => (
      <span className="text-sm text-muted-foreground">
        {format(new Date(row.original.created_at), "PPP")}
      </span>
    ),
  },
]

export function RAGIndexManager() {
  const queryClient = useQueryClient()
  const { data: indexes, isLoading } = useQuery({
    queryKey: ["ragIndexes"],
    queryFn: fetchRAGIndexes,
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isQueryDialogOpen, setIsQueryDialogOpen] = useState(false)
  const [isAddDocDialogOpen, setIsAddDocDialogOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState<RAGIndex | null>(null)
  const [newIndexName, setNewIndexName] = useState("")
  const [newIndexVectorDb, setNewIndexVectorDb] = useState("chromadb")
  const [queryText, setQueryText] = useState("")
  const [queryResult, setQueryResult] = useState<RAGQuery | null>(null)
  const [documentContent, setDocumentContent] = useState("")
  const [documentMetadata, setDocumentMetadata] = useState("")

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createIndexMutation = useMutation({
    mutationFn: () => createRAGIndex(newIndexName, newIndexVectorDb),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ragIndexes"] })
      showSuccessToast("RAG Index Created", `${newIndexName} created successfully`)
      setIsCreateDialogOpen(false)
      setNewIndexName("")
      setNewIndexVectorDb("chromadb")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create index", error.message)
    },
  })

  const queryMutation = useMutation({
    mutationFn: () => {
      if (!selectedIndex) throw new Error("No index selected")
      return queryRAGIndex(selectedIndex.id, queryText)
    },
    onSuccess: (result) => {
      setQueryResult(result)
      showSuccessToast("Query executed", `Latency: ${result.latency_ms}ms`)
    },
    onError: (error: Error) => {
      showErrorToast("Query failed", error.message)
    },
  })

  const addDocumentMutation = useMutation({
    mutationFn: () => {
      if (!selectedIndex) throw new Error("No index selected")
      let metadata = {}
      if (documentMetadata.trim()) {
        try {
          metadata = JSON.parse(documentMetadata)
        } catch {
          metadata = { note: documentMetadata }
        }
      }
      return addDocumentToIndex(selectedIndex.id, documentContent, metadata)
    },
    onSuccess: () => {
      showSuccessToast("Document added", "Document added to index successfully")
      setIsAddDocDialogOpen(false)
      setDocumentContent("")
      setDocumentMetadata("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to add document", error.message)
    },
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-60 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">RAG Index Manager</h2>
          <p className="text-muted-foreground">
            Manage your RAG indexes, documents, and queries
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Index
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create RAG Index</DialogTitle>
              <DialogDescription>
                Create a new RAG index for document storage and retrieval
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="index-name">Index Name</Label>
                <Input
                  id="index-name"
                  placeholder="e.g., Knowledge Base, Documentation"
                  value={newIndexName}
                  onChange={(e) => setNewIndexName(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="vector-db">Vector Database</Label>
                <Select value={newIndexVectorDb} onValueChange={setNewIndexVectorDb}>
                  <SelectTrigger id="vector-db">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="chromadb">ChromaDB</SelectItem>
                    <SelectItem value="milvus">Milvus</SelectItem>
                    <SelectItem value="weaviate">Weaviate</SelectItem>
                    <SelectItem value="qdrant">Qdrant</SelectItem>
                    <SelectItem value="supavec">SupaVec (pgvector)</SelectItem>
                    <SelectItem value="pinecone">Pinecone</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => createIndexMutation.mutate()}
                disabled={!newIndexName.trim() || createIndexMutation.isPending}
                className="w-full"
              >
                {createIndexMutation.isPending ? "Creating..." : "Create Index"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {indexes && indexes.length > 0 ? (
        <>
          <DataTable columns={indexColumns} data={indexes} />
          
          {selectedIndex && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{selectedIndex.name}</CardTitle>
                    <CardDescription>
                      Vector DB: {selectedIndex.vector_db_type}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Dialog open={isQueryDialogOpen} onOpenChange={setIsQueryDialogOpen}>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <Search className="h-4 w-4 mr-2" />
                          Query
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Query RAG Index</DialogTitle>
                          <DialogDescription>
                            Search for relevant documents in this index
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="query-text">Query</Label>
                            <Textarea
                              id="query-text"
                              placeholder="Enter your search query..."
                              value={queryText}
                              onChange={(e) => setQueryText(e.target.value)}
                              rows={3}
                            />
                          </div>
                          <Button
                            onClick={() => queryMutation.mutate()}
                            disabled={!queryText.trim() || queryMutation.isPending}
                            className="w-full"
                          >
                            {queryMutation.isPending ? "Querying..." : "Execute Query"}
                          </Button>
                          {queryResult && (
                            <div className="space-y-2">
                              <Separator />
                              <div>
                                <Label>Results</Label>
                                <ScrollArea className="h-60 rounded-md border p-4 mt-2">
                                  <pre className="text-xs">
                                    {JSON.stringify(queryResult.results, null, 2)}
                                  </pre>
                                </ScrollArea>
                                <p className="text-xs text-muted-foreground mt-2">
                                  Latency: {queryResult.latency_ms}ms
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>

                    <Dialog open={isAddDocDialogOpen} onOpenChange={setIsAddDocDialogOpen}>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <FileText className="h-4 w-4 mr-2" />
                          Add Document
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Add Document to Index</DialogTitle>
                          <DialogDescription>
                            Add a new document to this RAG index
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="doc-content">Document Content</Label>
                            <Textarea
                              id="doc-content"
                              placeholder="Enter document content..."
                              value={documentContent}
                              onChange={(e) => setDocumentContent(e.target.value)}
                              rows={8}
                            />
                          </div>
                          <div>
                            <Label htmlFor="doc-metadata">Metadata (JSON, optional)</Label>
                            <Textarea
                              id="doc-metadata"
                              placeholder='{"source": "url", "author": "name", ...}'
                              value={documentMetadata}
                              onChange={(e) => setDocumentMetadata(e.target.value)}
                              rows={4}
                              className="font-mono text-sm"
                            />
                          </div>
                          <Button
                            onClick={() => addDocumentMutation.mutate()}
                            disabled={!documentContent.trim() || addDocumentMutation.isPending}
                            className="w-full"
                          >
                            {addDocumentMutation.isPending ? "Adding..." : "Add Document"}
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                </div>
              </CardHeader>
            </Card>
          )}

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {indexes.map((index) => (
              <Card
                key={index.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedIndex(index)}
              >
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    {index.name}
                  </CardTitle>
                  <CardDescription>
                    <Badge variant="outline">{index.vector_db_type}</Badge>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Created {format(new Date(index.created_at), "PPP")}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground mb-4">
                No RAG indexes found. Create your first index to get started.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Index
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

