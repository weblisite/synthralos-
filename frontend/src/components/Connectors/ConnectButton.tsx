import { useState } from "react"
import { toast } from "sonner"
import { apiClient } from "@/lib/apiClient"

interface ConnectButtonProps {
  connectorId: string
  connectorName: string
  instanceId?: string
  onConnected?: () => void
  className?: string
}

export function ConnectButton({
  connectorId,
  connectorName,
  instanceId,
  onConnected,
  className = "",
}: ConnectButtonProps) {
  const [isConnecting, setIsConnecting] = useState(false)

  const handleConnect = async () => {
    setIsConnecting(true)

    try {
      // Build URL with query params
      const url = new URL(
        `/api/v1/connectors/${connectorId}/connect`,
        window.location.origin,
      )
      if (instanceId) {
        url.searchParams.set("instance_id", instanceId)
      }

      // Get OAuth URL from backend
      const response = await apiClient.request<{
        oauth_url: string | null
        connection_id: string
        nango_connection_id: string
        popup: boolean
        already_connected?: boolean
        message?: string
      }>(url.pathname + url.search, {
        method: "POST",
      })

      // If already connected, show message and return
      if (response.already_connected) {
        toast.success(response.message || "Already connected")
        setIsConnecting(false)
        onConnected?.()
        return
      }

      if (!response.oauth_url) {
        toast.error("Failed to get OAuth URL")
        setIsConnecting(false)
        return
      }

      // Open popup window
      const width = 600
      const height = 700
      const left = window.screenX + (window.outerWidth - width) / 2
      const top = window.screenY + (window.outerHeight - height) / 2

      const popupWindow = window.open(
        response.oauth_url,
        `Connect ${connectorName}`,
        `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`,
      )

      if (!popupWindow) {
        toast.error("Popup blocked. Please allow popups for this site.")
        setIsConnecting(false)
        return
      }

      // Listen for OAuth completion
      const checkPopup = setInterval(() => {
        if (popupWindow.closed) {
          clearInterval(checkPopup)
          setIsConnecting(false)
          // Check connection status
          onConnected?.()
        }
      }, 500)

      // Listen for message from popup (if Nango sends postMessage)
      const messageHandler = (event: MessageEvent) => {
        // Verify origin for security
        if (event.origin !== window.location.origin) {
          return
        }

        if (
          event.data.type === "NANGO_OAUTH_SUCCESS" ||
          event.data.type === "OAUTH_SUCCESS"
        ) {
          popupWindow?.close()
          setIsConnecting(false)
          toast.success(`Successfully connected to ${connectorName}`)
          onConnected?.()
          window.removeEventListener("message", messageHandler)
        } else if (
          event.data.type === "NANGO_OAUTH_ERROR" ||
          event.data.type === "OAUTH_ERROR"
        ) {
          popupWindow?.close()
          setIsConnecting(false)
          toast.error(
            event.data.message || `Failed to connect to ${connectorName}`,
          )
          window.removeEventListener("message", messageHandler)
        }
      }

      window.addEventListener("message", messageHandler)

      // Cleanup on unmount
      return () => {
        clearInterval(checkPopup)
        window.removeEventListener("message", messageHandler)
      }
    } catch (error: any) {
      console.error("Failed to connect:", error)
      toast.error(error.message || `Failed to connect to ${connectorName}`)
      setIsConnecting(false)
    }
  }

  return (
    <button
      onClick={handleConnect}
      disabled={isConnecting}
      className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {isConnecting ? (
        <span className="flex items-center gap-2">
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          Connecting...
        </span>
      ) : (
        "Connect"
      )}
    </button>
  )
}
