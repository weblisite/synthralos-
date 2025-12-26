import { createFileRoute } from "@tanstack/react-router"
import { SecuritySection } from "@/components/UserSettings/SecuritySection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/security" as any)({
  component: SecuritySettings,
  head: () => ({
    meta: [
      {
        title: "Security Settings - SynthralOS",
      },
    ],
  }),
})

function SecuritySettings() {
  return (
    <SettingsLayout currentSection="security">
      <SecuritySection />
    </SettingsLayout>
  )
}
