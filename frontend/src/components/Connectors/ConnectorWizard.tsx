/**
 * Connector Registration Wizard Component
 *
 * Multi-step wizard for registering new connectors.
 */

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { MonacoEditor } from "@/components/Common/MonacoEditor"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import { supabase } from "@/lib/supabase"

interface ConnectorWizardProps {
  onSuccess?: () => void
  onClose?: () => void
  endpoint?: string // Optional endpoint override (for admin)
  isPlatform?: boolean // Whether this is a platform connector
}

export function ConnectorWizard({ onSuccess, endpoint, isPlatform = false }: ConnectorWizardProps) {
  const [step, setStep] = useState(1)
  const [manifest, setManifest] = useState("")
  const [wheelUrl, setWheelUrl] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        showErrorToast("You must be logged in to register connectors")
        return
      }

      let parsedManifest
      try {
        parsedManifest = JSON.parse(manifest)
      } catch (e) {
        showErrorToast("Invalid JSON in manifest")
        return
      }

      const registerEndpoint = endpoint || "/api/v1/connectors/register"
      const response = await fetch(registerEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          manifest: parsedManifest,
          wheel_url: wheelUrl || undefined,
          is_platform: isPlatform,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to register connector")
      }

      showSuccessToast("Connector registered successfully")
      if (onSuccess) {
        onSuccess()
      }
    } catch (error) {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to register connector",
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <Tabs value={step.toString()} onValueChange={(v) => setStep(Number(v))}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="1">Manifest</TabsTrigger>
          <TabsTrigger value="2" disabled={!manifest}>
            Review & Submit
          </TabsTrigger>
        </TabsList>

        <TabsContent value="1" className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="manifest">Connector Manifest (JSON)</Label>
            <MonacoEditor
              value={manifest}
              onChange={(value) => setManifest(value || "")}
              language="json"
              height="400px"
              className="border rounded-md overflow-hidden"
            />
            <p className="text-sm text-muted-foreground">
              Paste the connector manifest JSON. This should include name, slug,
              version, actions, triggers, and OAuth configuration.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="wheelUrl">Wheel URL (Optional)</Label>
            <Input
              id="wheelUrl"
              type="url"
              placeholder="https://synthralos.ai/connector-1.0.0-py3-none-any.whl"
              value={wheelUrl}
              onChange={(e) => setWheelUrl(e.target.value)}
            />
            <p className="text-sm text-muted-foreground">
              URL to download the connector wheel file. If not provided, the
              connector must be installed separately.
            </p>
          </div>

          <div className="flex justify-end">
            <Button onClick={() => setStep(2)} disabled={!manifest}>
              Next: Review
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="2" className="space-y-4">
          <div className="space-y-4">
            <div>
              <Label>Manifest Preview</Label>
              <pre className="mt-2 rounded-md bg-muted p-4 text-sm overflow-auto max-h-96">
                {manifest ? JSON.stringify(JSON.parse(manifest), null, 2) : "No manifest"}
              </pre>
            </div>

            {wheelUrl && (
              <div>
                <Label>Wheel URL</Label>
                <div className="mt-2 text-sm text-muted-foreground">{wheelUrl}</div>
              </div>
            )}
          </div>

          <div className="flex justify-between">
            <Button variant="outline" onClick={() => setStep(1)}>
              Back
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? "Registering..." : "Register Connector"}
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}

