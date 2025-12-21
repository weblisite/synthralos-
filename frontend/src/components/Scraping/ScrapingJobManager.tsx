/**
 * Scraping Job Manager Component
 *
 * Manages web scraping jobs and results.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import {
  Eye,
  Globe,
  Loader2,
  Monitor,
  Network,
  Play,
  RefreshCw,
} from "lucide-react"
import { useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
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
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

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

const createCrawlJobs = async (
  urls: string[],
  engine?: string,
): Promise<ScrapeJob[]> => {
  return apiClient.request<ScrapeJob[]>("/api/v1/scraping/crawl", {
    method: "POST",
    body: JSON.stringify({
      urls,
      engine: engine,
    }),
  })
}

const monitorPageChanges = async (
  url: string,
  checkIntervalSeconds: number = 3600,
  selector?: string,
  notificationWebhook?: string,
): Promise<{
  id: string
  url: string
  check_interval_seconds: number
  baseline_hash: string
  created_at: string
}> => {
  return apiClient.request("/api/v1/scraping/change-detection", {
    method: "POST",
    body: JSON.stringify({
      url,
      check_interval_seconds: checkIntervalSeconds,
      selector: selector || undefined,
      notification_webhook: notificationWebhook || undefined,
    }),
  })
}

const processScrapeJob = async (jobId: string): Promise<void> => {
  try {
    await apiClient.request(`/api/v1/scraping/process/${jobId}`, {
      method: "POST",
    })
  } catch (error: any) {
    throw new Error(
      error.message || error.detail || "Failed to process scraping job",
    )
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
  const [isCrawlDialogOpen, setIsCrawlDialogOpen] = useState(false)
  const [isMonitorDialogOpen, setIsMonitorDialogOpen] = useState(false)
  const [url, setUrl] = useState("")
  const [crawlUrls, setCrawlUrls] = useState<string>("")
  const [monitorUrl, setMonitorUrl] = useState("")
  const [monitorInterval, setMonitorInterval] = useState("3600")
  const [monitorSelector, setMonitorSelector] = useState("")
  const [monitorWebhook, setMonitorWebhook] = useState("")
  const [selectedEngine, setSelectedEngine] = useState<string>("")
  const [crawlEngine, setCrawlEngine] = useState<string>("")
  const [autoSelectProxy, setAutoSelectProxy] = useState(true)

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createJobMutation = useMutation({
    mutationFn: () =>
      createScrapeJob(url, selectedEngine || undefined, autoSelectProxy),
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

  const crawlJobsMutation = useMutation({
    mutationFn: () => {
      const urls = crawlUrls
        .split("\n")
        .map((url) => url.trim())
        .filter((url) => url.length > 0)
      if (urls.length === 0) {
        throw new Error("Please provide at least one URL")
      }
      return createCrawlJobs(urls, crawlEngine || undefined)
    },
    onSuccess: (jobs) => {
      queryClient.invalidateQueries({ queryKey: ["scrapeJobs"] })
      showSuccessToast(
        "Crawl Jobs Created",
        `Created ${jobs.length} scraping jobs successfully`,
      )
      setIsCrawlDialogOpen(false)
      setCrawlUrls("")
      setCrawlEngine("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create crawl jobs", error.message)
    },
  })

  const monitorChangesMutation = useMutation({
    mutationFn: () => {
      if (!monitorUrl.trim()) {
        throw new Error("Please provide a URL to monitor")
      }
      const interval = parseInt(monitorInterval, 10) || 3600
      if (interval < 60 || interval > 86400) {
        throw new Error("Check interval must be between 60 and 86400 seconds")
      }
      return monitorPageChanges(
        monitorUrl,
        interval,
        monitorSelector || undefined,
        monitorWebhook || undefined,
      )
    },
    onSuccess: (data) => {
      showSuccessToast(
        "Change Detection Started",
        `Monitoring ${data.url} for changes (checking every ${data.check_interval_seconds}s)`,
      )
      setIsMonitorDialogOpen(false)
      setMonitorUrl("")
      setMonitorInterval("3600")
      setMonitorSelector("")
      setMonitorWebhook("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to start change detection", error.message)
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
        <div className="flex gap-2">
          <Dialog
            open={isCreateDialogOpen}
            onOpenChange={setIsCreateDialogOpen}
          >
            <DialogTrigger asChild>
              <Button>
                <Play className="h-4 w-4 mr-2" />
                New Scraping Job
              </Button>
            </DialogTrigger>
          </Dialog>
          <Dialog open={isCrawlDialogOpen} onOpenChange={setIsCrawlDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Network className="h-4 w-4 mr-2" />
                Crawl Multiple URLs
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Crawl Jobs</DialogTitle>
                <DialogDescription>
                  Create scraping jobs for multiple URLs at once
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="crawl-urls">URLs (one per line)</Label>
                  <textarea
                    id="crawl-urls"
                    className="w-full min-h-32 p-3 border rounded-md font-mono text-sm"
                    placeholder="https://example.com/page1&#10;https://example.com/page2&#10;https://example.com/page3"
                    value={crawlUrls}
                    onChange={(e) => setCrawlUrls(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Enter one URL per line.
                  </p>
                </div>
                <div>
                  <Label htmlFor="crawl-engine">
                    Scraping Engine (Optional)
                  </Label>
                  <Select value={crawlEngine} onValueChange={setCrawlEngine}>
                    <SelectTrigger id="crawl-engine">
                      <SelectValue placeholder="Auto-select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Auto-select</SelectItem>
                      <SelectItem value="playwright">Playwright</SelectItem>
                      <SelectItem value="scrapy">Scrapy</SelectItem>
                      <SelectItem value="beautifulsoup">
                        BeautifulSoup
                      </SelectItem>
                      <SelectItem value="selenium">Selenium</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={() => crawlJobsMutation.mutate()}
                  disabled={!crawlUrls.trim() || crawlJobsMutation.isPending}
                  className="w-full"
                >
                  {crawlJobsMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating Jobs...
                    </>
                  ) : (
                    <>
                      <Network className="h-4 w-4 mr-2" />
                      Create Crawl Jobs
                    </>
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog
            open={isMonitorDialogOpen}
            onOpenChange={setIsMonitorDialogOpen}
          >
            <DialogTrigger asChild>
              <Button variant="outline">
                <Monitor className="h-4 w-4 mr-2" />
                Monitor Changes
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Monitor Page Changes</DialogTitle>
                <DialogDescription>
                  Set up periodic monitoring for page content changes
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="monitor-url">URL to Monitor</Label>
                  <Input
                    id="monitor-url"
                    placeholder="https://example.com/page"
                    value={monitorUrl}
                    onChange={(e) => setMonitorUrl(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="monitor-interval">
                    Check Interval (seconds)
                  </Label>
                  <Input
                    id="monitor-interval"
                    type="number"
                    min="60"
                    max="86400"
                    placeholder="3600"
                    value={monitorInterval}
                    onChange={(e) => setMonitorInterval(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Minimum: 60 seconds (1 minute), Maximum: 86400 seconds (24
                    hours)
                  </p>
                </div>
                <div>
                  <Label htmlFor="monitor-selector">
                    CSS Selector (Optional)
                  </Label>
                  <Input
                    id="monitor-selector"
                    placeholder="#content, .main, div[class='article']"
                    value={monitorSelector}
                    onChange={(e) => setMonitorSelector(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Monitor specific element instead of entire page
                  </p>
                </div>
                <div>
                  <Label htmlFor="monitor-webhook">
                    Notification Webhook (Optional)
                  </Label>
                  <Input
                    id="monitor-webhook"
                    type="url"
                    placeholder="https://your-webhook-url.com/notify"
                    value={monitorWebhook}
                    onChange={(e) => setMonitorWebhook(e.target.value)}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Webhook URL to receive change notifications
                  </p>
                </div>
                <Button
                  onClick={() => monitorChangesMutation.mutate()}
                  disabled={
                    !monitorUrl.trim() || monitorChangesMutation.isPending
                  }
                  className="w-full"
                >
                  {monitorChangesMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Starting Monitor...
                    </>
                  ) : (
                    <>
                      <Monitor className="h-4 w-4 mr-2" />
                      Start Monitoring
                    </>
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="space-y-6">
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
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
                <Select
                  value={selectedEngine}
                  onValueChange={setSelectedEngine}
                >
                  <SelectTrigger id="engine">
                    <SelectValue placeholder="Auto-select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Auto-select</SelectItem>
                    <SelectItem value="beautifulsoup">
                      BeautifulSoup (Simple HTML)
                    </SelectItem>
                    <SelectItem value="playwright">
                      Playwright (JS Rendering)
                    </SelectItem>
                    <SelectItem value="scrapy">
                      Scrapy (Spider Framework)
                    </SelectItem>
                    <SelectItem value="crawl4ai">
                      Crawl4AI (Multi-page)
                    </SelectItem>
                    <SelectItem value="scrapegraph_ai">
                      ScrapeGraph AI (Visual)
                    </SelectItem>
                    <SelectItem value="jobspy">Jobspy (Job Boards)</SelectItem>
                    <SelectItem value="watercrawl">
                      WaterCrawl (Agent-driven)
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="auto-proxy"
                  checked={autoSelectProxy}
                  onCheckedChange={(checked) =>
                    setAutoSelectProxy(checked === true)
                  }
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
