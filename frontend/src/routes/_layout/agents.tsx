import { createFileRoute } from "@tanstack/react-router"
import { AgentCatalog } from "@/components/Agents/AgentCatalog"

export const Route = createFileRoute("/_layout/agents")({
  component: AgentsPage,
  head: () => ({
    meta: [
      {
        title: "Agents - SynthralOS",
      },
    ],
  }),
})

function AgentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Agent Management</h1>
        <p className="text-muted-foreground mt-2">
          Browse, configure, and execute AI agent frameworks
        </p>
      </div>
      <AgentCatalog />
    </div>
  )
}
