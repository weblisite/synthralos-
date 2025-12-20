/**
 * Browser Node Component
 *
 * Node for browser automation operations.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Monitor } from "lucide-react"

interface BrowserNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function BrowserNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as BrowserNodeData
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-slate-50 to-gray-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-slate-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Monitor className="h-4 w-4 text-slate-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Browser"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
