import { createFileRoute } from "@tanstack/react-router"
import { OSINTStreamManager } from "@/components/OSINT/OSINTStreamManager"

export const Route = createFileRoute("/_layout/osint")({
  component: OSINTPage,
  head: () => ({
    meta: [
      {
        title: "OSINT - SynthralOS",
      },
    ],
  }),
})

function OSINTPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">OSINT Management</h1>
        <p className="text-muted-foreground mt-2">
          Manage OSINT streams, signals, and alerts for real-time monitoring
        </p>
      </div>
      <OSINTStreamManager />
    </div>
  )
}
