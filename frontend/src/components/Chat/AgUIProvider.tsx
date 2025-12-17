/**
 * AgUI Provider Component
 *
 * Provider wrapper for ag-ui chat widget.
 * Manages chat state and WebSocket connections.
 */

import { createContext, useContext, useState, useCallback, useEffect, useRef, ReactNode } from "react"
import { supabase } from "@/lib/supabase"

interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: Date
  tool_calls?: Array<{
    id: string
    name: string
    arguments: Record<string, any>
  }>
}

interface ChatContextType {
  messages: ChatMessage[]
  isConnected: boolean
  isLoading: boolean
  sendMessage: (content: string, mode?: ChatMode) => Promise<void>
  clearMessages: () => void
  mode: ChatMode
  setMode: (mode: ChatMode) => void
}

type ChatMode = "automation" | "agent" | "agent_flow" | "code"

const ChatContext = createContext<ChatContextType | undefined>(undefined)

interface AgUIProviderProps {
  children: ReactNode
}

export function AgUIProvider({ children }: AgUIProviderProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [mode, setMode] = useState<ChatMode>("automation")
  const wsConnectionRef = useRef<WebSocket | null>(null)

  const connectWebSocket = useCallback(async () => {
    // Don't create a new connection if one already exists and is open
    if (wsConnectionRef.current && wsConnectionRef.current.readyState === WebSocket.OPEN) {
      setIsConnected(true)
      return
    }

    // Close existing connection if it exists
    if (wsConnectionRef.current) {
      wsConnectionRef.current.close()
      wsConnectionRef.current = null
    }

    try {
      const {
        data: { session },
      } = await supabase.auth.getSession()

      if (!session) {
        console.error("No session available for WebSocket connection")
        return
      }

      // WebSocket endpoint for ag-ui bridge
      const wsUrl = `ws://localhost:8000/api/v1/agws?token=${session.access_token}`
      const ws = new WebSocket(wsUrl)
      wsConnectionRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        console.log("WebSocket connected")
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          if (data.type === "message") {
            setMessages((prev) => [
              ...prev,
              {
                id: data.id || `msg-${Date.now()}`,
                role: data.role || "assistant",
                content: data.content || "",
                timestamp: new Date(data.timestamp || Date.now()),
                tool_calls: data.tool_calls,
              },
            ])
          } else if (data.type === "tool_call") {
            // Handle tool call updates
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === data.message_id
                  ? {
                      ...msg,
                      tool_calls: [...(msg.tool_calls || []), data.tool_call],
                    }
                  : msg,
              ),
            )
          } else if (data.type === "error") {
            console.error("WebSocket error:", data.error)
            setIsLoading(false)
          } else if (data.type === "done") {
            setIsLoading(false)
          }
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error)
        }
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        setIsConnected(false)
        setIsLoading(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        wsConnectionRef.current = null
        console.log("WebSocket disconnected")
      }
    } catch (error) {
      console.error("Failed to connect WebSocket:", error)
      setIsConnected(false)
      wsConnectionRef.current = null
    }
  }, [])

  const sendMessage = useCallback(
    async (content: string, messageMode?: ChatMode) => {
      const currentMode = messageMode || mode
      
      // Add user message
      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
        timestamp: new Date(),
      }
      
      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)

      try {
        const {
          data: { session },
        } = await supabase.auth.getSession()

        if (!session) {
          throw new Error("You must be logged in to send messages")
        }

        // If WebSocket is not connected, try to connect
        if (!wsConnectionRef.current || !isConnected) {
          await connectWebSocket()
          // Wait a bit for connection to establish
          await new Promise((resolve) => setTimeout(resolve, 500))
        }

        // Send via WebSocket if connected
        if (wsConnectionRef.current && isConnected) {
          wsConnectionRef.current.send(
            JSON.stringify({
              type: "message",
              content,
              mode: currentMode,
            }),
          )
        } else {
          // Fallback to HTTP POST
          const response = await fetch("/api/v1/chat", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${session.access_token}`,
            },
            body: JSON.stringify({
              message: content,
              mode: currentMode,
            }),
          })

          if (!response.ok) {
            throw new Error("Failed to send message")
          }

          const data = await response.json()
          
          // Handle streaming response if applicable
          if (data.message) {
            setMessages((prev) => [
              ...prev,
              {
                id: data.id || `assistant-${Date.now()}`,
                role: "assistant",
                content: data.message,
                timestamp: new Date(),
                tool_calls: data.tool_calls,
              },
            ])
          }
          
          setIsLoading(false)
        }
      } catch (error) {
        console.error("Failed to send message:", error)
        setMessages((prev) => [
          ...prev,
          {
            id: `error-${Date.now()}`,
            role: "system",
            content: `Error: ${error instanceof Error ? error.message : "Failed to send message"}`,
            timestamp: new Date(),
          },
        ])
        setIsLoading(false)
      }
    },
    [mode, isConnected, connectWebSocket],
  )

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  // Auto-connect on mount
  useEffect(() => {
    connectWebSocket()
    return () => {
      if (wsConnectionRef.current) {
        wsConnectionRef.current.close()
        wsConnectionRef.current = null
      }
    }
  }, [connectWebSocket])

  return (
    <ChatContext.Provider
      value={{
        messages,
        isConnected,
        isLoading,
        sendMessage,
        clearMessages,
        mode,
        setMode,
      }}
    >
      {children}
    </ChatContext.Provider>
  )
}

export function useChat() {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error("useChat must be used within AgUIProvider")
  }
  return context
}

