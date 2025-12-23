/**
 * Debug Panel Component
 *
 * Provides debugging interface for workflow executions:
 * - Enable/disable debug mode
 * - Step-by-step execution
 * - Breakpoint management
 * - Variable inspection
 * - Execution state inspection
 */

import { Bug, Pause, Play, StepForward, X } from "lucide-react"
import { useEffect, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/hooks/use-toast"
import { apiRequest } from "@/lib/api"

interface DebugPanelProps {
  executionId: string
  onClose?: () => void
}

interface DebugState {
  debugMode: boolean
  currentNodeId: string | null
  status: string
  executionData: Record<string, any>
  nodeResults: Record<string, any>
}

interface VariableScope {
  scope: string
  variables: Record<string, any>
}

export function DebugPanel({ executionId, onClose }: DebugPanelProps) {
  const [debugMode, setDebugMode] = useState(false)
  const [debugState, setDebugState] = useState<DebugState | null>(null)
  const [variables, setVariables] = useState<VariableScope[]>([])
  const [breakpoints, setBreakpoints] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()

  const loadDebugState = async () => {
    try {
      const state = await apiRequest<DebugState>(
        `/api/v1/workflows/executions/${executionId}/debug/state`,
      )
      setDebugState(state)
    } catch (error) {
      console.error("Failed to load debug state:", error)
    }
  }

  const loadVariables = async () => {
    try {
      const vars = await apiRequest<Record<string, any>>(
        `/api/v1/workflows/executions/${executionId}/debug/variables`,
      )
      setVariables([
        { scope: "workflow", variables: vars.variables?.workflow || {} },
        { scope: "execution_data", variables: vars.variables || {} },
      ])
    } catch (error) {
      console.error("Failed to load variables:", error)
    }
  }

  useEffect(() => {
    if (debugMode) {
      loadDebugState()
      loadVariables()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debugMode, loadDebugState, loadVariables])

  const enableDebugMode = async () => {
    setLoading(true)
    try {
      await apiRequest(
        `/api/v1/workflows/executions/${executionId}/debug/enable`,
        {
          method: "POST",
        },
      )
      setDebugMode(true)
      toast({
        title: "Debug mode enabled",
        description: "Execution is now in debug mode",
      })
      await loadDebugState()
    } catch (error: any) {
      toast({
        title: "Failed to enable debug mode",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const disableDebugMode = async () => {
    setLoading(true)
    try {
      await apiRequest(
        `/api/v1/workflows/executions/${executionId}/debug/disable`,
        {
          method: "POST",
        },
      )
      setDebugMode(false)
      toast({
        title: "Debug mode disabled",
        description: "Execution resumed",
      })
    } catch (error: any) {
      toast({
        title: "Failed to disable debug mode",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const stepOver = async () => {
    setLoading(true)
    try {
      const result = await apiRequest(
        `/api/v1/workflows/executions/${executionId}/debug/step`,
        {
          method: "POST",
        },
      )
      await loadDebugState()
      await loadVariables()
      toast({
        title: "Step executed",
        description: `Current node: ${result.current_node_id || "none"}`,
      })
    } catch (error: any) {
      toast({
        title: "Failed to step",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const toggleBreakpoint = async (nodeId: string) => {
    try {
      if (breakpoints.has(nodeId)) {
        await apiRequest(
          `/api/v1/workflows/executions/${executionId}/debug/breakpoint/${nodeId}`,
          { method: "DELETE" },
        )
        setBreakpoints((prev) => {
          const next = new Set(prev)
          next.delete(nodeId)
          return next
        })
      } else {
        await apiRequest(
          `/api/v1/workflows/executions/${executionId}/debug/breakpoint`,
          {
            method: "POST",
            body: JSON.stringify({ node_id: nodeId }),
          },
        )
        setBreakpoints((prev) => new Set(prev).add(nodeId))
      }
    } catch (error: any) {
      toast({
        title: "Failed to toggle breakpoint",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Bug className="h-5 w-5" />
              Debug Panel
            </CardTitle>
            <CardDescription>Execution ID: {executionId}</CardDescription>
          </div>
          {onClose && (
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="controls">
          <TabsList>
            <TabsTrigger value="controls">Controls</TabsTrigger>
            <TabsTrigger value="state">State</TabsTrigger>
            <TabsTrigger value="variables">Variables</TabsTrigger>
            <TabsTrigger value="breakpoints">Breakpoints</TabsTrigger>
          </TabsList>

          <TabsContent value="controls" className="space-y-4">
            <div className="flex items-center gap-2">
              {!debugMode ? (
                <Button onClick={enableDebugMode} disabled={loading}>
                  <Play className="h-4 w-4 mr-2" />
                  Enable Debug Mode
                </Button>
              ) : (
                <>
                  <Button onClick={stepOver} disabled={loading}>
                    <StepForward className="h-4 w-4 mr-2" />
                    Step Over
                  </Button>
                  <Button
                    onClick={disableDebugMode}
                    disabled={loading}
                    variant="outline"
                  >
                    <Pause className="h-4 w-4 mr-2" />
                    Disable Debug Mode
                  </Button>
                </>
              )}
            </div>

            {debugState && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Status:</span>
                  <Badge
                    variant={
                      debugState.status === "running" ? "default" : "secondary"
                    }
                  >
                    {debugState.status}
                  </Badge>
                </div>
                {debugState.currentNodeId && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Current Node:</span>
                    <code className="text-sm bg-muted px-2 py-1 rounded">
                      {debugState.currentNodeId}
                    </code>
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="state">
            <ScrollArea className="h-[400px]">
              <pre className="text-xs bg-muted p-4 rounded">
                {JSON.stringify(debugState, null, 2)}
              </pre>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="variables">
            <ScrollArea className="h-[400px]">
              <div className="space-y-4">
                {variables.map((scope) => (
                  <div key={scope.scope}>
                    <h4 className="font-semibold mb-2">{scope.scope}</h4>
                    <pre className="text-xs bg-muted p-4 rounded">
                      {JSON.stringify(scope.variables, null, 2)}
                    </pre>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="breakpoints">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Click on nodes in the workflow to set breakpoints
              </p>
              {breakpoints.size === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No breakpoints set
                </p>
              ) : (
                <div className="space-y-1">
                  {Array.from(breakpoints).map((nodeId) => (
                    <div
                      key={nodeId}
                      className="flex items-center justify-between p-2 bg-muted rounded"
                    >
                      <code className="text-sm">{nodeId}</code>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => toggleBreakpoint(nodeId)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
