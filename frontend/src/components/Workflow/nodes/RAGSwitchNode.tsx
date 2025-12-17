/**
 * RAG Switch Node Component
 *
 * Node for RAG routing decisions.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Database } from "lucide-react"

interface RAGSwitchNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function RAGSwitchNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as RAGSwitchNodeData
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-blue-50 to-cyan-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-blue-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Database className="h-4 w-4 text-blue-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "RAG Switch"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle
        type="source"
        position={Position.Right}
        id="chromadb"
        className="w-3 h-3"
        style={{ top: "25%" }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="milvus"
        className="w-3 h-3"
        style={{ top: "50%" }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="weaviate"
        className="w-3 h-3"
        style={{ top: "75%" }}
      />
    </div>
  )
}
