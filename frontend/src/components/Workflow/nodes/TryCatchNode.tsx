import { Handle, type NodeProps, Position } from "@xyflow/react"
import { AlertTriangle } from "lucide-react"

interface TryCatchNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function TryNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TryCatchNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-red-50 to-pink-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-red-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Try"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function CatchNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TryCatchNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-red-50 to-pink-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-red-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Catch"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function FinallyNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TryCatchNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-red-50 to-pink-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-red-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Finally"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
