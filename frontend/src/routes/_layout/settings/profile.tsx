import { createFileRoute } from "@tanstack/react-router"
import { ProfileSection } from "@/components/UserSettings/ProfileSection"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/profile")({
  component: ProfileSettings,
  head: () => ({
    meta: [
      {
        title: "Profile Settings - SynthralOS",
      },
    ],
  }),
})

function ProfileSettings() {
  return (
    <SettingsLayout currentSection="profile">
      <ProfileSection />
    </SettingsLayout>
  )
}
