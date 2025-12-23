import { createFileRoute } from "@tanstack/react-router"
import { TeamManagement } from "@/components/Teams/TeamManagement"

export const Route = createFileRoute("/_layout/teams")({
  component: TeamsPage,
  head: () => ({
    meta: [
      {
        title: "Teams - SynthralOS",
      },
    ],
  }),
})

function TeamsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Teams</h1>
        <p className="text-muted-foreground">
          Create and manage teams for collaboration
        </p>
      </div>
      <TeamManagement />
    </div>
  )
}
