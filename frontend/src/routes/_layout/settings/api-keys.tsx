import { createFileRoute } from "@tanstack/react-router"
import { APIKeys } from "@/components/UserSettings/APIKeys"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/api-keys")({
  component: APIKeysSettings,
  head: () => ({
    meta: [
      {
        title: "API Keys Settings - SynthralOS",
      },
    ],
  }),
})

function APIKeysSettings() {
  return (
    <SettingsLayout currentSection="api-keys">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">API Keys</h2>
          <p className="text-muted-foreground">
            Manage your API keys for external services
          </p>
        </div>
        <APIKeys />
      </div>
    </SettingsLayout>
  )
}
