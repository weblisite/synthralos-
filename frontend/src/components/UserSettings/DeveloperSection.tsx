import { Code, ExternalLink, Plus } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"

export function DeveloperSection() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [newTokenName, setNewTokenName] = useState("")

  const createTokenMutation = {
    isPending: false,
    mutate: (_name: string) => {
      // TODO: Implement API token creation endpoint
      showSuccessToast("API tokens", "Personal access tokens coming soon")
      setNewTokenName("")
    },
  }

  const handleCreateToken = () => {
    if (!newTokenName.trim()) {
      showErrorToast("Token name required")
      return
    }
    createTokenMutation.mutate(newTokenName.trim())
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Developer</h2>
        <p className="text-muted-foreground">
          Manage API tokens, webhooks, and developer resources
        </p>
      </div>

      {/* API Tokens */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code className="h-5 w-5" />
            Personal Access Tokens
          </CardTitle>
          <CardDescription>
            Generate and manage API access tokens for programmatic access
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Token name (e.g., 'Production API', 'CI/CD')"
              value={newTokenName}
              onChange={(e) => setNewTokenName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleCreateToken()
                }
              }}
            />
            <LoadingButton
              onClick={handleCreateToken}
              loading={createTokenMutation.isPending}
            >
              <Plus className="mr-2 h-4 w-4" />
              Create Token
            </LoadingButton>
          </div>
          <p className="text-sm text-muted-foreground">
            Personal access tokens allow you to authenticate with the API. Note:
            User API keys for external services are managed in the{" "}
            <a href="/settings/api-keys" className="text-primary underline">
              API Keys
            </a>{" "}
            section.
          </p>
        </CardContent>
      </Card>

      {/* Webhook Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle>Webhook Endpoints</CardTitle>
          <CardDescription>
            Configure webhook endpoints for receiving events
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Webhook management is available in workflow settings. Configure
            webhooks for individual workflows to receive execution events.
          </p>
          <Button variant="outline" asChild>
            <a href="/workflows">
              <ExternalLink className="mr-2 h-4 w-4" />
              Go to Workflows
            </a>
          </Button>
        </CardContent>
      </Card>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle>Documentation</CardTitle>
          <CardDescription>
            API documentation and developer resources
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">API Documentation</p>
                <p className="text-sm text-muted-foreground">
                  Interactive OpenAPI documentation for all endpoints
                </p>
              </div>
              <Button variant="outline" asChild>
                <a href="/api/docs" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Open Docs
                </a>
              </Button>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">OpenAPI Schema</p>
                <p className="text-sm text-muted-foreground">
                  Download the OpenAPI JSON schema
                </p>
              </div>
              <Button variant="outline" asChild>
                <a
                  href="/api/v1/openapi.json"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Download
                </a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
