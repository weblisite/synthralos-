/**
 * Logic Node Component
 *
 * Node for conditional logic and switches.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { GitBranch } from "lucide-react"

export function LogicNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-indigo-50 to-violet-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-indigo-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <GitBranch className="h-4 w-4 text-indigo-600" />
        <div className="font-semibold text-sm">{data.label || "Logic"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        className="w-3 h-3"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="false"
        className="w-3 h-3"
        style={{ top: "50%" }}
      />
    </div>
  )
}
