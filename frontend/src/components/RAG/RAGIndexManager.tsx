/**
 * RAG Index Manager Component
 *
 * Manages RAG indexes, documents, and queries.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import {
  CheckCircle,
  Database,
  FileText,
  Info,
  Loader2,
  Plus,
  Route,
  Search,
  Sparkles,
} from "lucide-react"
import { useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import { QueryDetails } from "./QueryDetails"

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
  return apiClient.request<RAGIndex[]>("/api/v1/rag/indexes")
}

const createRAGIndex = async (
  name: string,
  vectorDbType: string,
): Promise<RAGIndex> => {
  return apiClient.request<RAGIndex>("/api/v1/rag/index", {
    method: "POST",
    body: JSON.stringify({
      name,
      vector_db_type: vectorDbType,
    }),
  })
}

const queryRAGIndex = async (
  indexId: string,
  queryText: string,
): Promise<RAGQuery> => {
  return apiClient.request<RAGQuery>("/api/v1/rag/query", {
    method: "POST",
    body: JSON.stringify({
      index_id: indexId,
      query_text: queryText,
    }),
  })
}

const evaluateRouting = async (
  indexId: string,
  queryRequirements: Record<string, any>,
): Promise<{
  selected_vector_db: string
  reasoning: string
  confidence: number
}> => {
  return apiClient.request("/api/v1/rag/switch/evaluate", {
    method: "POST",
    body: JSON.stringify({
      index_id: indexId,
      query_requirements: queryRequirements,
    }),
  })
}

const validateAgent0Prompt = async (
  prompt: string,
  context?: Record<string, any>,
): Promise<{
  prompt: string
  validation: {
    is_valid: boolean
    warnings: string[]
    suggestions: string[]
  }
  recommended_index_type: string
}> => {
  return apiClient.request("/api/v1/rag/agent0/validate", {
    method: "POST",
    body: JSON.stringify({
      prompt,
      context: context || undefined,
    }),
  })
}

const startFinetuneJob = async (
  indexId: string,
  config: Record<string, any>,
  datasetUrls: string[],
): Promise<{
  id: string
  index_id: string
  status: string
  config: Record<string, any>
  dataset_count: number
  started_at: string
}> => {
  return apiClient.request("/api/v1/rag/finetune", {
    method: "POST",
    body: JSON.stringify({
      index_id: indexId,
      config,
      dataset_urls: datasetUrls,
    }),
  })
}

const addDocumentToIndex = async (
  indexId: string,
  content: string,
  metadata: Record<string, any>,
): Promise<void> => {
  await apiClient.request("/api/v1/rag/document", {
    method: "POST",
    body: JSON.stringify({
      index_id: indexId,
      content,
      document_metadata: metadata,
    }),
  })
}

const uploadDocumentToIndex = async (
  indexId: string,
  file: File,
  metadata: Record<string, any>,
): Promise<void> => {
  const formData = new FormData()
  formData.append("index_id", indexId)
  formData.append("file", file)
  formData.append("metadata", JSON.stringify(metadata))

  // Use apiClient for FormData upload - it handles FormData correctly
  await apiClient.request("/api/v1/rag/document/upload", {
    method: "POST",
    body: formData,
  })
}

const indexColumns: ColumnDef<RAGIndex>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => <div className="font-semibold">{row.original.name}</div>,
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
  const [isEvaluateDialogOpen, setIsEvaluateDialogOpen] = useState(false)
  const [isValidateDialogOpen, setIsValidateDialogOpen] = useState(false)
  const [isFinetuneDialogOpen, setIsFinetuneDialogOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState<RAGIndex | null>(null)
  const [newIndexName, setNewIndexName] = useState("")
  const [newIndexVectorDb, setNewIndexVectorDb] = useState("chromadb")
  const [queryText, setQueryText] = useState("")
  const [queryResult, setQueryResult] = useState<RAGQuery | null>(null)
  const [documentContent, setDocumentContent] = useState("")
  const [documentMetadata, setDocumentMetadata] = useState("")
  const [evaluateRequirements, setEvaluateRequirements] = useState("{}")
  const [evaluateResult, setEvaluateResult] = useState<any>(null)
  const [agent0Prompt, setAgent0Prompt] = useState("")
  const [agent0Context, setAgent0Context] = useState("{}")
  const [validateResult, setValidateResult] = useState<any>(null)
  const [finetuneConfig, setFinetuneConfig] = useState("{}")
  const [finetuneDatasetUrls, setFinetuneDatasetUrls] = useState("")

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createIndexMutation = useMutation({
    mutationFn: () => createRAGIndex(newIndexName, newIndexVectorDb),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ragIndexes"] })
      showSuccessToast(
        "RAG Index Created",
        `${newIndexName} created successfully`,
      )
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

  const uploadDocumentMutation = useMutation({
    mutationFn: async ({
      file,
      metadata,
    }: {
      file: File
      metadata: Record<string, any>
    }) => {
      if (!selectedIndex) throw new Error("No index selected")
      return uploadDocumentToIndex(selectedIndex.id, file, metadata)
    },
    onSuccess: () => {
      showSuccessToast(
        "Document uploaded",
        "Document uploaded and added to index successfully",
      )
      setIsAddDocDialogOpen(false)
      setDocumentMetadata("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to upload document", error.message)
    },
  })

  const evaluateRoutingMutation = useMutation({
    mutationFn: () => {
      if (!selectedIndex) throw new Error("No index selected")
      let requirements = {}
      if (evaluateRequirements.trim()) {
        try {
          requirements = JSON.parse(evaluateRequirements)
        } catch {
          throw new Error("Invalid JSON for query requirements")
        }
      }
      return evaluateRouting(selectedIndex.id, requirements)
    },
    onSuccess: (data) => {
      setEvaluateResult(data)
      showSuccessToast(
        "Routing evaluated",
        "Routing decision evaluated successfully",
      )
    },
    onError: (error: Error) => {
      showErrorToast("Failed to evaluate routing", error.message)
    },
  })

  const validateAgent0Mutation = useMutation({
    mutationFn: () => {
      if (!agent0Prompt.trim()) {
        throw new Error("Please provide a prompt")
      }
      let context
      if (agent0Context.trim()) {
        try {
          context = JSON.parse(agent0Context)
        } catch {
          throw new Error("Invalid JSON for context")
        }
      }
      return validateAgent0Prompt(agent0Prompt, context)
    },
    onSuccess: (data) => {
      setValidateResult(data)
      showSuccessToast(
        "Prompt validated",
        "Agent0 prompt validated successfully",
      )
    },
    onError: (error: Error) => {
      showErrorToast("Failed to validate prompt", error.message)
    },
  })

  const finetuneMutation = useMutation({
    mutationFn: () => {
      if (!selectedIndex) throw new Error("No index selected")
      let config = {}
      if (finetuneConfig.trim()) {
        try {
          config = JSON.parse(finetuneConfig)
        } catch {
          throw new Error("Invalid JSON for config")
        }
      }
      const urls = finetuneDatasetUrls
        .split("\n")
        .map((url) => url.trim())
        .filter((url) => url.length > 0)
      return startFinetuneJob(selectedIndex.id, config, urls)
    },
    onSuccess: (data) => {
      showSuccessToast(
        "Finetune job started",
        `Finetune job ${data.id} started with ${data.dataset_count} datasets`,
      )
      setIsFinetuneDialogOpen(false)
      setFinetuneConfig("{}")
      setFinetuneDatasetUrls("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to start finetune job", error.message)
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
                <Select
                  value={newIndexVectorDb}
                  onValueChange={setNewIndexVectorDb}
                >
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
                    <Dialog
                      open={isEvaluateDialogOpen}
                      onOpenChange={setIsEvaluateDialogOpen}
                    >
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <Route className="h-4 w-4 mr-2" />
                          Evaluate Routing
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Evaluate Routing Decision</DialogTitle>
                          <DialogDescription>
                            Evaluate which vector database would be selected for
                            a query
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="evaluate-requirements">
                              Query Requirements (JSON)
                            </Label>
                            <Textarea
                              id="evaluate-requirements"
                              placeholder='{"top_k": 5, "similarity_threshold": 0.7}'
                              value={evaluateRequirements}
                              onChange={(e) =>
                                setEvaluateRequirements(e.target.value)
                              }
                              rows={5}
                            />
                          </div>
                          <Button
                            onClick={() => evaluateRoutingMutation.mutate()}
                            disabled={evaluateRoutingMutation.isPending}
                            className="w-full"
                          >
                            {evaluateRoutingMutation.isPending ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Evaluating...
                              </>
                            ) : (
                              <>
                                <Route className="h-4 w-4 mr-2" />
                                Evaluate Routing
                              </>
                            )}
                          </Button>
                          {evaluateResult && (
                            <div className="space-y-2 p-4 border rounded">
                              <div className="font-medium">
                                Selected Vector DB:{" "}
                                {evaluateResult.selected_vector_db}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {evaluateResult.reasoning}
                              </div>
                              <div className="text-sm">
                                Confidence:{" "}
                                {(evaluateResult.confidence * 100).toFixed(1)}%
                              </div>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                    <Dialog
                      open={isValidateDialogOpen}
                      onOpenChange={setIsValidateDialogOpen}
                    >
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Validate Agent0
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Validate Agent0 Prompt</DialogTitle>
                          <DialogDescription>
                            Validate an Agent0 prompt for RAG usage
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="agent0-prompt">Agent0 Prompt</Label>
                            <Textarea
                              id="agent0-prompt"
                              placeholder="Enter your Agent0 prompt here..."
                              value={agent0Prompt}
                              onChange={(e) => setAgent0Prompt(e.target.value)}
                              rows={6}
                            />
                          </div>
                          <div>
                            <Label htmlFor="agent0-context">
                              Context (JSON, Optional)
                            </Label>
                            <Textarea
                              id="agent0-context"
                              placeholder='{"goal": "...", "belief": "..."}'
                              value={agent0Context}
                              onChange={(e) => setAgent0Context(e.target.value)}
                              rows={4}
                            />
                          </div>
                          <Button
                            onClick={() => validateAgent0Mutation.mutate()}
                            disabled={
                              !agent0Prompt.trim() ||
                              validateAgent0Mutation.isPending
                            }
                            className="w-full"
                          >
                            {validateAgent0Mutation.isPending ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Validating...
                              </>
                            ) : (
                              <>
                                <CheckCircle className="h-4 w-4 mr-2" />
                                Validate Prompt
                              </>
                            )}
                          </Button>
                          {validateResult && (
                            <div className="space-y-2 p-4 border rounded">
                              <div
                                className={`font-medium ${validateResult.validation.is_valid ? "text-green-600" : "text-red-600"}`}
                              >
                                {validateResult.validation.is_valid
                                  ? "✓ Valid"
                                  : "✗ Invalid"}
                              </div>
                              {validateResult.validation.warnings.length >
                                0 && (
                                <div>
                                  <div className="font-medium text-yellow-600">
                                    Warnings:
                                  </div>
                                  <ul className="list-disc list-inside text-sm">
                                    {validateResult.validation.warnings.map(
                                      (w: string, i: number) => (
                                        <li key={i}>{w}</li>
                                      ),
                                    )}
                                  </ul>
                                </div>
                              )}
                              {validateResult.validation.suggestions.length >
                                0 && (
                                <div>
                                  <div className="font-medium">
                                    Suggestions:
                                  </div>
                                  <ul className="list-disc list-inside text-sm">
                                    {validateResult.validation.suggestions.map(
                                      (s: string, i: number) => (
                                        <li key={i}>{s}</li>
                                      ),
                                    )}
                                  </ul>
                                </div>
                              )}
                              <div className="text-sm text-muted-foreground">
                                Recommended Index Type:{" "}
                                {validateResult.recommended_index_type}
                              </div>
                            </div>
                          )}
                        </div>
                      </DialogContent>
                    </Dialog>
                    <Dialog
                      open={isFinetuneDialogOpen}
                      onOpenChange={setIsFinetuneDialogOpen}
                    >
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <Sparkles className="h-4 w-4 mr-2" />
                          Start Finetune
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl">
                        <DialogHeader>
                          <DialogTitle>Start Fine-tuning Job</DialogTitle>
                          <DialogDescription>
                            Start a fine-tuning job for this RAG index
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label htmlFor="finetune-config">
                              Configuration (JSON)
                            </Label>
                            <Textarea
                              id="finetune-config"
                              placeholder='{"epochs": 10, "learning_rate": 0.001}'
                              value={finetuneConfig}
                              onChange={(e) =>
                                setFinetuneConfig(e.target.value)
                              }
                              rows={5}
                            />
                          </div>
                          <div>
                            <Label htmlFor="finetune-datasets">
                              Dataset URLs (one per line)
                            </Label>
                            <Textarea
                              id="finetune-datasets"
                              placeholder="https://example.com/dataset1.json&#10;https://example.com/dataset2.json"
                              value={finetuneDatasetUrls}
                              onChange={(e) =>
                                setFinetuneDatasetUrls(e.target.value)
                              }
                              rows={4}
                            />
                          </div>
                          <Button
                            onClick={() => finetuneMutation.mutate()}
                            disabled={finetuneMutation.isPending}
                            className="w-full"
                          >
                            {finetuneMutation.isPending ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Starting...
                              </>
                            ) : (
                              <>
                                <Sparkles className="h-4 w-4 mr-2" />
                                Start Fine-tuning Job
                              </>
                            )}
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                    <Dialog
                      open={isQueryDialogOpen}
                      onOpenChange={setIsQueryDialogOpen}
                    >
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
                            disabled={
                              !queryText.trim() || queryMutation.isPending
                            }
                            className="w-full"
                          >
                            {queryMutation.isPending
                              ? "Querying..."
                              : "Execute Query"}
                          </Button>
                          {queryResult && (
                            <div className="space-y-2">
                              <Separator />
                              <div>
                                <div className="flex items-center justify-between mb-2">
                                  <Label>Results</Label>
                                  <Dialog>
                                    <DialogTrigger asChild>
                                      <Button variant="outline" size="sm">
                                        <Info className="h-4 w-4 mr-2" />
                                        View Details
                                      </Button>
                                    </DialogTrigger>
                                    <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                                      <QueryDetails queryId={queryResult.id} />
                                    </DialogContent>
                                  </Dialog>
                                </div>
                                <ScrollArea className="h-60 rounded-md border p-4 mt-2">
                                  <pre className="text-xs">
                                    {JSON.stringify(
                                      queryResult.results,
                                      null,
                                      2,
                                    )}
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

                    <Dialog
                      open={isAddDocDialogOpen}
                      onOpenChange={setIsAddDocDialogOpen}
                    >
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
                            Upload a file or add text content to this RAG index
                          </DialogDescription>
                        </DialogHeader>
                        <Tabs defaultValue="upload" className="w-full">
                          <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="upload">
                              Upload File
                            </TabsTrigger>
                            <TabsTrigger value="text">Text Content</TabsTrigger>
                          </TabsList>
                          <TabsContent value="upload" className="space-y-4">
                            <div>
                              <Label htmlFor="file-upload-rag">
                                Upload Document File
                              </Label>
                              <Input
                                id="file-upload-rag"
                                type="file"
                                accept=".txt,.md,.pdf,.doc,.docx"
                                onChange={async (e) => {
                                  const file = e.target.files?.[0]
                                  if (!file) return

                                  if (file.size > 100 * 1024 * 1024) {
                                    showErrorToast(
                                      "File too large",
                                      "Maximum size is 100MB",
                                    )
                                    return
                                  }

                                  let metadata = {}
                                  if (documentMetadata.trim()) {
                                    try {
                                      metadata = JSON.parse(documentMetadata)
                                    } catch {
                                      metadata = { note: documentMetadata }
                                    }
                                  }

                                  uploadDocumentMutation.mutate({
                                    file,
                                    metadata,
                                  })
                                }}
                                className="cursor-pointer"
                              />
                              <p className="text-xs text-muted-foreground mt-2">
                                Supported formats: .txt, .md, .pdf, .doc, .docx
                                (max 100MB)
                              </p>
                            </div>
                            <div>
                              <Label htmlFor="doc-metadata-upload">
                                Metadata (JSON, optional)
                              </Label>
                              <Textarea
                                id="doc-metadata-upload"
                                placeholder='{"source": "url", "author": "name", ...}'
                                value={documentMetadata}
                                onChange={(e) =>
                                  setDocumentMetadata(e.target.value)
                                }
                                rows={4}
                                className="font-mono text-sm"
                              />
                            </div>
                            {uploadDocumentMutation.isPending && (
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Uploading and processing document...
                              </div>
                            )}
                          </TabsContent>
                          <TabsContent value="text" className="space-y-4">
                            <div>
                              <Label htmlFor="doc-content">
                                Document Content
                              </Label>
                              <Textarea
                                id="doc-content"
                                placeholder="Enter document content..."
                                value={documentContent}
                                onChange={(e) =>
                                  setDocumentContent(e.target.value)
                                }
                                rows={8}
                              />
                            </div>
                            <div>
                              <Label htmlFor="doc-metadata-text">
                                Metadata (JSON, optional)
                              </Label>
                              <Textarea
                                id="doc-metadata-text"
                                placeholder='{"source": "url", "author": "name", ...}'
                                value={documentMetadata}
                                onChange={(e) =>
                                  setDocumentMetadata(e.target.value)
                                }
                                rows={4}
                                className="font-mono text-sm"
                              />
                            </div>
                            <Button
                              onClick={() => addDocumentMutation.mutate()}
                              disabled={
                                !documentContent.trim() ||
                                addDocumentMutation.isPending
                              }
                              className="w-full"
                            >
                              {addDocumentMutation.isPending
                                ? "Adding..."
                                : "Add Document"}
                            </Button>
                          </TabsContent>
                        </Tabs>
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
