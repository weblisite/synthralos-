import { createFileRoute } from "@tanstack/react-router"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"
import { TeamsSection } from "@/components/UserSettings/TeamsSection"

export const Route = createFileRoute("/_layout/settings/teams" as any)({
  component: TeamsSettings,
  head: () => ({
    meta: [
      {
        title: "Teams Settings - SynthralOS",
      },
    ],
  }),
})

function TeamsSettings() {
  return (
    <SettingsLayout currentSection="teams">
      <TeamsSection />
    </SettingsLayout>
  )
}
