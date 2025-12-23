import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Database } from "lucide-react"

interface StorageNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function StorageNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as StorageNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-emerald-50 to-teal-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-emerald-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Database className="h-4 w-4 text-emerald-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Storage"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
