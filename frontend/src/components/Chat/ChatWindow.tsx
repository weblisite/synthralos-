/**
 * Chat Window Component
 *
 * Main chat interface using ag-ui styling patterns.
 * Displays messages, handles input, and shows tool calls.
 */

import { Bot, Code, Send, X, Zap } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useChat } from "./AgUIProvider"
import { ToolCallCard } from "./ToolCallCard"

export function ChatWindow() {
  const { messages, isLoading, sendMessage, clearMessages, mode, setMode } =
    useChat()
  const [input, setInput] = useState("")
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector(
        "[data-radix-scroll-area-viewport]",
      )
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const message = input.trim()
    setInput("")
    await sendMessage(message, mode)

    // Focus input after sending
    inputRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const getModeIcon = (chatMode: string) => {
    switch (chatMode) {
      case "automation":
        return <Zap className="h-4 w-4" />
      case "agent":
        return <Bot className="h-4 w-4" />
      case "agent_flow":
        return <Bot className="h-4 w-4" />
      case "code":
        return <Code className="h-4 w-4" />
      default:
        return <Bot className="h-4 w-4" />
    }
  }

  return (
    <div className="flex flex-col h-full bg-background border-l">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold">Chat Assistant</h2>
          <Select value={mode} onValueChange={(value) => setMode(value as any)}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="automation">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  <span>Automation</span>
                </div>
              </SelectItem>
              <SelectItem value="agent">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  <span>Agent</span>
                </div>
              </SelectItem>
              <SelectItem value="agent_flow">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  <span>Agent Flow</span>
                </div>
              </SelectItem>
              <SelectItem value="code">
                <div className="flex items-center gap-2">
                  <Code className="h-4 w-4" />
                  <span>Code</span>
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={clearMessages}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
              <Bot className="h-12 w-12 mb-4 opacity-50" />
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm mt-2">
                Ask me to help you build workflows, write code, or automate
                tasks.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {message.role !== "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : message.role === "system"
                        ? "bg-muted text-muted-foreground"
                        : "bg-muted"
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap break-words">
                    {message.content}
                  </div>
                  {message.tool_calls && message.tool_calls.length > 0 && (
                    <div className="mt-2 space-y-2">
                      {message.tool_calls.map((toolCall, idx) => (
                        <ToolCallCard key={idx} toolCall={toolCall} />
                      ))}
                    </div>
                  )}
                  <div className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                {message.role === "user" && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <span className="text-xs font-medium text-primary-foreground">
                      U
                    </span>
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="h-4 w-4 text-primary" />
              </div>
              <div className="bg-muted rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-75" />
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse delay-150" />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Ask me anything in ${mode} mode...`}
            disabled={isLoading}
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex items-center gap-2 mt-2">
          <Badge variant="outline" className="text-xs">
            {getModeIcon(mode)}
            <span className="ml-1 capitalize">{mode}</span>
          </Badge>
          <span className="text-xs text-muted-foreground">
            Press Enter to send
          </span>
        </div>
      </div>
    </div>
  )
}
