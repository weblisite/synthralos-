/**
 * Code Node Component
 *
 * Node for custom code execution.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Code } from "lucide-react"

export function CodeNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-orange-50 to-amber-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-orange-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Code className="h-4 w-4 text-orange-600" />
        <div className="font-semibold text-sm">{data.label || "Code"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
