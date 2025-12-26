import { createFileRoute } from "@tanstack/react-router"
import { IntegrationsSection } from "@/components/UserSettings/IntegrationsSection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/integrations" as any)({
  component: IntegrationsSettings,
  head: () => ({
    meta: [
      {
        title: "Integrations Settings - SynthralOS",
      },
    ],
  }),
})

function IntegrationsSettings() {
  return (
    <SettingsLayout currentSection="integrations">
      <IntegrationsSection />
    </SettingsLayout>
  )
}
