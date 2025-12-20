/**
 * Tool Call Card Component
 *
 * Displays tool call information in chat messages.
 */

import { CheckCircle2, Code, Loader2, XCircle } from "lucide-react"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"

interface ToolCallCardProps {
  toolCall: {
    id: string
    name: string
    arguments: Record<string, any>
    status?: "pending" | "running" | "completed" | "failed"
    result?: any
    error?: string
  }
}

export function ToolCallCard({ toolCall }: ToolCallCardProps) {
  const [isOpen, setIsOpen] = useState(false)

  const getStatusIcon = () => {
    switch (toolCall.status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-600" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "running":
        return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />
      default:
        return <Code className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = () => {
    switch (toolCall.status) {
      case "completed":
        return "bg-green-50 border-green-200"
      case "failed":
        return "bg-red-50 border-red-200"
      case "running":
        return "bg-blue-50 border-blue-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card className={`${getStatusColor()} border`}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-opacity-80 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusIcon()}
                <CardTitle className="text-sm font-medium">
                  {toolCall.name}
                </CardTitle>
              </div>
              <Badge variant="outline" className="text-xs">
                {toolCall.status || "pending"}
              </Badge>
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <CardContent className="pt-0 space-y-3">
            <div>
              <h4 className="text-xs font-semibold mb-1 text-muted-foreground">
                Arguments
              </h4>
              <pre className="text-xs bg-background p-2 rounded border overflow-auto max-h-40">
                {JSON.stringify(toolCall.arguments, null, 2)}
              </pre>
            </div>
            {toolCall.result && (
              <div>
                <h4 className="text-xs font-semibold mb-1 text-muted-foreground">
                  Result
                </h4>
                <pre className="text-xs bg-background p-2 rounded border overflow-auto max-h-40">
                  {JSON.stringify(toolCall.result, null, 2)}
                </pre>
              </div>
            )}
            {toolCall.error && (
              <div>
                <h4 className="text-xs font-semibold mb-1 text-red-600">
                  Error
                </h4>
                <p className="text-xs text-red-600 bg-red-50 p-2 rounded border border-red-200">
                  {toolCall.error}
                </p>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  )
}
