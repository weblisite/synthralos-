/**
 * OCR Switch Node Component
 *
 * Node for OCR engine routing decisions.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { FileText } from "lucide-react"

interface OCRSwitchNodeData extends Record<string, unknown> {
  label?: string
  config?: Record<string, any>
}

export function OCRSwitchNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as OCRSwitchNodeData
  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-teal-50 to-emerald-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-teal-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <FileText className="h-4 w-4 text-teal-600" />
        <div className="font-semibold text-sm">
          {nodeData.label || "OCR Switch"}
        </div>
      </div>
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle
        type="source"
        position={Position.Right}
        id="doctr"
        className="w-3 h-3"
        style={{ top: "20%" }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="easyocr"
        className="w-3 h-3"
        style={{ top: "40%" }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="paddleocr"
        className="w-3 h-3"
        style={{ top: "60%" }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="tesseract"
        className="w-3 h-3"
        style={{ top: "80%" }}
      />
    </div>
  )
}
