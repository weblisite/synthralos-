/**
 * Trigger Node Component
 *
 * Node for workflow triggers (webhook, schedule, manual).
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Play } from "lucide-react"
import { cn } from "@/lib/utils"
import { NodeStatusIndicator } from "../NodeStatusIndicator"

export function TriggerNode({ data, selected }: NodeProps) {
  const status = data.status || "idle"

  return (
    <div className="relative">
      <div
        className={cn(
          "px-4 py-2 shadow-lg rounded-lg bg-white border-2 min-w-[150px]",
          selected ? "border-primary" : "border-gray-300",
          status === "running" && "ring-2 ring-blue-500 ring-offset-2",
          status === "completed" && "ring-2 ring-green-500 ring-offset-2",
          status === "failed" && "ring-2 ring-red-500 ring-offset-2",
          status === "paused" && "ring-2 ring-yellow-500 ring-offset-2",
        )}
      >
        <div className="flex items-center gap-2">
          <Play className="h-4 w-4 text-primary" />
          <div className="font-semibold text-sm">{data.label || "Trigger"}</div>
        </div>
        <Handle type="source" position={Position.Right} className="w-3 h-3" />
      </div>
      <NodeStatusIndicator status={status} />
    </div>
  )
}
