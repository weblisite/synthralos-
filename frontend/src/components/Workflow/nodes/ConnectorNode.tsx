/**
 * Connector Node Component
 *
 * Node for connector actions.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Plug } from "lucide-react"

interface ConnectorNodeData extends Record<string, unknown> {
  label?: string
  config?: {
    connector_slug?: string
    action?: string
    [key: string]: any
  }
}

export function ConnectorNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as ConnectorNodeData
  const connectorName =
    nodeData.label || nodeData.config?.connector_slug || "Connector"

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-green-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Plug className="h-4 w-4 text-green-600" />
        <div className="font-semibold text-sm">{connectorName}</div>
      </div>
      {nodeData.config?.action && (
        <div className="text-xs text-muted-foreground mt-1">
          {nodeData.config.action}
        </div>
      )}
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
