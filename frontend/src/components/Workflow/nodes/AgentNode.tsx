/**
 * Agent Node Component
 *
 * Visual representation of an agent node in the workflow canvas.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Bot } from "lucide-react"

interface AgentNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function AgentNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as AgentNodeData
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-green-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Bot className="h-4 w-4 text-green-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Agent"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
