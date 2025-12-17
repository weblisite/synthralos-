/**
 * Node Palette Component
 *
 * Drag-and-drop palette of available workflow nodes.
 */

import type { Node } from "@xyflow/react"
import {
  Brain,
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
import { useCallback, useMemo } from "react"

interface NodeType {
  type: string
  label: string
  icon: React.ComponentType<{ className?: string }>
  category: string
  description: string
}

const nodeTypes: NodeType[] = [
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
    type: "connector",
    label: "Connector",
    icon: Plug,
    category: "Integrations",
    description: "SaaS app integration",
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
  const handleDragStart = useCallback(
    (event: React.DragEvent, nodeType: NodeType) => {
      event.dataTransfer.setData("application/reactflow", nodeType.type)
      event.dataTransfer.effectAllowed = "move"
    },
    [],
  )

  const handleClick = useCallback(
    (nodeType: NodeType) => {
      if (!onNodeAdd) return

      const newNode: Node = {
        id: `${nodeType.type}-${Date.now()}`,
        type: nodeType.type,
        position: { x: Math.random() * 400, y: Math.random() * 400 },
        data: {
          label: nodeType.label,
          config: {},
        },
      }

      onNodeAdd(newNode)
    },
    [onNodeAdd],
  )

  const groupedNodes = useMemo(() => {
    const groups: Record<string, NodeType[]> = {}
    nodeTypes.forEach((nodeType) => {
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
      </div>
    </div>
  )
}
