/**
 * OSINT Stream Manager Component
 *
 * Manages OSINT streams, signals, and alerts.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Search, Plus, Play, Pause, Eye, AlertCircle, Loader2 } from "lucide-react"
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
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"
import type { ColumnDef } from "@tanstack/react-table"

interface OSINTStream {
  id: string
  platform: string
  keywords: string[]
  engine: string
  is_active: boolean
  created_at: string
}

interface OSINTSignal {
  id: string
  source: string
  author: string | null
  text: string
  media: string[]
  link: string | null
  sentiment_score: number | null
  created_at: string
}

interface OSINTAlert {
  id: string
  stream_id: string | null
  alert_type: string
  message: string
  severity: string
  is_read: boolean
  created_at: string
}

const fetchOSINTStreams = async (): Promise<OSINTStream[]> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view OSINT streams")
  }

  const response = await fetch("/api/v1/osint/streams", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch OSINT streams")
  }

  const data = await response.json()
  return data.streams || []
}

const createOSINTStream = async (
  platform: string,
  keywords: string[],
  engine?: string,
): Promise<OSINTStream> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to create OSINT streams")
  }

  const response = await fetch("/api/v1/osint/stream", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      platform,
      keywords,
      engine: engine,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to create OSINT stream")
  }

  return response.json()
}

const updateStreamStatus = async (
  streamId: string,
  isActive: boolean,
): Promise<void> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to update stream status")
  }

  const response = await fetch(`/api/v1/osint/streams/${streamId}/status`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      is_active: isActive,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to update stream status")
  }
}

const executeStream = async (streamId: string): Promise<OSINTSignal[]> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to execute streams")
  }

  const response = await fetch(`/api/v1/osint/streams/${streamId}/execute`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to execute stream")
  }

  const data = await response.json()
  return data.signals || []
}

const fetchStreamSignals = async (streamId: string): Promise<OSINTSignal[]> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view stream signals")
  }

  const response = await fetch(`/api/v1/osint/streams/${streamId}/signals?limit=100`, {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch stream signals")
  }

  const data = await response.json()
  return data.signals || []
}

const fetchAlerts = async (): Promise<OSINTAlert[]> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view alerts")
  }

  const response = await fetch("/api/v1/osint/alerts?limit=100", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch alerts")
  }

  const data = await response.json()
  return data.alerts || []
}

const markAlertRead = async (alertId: string): Promise<void> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to mark alerts as read")
  }

  const response = await fetch(`/api/v1/osint/alerts/${alertId}/read`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to mark alert as read")
  }
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

const streamColumns: ColumnDef<OSINTStream>[] = [
  {
    accessorKey: "platform",
    header: "Platform",
    cell: ({ row }) => (
      <Badge variant="outline">{row.original.platform}</Badge>
    ),
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
      <span className="text-sm text-muted-foreground">{row.original.engine}</span>
    ),
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) => (
      <Badge className={row.original.is_active ? "bg-green-500" : "bg-gray-500"}>
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

function StreamActionsCell({ stream }: { stream: OSINTStream }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [isViewOpen, setIsViewOpen] = useState(false)
  const [signals, setSignals] = useState<OSINTSignal[]>([])
  const [isLoadingSignals, setIsLoadingSignals] = useState(false)

  const handleToggleStatus = async () => {
    try {
      await updateStreamStatus(stream.id, !stream.is_active)
      queryClient.invalidateQueries({ queryKey: ["osintStreams"] })
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
      <Button variant="outline" size="sm" onClick={handleExecute} disabled={isLoadingSignals}>
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
              Platform: {stream.platform} | Keywords: {stream.keywords.join(", ")}
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
                          <CardTitle className="text-sm">{signal.source}</CardTitle>
                          {signal.sentiment_score !== null && (
                            <Badge variant="outline">
                              Sentiment: {signal.sentiment_score.toFixed(2)}
                            </Badge>
                          )}
                        </div>
                        {signal.author && (
                          <CardDescription>Author: {signal.author}</CardDescription>
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

const alertColumns: ColumnDef<OSINTAlert>[] = [
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

function AlertActionsCell({ alert }: { alert: OSINTAlert }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleMarkRead = async () => {
    try {
      await markAlertRead(alert.id)
      queryClient.invalidateQueries({ queryKey: ["osintAlerts"] })
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

export function OSINTStreamManager() {
  const queryClient = useQueryClient()
  const { data: streams, isLoading: streamsLoading } = useQuery({
    queryKey: ["osintStreams"],
    queryFn: fetchOSINTStreams,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  const { data: alerts, isLoading: alertsLoading } = useQuery({
    queryKey: ["osintAlerts"],
    queryFn: fetchAlerts,
    refetchInterval: 10000,
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [platform, setPlatform] = useState("twitter")
  const [keywordsInput, setKeywordsInput] = useState("")
  const [selectedEngine, setSelectedEngine] = useState<string>("")

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createStreamMutation = useMutation({
    mutationFn: () => {
      const keywords = keywordsInput
        .split(",")
        .map((k) => k.trim())
        .filter((k) => k.length > 0)
      return createOSINTStream(platform, keywords, selectedEngine || undefined)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["osintStreams"] })
      showSuccessToast("OSINT Stream Created", "Stream created successfully")
      setIsCreateDialogOpen(false)
      setPlatform("twitter")
      setKeywordsInput("")
      setSelectedEngine("")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create stream", error.message)
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
          <h2 className="text-2xl font-semibold">OSINT Stream Manager</h2>
          <p className="text-muted-foreground">
            Manage OSINT streams, signals, and alerts for real-time monitoring
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Stream
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create OSINT Stream</DialogTitle>
              <DialogDescription>
                Create a new OSINT stream to monitor platforms for keywords
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
                <Select value={selectedEngine} onValueChange={setSelectedEngine}>
                  <SelectTrigger id="engine">
                    <SelectValue placeholder="Auto-select" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Auto-select</SelectItem>
                    <SelectItem value="twint">Twint (Twitter scraping)</SelectItem>
                    <SelectItem value="tweepy">Tweepy (Twitter API)</SelectItem>
                    <SelectItem value="social_listener">Social-Listener (Multi-platform)</SelectItem>
                    <SelectItem value="newscatcher">NewsCatcher (News aggregation)</SelectItem>
                    <SelectItem value="huginn">Huginn (Automation)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => createStreamMutation.mutate()}
                disabled={!keywordsInput.trim() || createStreamMutation.isPending}
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
                    No OSINT streams found. Create your first stream to get started.
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

