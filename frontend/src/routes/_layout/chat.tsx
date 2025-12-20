/**
 * Chat Page
 *
 * Main page for the conversational chat interface.
 */

import { createFileRoute } from "@tanstack/react-router"
import { ChatWindow } from "@/components/Chat/ChatWindow"

export const Route = createFileRoute("/_layout/chat")({
  component: ChatPage,
  head: () => ({
    meta: [
      {
        title: "Chat - SynthralOS",
      },
    ],
  }),
})

function ChatPage() {
  return (
    <div className="h-[calc(100vh-8rem)]">
      <ChatWindow />
    </div>
  )
}
