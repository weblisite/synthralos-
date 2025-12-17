import { createFileRoute } from "@tanstack/react-router"
import { BrowserSessionManager } from "@/components/Browser/BrowserSessionManager"

export const Route = createFileRoute("/_layout/browser")({
  component: BrowserPage,
  head: () => ({
    meta: [
      {
        title: "Browser - SynthralOS",
      },
    ],
  }),
})

function BrowserPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Browser Management</h1>
        <p className="text-muted-foreground mt-2">
          Manage browser automation sessions and actions
        </p>
      </div>
      <BrowserSessionManager />
    </div>
  )
}
