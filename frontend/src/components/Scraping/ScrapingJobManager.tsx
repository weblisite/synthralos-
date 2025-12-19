/**
 * Scraping Job Manager Component
 *
 * Manages web scraping jobs and results.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Globe, Play, Eye, Loader2, RefreshCw } from "lucide-react"
import { useState } from "react"
import { format } from "date-fns"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
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
import { Skeleton } from "@/components/ui/skeleton"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"
import type { ColumnDef } from "@tanstack/react-table"

interface ScrapeJob {
  id: string
  url: string
  engine: string
  proxy_id: string | null
  status: string
  started_at: string
  completed_at: string | null
  error_message: string | null
  result: Record<string, any> | null
}

const fetchScrapeJobs = async (): Promise<ScrapeJob[]> => {
  return apiClient.request<ScrapeJob[]>("/api/v1/scraping/jobs")
}

const createScrapeJob = async (
  url: string,
  engine?: string,
  autoSelectProxy: boolean = true,
): Promise<ScrapeJob> => {
  return apiClient.request<ScrapeJob>("/api/v1/scraping/scrape", {
    method: "POST",
    body: JSON.stringify({
      url,
      engine: engine,
      auto_select_proxy: autoSelectProxy,
    }),
  })
}

const processScrapeJob = async (jobId: string): Promise<void> => {
  try {
    await apiClient.request(`/api/v1/scraping/process/${jobId}`, {
      method: "POST",
    })
  } catch (error: any) {
    throw new Error(error.message || error.detail || "Failed to process scraping job")
  }
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

const columns: ColumnDef<ScrapeJob>[] = [
  {
    accessorKey: "url",
    header: "URL",
    cell: ({ row }) => (
      <div className="max-w-md truncate font-mono text-xs">
        {row.original.url}
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
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const job = row.original
      return <JobActionsCell job={job} />
    },
  },
]

function JobActionsCell({ job }: { job: ScrapeJob }) {
  const [isViewOpen, setIsViewOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleProcess = async () => {
    try {
      await processScrapeJob(job.id)
      queryClient.invalidateQueries({ queryKey: ["scrapeJobs"] })
      showSuccessToast("Scraping job processed successfully")
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to process job",
      )
    }
  }

  return (
    <div className="flex items-center gap-2">
      {job.status === "running" && (
        <Button variant="outline" size="sm" onClick={handleProcess}>
          <RefreshCw className="h-4 w-4 mr-2" />
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
            <DialogTitle>Scraping Job Details</DialogTitle>
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
                <Label>URL</Label>
                <p className="font-mono text-xs break-all">{job.url}</p>
              </div>
              {job.proxy_id && (
                <div>
                  <Label>Proxy ID</Label>
                  <p className="font-mono text-xs">{job.proxy_id}</p>
                </div>
              )}
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

export function ScrapingJobManager() {
  const queryClient = useQueryClient()
  const { data: jobs, isLoading } = useQuery({
    queryKey: ["scrapeJobs"],
    queryFn: fetchScrapeJobs,
    refetchInterval: 5000, // Refresh every 5 seconds for running jobs
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [url, setUrl] = useState("")
  const [selectedEngine, setSelectedEngine] = useState<string>("")
  const [autoSelectProxy, setAutoSelectProxy] = useState(true)

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createJobMutation = useMutation({
    mutationFn: () => createScrapeJob(url, selectedEngine || undefined, autoSelectProxy),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["scrapeJobs"] })
      showSuccessToast("Job started successfully")
      setIsCreateDialogOpen(false)
      setUrl("")
      setSelectedEngine("")
      setAutoSelectProxy(true)
    },
    onError: (error: Error) => {
      showErrorToast(error.message || "Failed to create scraping job")
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
          <h2 className="text-2xl font-semibold">Scraping Job Manager</h2>
          <p className="text-muted-foreground">
            Manage web scraping jobs with proxy support and multiple engines
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Play className="h-4 w-4 mr-2" />
              New Scraping Job
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Scraping Job</DialogTitle>
              <DialogDescription>
                Scrape content from a URL using multiple scraping engines
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="url">URL</Label>
                <Input
                  id="url"
                  placeholder="https://synthralos.ai"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="engine">Scraping Engine (Optional)</Label>
                <Select value={selectedEngine} onValueChange={setSelectedEngine}>
                  <SelectTrigger id="engine">
                    <SelectValue placeholder="Auto-select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Auto-select</SelectItem>
                    <SelectItem value="beautifulsoup">BeautifulSoup (Simple HTML)</SelectItem>
                    <SelectItem value="playwright">Playwright (JS Rendering)</SelectItem>
                    <SelectItem value="scrapy">Scrapy (Spider Framework)</SelectItem>
                    <SelectItem value="crawl4ai">Crawl4AI (Multi-page)</SelectItem>
                    <SelectItem value="scrapegraph_ai">ScrapeGraph AI (Visual)</SelectItem>
                    <SelectItem value="jobspy">Jobspy (Job Boards)</SelectItem>
                    <SelectItem value="watercrawl">WaterCrawl (Agent-driven)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="auto-proxy"
                  checked={autoSelectProxy}
                  onCheckedChange={(checked) => setAutoSelectProxy(checked === true)}
                />
                <Label htmlFor="auto-proxy" className="cursor-pointer">
                  Auto-select proxy
                </Label>
              </div>
              <Button
                onClick={() => createJobMutation.mutate()}
                disabled={!url.trim() || createJobMutation.isPending}
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
              <Globe className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground mb-4">
                No scraping jobs found. Create your first job to get started.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Play className="h-4 w-4 mr-2" />
                New Scraping Job
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

