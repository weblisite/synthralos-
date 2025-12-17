/**
 * OCR Job Manager Component
 *
 * Manages OCR jobs and results.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { FileText, Upload, Eye, Loader2 } from "lucide-react"
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
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view OCR jobs")
  }

  const response = await fetch("/api/v1/ocr/jobs", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch OCR jobs")
  }

  return response.json()
}

const createOCRJob = async (
  documentUrl: string,
  engine?: string,
): Promise<OCRJob> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to create OCR jobs")
  }

  const response = await fetch("/api/v1/ocr/extract", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      document_url: documentUrl,
      engine: engine,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to create OCR job")
  }

  return response.json()
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
    cell: ({ row }) => (
      <Badge variant="outline">{row.original.engine}</Badge>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      return (
        <Badge className={getStatusColor(status)}>
          {status}
        </Badge>
      )
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
      const job = row.original
      const [isViewOpen, setIsViewOpen] = useState(false)

      return (
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
              <DialogDescription>
                Job ID: {job.id}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Label>Status</Label>
                  <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
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
      )
    },
  },
]

export function OCRJobManager() {
  const queryClient = useQueryClient()
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["ocrJobs"],
    queryFn: fetchOCRJobs,
    refetchInterval: 5000, // Refresh every 5 seconds for running jobs
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [documentUrl, setDocumentUrl] = useState("")
  const [selectedEngine, setSelectedEngine] = useState<string>("")

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createJobMutation = useMutation({
    mutationFn: () => createOCRJob(documentUrl, selectedEngine || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ocrJobs"] })
      showSuccessToast("OCR Job Created", "Job started successfully")
      setIsCreateDialogOpen(false)
      setDocumentUrl("")
      setSelectedEngine("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create OCR job", error.message)
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
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Upload className="h-4 w-4 mr-2" />
              New OCR Job
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create OCR Job</DialogTitle>
              <DialogDescription>
                Extract text from a document URL using OCR
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="document-url">Document URL</Label>
                <Input
                  id="document-url"
                  placeholder="https://synthralos.ai/document.pdf"
                  value={documentUrl}
                  onChange={(e) => setDocumentUrl(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="engine">OCR Engine (Optional)</Label>
                <Select value={selectedEngine} onValueChange={setSelectedEngine}>
                  <SelectTrigger id="engine">
                    <SelectValue placeholder="Auto-select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Auto-select</SelectItem>
                    <SelectItem value="doctr">DocTR (Tables)</SelectItem>
                    <SelectItem value="easyocr">EasyOCR (Handwriting)</SelectItem>
                    <SelectItem value="paddleocr">PaddleOCR (Low-latency)</SelectItem>
                    <SelectItem value="tesseract">Tesseract (Fallback)</SelectItem>
                    <SelectItem value="google_vision">Google Vision API</SelectItem>
                    <SelectItem value="omniparser">Omniparser (Structured)</SelectItem>
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

