/**
 * OCR Job Manager Component
 *
 * Manages OCR jobs and results.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import { Eye, FileStack, FileText, Loader2, Play, Upload } from "lucide-react"
import { useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
import { FileUpload } from "@/components/Storage/FileUpload"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
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
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface OCRJob {
  id: string
  document_url: string
  engine: string
  status: string
  started_at: string
  completed_at: string | null
  error_message: string | null
  result: Record<string, any> | null
}

const fetchOCRJobs = async (): Promise<OCRJob[]> => {
  return apiClient.request<OCRJob[]>("/api/v1/ocr/jobs")
}

const createOCRJob = async (
  documentUrl: string,
  engine?: string,
): Promise<OCRJob> => {
  return apiClient.request<OCRJob>("/api/v1/ocr/extract", {
    method: "POST",
    body: JSON.stringify({
      document_url: documentUrl,
      engine: engine,
    }),
  })
}

const processOCRJob = async (jobId: string): Promise<void> => {
  await apiClient.request(`/api/v1/ocr/process/${jobId}`, {
    method: "POST",
  })
}

const batchExtractOCR = async (
  documentUrls: string[],
  engine?: string,
): Promise<{ jobs: OCRJob[]; total_count: number }> => {
  return apiClient.request<{ jobs: OCRJob[]; total_count: number }>(
    "/api/v1/ocr/batch",
    {
      method: "POST",
      body: JSON.stringify({
        document_urls: documentUrls,
        engine: engine,
      }),
    },
  )
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed":
      return "bg-green-500"
    case "failed":
      return "bg-red-500"
    case "running":
      return "bg-blue-500"
    default:
      return "bg-gray-500"
  }
}

const columns: ColumnDef<OCRJob>[] = [
  {
    accessorKey: "document_url",
    header: "Document URL",
    cell: ({ row }) => (
      <div className="max-w-md truncate font-mono text-xs">
        {row.original.document_url}
      </div>
    ),
  },
  {
    accessorKey: "engine",
    header: "Engine",
    cell: ({ row }) => <Badge variant="outline">{row.original.engine}</Badge>,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      return <Badge className={getStatusColor(status)}>{status}</Badge>
    },
  },
  {
    accessorKey: "started_at",
    header: "Started",
    cell: ({ row }) => (
      <span className="text-sm text-muted-foreground">
        {format(new Date(row.original.started_at), "PPP p")}
      </span>
    ),
  },
  {
    accessorKey: "completed_at",
    header: "Completed",
    cell: ({ row }) =>
      row.original.completed_at ? (
        <span className="text-sm text-muted-foreground">
          {format(new Date(row.original.completed_at), "PPP p")}
        </span>
      ) : (
        <span className="text-sm text-muted-foreground">N/A</span>
      ),
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      return <OCRJobActionsCell job={row.original} />
    },
  },
]

function OCRJobActionsCell({ job }: { job: OCRJob }) {
  const [isViewOpen, setIsViewOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleProcess = async () => {
    try {
      await processOCRJob(job.id)
      queryClient.invalidateQueries({ queryKey: ["ocrJobs"] })
      showSuccessToast("OCR job processing started")
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to process job",
      )
    }
  }

  return (
    <div className="flex items-center gap-2">
      {(job.status === "pending" || job.status === "failed") && (
        <Button variant="outline" size="sm" onClick={handleProcess}>
          <Play className="h-4 w-4 mr-2" />
          Process
        </Button>
      )}
      <Dialog open={isViewOpen} onOpenChange={setIsViewOpen}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm">
            <Eye className="h-4 w-4 mr-2" />
            View
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>OCR Job Details</DialogTitle>
            <DialogDescription>Job ID: {job.id}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <Label>Status</Label>
                <Badge className={getStatusColor(job.status)}>
                  {job.status}
                </Badge>
              </div>
              <div>
                <Label>Engine</Label>
                <p>{job.engine}</p>
              </div>
              <div>
                <Label>Started At</Label>
                <p>{format(new Date(job.started_at), "PPP p")}</p>
              </div>
              {job.completed_at && (
                <div>
                  <Label>Completed At</Label>
                  <p>{format(new Date(job.completed_at), "PPP p")}</p>
                </div>
              )}
            </div>
            {job.error_message && (
              <div>
                <Label>Error</Label>
                <p className="text-red-500">{job.error_message}</p>
              </div>
            )}
            {job.result && (
              <div>
                <Label>Result</Label>
                <ScrollArea className="h-60 rounded-md border p-4 mt-2">
                  <pre className="text-xs">
                    {JSON.stringify(job.result, null, 2)}
                  </pre>
                </ScrollArea>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export function OCRJobManager() {
  const queryClient = useQueryClient()
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["ocrJobs"],
    queryFn: fetchOCRJobs,
    refetchInterval: 5000, // Refresh every 5 seconds for running jobs
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isBatchDialogOpen, setIsBatchDialogOpen] = useState(false)
  const [documentUrl, setDocumentUrl] = useState("")
  const [batchUrls, setBatchUrls] = useState<string>("")
  const [selectedEngine, setSelectedEngine] = useState<string>("")
  const [batchEngine, setBatchEngine] = useState<string>("")
  const [uploadedFileUrl, setUploadedFileUrl] = useState<string | null>(null)

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createJobMutation = useMutation({
    mutationFn: () => {
      // Use uploaded file URL if available, otherwise use document URL
      const urlToUse = uploadedFileUrl || documentUrl
      if (!urlToUse) {
        throw new Error("Please upload a file or provide a document URL")
      }
      return createOCRJob(urlToUse, selectedEngine || undefined)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ocrJobs"] })
      showSuccessToast("OCR Job Created", "Job started successfully")
      setIsCreateDialogOpen(false)
      setDocumentUrl("")
      setUploadedFileUrl(null)
      setSelectedEngine("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create OCR job", error.message)
    },
  })

  const batchExtractMutation = useMutation({
    mutationFn: () => {
      const urls = batchUrls
        .split("\n")
        .map((url) => url.trim())
        .filter((url) => url.length > 0)
      if (urls.length === 0) {
        throw new Error("Please provide at least one document URL")
      }
      if (urls.length > 100) {
        throw new Error("Maximum 100 URLs allowed per batch")
      }
      return batchExtractOCR(urls, batchEngine || undefined)
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["ocrJobs"] })
      showSuccessToast(
        "Batch OCR Started",
        `Created ${data.total_count} OCR jobs successfully`,
      )
      setIsBatchDialogOpen(false)
      setBatchUrls("")
      setBatchEngine("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create batch OCR jobs", error.message)
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
          <h2 className="text-2xl font-semibold">OCR Job Manager</h2>
          <p className="text-muted-foreground">
            Extract text from documents using multiple OCR engines
          </p>
        </div>
      </div>
      <div className="flex gap-2">
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Upload className="h-4 w-4 mr-2" />
              New OCR Job
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create OCR Job</DialogTitle>
              <DialogDescription>
                Extract text from a document using OCR. Upload a file or provide
                a URL.
              </DialogDescription>
            </DialogHeader>
            <Tabs defaultValue="upload" className="w-full">
              <TabsList>
                <TabsTrigger value="upload">Upload File</TabsTrigger>
                <TabsTrigger value="url">From URL</TabsTrigger>
              </TabsList>
              <TabsContent value="upload" className="space-y-4">
                <div>
                  <Label>Upload Document</Label>
                  <FileUpload
                    bucket="ocr-documents"
                    accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.gif"
                    maxSize={50 * 1024 * 1024}
                    onUploadComplete={(result) => {
                      setUploadedFileUrl(result.url)
                      createJobMutation.mutate()
                    }}
                  />
                </div>
                {uploadedFileUrl && (
                  <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
                    <p className="text-sm text-green-800 dark:text-green-200">
                      File uploaded successfully. Creating OCR job...
                    </p>
                  </div>
                )}
                <div>
                  <Label htmlFor="engine-upload">OCR Engine (Optional)</Label>
                  <Select
                    value={selectedEngine}
                    onValueChange={setSelectedEngine}
                  >
                    <SelectTrigger id="engine-upload">
                      <SelectValue placeholder="Auto-select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Auto-select</SelectItem>
                      <SelectItem value="doctr">DocTR (Tables)</SelectItem>
                      <SelectItem value="easyocr">
                        EasyOCR (Handwriting)
                      </SelectItem>
                      <SelectItem value="paddleocr">
                        PaddleOCR (Low-latency)
                      </SelectItem>
                      <SelectItem value="tesseract">
                        Tesseract (Fallback)
                      </SelectItem>
                      <SelectItem value="google_vision">
                        Google Vision API
                      </SelectItem>
                      <SelectItem value="omniparser">
                        Omniparser (Structured)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </TabsContent>
              <TabsContent value="url" className="space-y-4">
                <div>
                  <Label htmlFor="document-url">Document URL</Label>
                  <Input
                    id="document-url"
                    placeholder="https://example.com/document.pdf"
                    value={documentUrl}
                    onChange={(e) => setDocumentUrl(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="engine-url">OCR Engine (Optional)</Label>
                  <Select
                    value={selectedEngine}
                    onValueChange={setSelectedEngine}
                  >
                    <SelectTrigger id="engine-url">
                      <SelectValue placeholder="Auto-select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Auto-select</SelectItem>
                      <SelectItem value="doctr">DocTR (Tables)</SelectItem>
                      <SelectItem value="easyocr">
                        EasyOCR (Handwriting)
                      </SelectItem>
                      <SelectItem value="paddleocr">
                        PaddleOCR (Low-latency)
                      </SelectItem>
                      <SelectItem value="tesseract">
                        Tesseract (Fallback)
                      </SelectItem>
                      <SelectItem value="google_vision">
                        Google Vision API
                      </SelectItem>
                      <SelectItem value="omniparser">
                        Omniparser (Structured)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={() => createJobMutation.mutate()}
                  disabled={!documentUrl.trim() || createJobMutation.isPending}
                  className="w-full"
                >
                  {createJobMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Job"
                  )}
                </Button>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
        <Dialog open={isBatchDialogOpen} onOpenChange={setIsBatchDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline">
              <FileStack className="h-4 w-4 mr-2" />
              Batch Extract
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Batch OCR Extract</DialogTitle>
              <DialogDescription>
                Extract text from multiple documents at once (max 100 URLs)
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="batch-urls">Document URLs (one per line)</Label>
                <textarea
                  id="batch-urls"
                  className="w-full min-h-32 p-3 border rounded-md font-mono text-sm"
                  placeholder="https://example.com/doc1.pdf&#10;https://example.com/doc2.pdf&#10;https://example.com/doc3.pdf"
                  value={batchUrls}
                  onChange={(e) => setBatchUrls(e.target.value)}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Enter one URL per line. Maximum 100 URLs per batch.
                </p>
              </div>
              <div>
                <Label htmlFor="batch-engine">OCR Engine (Optional)</Label>
                <Select value={batchEngine} onValueChange={setBatchEngine}>
                  <SelectTrigger id="batch-engine">
                    <SelectValue placeholder="Auto-select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Auto-select</SelectItem>
                    <SelectItem value="doctr">DocTR (Tables)</SelectItem>
                    <SelectItem value="easyocr">
                      EasyOCR (Handwriting)
                    </SelectItem>
                    <SelectItem value="paddleocr">
                      PaddleOCR (Low-latency)
                    </SelectItem>
                    <SelectItem value="tesseract">
                      Tesseract (Fallback)
                    </SelectItem>
                    <SelectItem value="google_vision">
                      Google Vision API
                    </SelectItem>
                    <SelectItem value="omniparser">
                      Omniparser (Structured)
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => batchExtractMutation.mutate()}
                disabled={!batchUrls.trim() || batchExtractMutation.isPending}
                className="w-full"
              >
                {batchExtractMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating Jobs...
                  </>
                ) : (
                  <>
                    <FileStack className="h-4 w-4 mr-2" />
                    Create Batch Jobs
                  </>
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {jobs && jobs.length > 0 ? (
        <DataTable columns={columns} data={jobs} />
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground mb-4">
                No OCR jobs found. Create your first job to get started.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Upload className="h-4 w-4 mr-2" />
                New OCR Job
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
