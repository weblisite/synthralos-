/**
 * Connector Node Component
 *
 * Node for connector actions.
 */

import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Plug } from "lucide-react"
import { useEffect, useState } from "react"
import { getConnectorLogoUrls } from "@/lib/connectorLogos"

interface ConnectorNodeData extends Record<string, unknown> {
  label?: string
  config?: {
    connector_slug?: string
    action?: string
    logo?: string
    [key: string]: any
  }
}

export function ConnectorNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as ConnectorNodeData
  const connectorName =
    nodeData.label || nodeData.config?.connector_slug || "Connector"
  const connectorSlug = nodeData.config?.connector_slug
  const [logoUrl, setLogoUrl] = useState<string | null>(null)

  useEffect(() => {
    // Reset logo when connector changes
    setLogoUrl(null)

    if (!connectorSlug) {
      return
    }

    const customLogo = nodeData.config?.logo

    // If custom logo is provided, use it directly
    if (customLogo) {
      const img = new Image()
      img.onload = () => setLogoUrl(customLogo)
      img.onerror = () => {
        // Fall back to logo URLs if custom logo fails
        loadLogoFromUrls()
      }
      img.src = customLogo
      return
    }

    // Load logo from available sources
    loadLogoFromUrls()

    function loadLogoFromUrls() {
      // Get logo URLs using utility function
      const possiblePaths = getConnectorLogoUrls(connectorSlug, customLogo)

      if (possiblePaths.length === 0) {
        setLogoUrl(null)
        return
      }

      // Try to load logos sequentially
      let currentIndex = 0
      const tryNextLogo = () => {
        if (currentIndex >= possiblePaths.length) {
          setLogoUrl(null)
          return
        }

        const img = new Image()
        img.onload = () => {
          setLogoUrl(possiblePaths[currentIndex]!)
        }
        img.onerror = () => {
          currentIndex++
          tryNextLogo()
        }
        img.src = possiblePaths[currentIndex]!
      }

      tryNextLogo()
    }
  }, [connectorSlug, nodeData.config?.logo])

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-green-50 to-emerald-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-green-300"
      }`}
    >
      <div className="flex items-center gap-2">
        {logoUrl ? (
          <img
            src={logoUrl}
            alt={connectorName}
            className="h-5 w-5 object-contain flex-shrink-0"
            onError={() => setLogoUrl(null)}
          />
        ) : (
          <Plug className="h-4 w-4 text-green-600 flex-shrink-0" />
        )}
        <div className="font-semibold text-sm truncate">{connectorName}</div>
      </div>
      {nodeData.config?.action && (
        <div className="text-xs text-muted-foreground mt-1">
          {nodeData.config.action}
        </div>
      )}
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
