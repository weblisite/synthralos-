import { createFileRoute } from "@tanstack/react-router"
import { NotificationsSection } from "@/components/UserSettings/NotificationsSection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/notifications" as any)({
  component: NotificationsSettings,
  head: () => ({
    meta: [
      {
        title: "Notification Settings - SynthralOS",
      },
    ],
  }),
})

function NotificationsSettings() {
  return (
    <SettingsLayout currentSection="notifications">
      <NotificationsSection />
    </SettingsLayout>
  )
}
