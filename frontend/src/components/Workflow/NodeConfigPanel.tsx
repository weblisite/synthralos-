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
                onValueChange={(value) =>
                  handleConfigUpdate(
                    "runtime",
                    value === "auto" ? undefined : value,
                  )
                }
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

        {node.type === "switch" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="switch-expression">Switch Expression</Label>
              <Input
                id="switch-expression"
                value={config.switch_expression || ""}
                onChange={(e) =>
                  handleConfigUpdate("switch_expression", e.target.value)
                }
                placeholder="input.status"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="switch-cases">Cases (JSON)</Label>
              <Textarea
                id="switch-cases"
                value={JSON.stringify(config.cases || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const cases = JSON.parse(e.target.value)
                    handleConfigUpdate("cases", cases)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"case1": "value1", "case2": "value2", "default": "default_value"}'
                rows={6}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                Define case values and their corresponding output values. Use
                "default" for default case.
              </p>
            </div>
          </>
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

        {node.type === "agent" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="agent-id">Agent ID</Label>
              <Input
                id="agent-id"
                value={config.agent_id || ""}
                onChange={(e) => handleConfigUpdate("agent_id", e.target.value)}
                placeholder="Enter agent ID"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="agent-task">Task</Label>
              <Textarea
                id="agent-task"
                value={config.task || ""}
                onChange={(e) => handleConfigUpdate("task", e.target.value)}
                placeholder="Enter task description"
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="agent-config">Agent Config (JSON)</Label>
              <Textarea
                id="agent-config"
                value={JSON.stringify(config.agent_config || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const agentConfig = JSON.parse(e.target.value)
                    handleConfigUpdate("agent_config", agentConfig)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"framework": "openai", "model": "gpt-4"}'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {(node.type === "sub_workflow" || node.type === "sub-workflow") && (
          <>
            <div className="space-y-2">
              <Label htmlFor="sub-workflow-id">Sub Workflow ID</Label>
              <Input
                id="sub-workflow-id"
                value={config.workflow_id || ""}
                onChange={(e) =>
                  handleConfigUpdate("workflow_id", e.target.value)
                }
                placeholder="Enter workflow ID"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sub-workflow-input">Input Data (JSON)</Label>
              <Textarea
                id="sub-workflow-input"
                value={JSON.stringify(config.input_data || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const inputData = JSON.parse(e.target.value)
                    handleConfigUpdate("input_data", inputData)
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

        {/* Loop Nodes */}
        {(node.type === "loop" ||
          node.type === "for" ||
          node.type === "while" ||
          node.type === "repeat") && (
          <>
            <div className="space-y-2">
              <Label htmlFor="loop-type">Loop Type</Label>
              <Select
                value={config.loop_type || node.type}
                onValueChange={(value) =>
                  handleConfigUpdate("loop_type", value)
                }
              >
                <SelectTrigger id="loop-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="for">For Loop (iterate array)</SelectItem>
                  <SelectItem value="while">While Loop (condition)</SelectItem>
                  <SelectItem value="repeat">Repeat (N times)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {config.loop_type === "for" && (
              <div className="space-y-2">
                <Label htmlFor="loop-array">Array Expression</Label>
                <Input
                  id="loop-array"
                  value={config.array_expression || ""}
                  onChange={(e) =>
                    handleConfigUpdate("array_expression", e.target.value)
                  }
                  placeholder="input.items or ['item1', 'item2']"
                />
              </div>
            )}
            {config.loop_type === "while" && (
              <div className="space-y-2">
                <Label htmlFor="loop-condition">Condition Expression</Label>
                <Input
                  id="loop-condition"
                  value={config.condition_expression || ""}
                  onChange={(e) =>
                    handleConfigUpdate("condition_expression", e.target.value)
                  }
                  placeholder="input.value < 10"
                />
              </div>
            )}
            {config.loop_type === "repeat" && (
              <div className="space-y-2">
                <Label htmlFor="loop-count">Repeat Count</Label>
                <Input
                  id="loop-count"
                  type="number"
                  value={config.repeat_count || 1}
                  onChange={(e) =>
                    handleConfigUpdate(
                      "repeat_count",
                      parseInt(e.target.value, 10),
                    )
                  }
                  placeholder="10"
                />
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="loop-variable">Loop Variable Name</Label>
              <Input
                id="loop-variable"
                value={config.loop_variable || "item"}
                onChange={(e) =>
                  handleConfigUpdate("loop_variable", e.target.value)
                }
                placeholder="item"
              />
            </div>
          </>
        )}

        {/* Delay/Wait Nodes */}
        {(node.type === "delay" || node.type === "wait") && (
          <>
            <div className="space-y-2">
              <Label htmlFor="delay-type">Delay Type</Label>
              <Select
                value={config.delay_type || "seconds"}
                onValueChange={(value) =>
                  handleConfigUpdate("delay_type", value)
                }
              >
                <SelectTrigger id="delay-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="seconds">Delay by seconds</SelectItem>
                  <SelectItem value="until_time">
                    Wait until specific time
                  </SelectItem>
                  <SelectItem value="until_condition">
                    Wait until condition
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            {config.delay_type === "seconds" && (
              <div className="space-y-2">
                <Label htmlFor="delay-seconds">Seconds</Label>
                <Input
                  id="delay-seconds"
                  type="number"
                  value={config.delay_seconds || 1}
                  onChange={(e) =>
                    handleConfigUpdate(
                      "delay_seconds",
                      parseInt(e.target.value, 10),
                    )
                  }
                  placeholder="5"
                />
              </div>
            )}
            {config.delay_type === "until_time" && (
              <div className="space-y-2">
                <Label htmlFor="delay-time">Target Time (ISO 8601)</Label>
                <Input
                  id="delay-time"
                  type="datetime-local"
                  value={config.target_time || ""}
                  onChange={(e) =>
                    handleConfigUpdate("target_time", e.target.value)
                  }
                />
              </div>
            )}
            {config.delay_type === "until_condition" && (
              <div className="space-y-2">
                <Label htmlFor="delay-condition">Condition Expression</Label>
                <Input
                  id="delay-condition"
                  value={config.condition_expression || ""}
                  onChange={(e) =>
                    handleConfigUpdate("condition_expression", e.target.value)
                  }
                  placeholder="input.status === 'ready'"
                />
              </div>
            )}
          </>
        )}

        {/* Try/Catch/Finally Nodes */}
        {node.type === "try" && (
          <div className="space-y-2">
            <Label htmlFor="try-scope">Try Block Scope</Label>
            <Textarea
              id="try-scope"
              value={config.try_scope || ""}
              onChange={(e) => handleConfigUpdate("try_scope", e.target.value)}
              placeholder="Description of what to try"
              rows={3}
            />
          </div>
        )}

        {node.type === "catch" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="catch-error-type">Error Type (Optional)</Label>
              <Input
                id="catch-error-type"
                value={config.error_type || ""}
                onChange={(e) =>
                  handleConfigUpdate("error_type", e.target.value)
                }
                placeholder="ValueError, KeyError, or leave empty for all"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="catch-handler">Error Handler Code</Label>
              <MonacoEditor
                value={config.error_handler || ""}
                onChange={(value) =>
                  handleConfigUpdate("error_handler", value || "")
                }
                language="python"
                height="200px"
                className="border rounded-md overflow-hidden"
              />
            </div>
          </>
        )}

        {node.type === "finally" && (
          <div className="space-y-2">
            <Label htmlFor="finally-code">Finally Block Code</Label>
            <MonacoEditor
              value={config.finally_code || ""}
              onChange={(value) =>
                handleConfigUpdate("finally_code", value || "")
              }
              language="python"
              height="200px"
              className="border rounded-md overflow-hidden"
            />
          </div>
        )}

        {/* Transform Nodes */}
        {node.type === "map" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="map-expression">Map Expression</Label>
              <Textarea
                id="map-expression"
                value={config.map_expression || ""}
                onChange={(e) =>
                  handleConfigUpdate("map_expression", e.target.value)
                }
                placeholder="item * 2 or item.upper()"
                rows={3}
                className="font-mono text-sm"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="map-input">Input Array Expression</Label>
              <Input
                id="map-input"
                value={config.input_array || "input.items"}
                onChange={(e) =>
                  handleConfigUpdate("input_array", e.target.value)
                }
                placeholder="input.items"
              />
            </div>
          </>
        )}

        {node.type === "filter" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="filter-condition">Filter Condition</Label>
              <Input
                id="filter-condition"
                value={config.filter_condition || ""}
                onChange={(e) =>
                  handleConfigUpdate("filter_condition", e.target.value)
                }
                placeholder="item.value > 10"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="filter-input">Input Array Expression</Label>
              <Input
                id="filter-input"
                value={config.input_array || "input.items"}
                onChange={(e) =>
                  handleConfigUpdate("input_array", e.target.value)
                }
                placeholder="input.items"
              />
            </div>
          </>
        )}

        {node.type === "reduce" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="reduce-function">Reduce Function</Label>
              <Textarea
                id="reduce-function"
                value={config.reduce_function || ""}
                onChange={(e) =>
                  handleConfigUpdate("reduce_function", e.target.value)
                }
                placeholder="(acc, item) => acc + item"
                rows={3}
                className="font-mono text-sm"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reduce-initial">Initial Value</Label>
              <Input
                id="reduce-initial"
                value={config.initial_value || "0"}
                onChange={(e) =>
                  handleConfigUpdate("initial_value", e.target.value)
                }
                placeholder="0"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reduce-input">Input Array Expression</Label>
              <Input
                id="reduce-input"
                value={config.input_array || "input.items"}
                onChange={(e) =>
                  handleConfigUpdate("input_array", e.target.value)
                }
                placeholder="input.items"
              />
            </div>
          </>
        )}

        {node.type === "merge" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="merge-strategy">Merge Strategy</Label>
              <Select
                value={config.merge_strategy || "deep"}
                onValueChange={(value) =>
                  handleConfigUpdate("merge_strategy", value)
                }
              >
                <SelectTrigger id="merge-strategy">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="deep">Deep Merge</SelectItem>
                  <SelectItem value="shallow">Shallow Merge</SelectItem>
                  <SelectItem value="array">Array Concatenation</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="merge-inputs">Input Sources (JSON)</Label>
              <Textarea
                id="merge-inputs"
                value={JSON.stringify(config.input_sources || [], null, 2)}
                onChange={(e) => {
                  try {
                    const sources = JSON.parse(e.target.value)
                    handleConfigUpdate("input_sources", sources)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='["input.source1", "input.source2"]'
                rows={3}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {node.type === "split" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="split-strategy">Split Strategy</Label>
              <Select
                value={config.split_strategy || "by_key"}
                onValueChange={(value) =>
                  handleConfigUpdate("split_strategy", value)
                }
              >
                <SelectTrigger id="split-strategy">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="by_key">By Key</SelectItem>
                  <SelectItem value="by_size">By Size</SelectItem>
                  <SelectItem value="by_condition">By Condition</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="split-config">Split Configuration (JSON)</Label>
              <Textarea
                id="split-config"
                value={JSON.stringify(config.split_config || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const splitConfig = JSON.parse(e.target.value)
                    handleConfigUpdate("split_config", splitConfig)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"keys": ["key1", "key2"]} or {"size": 10}'
                rows={3}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {/* Variable Nodes */}
        {node.type === "set_variable" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="variable-name">Variable Name</Label>
              <Input
                id="variable-name"
                value={config.variable_name || ""}
                onChange={(e) =>
                  handleConfigUpdate("variable_name", e.target.value)
                }
                placeholder="my_variable"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="variable-value">Variable Value (JSON)</Label>
              <Textarea
                id="variable-value"
                value={JSON.stringify(config.variable_value || null, null, 2)}
                onChange={(e) => {
                  try {
                    const value = e.target.value
                      ? JSON.parse(e.target.value)
                      : null
                    handleConfigUpdate("variable_value", value)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"key": "value"} or "string" or 123'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="variable-scope">Variable Scope</Label>
              <Select
                value={config.variable_scope || "workflow"}
                onValueChange={(value) =>
                  handleConfigUpdate("variable_scope", value)
                }
              >
                <SelectTrigger id="variable-scope">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="workflow">Workflow</SelectItem>
                  <SelectItem value="node">Node</SelectItem>
                  <SelectItem value="loop">Loop</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </>
        )}

        {node.type === "get_variable" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="get-variable-name">Variable Name</Label>
              <Input
                id="get-variable-name"
                value={config.variable_name || ""}
                onChange={(e) =>
                  handleConfigUpdate("variable_name", e.target.value)
                }
                placeholder="my_variable"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="get-variable-default">
                Default Value (JSON, Optional)
              </Label>
              <Textarea
                id="get-variable-default"
                value={JSON.stringify(config.default_value || null, null, 2)}
                onChange={(e) => {
                  try {
                    const value = e.target.value
                      ? JSON.parse(e.target.value)
                      : null
                    handleConfigUpdate("default_value", value)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='null or {"default": "value"}'
                rows={3}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {/* Control Flow Nodes */}
        {node.type === "break" && (
          <div className="space-y-2">
            <Label htmlFor="break-label">Loop Label (Optional)</Label>
            <Input
              id="break-label"
              value={config.loop_label || ""}
              onChange={(e) => handleConfigUpdate("loop_label", e.target.value)}
              placeholder="Leave empty to break nearest loop"
            />
          </div>
        )}

        {node.type === "continue" && (
          <div className="space-y-2">
            <Label htmlFor="continue-label">Loop Label (Optional)</Label>
            <Input
              id="continue-label"
              value={config.loop_label || ""}
              onChange={(e) => handleConfigUpdate("loop_label", e.target.value)}
              placeholder="Leave empty to continue nearest loop"
            />
          </div>
        )}

        {/* Storage Node */}
        {node.type === "storage" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="storage-operation">Operation</Label>
              <Select
                value={config.operation || "upload"}
                onValueChange={(value) =>
                  handleConfigUpdate("operation", value)
                }
              >
                <SelectTrigger id="storage-operation">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="upload">Upload File</SelectItem>
                  <SelectItem value="download">Download File</SelectItem>
                  <SelectItem value="list">List Files</SelectItem>
                  <SelectItem value="delete">Delete File</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="storage-provider">Storage Provider</Label>
              <Select
                value={config.provider || "s3"}
                onValueChange={(value) => handleConfigUpdate("provider", value)}
              >
                <SelectTrigger id="storage-provider">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="s3">Amazon S3</SelectItem>
                  <SelectItem value="gcs">Google Cloud Storage</SelectItem>
                  <SelectItem value="azure">Azure Blob Storage</SelectItem>
                  <SelectItem value="local">Local Storage</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="storage-path">File Path/Bucket</Label>
              <Input
                id="storage-path"
                value={config.file_path || ""}
                onChange={(e) =>
                  handleConfigUpdate("file_path", e.target.value)
                }
                placeholder="bucket-name/path/to/file.txt"
              />
            </div>
            {config.operation === "upload" && (
              <div className="space-y-2">
                <Label htmlFor="storage-data">File Data Expression</Label>
                <Input
                  id="storage-data"
                  value={config.file_data || "input.file_data"}
                  onChange={(e) =>
                    handleConfigUpdate("file_data", e.target.value)
                  }
                  placeholder="input.file_data"
                />
              </div>
            )}
          </>
        )}

        {/* Social Monitoring Node */}
        {node.type === "social_monitoring" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="osint-operation">Operation</Label>
              <Select
                value={config.operation || "stream"}
                onValueChange={(value) =>
                  handleConfigUpdate("operation", value)
                }
              >
                <SelectTrigger id="osint-operation">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="stream">Start Live Stream</SelectItem>
                  <SelectItem value="digest">Historical Digest</SelectItem>
                  <SelectItem value="search">Search</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="osint-source">Source Platform</Label>
              <Select
                value={config.source || "twitter"}
                onValueChange={(value) => handleConfigUpdate("source", value)}
              >
                <SelectTrigger id="osint-source">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="twitter">Twitter/X</SelectItem>
                  <SelectItem value="reddit">Reddit</SelectItem>
                  <SelectItem value="telegram">Telegram</SelectItem>
                  <SelectItem value="news">News/Blogs</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="osint-query">Query/Keywords (JSON)</Label>
              <Textarea
                id="osint-query"
                value={JSON.stringify(config.query || {}, null, 2)}
                onChange={(e) => {
                  try {
                    const query = JSON.parse(e.target.value)
                    handleConfigUpdate("query", query)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='{"keywords": ["keyword1", "keyword2"], "filters": {}}'
                rows={4}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {/* Human Approval Node */}
        {node.type === "human_approval" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="approval-message">Approval Message</Label>
              <Textarea
                id="approval-message"
                value={config.approval_message || ""}
                onChange={(e) =>
                  handleConfigUpdate("approval_message", e.target.value)
                }
                placeholder="Please approve this action..."
                rows={3}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="approval-timeout">Timeout (seconds)</Label>
              <Input
                id="approval-timeout"
                type="number"
                value={config.timeout_seconds || 3600}
                onChange={(e) =>
                  handleConfigUpdate(
                    "timeout_seconds",
                    parseInt(e.target.value, 10),
                  )
                }
                placeholder="3600"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="approval-options">Approval Options (JSON)</Label>
              <Textarea
                id="approval-options"
                value={JSON.stringify(
                  config.approval_options || ["approve", "reject"],
                  null,
                  2,
                )}
                onChange={(e) => {
                  try {
                    const options = JSON.parse(e.target.value)
                    handleConfigUpdate("approval_options", options)
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
                placeholder='["approve", "reject", "request_changes"]'
                rows={2}
                className="font-mono text-sm"
              />
            </div>
          </>
        )}

        {/* Notification Node */}
        {node.type === "notification" && (
          <>
            <div className="space-y-2">
              <Label htmlFor="notification-channel">Channel</Label>
              <Select
                value={config.channel || "email"}
                onValueChange={(value) => handleConfigUpdate("channel", value)}
              >
                <SelectTrigger id="notification-channel">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="sms">SMS</SelectItem>
                  <SelectItem value="slack">Slack</SelectItem>
                  <SelectItem value="discord">Discord</SelectItem>
                  <SelectItem value="webhook">Webhook</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="notification-recipient">Recipient</Label>
              <Input
                id="notification-recipient"
                value={config.recipient || ""}
                onChange={(e) =>
                  handleConfigUpdate("recipient", e.target.value)
                }
                placeholder="user@example.com or @channel"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="notification-subject">Subject</Label>
              <Input
                id="notification-subject"
                value={config.subject || ""}
                onChange={(e) => handleConfigUpdate("subject", e.target.value)}
                placeholder="Notification subject"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="notification-message">Message</Label>
              <Textarea
                id="notification-message"
                value={config.message || ""}
                onChange={(e) => handleConfigUpdate("message", e.target.value)}
                placeholder="Notification message body"
                rows={4}
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
