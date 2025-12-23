import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Download, Save } from "lucide-react"

interface VariableNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function SetVariableNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as VariableNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-yellow-50 to-orange-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-yellow-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Save className="h-4 w-4 text-yellow-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Set Variable"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function GetVariableNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as VariableNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-yellow-50 to-orange-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-yellow-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Download className="h-4 w-4 text-yellow-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Get Variable"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
