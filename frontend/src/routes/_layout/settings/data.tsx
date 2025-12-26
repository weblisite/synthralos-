import { createFileRoute } from "@tanstack/react-router"
import { DataPrivacySection } from "@/components/UserSettings/DataPrivacySection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/data")({
  component: DataSettings,
  head: () => ({
    meta: [
      {
        title: "Data & Privacy Settings - SynthralOS",
      },
    ],
  }),
})

function DataSettings() {
  return (
    <SettingsLayout currentSection="data">
      <DataPrivacySection />
    </SettingsLayout>
  )
}
