import { Handle, type NodeProps, Position } from "@xyflow/react"
import { ArrowRight, Pause } from "lucide-react"

interface ControlFlowNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function BreakNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as ControlFlowNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-gray-50 to-slate-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-gray-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Pause className="h-4 w-4 text-gray-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Break"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function ContinueNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as ControlFlowNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-gray-50 to-slate-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-gray-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <ArrowRight className="h-4 w-4 text-gray-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Continue"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
