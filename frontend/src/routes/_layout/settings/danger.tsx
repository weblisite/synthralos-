import { createFileRoute } from "@tanstack/react-router"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import { SettingsLayout } from "@/components/UserSettings/SettingsLayout"

export const Route = createFileRoute("/_layout/settings/danger" as any)({
  component: DangerZoneSettings,
  head: () => ({
    meta: [
      {
        title: "Danger Zone - SynthralOS",
      },
    ],
  }),
})

function DangerZoneSettings() {
  return (
    <SettingsLayout currentSection="danger">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Danger Zone</h2>
          <p className="text-muted-foreground">
            Irreversible and destructive actions
          </p>
        </div>
        <DeleteAccount />
      </div>
    </SettingsLayout>
  )
}
