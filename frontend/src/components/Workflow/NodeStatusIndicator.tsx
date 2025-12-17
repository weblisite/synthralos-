/**
 * Node Status Indicator Component
 *
 * Visual indicator overlay for node execution status.
 */

import type { Node } from "@xyflow/react"
import { CheckCircle2, Loader2, PauseCircle, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"

interface NodeStatusIndicatorProps {
  node: Node
  status: "idle" | "running" | "completed" | "failed" | "paused"
}

export function NodeStatusIndicator({
  node,
  status,
}: NodeStatusIndicatorProps) {
  if (status === "idle") {
    return null
  }

  const getStatusIcon = () => {
    switch (status) {
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-600" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "paused":
        return <PauseCircle className="h-4 w-4 text-yellow-600" />
      default:
        return null
    }
  }

  const getStatusRing = () => {
    switch (status) {
      case "running":
        return "ring-2 ring-blue-500 ring-offset-2"
      case "completed":
        return "ring-2 ring-green-500 ring-offset-2"
      case "failed":
        return "ring-2 ring-red-500 ring-offset-2"
      case "paused":
        return "ring-2 ring-yellow-500 ring-offset-2"
      default:
        return ""
    }
  }

  return (
    <div
      className={cn(
        "absolute -top-2 -right-2 z-10 bg-white rounded-full shadow-lg p-1",
        getStatusRing(),
      )}
    >
      {getStatusIcon()}
    </div>
  )
}
