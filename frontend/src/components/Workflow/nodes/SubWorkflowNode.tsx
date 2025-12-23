/**
 * Sub Workflow Node Component
 *
 * Visual representation of a sub-workflow node in the workflow canvas.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Workflow } from "lucide-react"

interface SubWorkflowNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function SubWorkflowNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as SubWorkflowNodeData
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-indigo-50 to-purple-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-indigo-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Workflow className="h-4 w-4 text-indigo-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Sub Workflow"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
