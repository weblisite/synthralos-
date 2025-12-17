/**
 * AI Node Component
 *
 * Node for AI prompt execution.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Brain } from "lucide-react"

export function AINode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-purple-50 to-blue-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-purple-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Brain className="h-4 w-4 text-purple-600" />
        <div className="font-semibold text-sm">{data.label || "AI Prompt"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
