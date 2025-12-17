/**
 * Agent Catalog Component
 *
 * Displays available agent frameworks and allows users to configure and execute agents.
 */

import { useQuery } from "@tanstack/react-query"
import { Bot, Play, Settings } from "lucide-react"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

interface AgentFramework {
  framework: string
  config: Record<string, any>
  is_enabled: boolean
}

interface AgentCatalogProps {
  onAgentSelect?: (framework: string) => void
}

const fetchAgentCatalog = async (): Promise<AgentFramework[]> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to view agent catalog")
  }

  const response = await fetch("/api/v1/agents/catalog", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch agent catalog")
  }

  const data = await response.json()
  // API returns { frameworks: [...], total: ... }
  return Array.isArray(data.frameworks) ? data.frameworks : (Array.isArray(data) ? data : [])
}

const executeAgentTask = async (
  taskType: string,
  inputData: Record<string, any>,
  framework?: string,
): Promise<{ task_id: string }> => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to execute agent tasks")
  }

  const response = await fetch("/api/v1/agents/run", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      task_type: taskType,
      input_data: inputData,
      framework: framework,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to execute agent task")
  }

  return response.json()
}

const getFrameworkDescription = (framework: string): string => {
  const descriptions: Record<string, string> = {
    agentgpt: "Simple, straightforward agent framework for basic tasks",
    autogpt: "Autonomous agent with recursive planning capabilities",
    babyagi: "BabyAGI - Task-driven autonomous agent",
    metagpt: "Multi-role agent framework for complex workflows",
    crewai: "Multi-agent collaboration framework",
    autogen: "Tool-calling planner with multi-agent support",
    archon: "Self-healing agent framework with error recovery",
    swarm: "Swarm intelligence for distributed agent tasks",
    camel_ai: "Communicative agent framework",
    kush_ai: "Advanced autonomous agent capabilities",
    kyro: "High-performance agent framework",
    riona: "Advanced AI agent with enhanced capabilities",
  }
  return descriptions[framework] || "Agent framework"
}

export function AgentCatalog({ onAgentSelect }: AgentCatalogProps) {
  const { data: frameworks, isLoading, error } = useQuery({
    queryKey: ["agentCatalog"],
    queryFn: fetchAgentCatalog,
  })

  const [selectedFramework, setSelectedFramework] = useState<string | null>(null)
  const [isExecuteDialogOpen, setIsExecuteDialogOpen] = useState(false)
  const [taskType, setTaskType] = useState("")
  const [inputData, setInputData] = useState("")
  const [isExecuting, setIsExecuting] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleExecute = async () => {
    if (!selectedFramework || !taskType.trim()) {
      showErrorToast("Please select a framework and provide a task type")
      return
    }

    setIsExecuting(true)
    try {
      let parsedInputData = {}
      if (inputData.trim()) {
        try {
          parsedInputData = JSON.parse(inputData)
        } catch {
          // If not JSON, treat as plain text
          parsedInputData = { prompt: inputData }
        }
      }

      const result = await executeAgentTask(taskType, parsedInputData, selectedFramework)
      showSuccessToast("Agent task started", `Task ID: ${result.task_id}`)
      setIsExecuteDialogOpen(false)
      setTaskType("")
      setInputData("")
    } catch (error) {
      showErrorToast(
        "Failed to execute agent task",
        error instanceof Error ? error.message : "Unknown error",
      )
    } finally {
      setIsExecuting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-48 mt-2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error || !frameworks) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            Failed to load agent catalog. Please try again later.
          </p>
        </CardContent>
      </Card>
    )
  }

  const enabledFrameworks = frameworks.filter((f) => f.is_enabled)
  const disabledFrameworks = frameworks.filter((f) => !f.is_enabled)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Agent Catalog</h2>
        <p className="text-muted-foreground">
          Browse and execute agent frameworks for various tasks
        </p>
      </div>

      {/* Enabled Frameworks */}
      {enabledFrameworks.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Available Frameworks</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {enabledFrameworks.map((framework) => (
              <Card key={framework.framework} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Bot className="h-5 w-5" />
                      {framework.framework.charAt(0).toUpperCase() + framework.framework.slice(1)}
                    </CardTitle>
                    <Badge variant="default">Enabled</Badge>
                  </div>
                  <CardDescription className="mt-2">
                    {getFrameworkDescription(framework.framework)}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Dialog
                    open={isExecuteDialogOpen && selectedFramework === framework.framework}
                    onOpenChange={(open) => {
                      setIsExecuteDialogOpen(open)
                      if (!open) {
                        setSelectedFramework(null)
                      }
                    }}
                  >
                    <DialogTrigger asChild>
                      <Button
                        className="w-full"
                        onClick={() => {
                          setSelectedFramework(framework.framework)
                          setIsExecuteDialogOpen(true)
                        }}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Execute
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>
                          Execute {framework.framework.charAt(0).toUpperCase() + framework.framework.slice(1)} Agent
                        </DialogTitle>
                        <DialogDescription>
                          Configure and execute an agent task using this framework
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="task-type">Task Type</Label>
                          <Input
                            id="task-type"
                            placeholder="e.g., research_task, data_analysis, content_generation"
                            value={taskType}
                            onChange={(e) => setTaskType(e.target.value)}
                          />
                        </div>
                        <div>
                          <Label htmlFor="input-data">Input Data (JSON or plain text)</Label>
                          <Textarea
                            id="input-data"
                            placeholder='{"prompt": "Your task description", "context": {...}}'
                            value={inputData}
                            onChange={(e) => setInputData(e.target.value)}
                            rows={6}
                            className="font-mono text-sm"
                          />
                        </div>
                        <Button
                          onClick={handleExecute}
                          disabled={isExecuting || !taskType.trim()}
                          className="w-full"
                        >
                          {isExecuting ? "Executing..." : "Execute Task"}
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                  {onAgentSelect && (
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => onAgentSelect(framework.framework)}
                    >
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Disabled Frameworks */}
      {disabledFrameworks.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Disabled Frameworks</h3>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {disabledFrameworks.map((framework) => (
              <Card key={framework.framework} className="opacity-60">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Bot className="h-5 w-5" />
                      {framework.framework.charAt(0).toUpperCase() + framework.framework.slice(1)}
                    </CardTitle>
                    <Badge variant="secondary">Disabled</Badge>
                  </div>
                  <CardDescription className="mt-2">
                    {getFrameworkDescription(framework.framework)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    This framework is currently disabled
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {frameworks.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground text-center">
              No agent frameworks available
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

