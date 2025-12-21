/**
 * Code Tool Registry Component
 *
 * Manages code tools, sandboxes, and code executions.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import type { ColumnDef } from "@tanstack/react-table"
import { format } from "date-fns"
import { Box, Code, Info, Loader2, Play, Plus } from "lucide-react"
import { useState } from "react"
import { DataTable } from "@/components/Common/DataTable"
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
import { ToolDetails } from "./ToolDetails"
import { ToolRegistration } from "./ToolRegistration"

interface CodeTool {
  id: string
  tool_id: string
  name: string
  version: string
  description: string | null
  runtime: string
  usage_count: number
  is_deprecated: boolean
  created_at: string
  updated_at: string
}

interface CodeSandbox {
  id: string
  name: string
  runtime: string
  config: Record<string, any>
  created_at: string
}

interface CodeExecution {
  id: string
  runtime: string
  language: string
  status: string
  exit_code: number | null
  duration_ms: number
  memory_mb: number | null
  started_at: string
  completed_at: string | null
  error_message: string | null
}

const fetchCodeTools = async (): Promise<CodeTool[]> => {
  const data = await apiClient.request<{ tools: CodeTool[] }>(
    "/api/v1/code/tools?limit=100",
  )
  return data.tools || []
}

const fetchSandboxes = async (): Promise<CodeSandbox[]> => {
  return apiClient.request<CodeSandbox[]>("/api/v1/code/sandboxes")
}

const createSandbox = async (
  name: string,
  runtime: string,
  config?: Record<string, any>,
): Promise<CodeSandbox> => {
  return apiClient.request<CodeSandbox>("/api/v1/code/sandbox", {
    method: "POST",
    body: JSON.stringify({
      name,
      runtime,
      config: config || {},
    }),
  })
}

const executeCode = async (
  code: string,
  language: string,
  runtime?: string,
  inputData?: Record<string, any>,
): Promise<CodeExecution> => {
  return apiClient.request<CodeExecution>("/api/v1/code/execute", {
    method: "POST",
    body: JSON.stringify({
      code,
      language,
      runtime: runtime,
      input_data: inputData || {},
    }),
  })
}

const executeInSandbox = async (
  sandboxId: string,
  code: string,
  language: string,
  inputData?: Record<string, any>,
): Promise<CodeExecution> => {
  return apiClient.request<CodeExecution>(
    `/api/v1/code/sandbox/${sandboxId}/execute`,
    {
      method: "POST",
      body: JSON.stringify({
        code,
        language,
        input_data: inputData || {},
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

const toolColumns: ColumnDef<CodeTool>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => (
      <div>
        <div className="font-semibold">{row.original.name}</div>
        <div className="text-xs text-muted-foreground">
          {row.original.tool_id} v{row.original.version}
        </div>
      </div>
    ),
  },
  {
    accessorKey: "runtime",
    header: "Runtime",
    cell: ({ row }) => <Badge variant="outline">{row.original.runtime}</Badge>,
  },
  {
    accessorKey: "usage_count",
    header: "Usage",
    cell: ({ row }) => (
      <span className="text-sm">{row.original.usage_count}</span>
    ),
  },
  {
    accessorKey: "is_deprecated",
    header: "Status",
    cell: ({ row }) => (
      <Badge variant={row.original.is_deprecated ? "secondary" : "default"}>
        {row.original.is_deprecated ? "Deprecated" : "Active"}
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
      const tool = row.original
      return <ToolActionsCell tool={tool} />
    },
  },
]

function ToolActionsCell({ tool }: { tool: CodeTool }) {
  const [isViewOpen, setIsViewOpen] = useState(false)

  return (
    <Dialog open={isViewOpen} onOpenChange={setIsViewOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Info className="h-4 w-4 mr-2" />
          Details
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <ToolDetails toolId={tool.id} onClose={() => setIsViewOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}

const sandboxColumns: ColumnDef<CodeSandbox>[] = [
  {
    accessorKey: "name",
    header: "Name",
    cell: ({ row }) => <div className="font-semibold">{row.original.name}</div>,
  },
  {
    accessorKey: "runtime",
    header: "Runtime",
    cell: ({ row }) => <Badge variant="outline">{row.original.runtime}</Badge>,
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
      const sandbox = row.original
      return <SandboxActionsCell sandbox={sandbox} />
    },
  },
]

function SandboxActionsCell({ sandbox }: { sandbox: CodeSandbox }) {
  const [isExecuteOpen, setIsExecuteOpen] = useState(false)
  const [code, setCode] = useState("")
  const [language, setLanguage] = useState("python")
  const [inputData, setInputData] = useState("")
  const [executionResult, setExecutionResult] = useState<CodeExecution | null>(
    null,
  )
  const [isExecuting, setIsExecuting] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleExecute = async () => {
    if (!code.trim()) {
      showErrorToast("Please provide code to execute")
      return
    }

    setIsExecuting(true)
    try {
      let parsedInputData = {}
      if (inputData.trim()) {
        try {
          parsedInputData = JSON.parse(inputData)
        } catch {
          parsedInputData = { input: inputData }
        }
      }

      const result = await executeInSandbox(
        sandbox.id,
        code,
        language,
        parsedInputData,
      )
      setExecutionResult(result)
      showSuccessToast("Code executed", `Status: ${result.status}`)
    } catch (error) {
      showErrorToast(
        "Execution failed",
        error instanceof Error ? error.message : "Unknown error",
      )
    } finally {
      setIsExecuting(false)
    }
  }

  return (
    <Dialog open={isExecuteOpen} onOpenChange={setIsExecuteOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Play className="h-4 w-4 mr-2" />
          Execute
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Execute Code in Sandbox</DialogTitle>
          <DialogDescription>
            Sandbox: {sandbox.name} ({sandbox.runtime})
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <Label htmlFor="language">Language</Label>
            <Select value={language} onValueChange={setLanguage}>
              <SelectTrigger id="language">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="python">Python</SelectItem>
                <SelectItem value="javascript">JavaScript</SelectItem>
                <SelectItem value="typescript">TypeScript</SelectItem>
                <SelectItem value="bash">Bash</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="code">Code</Label>
            <Textarea
              id="code"
              placeholder="Enter your code here..."
              value={code}
              onChange={(e) => setCode(e.target.value)}
              rows={12}
              className="font-mono text-sm"
            />
          </div>
          <div>
            <Label htmlFor="input-data">Input Data (JSON, optional)</Label>
            <Textarea
              id="input-data"
              placeholder='{"key": "value"}'
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              rows={4}
              className="font-mono text-sm"
            />
          </div>
          <Button
            onClick={handleExecute}
            disabled={!code.trim() || isExecuting}
            className="w-full"
          >
            {isExecuting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Executing...
              </>
            ) : (
              "Execute"
            )}
          </Button>
          {executionResult && (
            <div className="space-y-2">
              <Separator />
              <div>
                <Label>Execution Result</Label>
                <Card>
                  <CardContent className="pt-4">
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span>Status:</span>
                        <Badge
                          className={getStatusColor(executionResult.status)}
                        >
                          {executionResult.status}
                        </Badge>
                      </div>
                      {executionResult.exit_code !== null && (
                        <div className="flex items-center justify-between">
                          <span>Exit Code:</span>
                          <span>{executionResult.exit_code}</span>
                        </div>
                      )}
                      <div className="flex items-center justify-between">
                        <span>Duration:</span>
                        <span>{executionResult.duration_ms}ms</span>
                      </div>
                      {executionResult.memory_mb && (
                        <div className="flex items-center justify-between">
                          <span>Memory:</span>
                          <span>{executionResult.memory_mb}MB</span>
                        </div>
                      )}
                      {executionResult.error_message && (
                        <div>
                          <span className="text-red-500">Error:</span>
                          <p className="text-red-500 text-xs mt-1">
                            {executionResult.error_message}
                          </p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

export function CodeToolRegistry() {
  const queryClient = useQueryClient()
  const { data: tools, isLoading: toolsLoading } = useQuery({
    queryKey: ["codeTools"],
    queryFn: fetchCodeTools,
  })

  const { data: sandboxes, isLoading: sandboxesLoading } = useQuery({
    queryKey: ["codeSandboxes"],
    queryFn: fetchSandboxes,
  })

  const [isCreateSandboxOpen, setIsCreateSandboxOpen] = useState(false)
  const [isExecuteOpen, setIsExecuteOpen] = useState(false)
  const [sandboxName, setSandboxName] = useState("")
  const [sandboxRuntime, setSandboxRuntime] = useState("e2b")
  const [code, setCode] = useState("")
  const [language, setLanguage] = useState("python")
  const [runtime, setRuntime] = useState("e2b")
  const [inputData, setInputData] = useState("")
  const [executionResult, setExecutionResult] = useState<CodeExecution | null>(
    null,
  )

  const { showSuccessToast, showErrorToast } = useCustomToast()

  const createSandboxMutation = useMutation({
    mutationFn: () => createSandbox(sandboxName, sandboxRuntime),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["codeSandboxes"] })
      showSuccessToast("Sandbox Created", "Sandbox created successfully")
      setIsCreateSandboxOpen(false)
      setSandboxName("")
      setSandboxRuntime("e2b")
    },
    onError: (error: Error) => {
      showErrorToast("Failed to create sandbox", error.message)
    },
  })

  const executeCodeMutation = useMutation({
    mutationFn: () => {
      let parsedInputData = {}
      if (inputData.trim()) {
        try {
          parsedInputData = JSON.parse(inputData)
        } catch {
          parsedInputData = { input: inputData }
        }
      }
      return executeCode(code, language, runtime || undefined, parsedInputData)
    },
    onSuccess: (result) => {
      setExecutionResult(result)
      showSuccessToast("Code executed", `Status: ${result.status}`)
    },
    onError: (error: Error) => {
      showErrorToast("Execution failed", error.message)
    },
  })

  if (toolsLoading || sandboxesLoading) {
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
          <h2 className="text-2xl font-semibold">Code Tool Registry</h2>
          <p className="text-muted-foreground">
            Manage code tools, sandboxes, and execute code in secure
            environments
          </p>
        </div>
        <div className="flex gap-2">
          <ToolRegistration />
          <Dialog
            open={isCreateSandboxOpen}
            onOpenChange={setIsCreateSandboxOpen}
          >
            <DialogTrigger asChild>
              <Button variant="outline">
                <Box className="h-4 w-4 mr-2" />
                New Sandbox
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Sandbox</DialogTitle>
                <DialogDescription>
                  Create a persistent code sandbox environment
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="sandbox-name">Sandbox Name</Label>
                  <Input
                    id="sandbox-name"
                    placeholder="My Sandbox"
                    value={sandboxName}
                    onChange={(e) => setSandboxName(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="sandbox-runtime">Runtime</Label>
                  <Select
                    value={sandboxRuntime}
                    onValueChange={setSandboxRuntime}
                  >
                    <SelectTrigger id="sandbox-runtime">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="e2b">E2B (Secure)</SelectItem>
                      <SelectItem value="wasmedge">
                        WasmEdge (WebAssembly)
                      </SelectItem>
                      <SelectItem value="bacalhau">
                        Bacalhau (Distributed)
                      </SelectItem>
                      <SelectItem value="mcp_server">MCP Server</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  onClick={() => createSandboxMutation.mutate()}
                  disabled={
                    !sandboxName.trim() || createSandboxMutation.isPending
                  }
                  className="w-full"
                >
                  {createSandboxMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Sandbox"
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={isExecuteOpen} onOpenChange={setIsExecuteOpen}>
            <DialogTrigger asChild>
              <Button>
                <Play className="h-4 w-4 mr-2" />
                Execute Code
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl">
              <DialogHeader>
                <DialogTitle>Execute Code</DialogTitle>
                <DialogDescription>
                  Execute code in a secure runtime environment
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="exec-language">Language</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger id="exec-language">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="python">Python</SelectItem>
                        <SelectItem value="javascript">JavaScript</SelectItem>
                        <SelectItem value="typescript">TypeScript</SelectItem>
                        <SelectItem value="bash">Bash</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="exec-runtime">Runtime (Optional)</Label>
                    <Select value={runtime} onValueChange={setRuntime}>
                      <SelectTrigger id="exec-runtime">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">Auto-select</SelectItem>
                        <SelectItem value="e2b">E2B</SelectItem>
                        <SelectItem value="wasmedge">WasmEdge</SelectItem>
                        <SelectItem value="bacalhau">Bacalhau</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="exec-code">Code</Label>
                  <Textarea
                    id="exec-code"
                    placeholder="Enter your code here..."
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    rows={12}
                    className="font-mono text-sm"
                  />
                </div>
                <div>
                  <Label htmlFor="exec-input-data">
                    Input Data (JSON, optional)
                  </Label>
                  <Textarea
                    id="exec-input-data"
                    placeholder='{"key": "value"}'
                    value={inputData}
                    onChange={(e) => setInputData(e.target.value)}
                    rows={4}
                    className="font-mono text-sm"
                  />
                </div>
                <Button
                  onClick={() => executeCodeMutation.mutate()}
                  disabled={!code.trim() || executeCodeMutation.isPending}
                  className="w-full"
                >
                  {executeCodeMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Executing...
                    </>
                  ) : (
                    "Execute"
                  )}
                </Button>
                {executionResult && (
                  <div className="space-y-2">
                    <Separator />
                    <div>
                      <Label>Execution Result</Label>
                      <Card>
                        <CardContent className="pt-4">
                          <div className="space-y-2 text-sm">
                            <div className="flex items-center justify-between">
                              <span>Status:</span>
                              <Badge
                                className={getStatusColor(
                                  executionResult.status,
                                )}
                              >
                                {executionResult.status}
                              </Badge>
                            </div>
                            {executionResult.exit_code !== null && (
                              <div className="flex items-center justify-between">
                                <span>Exit Code:</span>
                                <span>{executionResult.exit_code}</span>
                              </div>
                            )}
                            <div className="flex items-center justify-between">
                              <span>Duration:</span>
                              <span>{executionResult.duration_ms}ms</span>
                            </div>
                            {executionResult.memory_mb && (
                              <div className="flex items-center justify-between">
                                <span>Memory:</span>
                                <span>{executionResult.memory_mb}MB</span>
                              </div>
                            )}
                            {executionResult.error_message && (
                              <div>
                                <span className="text-red-500">Error:</span>
                                <p className="text-red-500 text-xs mt-1">
                                  {executionResult.error_message}
                                </p>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs defaultValue="tools" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tools">Tools</TabsTrigger>
          <TabsTrigger value="sandboxes">Sandboxes</TabsTrigger>
        </TabsList>

        <TabsContent value="tools" className="space-y-4">
          {tools && tools.length > 0 ? (
            <DataTable columns={toolColumns} data={tools} />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <Code className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    No code tools found
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="sandboxes" className="space-y-4">
          {sandboxes && sandboxes.length > 0 ? (
            <DataTable columns={sandboxColumns} data={sandboxes} />
          ) : (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <Box className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground mb-4">
                    No sandboxes found. Create your first sandbox to get
                    started.
                  </p>
                  <Button onClick={() => setIsCreateSandboxOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    New Sandbox
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
