/**
 * Scraping Node Component
 *
 * Node for web scraping operations.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Globe } from "lucide-react"

export function ScrapingNode({ data, selected }: NodeProps) {
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-amber-50 to-yellow-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-amber-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Globe className="h-4 w-4 text-amber-600" />
        <div className="font-semibold text-sm">{data.label || "Scraping"}</div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
