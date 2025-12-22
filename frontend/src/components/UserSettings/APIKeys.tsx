/**
 * API Keys Management Component
 *
 * Allows users to manage their API keys for external services.
 */

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Copy, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { apiRequest } from "@/lib/api"

interface APIKey {
  id: string
  service_name: string
  service_display_name: string
  credential_type: string | null
  masked_key: string
  is_active: boolean
  last_used_at: string | null
  created_at: string
  updated_at: string
}

interface ServiceDefinition {
  display_name: string
  credential_types: string[]
}

// Service definitions (matching backend)
// Only includes services that are actually integrated and used in the platform
const SERVICE_DEFINITIONS: Record<string, ServiceDefinition> = {
  // LLM Providers (actually used in chat_processor.py and agent frameworks)
  openai: {
    display_name: "OpenAI",
    credential_types: ["api_key"],
  },
  anthropic: {
    display_name: "Anthropic Claude",
    credential_types: ["api_key"],
  },
  "google-ai": {
    display_name: "Google AI (Gemini)",
    credential_types: ["api_key"],
  },
  cohere: {
    display_name: "Cohere",
    credential_types: ["api_key"],
  },
  huggingface: {
    display_name: "Hugging Face",
    credential_types: ["api_key"],
  },
  replicate: {
    display_name: "Replicate",
    credential_types: ["api_key"],
  },
  // OCR Services (actually used in OCR service)
  "google-vision": {
    display_name: "Google Vision API",
    credential_types: ["api_key"],
  },
  // Social Media (actually used in OSINT service and connector manifests)
  twitter: {
    display_name: "Twitter/X",
    credential_types: ["bearer_token", "api_key_secret", "oauth"],
  },
  reddit: {
    display_name: "Reddit",
    credential_types: ["oauth"],
  },
  linkedin: {
    display_name: "LinkedIn",
    credential_types: ["oauth"],
  },
  // Code Execution (actually used in code execution service)
  e2b: {
    display_name: "E2B (Code Sandbox)",
    credential_types: ["api_key"],
  },
  // Vector Databases (actually used in RAG service)
  chromadb: {
    display_name: "ChromaDB",
    credential_types: ["auth_token"],
  },
  weaviate: {
    display_name: "Weaviate",
    credential_types: ["api_key"],
  },
  // Observability (actually used - LangSmith in dependencies)
  langsmith: {
    display_name: "LangSmith",
    credential_types: ["api_key"],
  },
  // Storage (actually used - connector manifests exist)
  "aws-s3": {
    display_name: "AWS S3",
    credential_types: ["access_key_secret"],
  },
  "azure-blob": {
    display_name: "Azure Blob Storage",
    credential_types: ["connection_string"],
  },
}

// Group services by category
const SERVICE_CATEGORIES = {
  "LLM Providers": [
    "openai",
    "anthropic",
    "google-ai",
    "cohere",
    "huggingface",
    "replicate",
  ],
  "OCR Services": ["google-vision"],
  "Social Media": ["twitter", "reddit", "linkedin"],
  "Code Execution": ["e2b"],
  "Vector Databases": ["chromadb", "weaviate"],
  Observability: ["langsmith"],
  Storage: ["aws-s3", "azure-blob"],
}

const createAPIKeySchema = (credentialType: string | null) => {
  const baseSchema = {
    service_name: z.string().min(1, "Service is required"),
    credential_type: z.string().nullable(),
    api_key: z.string().min(1, "API key is required"),
  }

  // Twitter-specific fields
  if (credentialType === "api_key_secret") {
    return z.object({
      ...baseSchema,
      api_secret: z.string().min(1, "API secret is required"),
    })
  }

  if (credentialType === "oauth") {
    return z.object({
      ...baseSchema,
      access_token: z.string().min(1, "Access token is required"),
      access_token_secret: z.string().min(1, "Access token secret is required"),
    })
  }

  return z.object(baseSchema)
}

export function APIKeys() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [selectedService, setSelectedService] = useState<string>("")
  const [selectedCredentialType, setSelectedCredentialType] = useState<
    string | null
  >(null)

  // Fetch API keys
  const { data: apiKeys = [], isLoading } = useQuery<APIKey[]>({
    queryKey: ["user-api-keys"],
    queryFn: async () => {
      return apiRequest<APIKey[]>("/api/v1/users/me/api-keys")
    },
  })

  // Create API key mutation
  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      return apiRequest<APIKey>("/api/v1/users/me/api-keys", {
        method: "POST",
        body: JSON.stringify(data),
      })
    },
    onSuccess: () => {
      showSuccessToast("API key added successfully")
      queryClient.invalidateQueries({ queryKey: ["user-api-keys"] })
      setIsAddDialogOpen(false)
      form.reset()
    },
    onError: (error: Error) => {
      showErrorToast(error.message || "Failed to add API key")
    },
  })

  // Delete API key mutation
  const deleteMutation = useMutation({
    mutationFn: async (keyId: string) => {
      return apiRequest(`/api/v1/users/me/api-keys/${keyId}`, {
        method: "DELETE",
      })
    },
    onSuccess: () => {
      showSuccessToast("API key deleted successfully")
      queryClient.invalidateQueries({ queryKey: ["user-api-keys"] })
    },
    onError: (error: Error) => {
      showErrorToast(error.message || "Failed to delete API key")
    },
  })

  // Test API key mutation
  const testMutation = useMutation({
    mutationFn: async (keyId: string) => {
      return apiRequest<{ valid: boolean; message: string }>(
        `/api/v1/users/me/api-keys/${keyId}/test`,
        {
          method: "POST",
        },
      )
    },
    onSuccess: (data) => {
      if (data.valid) {
        showSuccessToast("API key is valid")
      } else {
        showErrorToast(data.message || "API key validation failed")
      }
      queryClient.invalidateQueries({ queryKey: ["user-api-keys"] })
    },
    onError: (error: Error) => {
      showErrorToast(error.message || "Failed to test API key")
    },
  })

  // Form for adding API key
  const form = useForm({
    resolver: zodResolver(createAPIKeySchema(selectedCredentialType) as any),
    defaultValues: {
      service_name: "",
      credential_type: null,
      api_key: "",
      api_secret: "",
      access_token: "",
      access_token_secret: "",
    },
  })

  const handleServiceChange = (serviceName: string) => {
    setSelectedService(serviceName)
    const service = SERVICE_DEFINITIONS[serviceName]
    if (service && service.credential_types.length > 0) {
      const defaultType =
        service.credential_types.length === 1
          ? service.credential_types[0]
          : null
      setSelectedCredentialType(defaultType)
      form.setValue("service_name", serviceName)
      form.setValue("credential_type", defaultType)
    }
  }

  const handleCredentialTypeChange = (credentialType: string) => {
    setSelectedCredentialType(credentialType)
    form.setValue("credential_type", credentialType)
  }

  const onSubmit = (data: any) => {
    const payload: any = {
      service_name: data.service_name,
      credential_type: data.credential_type,
      api_key: data.api_key,
    }

    if (
      data.credential_type === "api_key_secret" ||
      data.credential_type === "access_key_secret"
    ) {
      payload.api_secret = data.api_secret
    }

    if (data.credential_type === "oauth") {
      payload.access_token = data.access_token
      payload.access_token_secret = data.access_token_secret
    }

    createMutation.mutate(payload)
  }

  const handleCopyKey = (maskedKey: string) => {
    navigator.clipboard.writeText(maskedKey)
    showSuccessToast("Copied to clipboard")
  }

  const handleDelete = (keyId: string, serviceName: string) => {
    if (
      !confirm(
        `Are you sure you want to delete the API key for ${serviceName}? This action cannot be undone.`,
      )
    ) {
      return
    }
    deleteMutation.mutate(keyId)
  }

  const handleTest = (keyId: string) => {
    testMutation.mutate(keyId)
  }

  // Group API keys by category
  const groupedKeys: Record<string, APIKey[]> = {}
  Object.keys(SERVICE_CATEGORIES).forEach((category) => {
    groupedKeys[category] = []
  })
  groupedKeys.Other = []

  apiKeys.forEach((key) => {
    let found = false
    Object.entries(SERVICE_CATEGORIES).forEach(([category, services]) => {
      if (services.includes(key.service_name)) {
        if (!groupedKeys[category]) {
          groupedKeys[category] = []
        }
        groupedKeys[category].push(key)
        found = true
      }
    })
    if (!found) {
      groupedKeys.Other.push(key)
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">API Keys</h3>
          <p className="text-sm text-muted-foreground">
            Manage your API keys for external services
          </p>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add API Key
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add API Key</DialogTitle>
              <DialogDescription>
                Add an API key for an external service. Keys are encrypted and
                stored securely.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4"
              >
                <FormField
                  control={form.control}
                  name="service_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Service</FormLabel>
                      <Select
                        onValueChange={(value) => {
                          field.onChange(value)
                          handleServiceChange(value)
                        }}
                        value={field.value}
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a service" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {Object.entries(SERVICE_DEFINITIONS).map(
                            ([key, service]) => (
                              <SelectItem key={key} value={key}>
                                {service.display_name}
                              </SelectItem>
                            ),
                          )}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {selectedService &&
                  SERVICE_DEFINITIONS[selectedService] &&
                  SERVICE_DEFINITIONS[selectedService].credential_types.length >
                    1 && (
                    <FormField
                      control={form.control}
                      name="credential_type"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Credential Type</FormLabel>
                          <Select
                            onValueChange={(value) => {
                              field.onChange(value)
                              handleCredentialTypeChange(value)
                            }}
                            value={field.value || ""}
                          >
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select credential type" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              {SERVICE_DEFINITIONS[
                                selectedService
                              ].credential_types.map((type) => (
                                <SelectItem key={type} value={type}>
                                  {type === "api_key"
                                    ? "API Key"
                                    : type === "bearer_token"
                                      ? "Bearer Token"
                                      : type === "auth_token"
                                        ? "Auth Token"
                                        : type === "secret_key"
                                          ? "Secret Key"
                                          : type === "api_key_secret"
                                            ? "API Key + Secret"
                                            : type === "access_key_secret"
                                              ? "Access Key + Secret"
                                              : type === "oauth"
                                                ? "OAuth"
                                                : type === "service_account"
                                                  ? "Service Account"
                                                  : type === "connection_string"
                                                    ? "Connection String"
                                                    : type}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}

                <FormField
                  control={form.control}
                  name="api_key"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        {selectedCredentialType === "bearer_token"
                          ? "Bearer Token"
                          : selectedCredentialType === "auth_token"
                            ? "Auth Token"
                            : selectedCredentialType === "secret_key"
                              ? "Secret Key"
                              : selectedCredentialType === "service_account"
                                ? "Service Account JSON"
                                : selectedCredentialType === "connection_string"
                                  ? "Connection String"
                                  : selectedCredentialType ===
                                      "access_key_secret"
                                    ? "Access Key"
                                    : "API Key"}
                      </FormLabel>
                      <FormControl>
                        <Textarea
                          {...field}
                          placeholder={
                            selectedCredentialType === "service_account"
                              ? "Paste your service account JSON"
                              : selectedCredentialType === "connection_string"
                                ? "Enter your connection string"
                                : "Enter your API key"
                          }
                          rows={
                            selectedCredentialType === "service_account" ? 8 : 3
                          }
                        />
                      </FormControl>
                      <FormDescription>
                        {selectedCredentialType === "service_account"
                          ? "Paste your complete service account JSON. It will be encrypted and stored securely."
                          : "Your credentials will be encrypted and stored securely."}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {(selectedCredentialType === "api_key_secret" ||
                  selectedCredentialType === "access_key_secret") && (
                  <FormField
                    control={form.control}
                    name="api_secret"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          {selectedCredentialType === "access_key_secret"
                            ? "Secret Access Key"
                            : "API Secret"}
                        </FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            placeholder="Enter your secret"
                            rows={3}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                )}

                {selectedCredentialType === "oauth" && (
                  <>
                    <FormField
                      control={form.control}
                      name="access_token"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Access Token</FormLabel>
                          <FormControl>
                            <Textarea
                              {...field}
                              placeholder="Enter your access token"
                              rows={3}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    <FormField
                      control={form.control}
                      name="access_token_secret"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Access Token Secret</FormLabel>
                          <FormControl>
                            <Textarea
                              {...field}
                              placeholder="Enter your access token secret"
                              rows={3}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </>
                )}

                <div className="flex justify-end gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsAddDialogOpen(false)
                      form.reset()
                    }}
                  >
                    Cancel
                  </Button>
                  <LoadingButton
                    type="submit"
                    loading={createMutation.isPending}
                  >
                    Add API Key
                  </LoadingButton>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="text-center py-8 text-muted-foreground">
          Loading API keys...
        </div>
      ) : apiKeys.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No API keys configured</p>
          <p className="text-sm mt-2">
            Add an API key to get started with external services
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedKeys).map(
            ([category, keys]) =>
              keys.length > 0 && (
                <div key={category} className="space-y-2">
                  <h4 className="text-sm font-semibold text-muted-foreground uppercase">
                    {category}
                  </h4>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Service</TableHead>
                        <TableHead>Credential Type</TableHead>
                        <TableHead>Key</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Last Used</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {keys.map((key) => (
                        <TableRow key={key.id}>
                          <TableCell className="font-medium">
                            {key.service_display_name}
                          </TableCell>
                          <TableCell>
                            {key.credential_type ? (
                              <Badge variant="outline">
                                {key.credential_type === "api_key"
                                  ? "API Key"
                                  : key.credential_type === "bearer_token"
                                    ? "Bearer Token"
                                    : key.credential_type === "auth_token"
                                      ? "Auth Token"
                                      : key.credential_type === "secret_key"
                                        ? "Secret Key"
                                        : key.credential_type ===
                                            "api_key_secret"
                                          ? "API Key + Secret"
                                          : key.credential_type ===
                                              "access_key_secret"
                                            ? "Access Key + Secret"
                                            : key.credential_type === "oauth"
                                              ? "OAuth"
                                              : key.credential_type ===
                                                  "service_account"
                                                ? "Service Account"
                                                : key.credential_type ===
                                                    "connection_string"
                                                  ? "Connection String"
                                                  : key.credential_type}
                              </Badge>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <code className="text-sm">{key.masked_key}</code>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleCopyKey(key.masked_key)}
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={key.is_active ? "default" : "secondary"}
                            >
                              {key.is_active ? "Active" : "Inactive"}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {key.last_used_at
                              ? new Date(key.last_used_at).toLocaleDateString()
                              : "Never"}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleTest(key.id)}
                                disabled={testMutation.isPending}
                              >
                                Test
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() =>
                                  handleDelete(key.id, key.service_display_name)
                                }
                                disabled={deleteMutation.isPending}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ),
          )}
        </div>
      )}
    </div>
  )
}
