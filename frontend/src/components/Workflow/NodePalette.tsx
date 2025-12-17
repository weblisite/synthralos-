/**
 * Node Palette Component
 *
 * Drag-and-drop palette of available workflow nodes.
 */

import type { Node } from "@xyflow/react"
import {
  Brain,
  ChevronDown,
  ChevronRight,
  Code,
  Database,
  FileText,
  GitBranch,
  Globe,
  Monitor,
  Network,
  Play,
  Plug,
} from "lucide-react"
import { useCallback, useEffect, useMemo, useState } from "react"
import { supabase } from "@/lib/supabase"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"

interface Connector {
  id: string
  slug: string
  name: string
  description?: string
  category?: string
}

interface NodeType {
  type: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  category: string
  description: string
  connectorSlug?: string
}

const baseNodeTypes: NodeType[] = [
  {
    type: "trigger",
    label: "Trigger",
    icon: Play,
    category: "Core",
    description: "Start workflow execution",
  },
  {
    type: "ai_prompt",
    label: "AI Prompt",
    icon: Brain,
    category: "AI",
    description: "LLM prompt node",
  },
  {
    type: "code",
    label: "Code",
    icon: Code,
    category: "Logic",
    description: "Custom code execution",
  },
  {
    type: "condition",
    label: "Condition",
    icon: GitBranch,
    category: "Logic",
    description: "Conditional branching",
  },
  {
    type: "switch",
    label: "Switch",
    icon: GitBranch,
    category: "Logic",
    description: "Multi-path routing",
  },
  {
    type: "rag_switch",
    label: "RAG Switch",
    icon: Database,
    category: "AI",
    description: "RAG routing decision",
  },
  {
    type: "ocr_switch",
    label: "OCR Switch",
    icon: FileText,
    category: "Processing",
    description: "OCR engine routing",
  },
  {
    type: "scraping",
    label: "Scraping",
    icon: Globe,
    category: "Data",
    description: "Web scraping",
  },
  {
    type: "browser",
    label: "Browser",
    icon: Monitor,
    category: "Automation",
    description: "Browser automation",
  },
  {
    type: "http_request",
    label: "HTTP Request",
    icon: Network,
    category: "Core",
    description: "HTTP API call",
  },
]

interface NodePaletteProps {
  onNodeAdd?: (node: Node) => void
}

export function NodePalette({ onNodeAdd }: NodePaletteProps) {
  const [connectors, setConnectors] = useState<Connector[]>([])
  const [isConnectorsLoading, setIsConnectorsLoading] = useState(true)
  const [isConnectorsExpanded, setIsConnectorsExpanded] = useState(false)

  const [hasFetchedConnectors, setHasFetchedConnectors] = useState(false)

  useEffect(() => {
    // Only fetch connectors when the section is expanded (lazy loading)
    if (!isConnectorsExpanded) {
      return
    }

    // If connectors are already loaded, don't fetch again
    if (hasFetchedConnectors) {
      return
    }

    const fetchConnectors = async () => {
      setIsConnectorsLoading(true)
      try {
        const {
          data: { session },
        } = await supabase.auth.getSession()

        if (!session) {
          setIsConnectorsLoading(false)
          return
        }

        const response = await fetch(`/api/v1/connectors/list?include_custom=true`, {
          headers: {
            Authorization: `Bearer ${session.access_token}`,
            "Content-Type": "application/json",
          },
        })

        if (response.ok) {
          const data = await response.json()
          const connectorsList = Array.isArray(data) ? data : (data.connectors || [])
          // Filter out deprecated connectors, show all others (draft, beta, stable)
          const activeConnectors = connectorsList.filter(
            (c: Connector & { status?: string }) =>
              !c.status || c.status !== "deprecated"
          )
          // Update connectors immediately to show progress
          setConnectors(activeConnectors)
          setHasFetchedConnectors(true)
          console.log(`[NodePalette] Loaded ${activeConnectors.length} connectors`)
        } else {
          const errorText = await response.text()
          console.error("[NodePalette] Failed to fetch connectors:", response.status, response.statusText, errorText)
        }
      } catch (error) {
        console.error("[NodePalette] Failed to fetch connectors:", error)
      } finally {
        setIsConnectorsLoading(false)
      }
    }

    fetchConnectors()
  }, [isConnectorsExpanded, hasFetchedConnectors])

  const connectorNodes = useMemo(() => {
    return connectors.map((connector) => ({
      type: `connector-${connector.slug}`,
      label: connector.name,
      icon: Plug,
      category: "App Connectors",
      description: connector.description || `${connector.name} integration`,
      connectorSlug: connector.slug,
    }))
  }, [connectors])

  const handleDragStart = useCallback(
    (event: React.DragEvent, nodeType: NodeType) => {
      event.dataTransfer.setData("application/reactflow", nodeType.type)
      if (nodeType.connectorSlug) {
        event.dataTransfer.setData("connector-slug", nodeType.connectorSlug)
      }
      event.dataTransfer.effectAllowed = "move"
    },
    [],
  )

  const handleClick = useCallback(
    (nodeType: NodeType) => {
      if (!onNodeAdd) return

      const newNode: Node = {
        id: `${nodeType.type}-${Date.now()}`,
        type: nodeType.type.startsWith("connector-") ? "connector" : nodeType.type,
        position: { x: Math.random() * 400, y: Math.random() * 400 },
        data: {
          label: nodeType.label,
          config: nodeType.connectorSlug
            ? { connector_slug: nodeType.connectorSlug }
            : {},
        },
      }

      onNodeAdd(newNode)
    },
    [onNodeAdd],
  )

  const groupedNodes = useMemo(() => {
    const groups: Record<string, NodeType[]> = {}
    baseNodeTypes.forEach((nodeType) => {
      if (!groups[nodeType.category]) {
        groups[nodeType.category] = []
      }
      groups[nodeType.category].push(nodeType)
    })
    return groups
  }, [])

  return (
    <div className="w-64 h-full bg-background border-r overflow-y-auto">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Node Palette</h2>
        <p className="text-sm text-muted-foreground">
          Drag or click to add nodes
        </p>
      </div>

      <div className="p-2 space-y-4">
        {Object.entries(groupedNodes).map(([category, nodes]) => (
          <div key={category} className="space-y-2">
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide px-2">
              {category}
            </h3>
            <div className="space-y-1">
              {nodes.map((nodeType) => {
                const Icon = nodeType.icon
                return (
                  <button
                    key={nodeType.type}
                    type="button"
                    draggable
                    onDragStart={(e) => handleDragStart(e, nodeType)}
                    onClick={() => handleClick(nodeType)}
                    className="flex items-center gap-2 p-2 rounded-md border cursor-move hover:bg-accent transition-colors w-full text-left"
                    title={nodeType.description}
                  >
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium">
                        {nodeType.label}
                      </div>
                      <div className="text-xs text-muted-foreground truncate">
                        {nodeType.description}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        ))}

        {/* App Connectors Expandable Section */}
        <div className="space-y-2">
          <Collapsible open={isConnectorsExpanded} onOpenChange={setIsConnectorsExpanded}>
            <CollapsibleTrigger className="flex items-center gap-2 w-full px-2 py-1 hover:bg-accent rounded-md transition-colors">
              {isConnectorsExpanded ? (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              )}
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                App Connectors ({connectors.length})
              </h3>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="space-y-1 mt-2">
                {isConnectorsLoading ? (
                  <div className="px-2 py-4 text-xs text-muted-foreground text-center space-y-2">
                    <div className="flex items-center justify-center gap-2">
                      <div className="h-3 w-3 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
                      <span>Loading connectors...</span>
                    </div>
                    {connectors.length > 0 && (
                      <div className="text-xs text-muted-foreground/70">
                        Loaded {connectors.length} so far...
                      </div>
                    )}
                  </div>
                ) : connectorNodes.length === 0 ? (
                  <div className="px-2 py-4 text-xs text-muted-foreground text-center">
                    No connectors available
                  </div>
                ) : (
                  connectorNodes.map((nodeType) => {
                    const Icon = nodeType.icon
                    return (
                      <button
                        key={nodeType.type}
                        type="button"
                        draggable
                        onDragStart={(e) => handleDragStart(e, nodeType)}
                        onClick={() => handleClick(nodeType)}
                        className="flex items-center gap-2 p-2 rounded-md border cursor-move hover:bg-accent transition-colors w-full text-left ml-4"
                        title={nodeType.description}
                      >
                        <Icon className="h-4 w-4 text-green-600" />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium">
                            {nodeType.label}
                          </div>
                          <div className="text-xs text-muted-foreground truncate">
                            {nodeType.description}
                          </div>
                        </div>
                      </button>
                    )
                  })
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </div>
    </div>
  )
}
