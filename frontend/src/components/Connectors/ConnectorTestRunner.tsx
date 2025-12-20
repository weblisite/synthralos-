/**
 * Connector Test Runner Component
 *
 * Allows testing connector actions and triggers.
 */

import { Loader2, Play } from "lucide-react"
import { useState } from "react"
import { MonacoEditor } from "@/components/Common/MonacoEditor"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

interface ConnectorTestRunnerProps {
  connectorSlug: string
  actions?: string[]
  triggers?: string[]
}

export function ConnectorTestRunner({
  connectorSlug,
  actions = [],
  triggers = [],
}: ConnectorTestRunnerProps) {
  const [testType, setTestType] = useState<"action" | "trigger">("action")
  const [selectedAction, setSelectedAction] = useState<string>("")
  const [selectedTrigger, setSelectedTrigger] = useState<string>("")
  const [inputData, setInputData] = useState("{}")
  const [result, setResult] = useState<any>(null)
  const [isRunning, setIsRunning] = useState(false)
  const { showErrorToast } = useCustomToast()

  const handleTest = async () => {
    setIsRunning(true)
    setResult(null)

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        showErrorToast("You must be logged in to test connectors")
        return
      }

      let parsedInput
      try {
        parsedInput = JSON.parse(inputData)
      } catch (_e) {
        showErrorToast("Invalid JSON in input data")
        return
      }

      if (testType === "action" && selectedAction) {
        const response = await fetch(
          `/api/v1/connectors/${connectorSlug}/${selectedAction}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${session.access_token}`,
            },
            body: JSON.stringify(parsedInput),
          },
        )

        if (!response.ok) {
          const error = await response.json()
          throw new Error(error.detail || "Test failed")
        }

        const data = await response.json()
        setResult(data)
      } else if (testType === "trigger" && selectedTrigger) {
        // Trigger testing would require webhook simulation
        showErrorToast(
          "Trigger testing requires webhook simulation (not implemented)",
        )
      }
    } catch (error) {
      showErrorToast(error instanceof Error ? error.message : "Test failed")
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Test Connector</CardTitle>
        <CardDescription>
          Test connector actions and triggers before using them in workflows
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <Label>Test Type</Label>
          <Select
            value={testType}
            onValueChange={(v) => setTestType(v as "action" | "trigger")}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="action">Action</SelectItem>
              <SelectItem value="trigger">Trigger</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {testType === "action" && actions.length > 0 && (
          <div className="space-y-2">
            <Label>Action</Label>
            <Select value={selectedAction} onValueChange={setSelectedAction}>
              <SelectTrigger>
                <SelectValue placeholder="Select an action" />
              </SelectTrigger>
              <SelectContent>
                {actions.map((action) => (
                  <SelectItem key={action} value={action}>
                    {action}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {testType === "trigger" && triggers.length > 0 && (
          <div className="space-y-2">
            <Label>Trigger</Label>
            <Select value={selectedTrigger} onValueChange={setSelectedTrigger}>
              <SelectTrigger>
                <SelectValue placeholder="Select a trigger" />
              </SelectTrigger>
              <SelectContent>
                {triggers.map((trigger) => (
                  <SelectItem key={trigger} value={trigger}>
                    {trigger}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        <div className="space-y-2">
          <Label>Input Data (JSON)</Label>
          <MonacoEditor
            value={inputData}
            onChange={(value) => setInputData(value || "{}")}
            language="json"
            height="200px"
            className="border rounded-md overflow-hidden"
          />
        </div>

        <Button
          onClick={handleTest}
          disabled={
            isRunning ||
            (testType === "action" && !selectedAction) ||
            (testType === "trigger" && !selectedTrigger)
          }
          className="w-full"
        >
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

        {result && (
          <div className="space-y-2">
            <Label>Result</Label>
            <pre className="rounded-md bg-muted p-4 text-sm overflow-auto max-h-96">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
