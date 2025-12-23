import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Filter, Layers, Merge, RefreshCw, Split } from "lucide-react"

interface TransformNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function MapNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TransformNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-cyan-50 to-blue-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-cyan-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <RefreshCw className="h-4 w-4 text-cyan-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Map"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function FilterNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TransformNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-cyan-50 to-blue-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-cyan-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Filter className="h-4 w-4 text-cyan-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Filter"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function ReduceNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TransformNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-cyan-50 to-blue-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-cyan-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Layers className="h-4 w-4 text-cyan-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "Reduce"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function MergeNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TransformNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-cyan-50 to-blue-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-cyan-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Merge className="h-4 w-4 text-cyan-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Merge"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}

export function SplitNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as TransformNodeData

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-cyan-50 to-blue-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-cyan-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Split className="h-4 w-4 text-cyan-600" />
        <div className="font-semibold text-sm">{nodeData.label || "Split"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
