import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Repeat } from "lucide-react"

interface LoopNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function LoopNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as LoopNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-purple-50 to-indigo-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-purple-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Repeat className="h-4 w-4 text-purple-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Loop"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
