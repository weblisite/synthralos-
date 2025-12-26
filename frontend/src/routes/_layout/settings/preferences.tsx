import { createFileRoute } from "@tanstack/react-router"
import { PreferencesSection } from "@/components/UserSettings/PreferencesSection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/preferences" as any)({
  component: PreferencesSettings,
  head: () => ({
    meta: [
      {
        title: "Preferences Settings - SynthralOS",
      },
    ],
  }),
})

function PreferencesSettings() {
  return (
    <SettingsLayout currentSection="preferences">
      <PreferencesSection />
    </SettingsLayout>
  )
}
