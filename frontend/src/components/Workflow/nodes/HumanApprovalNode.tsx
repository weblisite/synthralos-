import { Handle, type NodeProps, Position } from "@xyflow/react"
import { UserCheck } from "lucide-react"

interface HumanApprovalNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function HumanApprovalNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as HumanApprovalNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-rose-50 to-pink-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-rose-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <UserCheck className="h-4 w-4 text-rose-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Human Approval"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
