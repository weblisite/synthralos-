/**
 * Node Configuration Panel
 *
 * Side panel for configuring selected workflow nodes.
 */

import type { Node } from "@xyflow/react"
import { X } from "lucide-react"
import { useMemo } from "react"
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

interface NodeConfigPanelProps {
  node: Node | null
  onClose: () => void
  onUpdate: (nodeId: string, updates: Partial<Node>) => void
}

export function NodeConfigPanel({
  node,
  onClose,
  onUpdate,
}: NodeConfigPanelProps) {
  const config = useMemo(() => node?.data?.config || {}, [node])

  if (!node) {
    return (
      <div className="w-80 h-full bg-background border-l p-4">
        <p className="text-sm text-muted-foreground">
          Select a node to configure
        </p>
      </div>
    )
  }

  const handleConfigUpdate = (key: string, value: any) => {
    const updatedConfig = { ...config, [key]: value }
    onUpdate(node.id, {
      data: {
        ...node.data,
        config: updatedConfig,
      },
    })
  }

  const handleLabelUpdate = (label: string) => {
    onUpdate(node.id, {
      data: {
        ...node.data,
        label,
      },
    })
  }

  return (
    <div className="w-80 h-full bg-background border-l flex flex-col">
      <div className="p-4 border-b flex items-center justify-between">
        <h2 className="text-lg font-semibold">Node Configuration</h2>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="node-label">Label</Label>
          <Input
            id="node-label"
            value={node.data.label || ""}
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
              </div>
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
              />
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
                value={config.runtime || ""}
                onValueChange={(value) => handleConfigUpdate("runtime", value)}
              >
                <SelectTrigger id="code-runtime">
                  <SelectValue placeholder="Auto-select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Auto-select</SelectItem>
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
      </div>
    </div>
  )
}
