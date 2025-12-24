/**
 * Dashboard WebSocket Hook
 *
 * Provides real-time dashboard updates via WebSocket with polling fallback.
 * Automatically falls back to polling if WebSocket connection fails.
 */

import { useQueryClient } from "@tanstack/react-query"
import { useEffect, useRef, useState } from "react"
import { getApiUrl } from "@/lib/api"
import { supabase } from "@/lib/supabase"

interface WebSocketMessage {
  type: string
  event_type?: string
  data?: any
  timestamp?: string
  user_id?: string
  status?: string
}

export function useDashboardWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [usePollingFallback, setUsePollingFallback] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  // @ts-expect-error TS2554 - useQueryClient() parameter is optional but TypeScript incorrectly requires it
  const queryClient = useQueryClient()
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  useEffect(() => {
    const connect = async () => {
      // Get auth token
      const {
        data: { session },
      } = await supabase.auth.getSession()
      if (!session) {
        setUsePollingFallback(true)
        return
      }

      // Get WebSocket URL
      const apiUrl = getApiUrl()
      const wsProtocol = apiUrl.startsWith("https") ? "wss" : "ws"
      const wsHost = apiUrl.replace(/^https?:\/\//, "").replace(/\/$/, "")
      const wsUrl = `${wsProtocol}://${wsHost}/api/v1/realtime/dashboard?token=${session.access_token}`

      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen = () => {
          setIsConnected(true)
          setUsePollingFallback(false)
          reconnectAttemptsRef.current = 0
          console.log("[WebSocket] Dashboard connection established")

          // Subscribe to dashboard events
          ws.send(
            JSON.stringify({
              type: "subscribe",
              events: [
                "dashboard-stats-update",
                "execution-started",
                "execution-completed",
                "execution-failed",
                "system-metrics-update",
                "cost-analytics-update",
                "connector-stats-update",
              ],
            }),
          )
        }

        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            handleMessage(message)
          } catch (error) {
            console.error("[WebSocket] Failed to parse message:", error)
          }
        }

        ws.onerror = (error) => {
          console.error("[WebSocket] Connection error:", error)
          setIsConnected(false)
        }

        ws.onclose = () => {
          setIsConnected(false)
          wsRef.current = null

          // Reconnect logic
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1
            const delay = Math.min(
              1000 * 2 ** reconnectAttemptsRef.current,
              30000,
            )
            console.log(
              `[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`,
            )
            reconnectTimeoutRef.current = setTimeout(connect, delay)
          } else {
            // Max reconnect attempts reached, fall back to polling
            console.warn(
              "[WebSocket] Max reconnect attempts reached, falling back to polling",
            )
            setUsePollingFallback(true)
          }
        }
      } catch (error) {
        console.error("[WebSocket] Failed to create connection:", error)
        setUsePollingFallback(true)
      }
    }

    const handleMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case "connection":
          if (message.status === "connected") {
            console.log("[WebSocket] Connected to dashboard updates")
          }
          break

        case "user_update": {
          // Handle user-specific updates
          const eventType = message.event_type
          switch (eventType) {
            case "dashboard-stats-update":
            case "dashboard-stats-refresh":
              // Invalidate and refetch dashboard stats
              queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
              break

            case "execution-started":
            case "execution-completed":
            case "execution-failed":
              // Invalidate execution-related queries
              queryClient.invalidateQueries({
                queryKey: ["workflowExecutions"],
              })
              queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
              queryClient.invalidateQueries({ queryKey: ["workflowStats"] })
              break

            case "system-metrics-update":
              queryClient.invalidateQueries({ queryKey: ["systemMetrics"] })
              break

            case "cost-analytics-update":
              queryClient.invalidateQueries({ queryKey: ["costAnalytics"] })
              break

            case "connector-stats-update":
              queryClient.invalidateQueries({ queryKey: ["connectorStats"] })
              break

            default:
              console.log("[WebSocket] Unknown event type:", eventType)
          }
          break
        }

        case "pong":
          // Heartbeat response
          break

        case "error":
          console.error("[WebSocket] Server error:", message.data)
          break

        default:
          console.log("[WebSocket] Unknown message type:", message.type)
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [queryClient])

  return {
    isConnected,
    usePollingFallback,
  }
}
