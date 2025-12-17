import { createFileRoute } from "@tanstack/react-router"
import { ConnectorCatalog } from "@/components/Connectors/ConnectorCatalog"

export const Route = createFileRoute("/_layout/connectors")({
  component: ConnectorsPage,
  head: () => ({
    meta: [
      {
        title: "Connectors - SynthralOS",
      },
    ],
  }),
})

function ConnectorsPage() {
  return (
    <div className="space-y-6">
      <ConnectorCatalog />
    </div>
  )
}
