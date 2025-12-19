/**
 * Browser Session Manager Component
 *
 * Manages browser automation sessions and actions.
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Monitor, Play, X, Eye, Loader2 } from "lucide-react"
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
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
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

interface BrowserSession {
  id: string
  session_id: string
  browser_tool: string
  proxy_id: string | null
  status: string
  started_at: string
  closed_at: string | null
}

const fetchBrowserSessions = async (): Promise<BrowserSession[]> => {
  return apiClient.request<BrowserSession[]>("/api/v1/browser/sessions")
}

const createBrowserSession = async (
  browserTool: string,
): Promise<BrowserSession> => {
  return apiClient.request<BrowserSession>("/api/v1/browser/session", {
    method: "POST",
    body: JSON.stringify({
      browser_tool: browserTool,
    }),
  })
}

const closeBrowserSession = async (sessionId: string): Promise<void> => {
  await apiClient.request(`/api/v1/browser/session/${sessionId}/close`, {
    method: "POST",
  })
}

const getStatusColor = (status: string) => {
  switch (status) {
    case "active":
      return "bg-green-500"
    case "closed":
      return "bg-gray-500"
    case "error":
      return "bg-red-500"
    default:
      return "bg-gray-500"
  }
}

const columns: ColumnDef<BrowserSession>[] = [
  {
    accessorKey: "session_id",
    header: "Session ID",
    cell: ({ row }) => (
      <div className="font-mono text-xs">{row.original.session_id}</div>
    ),
  },
  {
    accessorKey: "browser_tool",
    header: "Browser Tool",
    cell: ({ row }) => (
      <Badge variant="outline">{row.original.browser_tool}</Badge>
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
    accessorKey: "closed_at",
    header: "Closed",
    cell: ({ row }) =>
      row.original.closed_at ? (
        <span className="text-sm text-muted-foreground">
          {format(new Date(row.original.closed_at), "PPP p")}
        </span>
      ) : (
        <span className="text-sm text-muted-foreground">N/A</span>
      ),
  },
  {
    id: "actions",
    header: "Actions",
    cell: ({ row }) => {
      const session = row.original
      return <SessionActionsCell session={session} />
    },
  },
]

function SessionActionsCell({ session }: { session: BrowserSession }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [isViewOpen, setIsViewOpen] = useState(false)

  const handleClose = async () => {
    try {
      await closeBrowserSession(session.session_id)
      queryClient.invalidateQueries({ queryKey: ["browserSessions"] })
      showSuccessToast("Session closed", "Browser session closed successfully")
    } catch (error) {
      showErrorToast(
        "Failed to close session",
        error instanceof Error ? error.message : "Unknown error",
      )
    }
  }

  return (
    <div className="flex items-center gap-2">
      {session.status === "active" && (
        <Button variant="outline" size="sm" onClick={handleClose}>
          <X className="h-4 w-4 mr-2" />
          Close
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
            <DialogTitle>Browser Session Details</DialogTitle>
            <DialogDescription>
              Session ID: {session.session_id}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <Label>Status</Label>
                <Badge className={getStatusColor(session.status)}>{session.status}</Badge>
              </div>
              <div>
                <Label>Browser Tool</Label>
                <p>{session.browser_tool}</p>
              </div>
              {session.proxy_id && (
                <div>
                  <Label>Proxy ID</Label>
                  <p className="font-mono text-xs">{session.proxy_id}</p>
                </div>
              )}
              <div>
                <Label>Started At</Label>
                <p>{format(new Date(session.started_at), "PPP p")}</p>
              </div>
              {session.closed_at && (
                <div>
                  <Label>Closed At</Label>
                  <p>{format(new Date(session.closed_at), "PPP p")}</p>
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export function BrowserSessionManager() {
  const queryClient = useQueryClient()
  const { data: sessions, isLoading } = useQuery({
    queryKey: ["browserSessions"],
    queryFn: fetchBrowserSessions,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [selectedBrowserTool, setSelectedBrowserTool] = useState("playwright")

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createSessionMutation = useMutation({
    mutationFn: () => createBrowserSession(selectedBrowserTool),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["browserSessions"] })
      showSuccessToast("Browser Session Created", "Session started successfully")
      setIsCreateDialogOpen(false)
      setSelectedBrowserTool("playwright")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create browser session", error.message)
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
          <h2 className="text-2xl font-semibold">Browser Session Manager</h2>
          <p className="text-muted-foreground">
            Manage browser automation sessions and actions
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Play className="h-4 w-4 mr-2" />
              New Session
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Browser Session</DialogTitle>
              <DialogDescription>
                Start a new browser automation session
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="browser-tool">Browser Tool</Label>
                <Select value={selectedBrowserTool} onValueChange={setSelectedBrowserTool}>
                  <SelectTrigger id="browser-tool">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="playwright">Playwright (JS-heavy pages)</SelectItem>
                    <SelectItem value="puppeteer">Puppeteer (Headless Chrome)</SelectItem>
                    <SelectItem value="browserbase">Browserbase (Fleet-scale)</SelectItem>
                    <SelectItem value="undetected_chromedriver">Undetected ChromeDriver (Anti-bot)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => createSessionMutation.mutate()}
                disabled={createSessionMutation.isPending}
                className="w-full"
              >
                {createSessionMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  "Create Session"
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {sessions && sessions.length > 0 ? (
        <DataTable columns={columns} data={sessions} />
      ) : (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <Monitor className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-sm text-muted-foreground mb-4">
                No browser sessions found. Create your first session to get started.
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Play className="h-4 w-4 mr-2" />
                New Session
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

