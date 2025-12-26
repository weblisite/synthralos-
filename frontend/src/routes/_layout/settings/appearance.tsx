import { createFileRoute } from "@tanstack/react-router"
import { AppearanceSection } from "@/components/UserSettings/AppearanceSection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/appearance" as any)({
  component: AppearanceSettings,
  head: () => ({
    meta: [
      {
        title: "Appearance Settings - SynthralOS",
      },
    ],
  }),
})

function AppearanceSettings() {
  return (
    <SettingsLayout currentSection="appearance">
      <AppearanceSection />
    </SettingsLayout>
  )
}
