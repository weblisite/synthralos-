/**
 * Tool Registration Component
 *
 * Allows users to register new code tools.
 * Integrates unused endpoint:
 * - POST /api/v1/code/register-tool
 */

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Code2, Loader2, Plus } from "lucide-react"
import { useState } from "react"
import { MonacoEditor } from "@/components/Common/MonacoEditor"
import { Button } from "@/components/ui/button"
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
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface ToolRegistrationData {
  name: string
  description: string
  language: string
  version: string
  author?: string
  repository_url?: string
  documentation_url?: string
  code?: string
  requirements?: string
  metadata?: Record<string, any>
}

export function ToolRegistration() {
  const [isOpen, setIsOpen] = useState(false)
  const [formData, setFormData] = useState<ToolRegistrationData>({
    name: "",
    description: "",
    language: "python",
    version: "1.0.0",
    author: "",
    repository_url: "",
    documentation_url: "",
    code: "",
    requirements: "",
  })
  const [metadataJson, setMetadataJson] = useState("{}")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const registrationMutation = useMutation({
    mutationFn: async (data: ToolRegistrationData) => {
      let parsedMetadata = {}
      try {
        parsedMetadata = JSON.parse(metadataJson)
      } catch (_e) {
        throw new Error("Invalid JSON in metadata field")
      }

      return apiClient.request("/api/v1/code/register-tool", {
        method: "POST",
        body: JSON.stringify({
          ...data,
          metadata: parsedMetadata,
        }),
      })
    },
    onSuccess: () => {
      showSuccessToast("Tool registered successfully")
      queryClient.invalidateQueries({ queryKey: ["codeTools"] })
      setIsOpen(false)
      // Reset form
      setFormData({
        name: "",
        description: "",
        language: "python",
        version: "1.0.0",
        author: "",
        repository_url: "",
        documentation_url: "",
        code: "",
        requirements: "",
      })
      setMetadataJson("{}")
    },
    onError: (error: Error) => {
      showErrorToast(
        error instanceof Error ? error.message : "Failed to register tool",
      )
    },
  })

  const handleSubmit = () => {
    if (!formData.name || !formData.description || !formData.language) {
      showErrorToast("Please fill in all required fields")
      return
    }
    registrationMutation.mutate(formData)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Register Tool
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Code2 className="h-5 w-5" />
            Register New Code Tool
          </DialogTitle>
          <DialogDescription>
            Register a new code tool that can be used in workflows and code
            execution
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">
                Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="my-tool"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="version">
                Version <span className="text-destructive">*</span>
              </Label>
              <Input
                id="version"
                value={formData.version}
                onChange={(e) =>
                  setFormData({ ...formData, version: e.target.value })
                }
                placeholder="1.0.0"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">
              Description <span className="text-destructive">*</span>
            </Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="A tool that does something useful..."
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="language">
                Language <span className="text-destructive">*</span>
              </Label>
              <Input
                id="language"
                value={formData.language}
                onChange={(e) =>
                  setFormData({ ...formData, language: e.target.value })
                }
                placeholder="python"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="author">Author</Label>
              <Input
                id="author"
                value={formData.author}
                onChange={(e) =>
                  setFormData({ ...formData, author: e.target.value })
                }
                placeholder="Your Name"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="repository_url">Repository URL</Label>
            <Input
              id="repository_url"
              type="url"
              value={formData.repository_url}
              onChange={(e) =>
                setFormData({ ...formData, repository_url: e.target.value })
              }
              placeholder="https://github.com/user/repo"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="documentation_url">Documentation URL</Label>
            <Input
              id="documentation_url"
              type="url"
              value={formData.documentation_url}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  documentation_url: e.target.value,
                })
              }
              placeholder="https://docs.example.com"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="code">Code</Label>
            <MonacoEditor
              value={formData.code || ""}
              onChange={(value) =>
                setFormData({ ...formData, code: value || "" })
              }
              language={formData.language}
              height="200px"
              className="border rounded-md overflow-hidden"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="requirements">Requirements</Label>
            <Textarea
              id="requirements"
              value={formData.requirements}
              onChange={(e) =>
                setFormData({ ...formData, requirements: e.target.value })
              }
              placeholder="requests==2.31.0&#10;numpy==1.24.0"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="metadata">Metadata (JSON)</Label>
            <MonacoEditor
              value={metadataJson}
              onChange={(value) => setMetadataJson(value || "{}")}
              language="json"
              height="150px"
              className="border rounded-md overflow-hidden"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={registrationMutation.isPending}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={registrationMutation.isPending}
            >
              {registrationMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Registering...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Register Tool
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
