import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Bell } from "lucide-react"

interface NotificationNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function NotificationNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as NotificationNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-sky-50 to-cyan-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-sky-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Bell className="h-4 w-4 text-sky-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Notification"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
