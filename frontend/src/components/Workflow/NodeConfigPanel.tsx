/**
 * Node Configuration Panel
 *
 * Side panel for configuring selected workflow nodes.
 */

import type { Edge, Node } from "@xyflow/react"
import { Copy, Trash2, X } from "lucide-react"
import { useCallback, useEffect, useMemo, useState } from "react"
import { MonacoEditor } from "@/components/Common/MonacoEditor"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
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
import useCustomToast from "@/hooks/useCustomToast"
import { apiClient } from "@/lib/apiClient"

interface NodeConfig {
  trigger_type?: string
  cron_expression?: string
  webhook_method?: string
  prompt?: string
  model?: string
  connector_slug?: string
  action?: string
  oauth_scopes?: string[]
  personalization?: string
  language?: string
  code?: string
  runtime?: string
  expression?: string
  method?: string
  url?: string
  headers?: Record<string, string>
  body?: string
  index_id?: string
  query_requirements?: Record<string, any>
  document_url?: string
  engine?: string
  selectors?: string[]
  action_type?: string
  action_data?: Record<string, any>
  [key: string]: any
}

interface NodeConfigPanelProps {
  node: Node | null
  workflowId?: string | null
  nodes?: Node[]
  edges?: Edge[]
  onClose: () => void
  onUpdate: (nodeId: string, updates: Partial<Node>) => void
  onDelete?: (nodeId: string) => void
}

export function NodeConfigPanel({
  node,
  workflowId,
  nodes = [],
  edges = [],
  onClose,
  onUpdate,
  onDelete,
}: NodeConfigPanelProps) {
  const config: NodeConfig = useMemo(
    () => (node?.data?.config || {}) as NodeConfig,
    [node],
  )
  const { showSuccessToast } = useCustomToast()

  // State for connector scopes
  const [connectorScopes, setConnectorScopes] = useState<string[]>([])
  const [selectedScopes, setSelectedScopes] = useState<string[]>(
    config.oauth_scopes || [],
  )
  const [isLoadingScopes, setIsLoadingScopes] = useState(false)

  const handleConfigUpdate = useCallback(
    (key: string, value: any) => {
      if (!node) return
      const updatedConfig = { ...config, [key]: value }
      onUpdate(node.id, {
        data: {
          ...node.data,
          config: updatedConfig,
        },
      })
    },
    [node, config, onUpdate],
  )

  // Fetch connector scopes when connector node is selected
  useEffect(() => {
    if (node?.type === "connector" && config.connector_slug) {
      setIsLoadingScopes(true)
      apiClient
        .request(`/api/v1/connectors/${config.connector_slug}`)
        .then((details: any) => {
          const scopes =
            details.manifest?.oauth?.scopes || details.manifest?.scopes || []
          setConnectorScopes(scopes)
          // If no scopes selected yet, select all by default
          if (
            scopes.length > 0 &&
            (!config.oauth_scopes || config.oauth_scopes.length === 0)
          ) {
            setSelectedScopes(scopes)
            handleConfigUpdate("oauth_scopes", scopes)
          }
        })
        .catch((error) => {
          console.error("Failed to fetch connector scopes:", error)
        })
        .finally(() => {
          setIsLoadingScopes(false)
        })
    }
  }, [
    node?.type,
    config.connector_slug,
    config.oauth_scopes,
    handleConfigUpdate,
  ])

  // Calculate available fields from previous nodes for personalization
  const availableFields = useMemo(() => {
    if (!node || nodes.length === 0 || edges.length === 0) return []

    // Get all nodes that connect to this node
    const incomingEdges = edges.filter((e) => e.target === node.id)
    const previousNodes = nodes.filter((n) =>
      incomingEdges.some((e) => e.source === n.id),
    )

    // Extract available fields from previous nodes
    return previousNodes.map((prevNode) => {
      const nodeType = prevNode.type || "unknown"
      const nodeLabel = (prevNode.data?.label as string) || nodeType

      // Common fields based on node type
      let fields: string[] = ["output"]
      if (nodeType === "connector") {
        fields = ["output", "response", "data"]
      } else if (nodeType === "ai_prompt") {
        fields = ["output", "response", "content"]
      } else if (nodeType === "http_request") {
        fields = ["output", "response", "status", "body"]
      } else if (nodeType === "code") {
        fields = ["output", "result", "stdout", "stderr"]
      }

      return {
        nodeId: prevNode.id,
        nodeLabel,
        fields,
      }
    })
  }, [node, nodes, edges])

  if (!node) {
    return null
  }

  const handleLabelUpdate = (label: string) => {
    onUpdate(node.id, {
      data: {
        ...node.data,
        label,
      },
    })
  }

  const handleDelete = () => {
    if (!node || !onDelete) return

    // Confirm deletion
    if (
      window.confirm(
        `Are you sure you want to delete "${node.data.label || node.type}" node?`,
      )
    ) {
      onDelete(node.id)
      onClose()
    }
  }

  return (
    <div className="h-full bg-background flex flex-col">
      <div className="p-4 border-b flex items-center justify-between">
        <h2 className="text-lg font-semibold">Node Configuration</h2>
        <div className="flex items-center gap-2">
          {onDelete && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDelete}
              className="text-destructive hover:text-destructive hover:bg-destructive/10"
              title="Delete node (or press Delete key)"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="node-label">Label</Label>
          <Input
            id="node-label"
            value={(node.data.label as string) || ""}
            onChange={(e) => handleLabelUpdate(e.target.value)}
            placeholder="Node label"
          />
        </div>

        {node.type === "trigger" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="trigger-type">Trigger Type</Label>
              <Select
                value={config.trigger_type || "manual"}
                onValueChange={(value) =>
                  handleConfigUpdate("trigger_type", value)
                }
              >
                <SelectTrigger id="trigger-type">
                  <SelectValue placeholder="Select trigger type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manual">Manual</SelectItem>
                  <SelectItem value="webhook">Webhook</SelectItem>
                  <SelectItem value="schedule">Schedule (CRON)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {config.trigger_type === "schedule" && (
              <div className="space-y-2">
                <Label htmlFor="cron-expression">CRON Expression</Label>
                <Input
                  id="cron-expression"
                  value={config.cron_expression || ""}
                  onChange={(e) =>
                    handleConfigUpdate("cron_expression", e.target.value)
                  }
                  placeholder="0 0 * * *"
                />
                <p className="text-xs text-muted-foreground">
                  Example: 0 0 * * * (runs daily at midnight)
                </p>
              </div>
            )}

            {config.trigger_type === "webhook" && (
              <>
                <div className="space-y-2">
                  <Label>Webhook URL</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      value={
                        workflowId
                          ? `${window.location.origin}/api/v1/workflows/${workflowId}/webhook/${node.id}`
                          : "Save workflow to generate webhook URL"
                      }
                      readOnly
                      className="font-mono text-xs"
                    />
                    {workflowId && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => {
                          const webhookUrl = `${window.location.origin}/api/v1/workflows/${workflowId}/webhook/${node.id}`
                          navigator.clipboard.writeText(webhookUrl)
                          showSuccessToast("Webhook URL copied!")
                        }}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Send HTTP POST to this URL to trigger the workflow
                  </p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="webhook-method">HTTP Method</Label>
                  <Select
                    value={config.webhook_method || "POST"}
                    onValueChange={(value) =>
                      handleConfigUpdate("webhook_method", value)
                    }
                  >
                    <SelectTrigger id="webhook-method">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="POST">POST</SelectItem>
                      <SelectItem value="GET">GET</SelectItem>
                      <SelectItem value="PUT">PUT</SelectItem>
                      <SelectItem value="PATCH">PATCH</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
          </>
        )}

        {node.type === "ai_prompt" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="prompt">Prompt</Label>
              <Textarea
                id="prompt"
                value={config.prompt || ""}
                onChange={(e) => handleConfigUpdate("prompt", e.target.value)}
                placeholder="Enter your prompt..."
                rows={4}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="model">Model</Label>
              <Select
                value={config.model || "gpt-4"}
                onValueChange={(value) => handleConfigUpdate("model", value)}
              >
                <SelectTrigger id="model">
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3-opus">Claude 3 Opus</SelectItem>
                  <SelectItem value="claude-3-sonnet">
                    Claude 3 Sonnet
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </>
        )}

        {node.type === "connector" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="connector-slug">Connector</Label>
              <Input
                id="connector-slug"
                value={config.connector_slug || ""}
                onChange={(e) =>
                  handleConfigUpdate("connector_slug", e.target.value)
                }
                placeholder="slack, github, etc."
                disabled={!!config.connector_slug}
              />
              {config.connector_slug && (
                <p className="text-xs text-muted-foreground">
                  Connector is set from node selection. Edit the node to change.
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="action">Action</Label>
              <Input
                id="action"
                value={config.action || ""}
                onChange={(e) => handleConfigUpdate("action", e.target.value)}
                placeholder="send_message, create_issue, etc."
              />
            </div>
            {connectorScopes.length > 0 && (
              <div className="space-y-2">
                <Label>OAuth Scopes</Label>
                {isLoadingScopes ? (
                  <p className="text-xs text-muted-foreground">
                    Loading scopes...
                  </p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto border rounded p-2">
                    {connectorScopes.map((scope) => (
                      <label
                        key={scope}
                        className="flex items-center gap-2 cursor-pointer hover:bg-muted/50 p-1 rounded"
                      >
                        <Checkbox
                          checked={selectedScopes.includes(scope)}
                          onCheckedChange={(checked) => {
                            let updated: string[]
                            if (checked) {
                              updated = [...selectedScopes, scope]
                            } else {
                              updated = selectedScopes.filter(
                                (s) => s !== scope,
                              )
                            }
                            setSelectedScopes(updated)
                            handleConfigUpdate("oauth_scopes", updated)
                          }}
                        />
                        <span className="text-sm">{scope}</span>
                      </label>
                    ))}
                  </div>
                )}
                <p className="text-xs text-muted-foreground">
                  Select OAuth scopes required for this connector action
                </p>
              </div>
            )}
          </>
        )}

        {node.type === "code" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="code-language">Language</Label>
              <Select
                value={config.language || "python"}
                onValueChange={(value) => handleConfigUpdate("language", value)}
              >
                <SelectTrigger id="code-language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="python">Python</SelectItem>
                  <SelectItem value="javascript">JavaScript</SelectItem>
                  <SelectItem value="typescript">TypeScript</SelectItem>
                  <SelectItem value="bash">Bash</SelectItem>
                  <SelectItem value="json">JSON</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="code">Code</Label>
              <MonacoEditor
                value={config.code || ""}
                onChange={(value) => handleConfigUpdate("code", value || "")}
                language={config.language || "python"}
                height="300px"
                className="border rounded-md overflow-hidden"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="code-runtime">Runtime (Optional)</Label>
              <Select
                value={config.runtime || "auto"}
                onValueChange={(value) => handleConfigUpdate("runtime", value === "auto" ? undefined : value)}
              >
                <SelectTrigger id="code-runtime">
                  <SelectValue placeholder="Auto-select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto-select</SelectItem>
                  <SelectItem value="e2b">E2B</SelectItem>
                  <SelectItem value="wasmedge">WasmEdge</SelectItem>
                  <SelectItem value="bacalhau">Bacalhau</SelectItem>
                  <SelectItem value="cline_node">Cline Node</SelectItem>
                  <SelectItem value="mcp_server">MCP Server</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </>
        )}

        {node.type === "condition" && (
          <div className="space-y-2">
            <Label htmlFor="condition-expression">Condition Expression</Label>
            <Input
              id="condition-expression"
              value={config.expression || ""}
              onChange={(e) => handleConfigUpdate("expression", e.target.value)}
              placeholder="input.value > 10"
            />
          </div>
        )}

        {node.type === "http_request" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="http-method">Method</Label>
              <Select
                value={config.method || "GET"}
                onValueChange={(value) => handleConfigUpdate("method", value)}
              >
                <SelectTrigger id="http-method">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GET">GET</SelectItem>
                  <SelectItem value="POST">POST</SelectItem>
                  <SelectItem value="PUT">PUT</SelectItem>
                  <SelectItem value="DELETE">DELETE</SelectItem>
                  <SelectItem value="PATCH">PATCH</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="http-url">URL</Label>
              <Input
                id="http-url"
                value={config.url || ""}
                onChange={(e) => handleConfigUpdate("url", e.target.value)}
                placeholder="https://api.synthralos.ai/endpoint"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="http-headers">Headers (JSON)</Label>
              <Textarea
                id="http-headers"
                value={JSON.stringify(config.headers || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const headers = JSON.parse(e.target.value)
                    handleConfigUpdate("headers", headers)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"Authorization": "Bearer token"}'
                rows={3}
                className="font-mono text-sm"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="http-body">Body (JSON)</Label>
              <Textarea
                id="http-body"
                value={config.body ? JSON.stringify(config.body, null, 2) : ""}
                onChange={(e) => {
                  try {
                    const body = e.target.value
                      ? JSON.parse(e.target.value)
                      : null
                    handleConfigUpdate("body", body)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"key": "value"}'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {node.type === "rag_switch" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="rag-index-id">RAG Index ID</Label>
              <Input
                id="rag-index-id"
                value={config.index_id || ""}
                onChange={(e) => handleConfigUpdate("index_id", e.target.value)}
                placeholder="UUID of RAG index"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="rag-query-requirements">
                Query Requirements (JSON)
              </Label>
              <Textarea
                id="rag-query-requirements"
                value={JSON.stringify(config.query_requirements || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const requirements = JSON.parse(e.target.value)
                    handleConfigUpdate("query_requirements", requirements)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"file_size": 1000, "dataset_size": 10000}'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {node.type === "ocr_switch" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="ocr-document-url">Document URL</Label>
              <Input
                id="ocr-document-url"
                value={config.document_url || ""}
                onChange={(e) =>
                  handleConfigUpdate("document_url", e.target.value)
                }
                placeholder="https://synthralos.ai/document.pdf"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ocr-query-requirements">
                Query Requirements (JSON)
              </Label>
              <Textarea
                id="ocr-query-requirements"
                value={JSON.stringify(config.query_requirements || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const requirements = JSON.parse(e.target.value)
                    handleConfigUpdate("query_requirements", requirements)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"layout_type": "structured", "handwriting": false}'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {node.type === "scraping" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="scraping-url">URL</Label>
              <Input
                id="scraping-url"
                value={config.url || ""}
                onChange={(e) => handleConfigUpdate("url", e.target.value)}
                placeholder="https://synthralos.ai"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="scraping-engine">Engine</Label>
              <Select
                value={config.engine || "beautifulsoup"}
                onValueChange={(value) => handleConfigUpdate("engine", value)}
              >
                <SelectTrigger id="scraping-engine">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="beautifulsoup">BeautifulSoup</SelectItem>
                  <SelectItem value="playwright">Playwright</SelectItem>
                  <SelectItem value="scrapy">Scrapy</SelectItem>
                  <SelectItem value="crawl4ai">Crawl4AI</SelectItem>
                  <SelectItem value="watercrawl">WaterCrawl</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="scraping-selectors">Selectors (JSON)</Label>
              <Textarea
                id="scraping-selectors"
                value={JSON.stringify(config.selectors || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const selectors = JSON.parse(e.target.value)
                    handleConfigUpdate("selectors", selectors)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"title": "h1", "content": ".article"}'
                rows={3}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {node.type === "browser" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="browser-action">Action Type</Label>
              <Select
                value={config.action_type || "navigate"}
                onValueChange={(value) =>
                  handleConfigUpdate("action_type", value)
                }
              >
                <SelectTrigger id="browser-action">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="navigate">Navigate</SelectItem>
                  <SelectItem value="click">Click</SelectItem>
                  <SelectItem value="fill">Fill Form</SelectItem>
                  <SelectItem value="screenshot">Screenshot</SelectItem>
                  <SelectItem value="extract">Extract Data</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="browser-action-data">Action Data (JSON)</Label>
              <Textarea
                id="browser-action-data"
                value={JSON.stringify(config.action_data || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const actionData = JSON.parse(e.target.value)
                    handleConfigUpdate("action_data", actionData)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"url": "https://synthralos.ai", "selector": "#button"}'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {/* Personalization Values - Available for all node types except trigger */}
        {node.type !== "trigger" && availableFields.length > 0 && (
          <div className="space-y-2 border-t pt-4">
            <Label htmlFor="personalization">Personalization Values</Label>
            <Select
              value={config.personalization || ""}
              onValueChange={(value) =>
                handleConfigUpdate("personalization", value)
              }
            >
              <SelectTrigger id="personalization">
                <SelectValue placeholder="Select from previous nodes" />
              </SelectTrigger>
              <SelectContent>
                {availableFields.map(({ nodeId, nodeLabel, fields }) => (
                  <div key={nodeId}>
                    <div className="px-2 py-1 text-xs font-semibold text-muted-foreground">
                      {nodeLabel}
                    </div>
                    {fields.map((field) => (
                      <SelectItem
                        key={`${nodeId}.${field}`}
                        value={`${nodeId}.${field}`}
                      >
                        {field}
                      </SelectItem>
                    ))}
                  </div>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Reference output values from previous nodes using dot notation
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
