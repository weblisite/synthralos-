/**
 * Test Panel Component
 *
 * Provides workflow testing interface:
 * - Run workflow in test mode
 * - Set mock node results
 * - Validate test results
 */

import { CheckCircle2, Loader2, Play, XCircle } from "lucide-react"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiRequest } from "@/lib/api"

interface TestPanelProps {
  workflowId: string
}

export function TestPanel({ workflowId }: TestPanelProps) {
  const [testData, setTestData] = useState("{}")
  const [mockNodes, setMockNodes] = useState<Record<string, string>>({})
  const [executionId, setExecutionId] = useState<string | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const addMockNode = () => {
    const newNodeId = `node_${Object.keys(mockNodes).length + 1}`
    setMockNodes((prev) => ({ ...prev, [newNodeId]: "{}" }))
  }

  const removeMockNode = (nodeId: string) => {
    setMockNodes((prev) => {
      const next = { ...prev }
      delete next[nodeId]
      return next
    })
  }

  const runTest = async () => {
    setIsRunning(true)
    setTestResult(null)

    try {
      let parsedTestData = {}
      try {
        parsedTestData = JSON.parse(testData)
      } catch (_e) {
        showErrorToast("Test data must be valid JSON", "Invalid JSON")
        return
      }

      const parsedMockNodes: Record<string, any> = {}
      for (const [nodeId, mockData] of Object.entries(mockNodes)) {
        try {
          parsedMockNodes[nodeId] = JSON.parse(mockData)
        } catch (_e) {
          showErrorToast(
            `Mock data for ${nodeId} must be valid JSON`,
            "Invalid JSON",
          )
          return
        }
      }

      const result = await apiRequest<{ execution_id: string }>(
        `/api/v1/workflows/${workflowId}/test`,
        {
          method: "POST",
          body: JSON.stringify({
            test_data: parsedTestData,
            mock_nodes: parsedMockNodes,
          }),
        },
      )

      setExecutionId(result.execution_id)
      setTestResult(result)

      showSuccessToast(`Execution ID: ${result.execution_id}`, "Test started")
    } catch (error: any) {
      showErrorToast(error.message || "Test failed", "Test failed")
    } finally {
      setIsRunning(false)
    }
  }

  const validateResult = async () => {
    if (!executionId) return

    try {
      const result = await apiRequest<{ valid: boolean; errors?: string[] }>(
        `/api/v1/workflows/executions/${executionId}/test/validate`,
        {
          method: "POST",
          body: JSON.stringify({
            expected_outputs: testResult?.expected_outputs || {},
          }),
        },
      )

      setTestResult(result)

      if (result.valid) {
        showSuccessToast("All validations passed", "Test passed")
      } else {
        showErrorToast(
          `${result.errors?.length || 0} errors found`,
          "Test failed",
        )
      }
    } catch (error: any) {
      showErrorToast(error.message || "Validation failed", "Validation failed")
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Test Workflow</CardTitle>
        <CardDescription>
          Run workflow in test mode with mock data
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="test-data">Test Data (JSON)</Label>
          <Textarea
            id="test-data"
            value={testData}
            onChange={(e) => setTestData(e.target.value)}
            placeholder='{"key": "value"}'
            className="font-mono text-sm"
            rows={4}
          />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Mock Node Results</Label>
            <Button variant="outline" size="sm" onClick={addMockNode}>
              Add Mock Node
            </Button>
          </div>
          <ScrollArea className="h-32">
            <div className="space-y-2">
              {Object.entries(mockNodes).map(([nodeId, mockData]) => (
                <div key={nodeId} className="flex items-center gap-2">
                  <Input
                    value={nodeId}
                    onChange={(e) => {
                      const newMockNodes = { ...mockNodes }
                      delete newMockNodes[nodeId]
                      newMockNodes[e.target.value] = mockData
                      setMockNodes(newMockNodes)
                    }}
                    placeholder="Node ID"
                    className="flex-1"
                  />
                  <Textarea
                    value={mockData}
                    onChange={(e) =>
                      setMockNodes((prev) => ({
                        ...prev,
                        [nodeId]: e.target.value,
                      }))
                    }
                    placeholder='{"output": "value"}'
                    className="flex-1 font-mono text-sm"
                    rows={2}
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeMockNode(nodeId)}
                  >
                    <XCircle className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>

        <Button onClick={runTest} disabled={isRunning} className="w-full">
          {isRunning ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Running Test...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Run Test
            </>
          )}
        </Button>

        {testResult && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Test Result</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Status:</span>
                <Badge
                  variant={
                    testResult.status === "completed" ? "default" : "secondary"
                  }
                >
                  {testResult.status}
                </Badge>
              </div>
              {testResult.valid !== undefined && (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Valid:</span>
                  {testResult.valid ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                  )}
                </div>
              )}
              {testResult.errors && testResult.errors.length > 0 && (
                <div className="space-y-1">
                  <span className="text-sm font-medium">Errors:</span>
                  <ul className="list-disc list-inside text-sm text-destructive">
                    {testResult.errors.map((error: string, idx: number) => (
                      <li key={idx}>{error}</li>
                    ))}
                  </ul>
                </div>
              )}
              {executionId && (
                <Button variant="outline" size="sm" onClick={validateResult}>
                  Validate Result
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  )
}
