/**
 * Node Palette Component
 *
 * Drag-and-drop palette of available workflow nodes.
 */

import type { Node } from "@xyflow/react"
import {
  AlertTriangle,
  ArrowRight,
  Bell,
  Bot,
  Brain,
  ChevronDown,
  ChevronRight,
  Clock,
  Code,
  Database,
  Download,
  FileText,
  Filter,
  GitBranch,
  Globe,
  Layers,
  Merge,
  Monitor,
  Network,
  Pause,
  Play,
  Plug,
  RefreshCw,
  Repeat,
  Save,
  Search,
  Split,
  UserCheck,
  Workflow,
} from "lucide-react"
import { useCallback, useEffect, useMemo, useState } from "react"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { apiClient } from "@/lib/apiClient"
import { getConnectorLogoUrls } from "@/lib/connectorLogos"

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
  {
    type: "agent",
    label: "Agent",
    icon: Bot,
    category: "AI",
    description: "AI agent execution",
  },
  {
    type: "sub_workflow",
    label: "Sub Workflow",
    icon: Workflow,
    category: "Core",
    description: "Execute nested workflow",
  },
  {
    type: "loop",
    label: "Loop",
    icon: Repeat,
    category: "Logic",
    description: "Iterate over items",
  },
  {
    type: "for",
    label: "For Loop",
    icon: Repeat,
    category: "Logic",
    description: "For each item in array",
  },
  {
    type: "while",
    label: "While Loop",
    icon: Repeat,
    category: "Logic",
    description: "Repeat while condition is true",
  },
  {
    type: "repeat",
    label: "Repeat",
    icon: Repeat,
    category: "Logic",
    description: "Repeat N times",
  },
  {
    type: "delay",
    label: "Delay",
    icon: Clock,
    category: "Control",
    description: "Wait for specified duration",
  },
  {
    type: "wait",
    label: "Wait",
    icon: Clock,
    category: "Control",
    description: "Wait until condition or time",
  },
  {
    type: "try",
    label: "Try",
    icon: AlertTriangle,
    category: "Control",
    description: "Try block for error handling",
  },
  {
    type: "catch",
    label: "Catch",
    icon: AlertTriangle,
    category: "Control",
    description: "Catch errors from try block",
  },
  {
    type: "finally",
    label: "Finally",
    icon: AlertTriangle,
    category: "Control",
    description: "Finally block always executes",
  },
  {
    type: "map",
    label: "Map",
    icon: RefreshCw,
    category: "Data",
    description: "Transform each item in array",
  },
  {
    type: "filter",
    label: "Filter",
    icon: Filter,
    category: "Data",
    description: "Filter items by condition",
  },
  {
    type: "reduce",
    label: "Reduce",
    icon: Layers,
    category: "Data",
    description: "Reduce array to single value",
  },
  {
    type: "merge",
    label: "Merge",
    icon: Merge,
    category: "Data",
    description: "Merge multiple data sources",
  },
  {
    type: "split",
    label: "Split",
    icon: Split,
    category: "Data",
    description: "Split data into multiple outputs",
  },
  {
    type: "set_variable",
    label: "Set Variable",
    icon: Save,
    category: "Variables",
    description: "Set workflow variable",
  },
  {
    type: "get_variable",
    label: "Get Variable",
    icon: Download,
    category: "Variables",
    description: "Get workflow variable value",
  },
  {
    type: "break",
    label: "Break",
    icon: Pause,
    category: "Control",
    description: "Exit loop immediately",
  },
  {
    type: "continue",
    label: "Continue",
    icon: ArrowRight,
    category: "Control",
    description: "Skip to next loop iteration",
  },
  {
    type: "storage",
    label: "Storage",
    icon: Database,
    category: "Data",
    description: "Store or retrieve files",
  },
  {
    type: "social_monitoring",
    label: "Social Monitoring",
    icon: Search,
    category: "Data",
    description: "Social media monitoring and intelligence",
  },
  {
    type: "human_approval",
    label: "Human Approval",
    icon: UserCheck,
    category: "Control",
    description: "Wait for human approval",
  },
  {
    type: "notification",
    label: "Notification",
    icon: Bell,
    category: "Integration",
    description: "Send notification",
  },
]

interface NodePaletteProps {
  onNodeAdd?: (node: Node) => void
}

// Component to display connector items with logos in the palette
function ConnectorPaletteItem({
  nodeType,
  onDragStart,
  onClick,
}: {
  nodeType: NodeType
  onDragStart: (e: React.DragEvent, nodeType: NodeType) => void
  onClick: (nodeType: NodeType) => void
}) {
  const [logoUrl, setLogoUrl] = useState<string | null>(null)
  const Icon = nodeType.icon

  useEffect(() => {
    if (nodeType.connectorSlug && !logoUrl) {
      const logoUrls = getConnectorLogoUrls(nodeType.connectorSlug)
      let currentIndex = 0

      const tryNextLogo = () => {
        if (currentIndex >= logoUrls.length) {
          setLogoUrl(null)
          return
        }

        const img = new Image()
        img.onload = () => setLogoUrl(logoUrls[currentIndex]!)
        img.onerror = () => {
          currentIndex++
          tryNextLogo()
        }
        img.src = logoUrls[currentIndex]!
      }

      tryNextLogo()
    }
  }, [nodeType.connectorSlug, logoUrl])

  return (
    <button
      type="button"
      draggable
      onDragStart={(e) => onDragStart(e, nodeType)}
      onClick={() => onClick(nodeType)}
      className="flex items-center gap-2 p-2 rounded-md border cursor-move hover:bg-accent transition-colors w-full text-left ml-4"
      title={nodeType.description}
    >
      {logoUrl ? (
        <img
          src={logoUrl}
          alt={nodeType.label}
          className="h-4 w-4 object-contain flex-shrink-0"
          onError={() => setLogoUrl(null)}
        />
      ) : (
        <Icon className="h-4 w-4 text-green-600 flex-shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium">{nodeType.label}</div>
        <div className="text-xs text-muted-foreground truncate">
          {nodeType.description}
        </div>
      </div>
    </button>
  )
}

export function NodePalette({ onNodeAdd }: NodePaletteProps) {
  const [connectors, setConnectors] = useState<Connector[]>([])
  const [isConnectorsLoading, setIsConnectorsLoading] = useState(false)
  const [isConnectorsExpanded, setIsConnectorsExpanded] = useState(false)

  const [hasFetchedConnectors, setHasFetchedConnectors] = useState(false)

  useEffect(() => {
    // Fetch connectors when the section is expanded (lazy loading)
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
        const data = await apiClient.request<
          { connectors?: any[]; total_count?: number } | any[]
        >(`/api/v1/connectors/list?include_custom=true`)
        console.log("[NodePalette] Raw API response:", data)

        // Handle both response formats: array or object with connectors property
        const connectorsList = Array.isArray(data)
          ? data
          : data.connectors || []
        console.log(
          "[NodePalette] Parsed connectors list:",
          connectorsList.length,
          "items",
        )

        // Filter out deprecated connectors, show all others (draft, beta, stable)
        const activeConnectors = connectorsList.filter(
          (c: Connector & { status?: string }) =>
            !c.status || c.status !== "deprecated",
        )
        console.log(
          "[NodePalette] Active connectors (non-deprecated):",
          activeConnectors.length,
        )

        // Update connectors immediately to show progress
        setConnectors(activeConnectors)
        setHasFetchedConnectors(true)
        console.log(
          `[NodePalette] Successfully loaded ${activeConnectors.length} connectors`,
        )
      } catch (error) {
        console.error("[NodePalette] Failed to fetch connectors:", error)
        // Set empty array on error to show "No connectors available" instead of loading forever
        setConnectors([])
        setHasFetchedConnectors(true)
      } finally {
        setIsConnectorsLoading(false)
      }
    }

    fetchConnectors()
  }, [isConnectorsExpanded, hasFetchedConnectors])

  // Fetch connector count on mount to show in header (lightweight)
  useEffect(() => {
    // Skip if already fetched (e.g., from expansion)
    if (hasFetchedConnectors) {
      return
    }

    const fetchConnectorCount = async () => {
      try {
        const data = await apiClient.request<
          { connectors?: any[]; total_count?: number } | any[]
        >(`/api/v1/connectors/list?include_custom=true`)

        // Handle both response formats: array or object with connectors property
        const connectorsList = Array.isArray(data)
          ? data
          : data.connectors || []

        // Filter out deprecated connectors
        const activeConnectors = connectorsList.filter(
          (c: Connector & { status?: string }) =>
            !c.status || c.status !== "deprecated",
        )

        // Set connectors for count display (will be refreshed if expanded)
        setConnectors(activeConnectors)
        setHasFetchedConnectors(true)
      } catch (error) {
        console.error("[NodePalette] Failed to fetch connector count:", error)
        // Don't set empty array here - let it show 0 until expanded
      }
    }

    fetchConnectorCount()
  }, [hasFetchedConnectors])

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

      // Calculate center position - will be handled by WorkflowBuilder
      // For now, use a placeholder that will be updated
      const newNode: Node = {
        id: `${nodeType.type}-${Date.now()}`,
        type: nodeType.type.startsWith("connector-")
          ? "connector"
          : nodeType.type,
        position: { x: 0, y: 0 }, // Will be calculated by WorkflowBuilder
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
    <div className="w-64 h-full bg-background border-r flex flex-col flex-shrink-0 overflow-hidden">
      <div className="p-4 border-b flex-shrink-0">
        <h2 className="text-lg font-semibold">Node Palette</h2>
        <p className="text-sm text-muted-foreground">
          Drag or click to add nodes
        </p>
      </div>

      <div className="p-2 space-y-4 overflow-y-auto flex-1 min-h-0">
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
          <Collapsible
            open={isConnectorsExpanded}
            onOpenChange={setIsConnectorsExpanded}
          >
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
                  connectorNodes.map((nodeType) => (
                    <ConnectorPaletteItem
                      key={nodeType.type}
                      nodeType={nodeType}
                      onDragStart={handleDragStart}
                      onClick={handleClick}
                    />
                  ))
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </div>
    </div>
  )
}
