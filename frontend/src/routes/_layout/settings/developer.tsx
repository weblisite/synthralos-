import { createFileRoute } from "@tanstack/react-router"
import { DeveloperSection } from "@/components/UserSettings/DeveloperSection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/developer" as any)({
  component: DeveloperSettings,
  head: () => ({
    meta: [
      {
        title: "Developer Settings - SynthralOS",
      },
    ],
  }),
})

function DeveloperSettings() {
  return (
    <SettingsLayout currentSection="developer">
      <DeveloperSection />
    </SettingsLayout>
  )
}
