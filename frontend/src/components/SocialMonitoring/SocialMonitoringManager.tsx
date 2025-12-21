/**
 * Social Monitoring Manager Component
 *
 * Manages social media streams, signals, and alerts for real-time monitoring.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import {
  AlertCircle,
  Eye,
  FileStack,
  Loader2,
  Pause,
  Play,
  Plus,
  Search,
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
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface SocialMonitoringStream {
  id: string
  platform: string
  keywords: string[]
  engine: string
  is_active: boolean
  created_at: string
}

interface SocialMonitoringSignal {
  id: string
  source: string
  author: string | null
  text: string
  media: string[]
  link: string | null
  sentiment_score: number | null
  created_at: string
}

interface SocialMonitoringAlert {
  id: string
  stream_id: string | null
  alert_type: string
  message: string
  severity: string
  is_read: boolean
  created_at: string
}

const fetchSocialMonitoringStreams = async (): Promise<
  SocialMonitoringStream[]
> => {
  const data = await apiClient.request<{ streams: OSINTStream[] }>(
    "/api/v1/osint/streams",
  )
  return data.streams || []
}

const createSocialMonitoringStream = async (
  platform: string,
  keywords: string[],
  engine?: string,
): Promise<SocialMonitoringStream> => {
  return apiClient.request<OSINTStream>("/api/v1/osint/stream", {
    method: "POST",
    body: JSON.stringify({
      platform,
      keywords,
      engine: engine,
    }),
  })
}

const createDigest = async (
  platform: string,
  keywords: string[],
  engine?: string,
): Promise<{
  stream_id: string
  signals: SocialMonitoringSignal[]
  total_count: number
}> => {
  return apiClient.request<{
    stream_id: string
    signals: SocialMonitoringSignal[]
    total_count: number
  }>("/api/v1/osint/digest", {
    method: "POST",
    body: JSON.stringify({
      platform,
      keywords,
      engine: engine,
    }),
  })
}

const updateStreamStatus = async (
  streamId: string,
  isActive: boolean,
): Promise<void> => {
  await apiClient.request(`/api/v1/osint/streams/${streamId}/status`, {
    method: "PATCH",
    body: JSON.stringify({
      is_active: isActive,
    }),
  })
}

const executeStream = async (
  streamId: string,
): Promise<SocialMonitoringSignal[]> => {
  const data = await apiClient.request<{ signals: OSINTSignal[] }>(
    `/api/v1/osint/streams/${streamId}/execute`,
    {
      method: "POST",
    },
  )
  return data.signals || []
}

const fetchStreamSignals = async (
  streamId: string,
): Promise<SocialMonitoringSignal[]> => {
  const data = await apiClient.request<{ signals: OSINTSignal[] }>(
    `/api/v1/osint/streams/${streamId}/signals?limit=100`,
  )
  return data.signals || []
}

const fetchAlerts = async (): Promise<SocialMonitoringAlert[]> => {
  const data = await apiClient.request<{ alerts: OSINTAlert[] }>(
    "/api/v1/osint/alerts?limit=100",
  )
  return data.alerts || []
}

const markAlertRead = async (alertId: string): Promise<void> => {
  await apiClient.request(`/api/v1/osint/alerts/${alertId}/read`, {
    method: "POST",
  })
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "critical":
      return "bg-red-600"
    case "high":
      return "bg-orange-500"
    case "medium":
      return "bg-yellow-500"
    case "low":
      return "bg-blue-500"
    default:
      return "bg-gray-500"
  }
}

const streamColumns: ColumnDef<SocialMonitoringStream>[] = [
  {
    accessorKey: "platform",
    header: "Platform",
    cell: ({ row }) => <Badge variant="outline">{row.original.platform}</Badge>,
  },
  {
    accessorKey: "keywords",
    header: "Keywords",
    cell: ({ row }) => (
      <div className="flex flex-wrap gap-1">
        {row.original.keywords.slice(0, 3).map((keyword, idx) => (
          <Badge key={idx} variant="secondary" className="text-xs">
            {keyword}
          </Badge>
        ))}
        {row.original.keywords.length > 3 && (
          <Badge variant="secondary" className="text-xs">
            +{row.original.keywords.length - 3}
          </Badge>
        )}
      </div>
    ),
  },
  {
    accessorKey: "engine",
    header: "Engine",
    cell: ({ row }) => (
      <span className="text-sm text-muted-foreground">
        {row.original.engine}
      </span>
    ),
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <Badge
        className={row.original.is_active ? "bg-green-500" : "bg-gray-500"}
      >
        {row.original.is_active ? "Active" : "Inactive"}
      </Badge>
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
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const stream = row.original
      return <StreamActionsCell stream={stream} />
    },
  },
]

function StreamActionsCell({ stream }: { stream: SocialMonitoringStream }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [signals, setSignals] = useState<SocialMonitoringSignal[]>([])
  const [isLoadingSignals, setIsLoadingSignals] = useState(false)

  const handleToggleStatus = async () => {
    try {
      await updateStreamStatus(stream.id, !stream.is_active)
      queryClient.invalidateQueries({ queryKey: ["socialMonitoringStreams"] })
      showSuccessToast(
        "Stream status updated",
        `Stream ${stream.is_active ? "paused" : "activated"}`,
      )
    } catch (error) {
      showErrorToast(
        "Failed to update stream",
        error instanceof Error ? error.message : "Unknown error",
      )
    }
  }

  const handleExecute = async () => {
    try {
      setIsLoadingSignals(true)
      const result = await executeStream(stream.id)
      setSignals(result)
      showSuccessToast("Stream executed", `Collected ${result.length} signals`)
    } catch (error) {
      showErrorToast(
        "Failed to execute stream",
        error instanceof Error ? error.message : "Unknown error",
      )
    } finally {
      setIsLoadingSignals(false)
    }
  }

  const handleViewSignals = async () => {
    setIsViewOpen(true)
    setIsLoadingSignals(true)
    try {
      const result = await fetchStreamSignals(stream.id)
      setSignals(result)
    } catch (error) {
      showErrorToast(
        "Failed to load signals",
        error instanceof Error ? error.message : "Unknown error",
      )
    } finally {
      setIsLoadingSignals(false)
    }
  }

  return (
    <div className="flex items-center gap-2">
      {stream.is_active ? (
        <Button variant="outline" size="sm" onClick={handleToggleStatus}>
          <Pause className="h-4 w-4 mr-2" />
          Pause
        </Button>
      ) : (
        <Button variant="outline" size="sm" onClick={handleToggleStatus}>
          <Play className="h-4 w-4 mr-2" />
          Activate
        </Button>
      )}
      <Button
        variant="outline"
        size="sm"
        onClick={handleExecute}
        disabled={isLoadingSignals}
      >
        {isLoadingSignals ? (
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
        ) : (
          <Search className="h-4 w-4 mr-2" />
        )}
        Execute
      </Button>
      <Dialog open={isViewOpen} onOpenChange={setIsViewOpen}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm" onClick={handleViewSignals}>
            <Eye className="h-4 w-4 mr-2" />
            View
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Stream Signals</DialogTitle>
            <DialogDescription>
              Platform: {stream.platform} | Keywords:{" "}
              {stream.keywords.join(", ")}
            </DialogDescription>
          </DialogHeader>
          {isLoadingSignals ? (
            <Skeleton className="h-60 w-full" />
          ) : (
            <ScrollArea className="h-96">
              <div className="space-y-4">
                {signals.length > 0 ? (
                  signals.map((signal) => (
                    <Card key={signal.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm">
                            {signal.source}
                          </CardTitle>
                          {signal.sentiment_score !== null && (
                            <Badge variant="outline">
                              Sentiment: {signal.sentiment_score.toFixed(2)}
                            </Badge>
                          )}
                        </div>
                        {signal.author && (
                          <CardDescription>
                            Author: {signal.author}
                          </CardDescription>
                        )}
                      </CardHeader>
                      <CardContent>
                        <p className="text-sm mb-2">{signal.text}</p>
                        {signal.link && (
                          <a
                            href={signal.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-500 hover:underline"
                          >
                            {signal.link}
                          </a>
                        )}
                        {signal.media.length > 0 && (
                          <div className="mt-2 flex gap-2">
                            {signal.media.map((url, idx) => (
                              <a
                                key={idx}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-500 hover:underline"
                              >
                                Media {idx + 1}
                              </a>
                            ))}
                          </div>
                        )}
                        <p className="text-xs text-muted-foreground mt-2">
                          {format(new Date(signal.created_at), "PPP p")}
                        </p>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    No signals found
                  </p>
                )}
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

const alertColumns: ColumnDef<SocialMonitoringAlert>[] = [
  {
    accessorKey: "severity",
    header: "Severity",
    cell: ({ row }) => (
      <Badge className={getSeverityColor(row.original.severity)}>
        {row.original.severity}
      </Badge>
    ),
  },
  {
    accessorKey: "alert_type",
    header: "Type",
    cell: ({ row }) => (
      <span className="text-sm">{row.original.alert_type}</span>
    ),
  },
  {
    accessorKey: "message",
    header: "Message",
    cell: ({ row }) => (
      <div className="max-w-md truncate text-sm">{row.original.message}</div>
    ),
  },
  {
    accessorKey: "is_read",
    header: "Status",
    cell: ({ row }) => (
      <Badge variant={row.original.is_read ? "secondary" : "default"}>
        {row.original.is_read ? "Read" : "Unread"}
      </Badge>
    ),
  },
  {
    accessorKey: "created_at",
    header: "Created",
    cell: ({ row }) => (
      <span className="text-sm text-muted-foreground">
        {format(new Date(row.original.created_at), "PPP p")}
      </span>
    ),
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const alert = row.original
      return <AlertActionsCell alert={alert} />
    },
  },
]

function AlertActionsCell({ alert }: { alert: SocialMonitoringAlert }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleMarkRead = async () => {
    try {
      await markAlertRead(alert.id)
      queryClient.invalidateQueries({ queryKey: ["socialMonitoringAlerts"] })
      showSuccessToast("Alert marked as read")
    } catch (error) {
      showErrorToast(
        "Failed to mark alert as read",
        error instanceof Error ? error.message : "Unknown error",
      )
    }
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleMarkRead}
      disabled={alert.is_read}
    >
      {alert.is_read ? "Read" : "Mark Read"}
    </Button>
  )
}

export function SocialMonitoringManager() {
  const queryClient = useQueryClient()
  const { data: streams, isLoading: streamsLoading } = useQuery({
    queryKey: ["socialMonitoringStreams"],
    queryFn: fetchSocialMonitoringStreams,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ["socialMonitoringAlerts"],
    queryFn: fetchAlerts,
    refetchInterval: 10000,
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isDigestDialogOpen, setIsDigestDialogOpen] = useState(false)
  const [platform, setPlatform] = useState("twitter")
  const [digestPlatform, setDigestPlatform] = useState("twitter")
  const [keywordsInput, setKeywordsInput] = useState("")
  const [digestKeywordsInput, setDigestKeywordsInput] = useState("")
  const [selectedEngine, setSelectedEngine] = useState<string>("")
  const [digestEngine, setDigestEngine] = useState<string>("")
  const [digestResults, setDigestResults] = useState<SocialMonitoringSignal[]>(
    [],
  )

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createStreamMutation = useMutation({
    mutationFn: () => {
      const keywords = keywordsInput
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k.length > 0)
      return createSocialMonitoringStream(
        platform,
        keywords,
        selectedEngine || undefined,
      )
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["socialMonitoringStreams"] })
      showSuccessToast(
        "Social Monitoring Stream Created",
        "Stream created successfully",
      )
      setIsCreateDialogOpen(false)
      setPlatform("twitter")
      setKeywordsInput("")
      setSelectedEngine("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create stream", error.message)
    },
  })

  const createDigestMutation = useMutation({
    mutationFn: () => {
      const keywords = digestKeywordsInput
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k.length > 0)
      return createDigest(digestPlatform, keywords, digestEngine || undefined)
    },
    onSuccess: (data) => {
      setDigestResults(data.signals || [])
      showSuccessToast(
        "Digest created",
        `Collected ${data.total_count} signals from batch query`,
      )
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create digest", error.message)
    },
  })

  if (streamsLoading || alertsLoading) {
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
          <h2 className="text-2xl font-semibold">Social Monitoring Manager</h2>
          <p className="text-muted-foreground">
            Manage social media streams, signals, and alerts for real-time
            monitoring
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog
            open={isCreateDialogOpen}
            onOpenChange={setIsCreateDialogOpen}
          >
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Stream
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Social Monitoring Stream</DialogTitle>
                <DialogDescription>
                  Create a new social monitoring stream to monitor platforms for
                  keywords
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="platform">Platform</Label>
                  <Select value={platform} onValueChange={setPlatform}>
                    <SelectTrigger id="platform">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="twitter">Twitter</SelectItem>
                      <SelectItem value="reddit">Reddit</SelectItem>
                      <SelectItem value="news">News</SelectItem>
                      <SelectItem value="telegram">Telegram</SelectItem>
                      <SelectItem value="linkedin">LinkedIn</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="keywords">Keywords (comma-separated)</Label>
                  <Textarea
                    id="keywords"
                    placeholder="keyword1, keyword2, keyword3"
                    value={keywordsInput}
                    onChange={(e) => setKeywordsInput(e.target.value)}
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="engine">Engine (Optional)</Label>
                  <Select
                    value={selectedEngine}
                    onValueChange={setSelectedEngine}
                  >
                    <SelectTrigger id="engine">
                      <SelectValue placeholder="Auto-select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Auto-select</SelectItem>
                      <SelectItem value="twint">
                        Twint (Twitter scraping)
                      </SelectItem>
                      <SelectItem value="tweepy">
                        Tweepy (Twitter API)
                      </SelectItem>
                      <SelectItem value="social_listener">
                        Social-Listener (Multi-platform)
                      </SelectItem>
                      <SelectItem value="newscatcher">
                        NewsCatcher (News aggregation)
                      </SelectItem>
                      <SelectItem value="huginn">
                        Huginn (Automation)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={() => createStreamMutation.mutate()}
                  disabled={
                    !keywordsInput.trim() || createStreamMutation.isPending
                  }
                  className="w-full"
                >
                  {createStreamMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Stream"
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          <Dialog
            open={isDigestDialogOpen}
            onOpenChange={setIsDigestDialogOpen}
          >
            <DialogTrigger asChild>
              <Button variant="outline">
                <FileStack className="h-4 w-4 mr-2" />
                Batch Query
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Batch OSINT Query</DialogTitle>
                <DialogDescription>
                  Execute a one-time query to collect signals without creating a
                  stream
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="digest-platform">Platform</Label>
                  <Select
                    value={digestPlatform}
                    onValueChange={setDigestPlatform}
                  >
                    <SelectTrigger id="digest-platform">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="twitter">Twitter</SelectItem>
                      <SelectItem value="reddit">Reddit</SelectItem>
                      <SelectItem value="news">News</SelectItem>
                      <SelectItem value="github">GitHub</SelectItem>
                      <SelectItem value="hackernews">HackerNews</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="digest-keywords">
                    Keywords (comma-separated)
                  </Label>
                  <Textarea
                    id="digest-keywords"
                    placeholder="keyword1, keyword2, keyword3"
                    value={digestKeywordsInput}
                    onChange={(e) => setDigestKeywordsInput(e.target.value)}
                    rows={3}
                  />
                </div>
                <div>
                  <Label htmlFor="digest-engine">Engine (Optional)</Label>
                  <Select value={digestEngine} onValueChange={setDigestEngine}>
                    <SelectTrigger id="digest-engine">
                      <SelectValue placeholder="Auto-select" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Auto-select</SelectItem>
                      <SelectItem value="twitter_api">Twitter API</SelectItem>
                      <SelectItem value="reddit_api">Reddit API</SelectItem>
                      <SelectItem value="news_api">News API</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={() => createDigestMutation.mutate()}
                  disabled={
                    !digestKeywordsInput.trim() ||
                    createDigestMutation.isPending
                  }
                  className="w-full"
                >
                  {createDigestMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Querying...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Execute Batch Query
                    </>
                  )}
                </Button>
                {digestResults.length > 0 && (
                  <div className="space-y-2">
                    <Label>Results ({digestResults.length} signals)</Label>
                    <ScrollArea className="h-64 rounded-md border p-4">
                      <div className="space-y-2">
                        {digestResults.map((signal) => (
                          <div
                            key={signal.id}
                            className="p-2 border rounded text-sm"
                          >
                            <div className="font-medium">{signal.source}</div>
                            <div className="text-muted-foreground">
                              {signal.text}
                            </div>
                            {signal.link && (
                              <a
                                href={signal.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 text-xs"
                              >
                                View Source
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="streams" className="space-y-4">
        <TabsList>
          <TabsTrigger value="streams">Streams</TabsTrigger>
          <TabsTrigger value="alerts">
            Alerts
            {alerts && alerts.filter((a) => !a.is_read).length > 0 && (
              <Badge className="ml-2 bg-red-500">
                {alerts.filter((a) => !a.is_read).length}
              </Badge>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="streams" className="space-y-4">
          {streams && streams.length > 0 ? (
            <DataTable columns={streamColumns} data={streams} />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground mb-4">
                    No social monitoring streams found. Create your first stream
                    to get started.
                  </p>
                  <Button onClick={() => setIsCreateDialogOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Stream
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="alerts" className="space-y-4">
          {alerts && alerts.length > 0 ? (
            <DataTable columns={alertColumns} data={alerts} />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    No alerts found
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
